from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from .models import *
from .pdf import *
from io import BytesIO
from rest_framework_simplejwt.tokens import RefreshToken
from ..usuario.models import Rol  

User = get_user_model()

class AuthenticationTestCase(APITestCase):
    """Pruebas de autenticación JWT"""
    
    def setUp(self):
        self.client = APIClient()
        self.user_data = {
            'username': 'testuser',
            'password': 'testpass123',
            'email': 'test@example.com'
        }
        self.user = User.objects.create_user(**self.user_data)
    
    def test_jwt_authentication(self):
        """Prueba la obtención de tokens JWT"""
        url = reverse('token_obtain_pair')
        response = self.client.post(url, {
            'username': self.user_data['username'],
            'password': self.user_data['password']
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
    
    def test_protected_endpoint_without_token(self):
        """Prueba acceso a endpoint protegido sin token"""
        url = reverse('producto-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_protected_endpoint_with_token(self):
        """Prueba acceso a endpoint protegido con token válido"""
        refresh = RefreshToken.for_user(self.user)
        access_token = str(refresh.access_token)
        
        url = reverse('producto-list')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.get(url)
        
        # Puede ser 200 OK o 403 FORBIDDEN dependiendo de los permisos
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN])

class PermissionTestCase(APITestCase):
    """Pruebas de permisos personalizados"""
    
    def setUp(self):
        self.client = APIClient()
        
        
        self.rol_admin = Rol.objects.create(name='administrador')
        self.rol_employee = Rol.objects.create(name='empleado')
        self.rol_client = Rol.objects.create(name='cliente')
        
    
        self.admin_user = User.objects.create_user(
            username='admin', 
            password='adminpass123',
            email='admin@example.com'
        )
        self.admin_user.rol = self.rol_admin
        self.admin_user.save()
        
        self.employee_user = User.objects.create_user(
            username='employee',
            password='employeepass123',
            email='employee@example.com'
        )
        self.employee_user.rol = self.rol_employee
        self.employee_user.save()
        
        self.client_user = User.objects.create_user(
            username='client',
            password='clientpass123',
            email='client@example.com'
        )
        self.client_user.rol = self.rol_client
        self.client_user.save()
        
     
        self.categoria = Categoria.objects.create(nombre='Medicamentos')
        self.proveedor = Proveedor.objects.create(
            nombre='Proveedor Test', 
            contacto='test@proveedor.com',
            usuario=self.admin_user
        )
        
        self.producto = Producto.objects.create(
            nombre='Paracetamol', 
            precio=10.50, 
            stock=100,
            id_categoria=self.categoria, 
            id_proveedor=self.proveedor
        )
        
        self.cliente = Cliente.objects.create(
            nombre='Cliente Test', 
            correo='cliente@test.com', 
            telefono='3101234567',
            usuario=self.client_user
        )
        
        self.empleado = Empleado.objects.create(
            nombre='Empleado Test', 
            telefono='3111111111',
            usuario=self.employee_user
        )

class CategoriaCRUDTestCase(APITestCase):
    """Pruebas CRUD completas para el modelo Categoria"""
    
    def setUp(self):
        self.client = APIClient()
      
        self.rol_admin = Rol.objects.create(name='administrador')
        
        self.admin_user = User.objects.create_user(
            username='admin', 
            password='adminpass123',
            email='admin@example.com'
        )
        self.admin_user.rol = self.rol_admin
        self.admin_user.save()
        
       
        refresh = RefreshToken.for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}')
        
        self.categoria_data = {'nombre': 'Vitaminas'}
        self.categoria = Categoria.objects.create(nombre='Medicamentos')
    
    def test_crear_categoria(self):
        """Prueba creación de categoría"""
        url = reverse('categoria-list')
        response = self.client.post(url, self.categoria_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Categoria.objects.count(), 2)
        self.assertEqual(response.data['nombre'], 'Vitaminas')
    
    def test_listar_categorias(self):
        """Prueba listado de categorías"""
        url = reverse('categoria-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_obtener_categoria_especifica(self):
        """Prueba obtener categoría específica"""
        url = reverse('categoria-detail', args=[self.categoria.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nombre'], 'Medicamentos')
    
    def test_actualizar_categoria(self):
        """Prueba actualización de categoría"""
        url = reverse('categoria-detail', args=[self.categoria.id])
        updated_data = {'nombre': 'Medicamentos Generales'}
        response = self.client.patch(url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.categoria.refresh_from_db()
        self.assertEqual(self.categoria.nombre, 'Medicamentos Generales')
    
    def test_eliminar_categoria(self):
        """Prueba eliminación de categoría"""
        url = reverse('categoria-detail', args=[self.categoria.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Categoria.objects.filter(id=self.categoria.id).exists())

class ProductoCRUDTestCase(APITestCase):
    """Pruebas CRUD completas para el modelo Producto"""
    
    def setUp(self):
        self.client = APIClient()
        # Crear rol admin
        self.rol_admin = Rol.objects.create(name='administrador')
        
        self.admin_user = User.objects.create_user(
            username='admin', 
            password='adminpass123',
            email='admin@example.com'
        )
        self.admin_user.rol = self.rol_admin
        self.admin_user.save()
        
        # Autenticar como admin
        refresh = RefreshToken.for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}')
        
        # Datos de prueba
        self.categoria = Categoria.objects.create(nombre='Medicamentos')
        self.proveedor = Proveedor.objects.create(
            nombre='Proveedor Test', 
            contacto='test@proveedor.com',
            usuario=self.admin_user
        )
        
        self.producto_data = {
            'nombre': 'Ibuprofeno',
            'precio': 15.75,
            'stock': 50,
            'id_categoria': self.categoria.id,
            'id_proveedor': self.proveedor.id
        }
        
        self.producto = Producto.objects.create(
            nombre='Paracetamol', 
            precio=10.50, 
            stock=100,
            id_categoria=self.categoria, 
            id_proveedor=self.proveedor
        )
    
    def test_crear_producto(self):
        """Prueba creación de producto"""
        url = reverse('producto-list')
        response = self.client.post(url, self.producto_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Producto.objects.count(), 2)
        self.assertEqual(Producto.objects.get(nombre='Ibuprofeno').precio, 15.75)
    
    def test_listar_productos(self):
        """Prueba listado de productos"""
        url = reverse('producto-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_obtener_producto_especifico(self):
        """Prueba obtener producto específico"""
        url = reverse('producto-detail', args=[self.producto.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nombre'], 'Paracetamol')
    
    def test_actualizar_producto(self):
        """Prueba actualización de producto"""
        url = reverse('producto-detail', args=[self.producto.id])
        updated_data = {'precio': 12.25, 'stock': 150}
        response = self.client.patch(url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.precio, 12.25)
        self.assertEqual(self.producto.stock, 150)
    
    def test_eliminar_producto(self):
        """Prueba eliminación de producto"""
        url = reverse('producto-detail', args=[self.producto.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Producto.objects.filter(id=self.producto.id).exists())

class MovimientoCRUDTestCase(APITestCase):
    """Pruebas CRUD completas para el modelo Movimiento"""

    def setUp(self):
        self.client = APIClient()
        # Crear roles
        self.rol_admin = Rol.objects.create(name='administrador')
        self.rol_client = Rol.objects.create(name='cliente')

        self.admin_user = User.objects.create_user(
            username='admin', 
            password='adminpass123',
            email='admin@example.com'
        )
        self.admin_user.rol = self.rol_admin
        self.admin_user.save()

        self.client_user = User.objects.create_user(
            username='client',
            password='clientpass123',
            email='client@example.com'
        )
        self.client_user.rol = self.rol_client
        self.client_user.save()

        # Autenticar como admin
        refresh = RefreshToken.for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}')

        # Datos de prueba
        self.categoria = Categoria.objects.create(nombre='Medicamentos')
        self.proveedor = Proveedor.objects.create(
            nombre='Proveedor Test', 
            contacto='test@proveedor.com',
            usuario=self.admin_user
        )
        self.producto = Producto.objects.create(
            nombre='Paracetamol', 
            precio=10.50, 
            stock=100,
            id_categoria=self.categoria, 
            id_proveedor=self.proveedor
        )
        self.cliente = Cliente.objects.create(
            nombre='Cliente Test', 
            correo='cliente@test.com', 
            telefono='3101234567',
            usuario=self.client_user
        )

        self.movimiento_data = {
            'tipo': 'entrada',
            'cantidad': 10,
            'id_producto': self.producto.id,
            'id_cliente': self.cliente.id
        }

        self.movimiento = Movimiento.objects.create(
            tipo='salida', 
            cantidad=5, 
            id_producto=self.producto, 
            id_cliente=self.cliente
        )

    def test_crear_movimiento(self):
        """Prueba creación de movimiento"""
        url = reverse('movimiento-list')
        response = self.client.post(url, self.movimiento_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Movimiento.objects.count(), 2)
        self.assertEqual(Movimiento.objects.get(tipo='entrada').cantidad, 10)

    def test_listar_movimientos(self):
        """Prueba listado de movimientos"""
        url = reverse('movimiento-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_obtener_movimiento_especifico(self):
        """Prueba obtener movimiento específico"""
        url = reverse('movimiento-detail', args=[self.movimiento.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['tipo'], 'salida')

    def test_actualizar_movimiento(self):
        """Prueba actualización de movimiento"""
        url = reverse('movimiento-detail', args=[self.movimiento.id])
        updated_data = {'cantidad': 15}
        response = self.client.patch(url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.movimiento.refresh_from_db()
        self.assertEqual(self.movimiento.cantidad, 15)

    def test_eliminar_movimiento(self):
        """Prueba eliminación de movimiento"""
        url = reverse('movimiento-detail', args=[self.movimiento.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Movimiento.objects.filter(id=self.movimiento.id).exists())

class DetalleVentaCRUDTestCase(APITestCase):
    """Pruebas CRUD completas para el modelo DetalleVenta"""

    def setUp(self):
        self.client = APIClient()
        # Crear roles
        self.rol_admin = Rol.objects.create(name='administrador')
        self.rol_employee = Rol.objects.create(name='empleado')
        self.rol_client = Rol.objects.create(name='cliente')

        self.admin_user = User.objects.create_user(
            username='admin', 
            password='adminpass123',
            email='admin@example.com'
        )
        self.admin_user.rol = self.rol_admin
        self.admin_user.save()

        self.employee_user = User.objects.create_user(
            username='employee',
            password='employeepass123',
            email='employee@example.com'
        )
        self.employee_user.rol = self.rol_employee
        self.employee_user.save()

        self.client_user = User.objects.create_user(
            username='client',
            password='clientpass123',
            email='client@example.com'
        )
        self.client_user.rol = self.rol_client
        self.client_user.save()

        # Autenticar como admin
        refresh = RefreshToken.for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}')

        # Datos de prueba
        self.categoria = Categoria.objects.create(nombre='Medicamentos')
        self.proveedor = Proveedor.objects.create(
            nombre='Proveedor Test', 
            contacto='test@proveedor.com',
            usuario=self.admin_user
        )
        self.producto = Producto.objects.create(
            nombre='Paracetamol', 
            precio=10.50, 
            stock=100,
            id_categoria=self.categoria, 
            id_proveedor=self.proveedor
        )
        self.cliente = Cliente.objects.create(
            nombre='Cliente Test', 
            correo='cliente@test.com', 
            telefono='3101234567',
            usuario=self.client_user
        )
        self.empleado = Empleado.objects.create(
            nombre='Empleado Test', 
            telefono='3111111111',
            usuario=self.employee_user
        )
        self.factura = FacturaVenta.objects.create(
            id_cliente=self.cliente,
            id_empleado=self.empleado
        )

        self.detalle_venta_data = {
            'cantidad': 3,
            'precio_unitario': 12.00,
            'id_factura': self.factura.id,
            'id_producto': self.producto.id
        }

        self.detalle_venta = DetalleVenta.objects.create(
            cantidad=2, 
            precio_unitario=10.50, 
            id_factura=self.factura, 
            id_producto=self.producto
        )

    def test_crear_detalle_venta(self):
        """Prueba creación de detalle de venta"""
        url = reverse('detalleventa-list')
        response = self.client.post(url, self.detalle_venta_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(DetalleVenta.objects.count(), 2)
        self.assertEqual(DetalleVenta.objects.get(cantidad=3).precio_unitario, 12.00)

    def test_listar_detalles_venta(self):
        """Prueba listado de detalles de venta"""
        url = reverse('detalleventa-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_obtener_detalle_venta_especifico(self):
        """Prueba obtener detalle de venta específico"""
        url = reverse('detalleventa-detail', args=[self.detalle_venta.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['cantidad'], 2)

    def test_actualizar_detalle_venta(self):
        """Prueba actualización de detalle de venta"""
        url = reverse('detalleventa-detail', args=[self.detalle_venta.id])
        updated_data = {'cantidad': 4, 'precio_unitario': 11.00}
        response = self.client.patch(url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.detalle_venta.refresh_from_db()
        self.assertEqual(self.detalle_venta.cantidad, 4)
        self.assertEqual(self.detalle_venta.precio_unitario, 11.00)

    def test_eliminar_detalle_venta(self):
        """Prueba eliminación de detalle de venta"""
        url = reverse('detalleventa-detail', args=[self.detalle_venta.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(DetalleVenta.objects.filter(id=self.detalle_venta.id).exists())

class PDFGenerationTestCase(APITestCase):
    """Pruebas específicas para generación de PDFs"""
    
    def setUp(self):
        self.client = APIClient()
        # Crear roles
        self.rol_admin = Rol.objects.create(name='administrador')
        self.rol_employee = Rol.objects.create(name='empleado')
        self.rol_client = Rol.objects.create(name='cliente')

        self.admin_user = User.objects.create_user(
            username='admin', 
            password='adminpass123',
            email='admin@example.com'
        )
        self.admin_user.rol = self.rol_admin
        self.admin_user.save()
        
        self.client_user = User.objects.create_user(
            username='client',
            password='clientpass123',
            email='client@example.com'
        )
        self.client_user.rol = self.rol_client
        self.client_user.save()
        
        self.employee_user = User.objects.create_user(
            username='employee',
            password='employeepass123',
            email='employee@example.com'
        )
        self.employee_user.rol = self.rol_employee
        self.employee_user.save()
        
        # Autenticar como admin
        refresh = RefreshToken.for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}')
        
        # Datos de prueba
        self.categoria = Categoria.objects.create(nombre='Medicamentos')
        self.proveedor = Proveedor.objects.create(
            nombre='Proveedor Test', 
            contacto='test@proveedor.com',
            usuario=self.admin_user
        )
        
        self.producto = Producto.objects.create(
            nombre='Paracetamol', 
            precio=10.50, 
            stock=100,
            id_categoria=self.categoria, 
            id_proveedor=self.proveedor
        )
        
        self.cliente = Cliente.objects.create(
            nombre='Cliente Test', 
            correo='cliente@test.com', 
            telefono='3101234567',
            usuario=self.client_user
        )
        
        self.empleado = Empleado.objects.create(
            nombre='Empleado Test', 
            telefono='3111111111',
            usuario=self.employee_user
        )
        
        self.factura = FacturaVenta.objects.create(
            id_cliente=self.cliente,
            id_empleado=self.empleado
        )
        
        self.movimiento = Movimiento.objects.create(
            tipo='salida', 
            cantidad=5, 
            id_producto=self.producto, 
            id_cliente=self.cliente
        )
        
        self.detalle_venta = DetalleVenta.objects.create(
            cantidad=2, 
            precio_unitario=10.50, 
            id_factura=self.factura, 
            id_producto=self.producto
        )
    
    def test_generar_pdf_movimiento_especifico(self):
        """Prueba generación de PDF para movimiento específico"""
        pdf_file = build_movimiento_id_pdf(self.movimiento)
        self.assertIsInstance(pdf_file, BytesIO)
        self.assertGreater(len(pdf_file.getvalue()), 0)
    
    def test_generar_pdf_todos_movimientos(self):
        """Prueba generación de PDF para todos los movimientos"""
        movimientos = Movimiento.objects.all()
        pdf_file = build_todos_movimientos_pdf(movimientos)
        self.assertIsInstance(pdf_file, BytesIO)
        self.assertGreater(len(pdf_file.getvalue()), 0)
    
    def test_generar_pdf_producto_especifico(self):
        """Prueba generación de PDF para producto específico"""
        pdf_file = build_producto_id_pdf(self.producto)
        self.assertIsInstance(pdf_file, BytesIO)
        self.assertGreater(len(pdf_file.getvalue()), 0)
    
    def test_generar_pdf_todos_productos(self):
        """Prueba generación de PDF para todos los productos"""
        productos = Producto.objects.all()
        pdf_file = build_todos_productos_pdf(productos)
        self.assertIsInstance(pdf_file, BytesIO)
        self.assertGreater(len(pdf_file.getvalue()), 0)
    
    def test_generar_pdf_detalle_venta_especifico(self):
        """Prueba generación de PDF para detalle de venta específico"""
        pdf_file = build_detalle_venta_id_pdf(self.detalle_venta)
        self.assertIsInstance(pdf_file, BytesIO)
        self.assertGreater(len(pdf_file.getvalue()), 0)
    
    def test_generar_pdf_todos_detalles_venta(self):
        """Prueba generación de PDF para todos los detalles de venta"""
        detalles_venta = DetalleVenta.objects.all()
        pdf_file = build_todos_detalles_venta_pdf(detalles_venta)
        self.assertIsInstance(pdf_file, BytesIO)
        self.assertGreater(len(pdf_file.getvalue()), 0)
    
    def test_endpoints_pdf_movimientos(self):
        """Prueba los endpoints de PDF para movimientos"""
        url = reverse('movimiento-pdf', args=[self.movimiento.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        
        url = reverse('movimiento-all-pdf')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/pdf')
    
    def test_endpoints_pdf_productos(self):
        """Prueba los endpoints de PDF para productos"""
        url = reverse('producto-pdf', args=[self.producto.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        
        url = reverse('producto-all-pdf')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/pdf')
    
    def test_endpoints_pdf_detalles_venta(self):
        """Prueba los endpoints de PDF para detalles de venta"""
        url = reverse('detalleventa-pdf', args=[self.detalle_venta.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        
      
        url = reverse('detalleventa-all-pdf')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/pdf')

class IntegrationTestCase(APITestCase):
    """Pruebas de integración que combinan múltiples funcionalidades"""
    
    def setUp(self):
        self.client = APIClient()
        self.rol_admin = Rol.objects.create(name='administrador')
        
        self.admin_user = User.objects.create_user(
            username='admin', 
            password='adminpass123',
            email='admin@example.com'
        )
        self.admin_user.rol = self.rol_admin
        self.admin_user.save()
        
        
        refresh = RefreshToken.for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}')
        
    
        self.categoria = Categoria.objects.create(nombre='Medicamentos')
        self.proveedor = Proveedor.objects.create(
            nombre='Proveedor Test', 
            contacto='test@proveedor.com',
            usuario=self.admin_user
        )
    
    def test_flujo_completo_producto_movimiento(self):
        """Prueba un flujo completo: crear producto -> crear movimiento -> generar PDF"""
      
        producto_data = {
            'nombre': 'Ibuprofeno',
            'precio': 15.75,
            'stock': 50,
            'id_categoria': self.categoria.id,
            'id_proveedor': self.proveedor.id
        }
        
        response = self.client.post(reverse('producto-list'), producto_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        producto_id = response.data['id']
        
        rol_client = Rol.objects.create(name='cliente')
        cliente_user = User.objects.create_user(
            username='cliente_test',
            password='cliente123',
            email='cliente@test.com'
        )
        cliente_user.rol = rol_client
        cliente_user.save()
        
        cliente = Cliente.objects.create(
            nombre='Cliente Test',
            correo='cliente@test.com',
            telefono='3101234567',
            usuario=cliente_user
        )
        
       
        movimiento_data = {
            'tipo': 'entrada',
            'cantidad': 10,
            'id_producto': producto_id,
            'id_cliente': cliente.id
        }
        
        response = self.client.post(reverse('movimiento-list'), movimiento_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        movimiento_id = response.data['id']
        
        movimiento = Movimiento.objects.get(id=movimiento_id)
        pdf_file = build_movimiento_id_pdf(movimiento)
        self.assertIsInstance(pdf_file, BytesIO)
        self.assertGreater(len(pdf_file.getvalue()), 0)
        
        url = reverse('movimiento-pdf', args=[movimiento_id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/pdf')