from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from .serializers import (
    UserSerailizer,
    UserCreateSerializer,
    LoginSerializer,
    ChangePasswordSerializer,
)
from rest_framework.pagination import LimitOffsetPagination


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        refresh = RefreshToken.for_user(user)

        response = Response(
            {
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
                "user": UserSerailizer(user).data,
            }
        )
        response.set_cookie(
            key="access_token",
            value=str(refresh.access_token),
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=70,  # TODO set the max age for 3600 again
        )
        response.set_cookie(
            key="refresh_token",
            value=str(refresh),
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=604800,
        )
        return response


class RefreshTokenView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            refresh_token = request.COOKIES.get("refresh_token")
            if not refresh_token:
                return Response(
                    {"detail": "refresh token not provided "},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
            try:
                refresh = RefreshToken(refresh_token)
            except Exception as error:
                return Response(
                    {"detail": f"Invalid or expired refresh token: {str(error)}"},
                    status=401,
                )
            access_token = str(refresh.access_token)
            response = Response(
                {"detail": "successfully refreshed the access token"},
                status=status.HTTP_200_OK,
            )
            response.set_cookie(
                key="access_token",
                value=access_token,
                httponly=True,
                secure=True,
                samesite="lax",
                max_age=3600,
            )
            return response
        except Exception as error:
            return Response(
                {"detail": "Invalid or expired refresh token {error}"},
                status=status.HTTP_401_UNAUTHORIZED,
            )


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.COOKIES.get("refresh_token")
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            response = Response(
                {"detail": "successfully logged out"}, status=status.HTTP_200_OK
            )
            response.delete_cookie("access_token")
            response.delete_cookie("refresh_token")
            return response
        except Exception as error:
            response = Response(
                {"detail": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST
            )
            response.delete_cookie("access_token")
            response.delete_cookie("refresh_token")
            return response


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    pagination_class = LimitOffsetPagination

    def get_serializer_class(self):
        if self.action == "create":
            return UserCreateSerializer
        else:
            return UserSerailizer

    def get_permissions(self):
        if self.action == "create":
            return [AllowAny()]
        elif self.action in ["update", "partial_update", "destroy"]:
            return [IsAdminUser()]
        else:
            return [IsAuthenticated()]

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated])
    def change_password(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data["new_password"])
        request.user.save()

        return Response(
            {"detail": "Password changed successfully"}, status=status.HTTP_200_OK
        )


class AuthCheckView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"authenticated": True, "user": request.user.username})
