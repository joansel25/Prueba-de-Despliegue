from rest_framework import viewsets
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import Usuario, Rol
from .serializers import (
    UsuarioSerializer,
    RolSerializer,
    CustomTokenObtainPairSerializer
)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class UsuarioViewset(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer

class RolViewset(viewsets.ModelViewSet):
    queryset = Rol.objects.all()
    serializer_class = RolSerializer
