from django import forms
from captcha.fields import CaptchaField

class RegisterForm(forms.Form):
    username = forms.CharField(label="نام کاربری", max_length=150)
    email = forms.EmailField(label="ایمیل")
    password = forms.CharField(label="رمز عبور", widget=forms.PasswordInput)
    captcha = CaptchaField(label="کد امنیتی")  # اضافه کردن فیلد کپچا

class LoginForm(forms.Form):
    username = forms.CharField(label="نام کاربری", max_length=150)
    password = forms.CharField(label="رمز عبور", widget=forms.PasswordInput)
    captcha = CaptchaField(label="کد امنیتی")  # اضافه کردن فیلد کپچا