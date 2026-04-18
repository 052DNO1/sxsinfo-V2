"""
缓存配置路由
"""

from django.urls import path
from rest_framework.routers import DefaultRouter
from apps.cache_config.views import (
    CacheConfigViewSet, ApiStatsViewSet, CacheOperationLogViewSet,
    CacheClearView, CacheConfigOverviewView, AutoDiscoverAPIView
)

router = DefaultRouter()
router.register(r'configs', CacheConfigViewSet, basename='cache-config')
router.register(r'stats', ApiStatsViewSet, basename='api-stats')
router.register(r'logs', CacheOperationLogViewSet, basename='cache-log')

urlpatterns = [
    path('clear/', CacheClearView.as_view(), name='cache-clear'),
    path('overview/', CacheConfigOverviewView.as_view(), name='cache-overview'),
    path('auto-discover/', AutoDiscoverAPIView.as_view(), name='cache-auto-discover'),
]

urlpatterns += router.urls
