from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import SearchLog, User
from django.contrib.auth.hashers import make_password
from .models import Word
from django.contrib.auth.hashers import check_password
from .forms import LoginForm, RegisterForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth import get_user_model
from django.contrib.auth.views import PasswordResetConfirmView
from django.db.models import Count
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            # بررسی وجود کاربر
            if User.objects.filter(username=username).exists():
                messages.error(request, 'کاربری با این نام کاربری وجود دارد.')
            elif User.objects.filter(email=email).exists():
                messages.error(request, 'کاربری با این ایمیل وجود دارد.')
            else:
                # ذخیره کاربر جدید
                user = User(username=username, email=email, password=make_password(password))
                user.save()
                  # ذخیره نشست کاربر جدید
                login(request, user)
                messages.success(request, 'ثبت‌نام با موفقیت انجام شد! شما وارد سیستم شده‌اید.')
                return redirect('manage')  # انتقال به صفحه مدیریت
        else:
            messages.error(request, 'لطفاً اطلاعات وارد شده را بررسی کنید.')
    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


User = get_user_model()  # استفاده از مدل کاربر سفارشی

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            # بررسی کاربر
            user = User.objects.filter(username=username).first()
            if user and check_password(password, user.password):
                login(request, user)  # بررسی رمز عبور هش‌شده
                messages.success(request, f'خوش آمدید، {user.username}!')
                return redirect('manage')  # انتقال به صفحه مدیریت کلمات
            else:
                messages.error(request, 'نام کاربری یا رمز عبور اشتباه است.')
        else:
            messages.error(request, 'لطفاً اطلاعات وارد شده را بررسی کنید.')
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})



@login_required
def manage_words(request):
    # دریافت کلمات مربوط به کاربر جاری
    words = Word.objects.filter(user=request.user)
    existing_word = None  # برای ارسال به قالب
    is_admin = request.user.is_admin  # بررسی اینکه کاربر ادمین است یا خیر

    if request.method == 'POST':
        word = request.POST.get('word')
        definition = request.POST.get('definition')

        if not word or not definition:
            messages.error(request, 'لطفاً تمامی فیلدها را پر کنید.')
        else:
            # بررسی وجود کلمه
            existing_word = Word.objects.filter(user=request.user, word=word).first()

            if existing_word:
                # اگر کلمه وجود دارد، پیام هشدار به قالب ارسال می‌شود
                messages.warning(request, f'کلمه "{word}" قبلاً ذخیره شده است. آیا مایل به ویرایش آن هستید؟')
                return render(request, 'accounts/manage.html', {
                    'words': words,
                    'username': request.user.username,
                    'is_admin': is_admin,  # مقدار is_admin را به قالب ارسال می‌کنیم
                    'existing_word': existing_word,
                })
            else:
                # افزودن کلمه جدید
                Word.objects.create(user=request.user, word=word, definition=definition)
                messages.success(request, f'کلمه "{word}" اضافه شد.')
                return redirect('manage')

    return render(request, 'accounts/manage.html', {
        'words': words,
        'username': request.user.username,
        'is_admin': is_admin,  # مقدار is_admin را به قالب ارسال می‌کنیم
        'existing_word': existing_word,
    })



def home(request):
    if request.user.is_authenticated:
        return redirect('manage')  # کاربر وارد شده است، به صفحه مدیریت برود
    else:
        return redirect('login')  # کاربر وارد نشده است، به صفحه ورود برود


@login_required
def delete_word(request, word_id):
    word = Word.objects.filter(id=word_id, user=request.user).first()  # فقط کلمات کاربر جاری قابل حذف هستند
    if word:
        word.delete()
        messages.success(request, f'کلمه "{word.word}" حذف شد.')
    else:
        messages.error(request, 'کلمه موردنظر یافت نشد.')
    return redirect('manage')


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    def form_valid(self, form):
        user = form.save()
        print("Password changed for user:", user.username)
        return super().form_valid(form)
    
@login_required
def search_words(request):
    # بررسی اینکه کاربر وارد شده است یا خیر
    if not request.user.is_authenticated:
        return redirect('login')  # اگر کاربر وارد نشده باشد، به صفحه ورود هدایت شود

    query = request.GET.get('query', '').strip()  # دریافت کوئری از فرم
    results = []  # پیش‌فرض: نتایج خالی

    if query:  # اگر کوئری وجود داشت
        # جستجو فقط در کلماتی که توسط کاربر فعلی اضافه شده‌اند
        results = Word.objects.filter(
            Q(word__icontains=query) | Q(definition__icontains=query),
            user=request.user  # فیلتر کردن کلمات متعلق به کاربر فعلی
        )
         # ذخیره جستجو در مدل SearchLog
        for result in results:
            SearchLog.objects.create(user=request.user, word=result)

    return render(request, 'accounts/search.html', {'results': results, 'query': query})

def is_admin(user):
    return user.is_authenticated and user.is_admin  # یا user.is_staff اگر از مدل پیش‌فرض Django استفاده می‌کنید

@login_required
def statistics_view(request):
    # بررسی اینکه کاربر ادمین است یا خیر
    if not request.user.is_admin:
        messages.error(request, "دسترسی به این صفحه فقط برای ادمین امکان‌پذیر است.")
        return redirect('manage')  # هدایت به صفحه مدیریت لغات

    # محاسبه تعداد کل کاربران و کلمات
    total_users = User.objects.count()
    total_words = Word.objects.count()

    # پیدا کردن محبوب‌ترین کلمه جستجو شده
    most_searched = SearchLog.objects.values('word__word').annotate(search_count=Count('id')).order_by('-search_count').first()
    most_searched_word_name = most_searched['word__word'] if most_searched else "هیچ کلمه‌ای"

    context = {
        'total_users': total_users,
        'total_words': total_words,
        'most_searched_word': most_searched_word_name,
    }
    return render(request, 'accounts/statistics.html', context)



def edit_word(request, word_id):
    word = get_object_or_404(Word, id=word_id, user=request.user)  # کلمه باید متعلق به کاربر باشد

    if request.method == 'POST':
        new_word = request.POST.get('word').strip()
        new_definition = request.POST.get('definition').strip()

        if not new_word or not new_definition:
            messages.error(request, 'لطفاً تمامی فیلدها را پر کنید.')
        else:
            word.word = new_word
            word.definition = new_definition
            word.save()
            messages.success(request, 'تغییرات با موفقیت ذخیره شد!')
            return redirect('manage')

    return render(request, 'accounts/edit_word.html', {'word': word, 'username': request.user.username})
