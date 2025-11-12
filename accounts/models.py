from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from datetime import timedelta
from django.core.validators import RegexValidator


class UserStatus(models.TextChoices):
    ACTIVE = "ACTIVE", "Active"
    DEACTIVATED = "DEACTIVATED", "Deactivated"
    SUSPENDED = "SUSPENDED", "Suspended"
    BANNED = "BANNED", "Banned"

def id_front_upload_to(instance, filename):
    return f"id_cards/{instance.pk}/front/{filename}"

def id_back_upload_to(instance, filename):
    return f"id_cards/{instance.pk}/back/{filename}"

class UserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, phone_number, governorate, city, street, password=None, **extra):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            governorate=governorate,
            city=city,
            street=street,
            status=UserStatus.ACTIVE,
            **extra
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name="Admin", last_name="User", password=None, **extra):
        user = self.create_user(
            email=email,
            first_name=first_name,
            last_name=last_name,
            phone_number=extra.get("phone_number", "0000000000"),
            governorate=extra.get("governorate", "N/A"),
            city=extra.get("city", "N/A"),
            street=extra.get("street", "N/A"),
            password=password,
        )
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


def avatar_upload_to(instance, filename):
    return f"avatars/{instance.pk}/{filename}"


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)

    first_name = models.CharField(max_length=50)
    last_name  = models.CharField(max_length=50)

    phone_number = models.CharField(max_length=15)
    governorate  = models.CharField(max_length=255)
    city         = models.CharField(max_length=255)
    street       = models.CharField(max_length=255)

    photo = models.ImageField(upload_to=avatar_upload_to, default="avatars/default.png", blank=True)

    status = models.CharField(max_length=16, choices=UserStatus.choices, default=UserStatus.ACTIVE, db_index=True)
    id_card_front = models.ImageField(upload_to=id_front_upload_to, blank=True, null=True)
    id_card_back  = models.ImageField(upload_to=id_back_upload_to,  blank=True, null=True)
    national_id_number = models.CharField(
        max_length=14,
        blank=True,
        null=True,
        unique=True,
        validators=[RegexValidator(regex=r"^\d{14}$", message="National ID must be 14 digits.")]
    )
    national_id_barcode = models.CharField(
        max_length=64,
        blank=True,
        null=True
    )
    deactivated_at = models.DateTimeField(null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff  = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name", "phone_number", "governorate", "city", "street"]

    objects = UserManager()

    def __str__(self):
        return self.email

    SOFT_DELETE_WINDOW_DAYS = 30

    def soft_deactivate(self):
        self.status = UserStatus.DEACTIVATED
        self.deactivated_at = timezone.now()
        self.is_active = False 
        self.save(update_fields=["status", "deactivated_at", "is_active"])

    def can_be_restored(self) -> bool:
        if self.status != UserStatus.DEACTIVATED or not self.deactivated_at:
            return False
        return timezone.now() <= self.deactivated_at + timedelta(days=self.SOFT_DELETE_WINDOW_DAYS)

    def restore(self):
        self.status = UserStatus.ACTIVE
        self.deactivated_at = None
        self.is_active = True
        self.save(update_fields=["status", "deactivated_at", "is_active"])

    def soft_window_expired(self) -> bool:
        return (self.status == UserStatus.DEACTIVATED
                and self.deactivated_at
                and timezone.now() > self.deactivated_at + timedelta(days=self.SOFT_DELETE_WINDOW_DAYS))
