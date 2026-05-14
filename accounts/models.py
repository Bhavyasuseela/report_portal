from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
import random
from django.utils import timezone
from datetime import timedelta


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')
        extra_fields.setdefault('must_reset_password', False)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('author', 'Author'),
        ('convener', 'Convener'),
        ('reviewer', 'Reviewer'),
        ('librarian', 'Librarian'),
        ('head', 'Head'),
        ('admin', 'Admin'),
    ]
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=200, blank=True)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    designation = models.CharField(max_length=200, blank=True)
    department = models.CharField(max_length=200, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='author')
    is_active = models.BooleanField(default=True)
    is_approved = models.BooleanField(default=False,
        help_text='For self-registered authors: must be approved by admin before they can log in.')
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(blank=True, null=True)

    # Multi-role support: comma-separated list of extra roles this user can log in as
    # e.g. "author" means a reviewer can also log in as author
    extra_roles = models.CharField(max_length=200, blank=True, default='',
        help_text='Comma-separated additional roles this user can access')

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'User'

    def __str__(self):
        return f"{self.email} ({self.role})"

    def get_all_roles(self):
        """Return all roles this user can access."""
        roles = [self.role]
        if self.extra_roles:
            for r in self.extra_roles.split(','):
                r = r.strip()
                if r and r not in roles:
                    roles.append(r)
        return roles

    def can_access_role(self, role):
        return role in self.get_all_roles()

    def generate_otp(self):
        self.otp = str(random.randint(100000, 999999))
        self.otp_created_at = timezone.now()
        self.save()
        return self.otp

    def verify_otp(self, entered_otp):
        if not self.otp or not self.otp_created_at:
            return False
        expiry = self.otp_created_at + timedelta(minutes=10)
        if timezone.now() > expiry:
            return False
        return self.otp == entered_otp

    def clear_otp(self):
        self.otp = None
        self.otp_created_at = None
        self.save()

    # Flag: user must reset password on next login (for default passwords)
    must_reset_password = models.BooleanField(default=True)

    # Password reset via email link
    password_reset_token = models.CharField(max_length=64, blank=True, null=True)
    password_reset_expires = models.DateTimeField(blank=True, null=True)

    def generate_password_reset_token(self):
        import secrets
        self.password_reset_token = secrets.token_urlsafe(32)
        self.password_reset_expires = timezone.now() + timedelta(hours=1)
        self.save()
        return self.password_reset_token

    def verify_password_reset_token(self, token):
        if not self.password_reset_token or not self.password_reset_expires:
            return False
        if timezone.now() > self.password_reset_expires:
            return False
        return self.password_reset_token == token

    def clear_password_reset_token(self):
        self.password_reset_token = None
        self.password_reset_expires = None
        self.save()
