from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from .serializers import UserSignupSerializer, LoginSerializer
from .models import UserStatus
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from .serializers import ProfileUpdateSerializer, ChangePasswordSerializer,MagicLinkForgotSerializer,MagicLinkVerifySerializer,MagicLinkConfirmSerializer


class SignUpView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        s = UserSignupSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        s.save() 
        return Response({"message": "User created successfully"}, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        s = LoginSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        user = s.validated_data

        refresh = RefreshToken.for_user(user)
        return Response({"access_token": str(refresh.access_token)}, status=200)


def _file_abs_url(request, f):
    try:
        if f and getattr(f, "name", None):
            return request.build_absolute_uri(f.url)
    except Exception:
        return None
    return None

class ProfileView(APIView):
    """
    GET  /api/accounts/profile/   
    PATCH /api/accounts/profile/  
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def get(self, request):
        u = request.user
        return Response({
            "email": u.email,
            "first_name": u.first_name,
            "last_name": u.last_name,
            "phone_number": u.phone_number,
            "governorate": u.governorate,
            "city": u.city,
            "street": u.street,
            "status": u.status,
            "photo":             _file_abs_url(request, u.photo),         
            "id_card_front":     _file_abs_url(request, u.id_card_front), 
            "id_card_back":      _file_abs_url(request, u.id_card_back),  
            "national_id_number":  u.national_id_number,                  
            "national_id_barcode": u.national_id_barcode                  
        }, status=200)


    def patch(self, request):
        s = ProfileUpdateSerializer(instance=request.user, data=request.data, partial=True)
        s.is_valid(raise_exception=True)
        user = s.save()

        def abs_url(f):
            return request.build_absolute_uri(f.url) if getattr(f, "url", None) else None

        return Response({
            "detail": "Profile updated",
            "user": {
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "phone_number": user.phone_number,
                "governorate": user.governorate,
                "city": user.city,
                "street": user.street,
                "status": user.status,
                "photo":           abs_url(user.photo),
                # الجديد:
                "id_card_front":   abs_url(user.id_card_front),
                "id_card_back":    abs_url(user.id_card_back),
                "national_id_number":  user.national_id_number,
                "national_id_barcode": user.national_id_barcode,
            }
        }, status=200)


class DeactivateMeView(APIView):
    """
    Soft-delete endpoint: user presses 'delete' -> we mark DEACTIVATED
    Login within 30 days will restore automatically; after that, purge job will hard-delete.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        u = request.user
        if u.status == UserStatus.BANNED:
            return Response({"detail": "Account is banned."}, status=403)
        if u.status == UserStatus.SUSPENDED:
            return Response({"detail": "Account is suspended."}, status=403)
        if u.status == UserStatus.DEACTIVATED:
            return Response({"detail": "Already deactivated."}, status=200)

        u.soft_deactivate()
        return Response({"detail": "Account deactivated. You can restore by logging in within 30 days."}, status=200)



class ChangePasswordView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        s = ChangePasswordSerializer(data=request.data, context={"request": request})
        s.is_valid(raise_exception=True)
        s.save()
        return Response({"detail": "Password updated successfully."}, status=200)


class PasswordForgotMagicLinkView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        s = MagicLinkForgotSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        s.save(request=request)
        return Response({"detail": "If that email exists, a reset link was sent."}, status=200)


class PasswordResetVerifyView(APIView):

    permission_classes = [permissions.AllowAny]

    def get(self, request):
        s = MagicLinkVerifySerializer(data={"token": request.query_params.get("token", "")})
        s.is_valid(raise_exception=True)
        return Response({"detail": "Token is valid."}, status=200)


class PasswordResetConfirmView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        s = MagicLinkConfirmSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        s.save()
        return Response({"detail": "Password updated successfully."}, status=200)
