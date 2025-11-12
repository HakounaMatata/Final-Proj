from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, UserStatus
from django.core.validators import FileExtensionValidator
from django.contrib.auth.password_validation import validate_password
from .utils import make_reset_token, read_reset_token
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.core.mail import send_mail

MAX_PHOTO_MB = 3
VALID_EXTS = {"jpg", "jpeg", "png", "webp"}
class UserSignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "email", "password",
            "first_name", "last_name",
            "phone_number", "governorate", "city", "street",
            "photo",
        ]

    def create(self, validated):
        photo = validated.pop("photo", None)
        user = User.objects.create_user(**validated)
        if photo:
            user.photo = photo
            user.save(update_fields=["photo"])
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data["email"].strip().lower()
        password = data["password"]

        user = User.objects.filter(email=email).first()
        if not user or not user.check_password(password):
            raise serializers.ValidationError({"detail": "Invalid credentials."})

        if user.status == UserStatus.BANNED:
            raise serializers.ValidationError({"detail": "Account is banned."})
        if user.status == UserStatus.SUSPENDED:
            raise serializers.ValidationError({"detail": "Account is suspended."})

        if user.status == UserStatus.DEACTIVATED:
            if user.soft_window_expired():
                user.delete()
                raise serializers.ValidationError({"detail": "Account permanently deleted."})
            user.restore()

        return user


class ProfileUpdateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=False)

    class Meta:
        model = User
        fields = [
            "email",
            "first_name", "last_name",
            "phone_number", "governorate", "city", "street",
            "photo","id_card_front", "id_card_back",
            "national_id_number", "national_id_barcode",
        ]
        extra_kwargs = {
            "first_name": {"required": False},
            "last_name": {"required": False},
            "phone_number": {"required": False},
            "governorate": {"required": False},
            "city": {"required": False},
            "street": {"required": False},
            "photo": {"required": False},
            "id_card_front": {"required": False},
            "id_card_back": {"required": False},
            "national_id_number": {"required": False, "allow_null": True, "allow_blank": True},
            "national_id_barcode": {"required": False, "allow_null": True, "allow_blank": True},
        }

    def validate_email(self, value):
        user = self.instance
        if value and value.lower() != user.email.lower():
            if User.objects.filter(email__iexact=value).exclude(pk=user.pk).exists():
                raise serializers.ValidationError("This email is already in use.")
        return value


    def _validate_image(self, value):
        if not value:
            return value
        if value.size > MAX_PHOTO_MB * 1024 * 1024:
            raise serializers.ValidationError(f"Image too large (>{MAX_PHOTO_MB}MB).")
        ext = (value.name.rsplit(".", 1)[-1].lower() if "." in value.name else "")
        if ext not in VALID_EXTS:
            raise serializers.ValidationError("Only JPG/JPEG/PNG/WebP are allowed.")
        return value

    def validate_photo(self, value):
        return self._validate_image(value)

    # NEW:
    def validate_id_card_front(self, value):
        return self._validate_image(value)

    def validate_id_card_back(self, value):
        return self._validate_image(value)

    def validate_national_id_number(self, value):
        if value in (None, ""):
            return value
        v = str(value).strip()
        if len(v) != 14 or not v.isdigit():
            raise serializers.ValidationError("National ID must be exactly 14 digits.")
        return v

    def update(self, instance, validated_data):
        email = validated_data.get("email")
        if email:
            instance.email = email.strip().lower()

        for field in ["first_name", "last_name", "phone_number", "governorate", "city", "street",
                      "national_id_number", "national_id_barcode"]:
            if field in validated_data:
                setattr(instance, field, validated_data[field])

        for img_field in ["photo", "id_card_front", "id_card_back"]:
            if img_field in validated_data and validated_data[img_field]:
                setattr(instance, img_field, validated_data[img_field])

        if "photo" in validated_data and validated_data["photo"]:
            instance.photo = validated_data["photo"]

        instance.save()
        return instance


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = self.context["request"].user
        if not user.check_password(data["current_password"]):
            raise serializers.ValidationError({"current_password": "Incorrect current password."})
        validate_password(data["new_password"], user=user)
        return data

    def save(self, **kwargs):
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.save(update_fields=["password"])
        return user




class MagicLinkForgotSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def save(self, *, request):
        email = self.validated_data["email"].strip().lower()
        user = User.objects.filter(email__iexact=email).first()

        if not user:
            return

        token = make_reset_token({"uid": user.pk})

        frontend_url = getattr(settings, "SITE_URL", "http://localhost:5173")
        link = f"{frontend_url}/reset-password?token={token}"

        subject = "Password Reset"
        message = f"Click the link to reset your password (valid for 30 minutes):\n{link}"
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=True)


class MagicLinkVerifySerializer(serializers.Serializer):
    token = serializers.CharField()

    def validate(self, data):
        try:
            payload = read_reset_token(data["token"])
            data["uid"] = payload.get("uid")
        except ValueError as e:
            raise serializers.ValidationError({"detail": str(e)})
        return data


class MagicLinkConfirmSerializer(serializers.Serializer):
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        if data["new_password"] != data["confirm_password"]:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        try:
            payload = read_reset_token(data["token"])
            data["uid"] = payload.get("uid")
        except ValueError as e:
            raise serializers.ValidationError({"detail": str(e)})

        user = get_object_or_404(User, pk=data["uid"])
        validate_password(data["new_password"], user=user)
        return data

    def save(self):
        from .models import UserStatus
        uid = self.validated_data["uid"]
        user = get_object_or_404(User, pk=uid)
        user.set_password(self.validated_data["new_password"])

        if getattr(user, "status", None) == "DEACTIVATED":
            try:
                user.restore()
            except Exception:
                pass

        user.save(update_fields=["password"])
        return user
