# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FileViewSet, VideoViewSet,RealTimeViewSet

router = DefaultRouter()
router.register(r'files', FileViewSet)
router.register(r'videos', VideoViewSet)
router.register(r'live', RealTimeViewSet)

urlpatterns = [
    path('upload/', include(router.urls)),
]
