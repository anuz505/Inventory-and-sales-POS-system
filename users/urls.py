from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, LoginView, LogoutView, RefreshTokenView

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="users")

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("refresh/", RefreshTokenView.as_view(), name="refresh_token"),
    path("", include(router.urls)),
]
