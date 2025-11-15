from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from .models import Usuario, Rol
from .serializers import UsuarioSerializer

User = get_user_model()

class UsuarioModelTests(TestCase):
    def setUp(self):
        """Configuración inicial para pruebas del modelo Usuario"""
        self.rol_cliente = Rol.objects.create(name='cliente')
        self.usuario_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'rol': self.rol_cliente,
            'telefono': '1234567890'
        }

    def test_crear_usuario(self):
        """Prueba para crear un nuevo usuario en la base de datos"""
        usuario = Usuario.objects.create_user(**self.usuario_data)
        # Verificar que el usuario se creó correctamente
        self.assertEqual(usuario.username, 'testuser')
        self.assertEqual(usuario.rol, self.rol_cliente)
        self.assertEqual(usuario.telefono, '1234567890')
        self.assertTrue(usuario.check_password('testpass123'))

    def test_crear_superusuario(self):
        """Prueba para crear un superusuario"""
        superuser = Usuario.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123',
            telefono='0987654321'
        )

        self.assertTrue(superuser.is_superuser)
        self.assertTrue(superuser.is_staff)

    def test_str_representation(self):
        """Prueba la representación en string del modelo"""
        usuario = Usuario.objects.create_user(**self.usuario_data)
        expected_str = usuario.username
        self.assertEqual(str(usuario), expected_str)

    def test_campos_obligatorios(self):
        """Prueba que los campos obligatorios funcionen correctamente"""
        with self.assertRaises(ValueError):
            Usuario.objects.create_user(username='', password='testpass123')

class UsuarioAPITests(APITestCase):
    def setUp(self):
        """Configuración inicial para pruebas de API"""
        # Crear roles
        self.rol_empleado = Rol.objects.create(name='empleado')
        self.rol_cliente = Rol.objects.create(name='cliente')
        self.rol_proveedor = Rol.objects.create(name='proveedor')

        # Crear usuario para autenticación
        self.user = Usuario.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            rol=self.rol_empleado,
            telefono='1234567890'
        )
        
        # Crear otro usuario para pruebas
        self.other_user = Usuario.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123',
            rol=self.rol_cliente,
            telefono='0987654321'
        )
        
        # Datos para crear nuevo usuario
        self.new_user_data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'newpass123',
            'rol': self.rol_proveedor.id,
            'telefono': '5555555555'
        }
        
        self.client.force_authenticate(user=self.user)

    def test_listar_usuarios_sin_autenticacion(self):
        """Prueba listar usuarios SIN autenticación"""
        self.client.force_authenticate(user=None)
        url = reverse('usuario-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_listar_usuarios_con_autenticacion(self):
        """Prueba listar usuarios CON autenticación"""
        url = reverse('usuario-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_crear_usuario_sin_autenticacion(self):
        """Prueba crear usuario SIN autenticación"""
        self.client.force_authenticate(user=None)  
        url = reverse('usuario-list')
        response = self.client.post(url, self.new_user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_crear_usuario_con_autenticacion(self):
        """Prueba crear usuario CON autenticación"""
        url = reverse('usuario-list')
        response = self.client.post(url, self.new_user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Usuario.objects.count(), 3)
        self.assertEqual(response.data['username'], 'newuser')
        self.assertEqual(response.data['rol'], self.rol_proveedor.id)

    def test_obtener_usuario_especifico_con_autenticacion(self):
        """Prueba obtener un usuario específico CON autenticación"""
        url = reverse('usuario-detail', args=[self.other_user.id])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'otheruser')
        self.assertEqual(response.data['rol'], self.rol_cliente.id)

    def test_actualizar_usuario_con_autenticacion(self):
        """Prueba actualizar un usuario CON autenticación"""
        url = reverse('usuario-detail', args=[self.user.id])
        
        # Usar PATCH para actualización parcial
        updated_data = {
            'username': 'user_updated',
            'email': 'updated@example.com',
            'rol': self.rol_empleado.id,
            'telefono': '9999999999'
        }
        
        response = self.client.patch(url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'user_updated')
        self.assertEqual(self.user.telefono, '9999999999')
        self.assertEqual(self.user.email, 'updated@example.com')

    def test_actualizar_usuario_sin_autenticacion(self):
        """Prueba actualizar un usuario SIN autenticación"""
        self.client.force_authenticate(user=None)
        url = reverse('usuario-detail', args=[self.user.id])
        updated_data = {'username': 'user_updated'}
        response = self.client.patch(url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_eliminar_usuario_con_autenticacion(self):
        """Prueba eliminar un usuario CON autenticación"""
        url = reverse('usuario-detail', args=[self.other_user.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Usuario.objects.count(), 1)

    def test_eliminar_usuario_sin_autenticacion(self):
        """Prueba eliminar un usuario SIN autenticación"""
        self.client.force_authenticate(user=None)  
        url = reverse('usuario-detail', args=[self.user.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_roles_validos(self):
        """Prueba que solo se acepten roles válidos"""
        invalid_user_data = {
            'username': 'invaliduser',
            'email': 'invalid@example.com',
            'password': 'invalidpass123',
            'rol': 9999,  
            'telefono': '1111111111'
        }
        url = reverse('usuario-list')
        response = self.client.post(url, invalid_user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_username_unico(self):
        """Prueba que el username sea único"""
        duplicate_user_data = {
            'username': 'testuser', 
            'email': 'different@example.com',
            'password': 'differentpass123',
            'rol': self.rol_cliente.id,
            'telefono': '2222222222'
        }
        url = reverse('usuario-list')
        response = self.client.post(url, duplicate_user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_campos_requeridos(self):
        """Prueba que los campos requeridos sean obligatorios"""
        incomplete_data = {
            'username': 'incompleteuser',
        }
        url = reverse('usuario-list')
        response = self.client.post(url, incomplete_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class UsuarioSerializerTests(TestCase):
    def setUp(self):
        self.rol_cliente = Rol.objects.create(name='cliente')
        self.rol_empleado = Rol.objects.create(name='empleado')

    def test_serializer_valido(self):
        """Prueba que el serializer valide datos correctos"""
        data = {
            'username': 'serializertest',
            'email': 'serializer@example.com',
            'password': 'serializerpass123',
            'rol': self.rol_cliente.id,
            'telefono': '3333333333'
        }
        serializer = UsuarioSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_serializer_invalido(self):
        """Prueba que el serializer rechace datos incorrectos"""
        data = {
            'username': '',  
            'email': 'invalid-email', 
            'rol': 9999  
        }
        serializer = UsuarioSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('username', serializer.errors)
        self.assertIn('email', serializer.errors)
        self.assertIn('rol', serializer.errors)

    def test_serializer_representation(self):
        """Prueba la representación del serializer"""
        usuario = Usuario.objects.create_user(
            username='repruser',
            email='repr@example.com',
            password='reprpass123',
            rol=self.rol_empleado,
            telefono='4444444444'
        )
        serializer = UsuarioSerializer(usuario)
        self.assertIn('username', serializer.data)
        self.assertIn('email', serializer.data)
        self.assertIn('rol', serializer.data)
        self.assertIn('telefono', serializer.data)