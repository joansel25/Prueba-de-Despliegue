from rest_framework import viewsets
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import Usuario
from .serializers import UsuarioSerializer, CustomTokenObtainPairSerializer

# 🔹 Login JWT personalizado
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

# 🔹 CRUD de usuarios
class UsuarioViewset(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UsuarioViewset, CustomTokenObtainPairView

router = DefaultRouter()
router.register(r'usuarios', UsuarioViewset)

urlpatterns = [
    path('auth/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('', include(router.urls)),
]