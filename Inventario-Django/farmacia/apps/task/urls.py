"""Definimos las rutas de la app Task, manteniendo el código modular y organizado."""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'categorias', CategoriaViewSet, basename='categoria')
router.register(r'productos', ProductoViewset, basename='producto')
router.register(r'proveedores', ProveedorViewset, basename='proveedor')
router.register(r'clientes', ClienteViewset, basename='cliente')
router.register(r'empleados', EmpleadoViewset, basename='empleado')
router.register(r'facturasventa', FacturaVentaViewset, basename='facturaventa')
router.register(r'detallesventa', DetalleVentaViewset, basename='detalleventa')
router.register(r'movimientos', MovimientoViewset, basename='movimiento')

urlpatterns = router.urls
