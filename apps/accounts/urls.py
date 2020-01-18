from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views as v

router = DefaultRouter(trailing_slash=False)
router.register(r'users', v.UserViewSet)
router.register(r'permissions', v.UserPermissionViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/obtain_token', v.ObtainJWTAPIView.as_view()),
    path('auth/verify_token', v.VerifyJWTAPIView.as_view()),
]
