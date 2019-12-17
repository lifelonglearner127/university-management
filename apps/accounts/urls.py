from django.urls import path
from . import views as v

urlpatterns = [
    path('auth/obtain_token', v.ObtainJWTAPIView.as_view()),
    path('auth/verify_token', v.VerifyJWTAPIView.as_view()),
]
