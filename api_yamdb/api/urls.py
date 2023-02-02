from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import APIGetToken, APIUserSignup


router_v1 = DefaultRouter()
router_v1.register()

urlpatterns = [
    path('v1/auth/signup/', APIUserSignup.as_view(), name='api_signup'),
    path('v1/auth/token/', APIGetToken.as_view(), name='api_get_token'),
    path('v1/', include(router_v1.urls)),

]
