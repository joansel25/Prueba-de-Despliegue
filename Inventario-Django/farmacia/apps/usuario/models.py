from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from model_utils.models import TimeStampedModel

class Rol(models.Model):
    name = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return self.name

class UsuarioLegacy(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.name

class Usuario(AbstractUser ):             
    telefono = models.CharField(max_length=20, blank=True, null=True)
    rol = models.ForeignKey(Rol, null=True, blank=True, on_delete=models.SET_NULL, related_name='usuarios')#unique
    objects = UserManager()

    def __str__(self):
        return self.username
