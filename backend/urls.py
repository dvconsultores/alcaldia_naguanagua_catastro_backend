from rest_framework.authtoken import views as vx
from rest_framework import routers
from django.urls import include, path
from . import views

router = routers.DefaultRouter()
router.register(r'ambito', views.AmbitoViewset,basename='ambito')
urlpatterns = [
    # Base
    path('', include(router.urls)),
    path('signin/', views.SignIn),
]