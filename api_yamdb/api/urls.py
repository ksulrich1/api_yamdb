from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework.routers import SimpleRouter

from .views import APIGetToken, APIUserSignup
from .views import (APIGetToken, CommentViewSet,
                    ReviewViewSet)

router_v1 = DefaultRouter()
router = SimpleRouter()
router_v1.register()

router.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='reviews'
)
router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comments'
)

urlpatterns = [
    path('v1/auth/signup/', APIUserSignup.as_view(), name='api_signup'),
    path('v1/auth/token/', APIGetToken.as_view(), name='api_get_token'),
    path('v1/', include(router_v1.urls)),

]
