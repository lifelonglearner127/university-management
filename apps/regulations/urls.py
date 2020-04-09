from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views as v


router = DefaultRouter(trailing_slash=False)
router.register(r'attendance-places', v.AttendancePlaceViewSet)
router.register(r'attendance-times', v.AttendanceTimeViewSet)
router.register(r'attendance-rules', v.AttendanceRuleViewSet)
router.register(r'attendance-daily-reports', v.AttendanceDailyReportViewSet)
router.register(r'attendance-date-person-reports', v.AttendanceDatePersonViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('attendance-status', v.AttendanceStatusAPIView.as_view()),
    path('attend', v.AttendAPIView.as_view()),
    path('attendance-comment', v.AttendanceCommentAPIView.as_view())
]
