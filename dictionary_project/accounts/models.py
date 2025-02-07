from django.db import models
from django.conf import settings
from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models

class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None):
        if not email:
            raise ValueError('ایمیل الزامی است.')
        if not username:
            raise ValueError('نام کاربری الزامی است.')

        user = self.model(
            email=self.normalize_email(email),
            username=username,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None):
        user = self.create_user(
            username=username,
            email=email,
            password=password,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

class Word(models.Model):
    word = models.CharField(max_length=100)
    definition = models.TextField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    def __str__(self):
        return self.word

    class Meta:
        unique_together = ('word', 'user')  # هر کاربر فقط یک کلمه خاص را می‌تواند ذخیره کند


class SearchLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)  # کاربری که جستجو کرده
    word = models.ForeignKey('Word', on_delete=models.CASCADE)  # کلمه‌ای که جستجو شده
    timestamp = models.DateTimeField(auto_now_add=True)  # زمان جستجو

    def __str__(self):
        return f"{self.user} - {self.word}"
