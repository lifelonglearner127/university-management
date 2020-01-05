from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views as v


router = DefaultRouter(trailing_slash=False)
router.register(r'departments', v.DepartmentViewSet)
router.register(r'teachers', v.TeacherViewSet)

urlpatterns = [
    path('', include(router.urls))
]
