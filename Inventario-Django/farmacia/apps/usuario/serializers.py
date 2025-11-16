from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Usuario, Rol



class RolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rol
        fields = '__all__'



class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = '__all__'
        extra_kwargs = {
            "password": {"write_only": True}  
        }

   
    def create(self, validated_data):
        password = validated_data.pop("password", None)
        user = Usuario(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user



class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Serializer personalizado para añadir datos extras al token JWT"""

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)


        token['username'] = user.username
        token['email'] = user.email
        token['telefono'] = user.telefono
        token['rol'] = user.rol.name if user.rol else None

        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        data['user'] = {
            "id": self.user.id,
            "username": self.user.username,
            "email": self.user.email,
            "telefono": self.user.telefono,
            "rol": self.user.rol.name if self.user.rol else None,
        }

        return data
