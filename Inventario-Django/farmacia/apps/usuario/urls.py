from django.urls import path
from .views import CustomTokenObtainPairView
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'usuarios', UsuarioViewset, basename='usuario')
router.register(r'roles', RolViewset, basename='roles')

urlpatterns = router.urls