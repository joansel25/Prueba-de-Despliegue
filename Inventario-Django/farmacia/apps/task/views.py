"""ViewSets gestionamos operaciones CRUD con autenticaciÃ³n, 
permisos y generaciÃ³n de PDFs."""

from rest_framework import viewsets
from .models import *
from .serializers import *
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated
from .permissions import *
from django.http import HttpResponse
from .pdf import *
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from rest_framework import filters


class CategoriaViewSet(viewsets.ModelViewSet):
    """Gestiona categorÃ­as con permisos especificos y documentaciÃ³n Swagger para list/create."""
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    @swagger_auto_schema(
        operation_description="Listar todas las categorias disponibles en el sistema ",
        responses={200: CategoriaSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Crea una nueva categorÃ­a en el sistema.",
        responses={201: CategoriaSerializer()}
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


class ProductoViewset(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
    permission_classes = [IsAuthenticated, IsAdmin | IsEmployee]
    filter_backends = [filters.SearchFilter]
    search_fields = ['nombre', 'id_categoria__nombre']

    @action(detail=True, methods=['get'])
    def pdf(self, request, pk=None):
        producto = self.get_object()
        pdf_file = build_producto_id_pdf(producto)

        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="producto_{producto.nombre}.pdf"'
        return response

    @action(detail=False, methods=['get'])
    def all_pdf(self, request):
        productos = self.get_queryset()
        pdf_file = build_todos_productos_pdf(productos)

        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="todos_productos.pdf"'
        return response


class ProveedorViewset(viewsets.ModelViewSet):
    """Gestiona proveedores con permisos para admin/proveedor."""
    queryset = Proveedor.objects.all()
    serializer_class = ProveedorSerializer
    permission_classes = [IsAuthenticated, IsAdmin | IsProvider]


class ClienteViewset(viewsets.ModelViewSet):
    """Maneja clientes con permisos amplios."""
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    permission_classes = [IsAuthenticated, IsClient | IsEmployee | IsAdmin]


class EmpleadoViewset(viewsets.ModelViewSet):
    """Gestiona empleados restringido a admin."""
    queryset = Empleado.objects.all()
    serializer_class = EmpleadoSerializer
    permission_classes = [IsAuthenticated, IsAdmin]


class FacturaVentaViewset(viewsets.ModelViewSet):
    queryset = FacturaVenta.objects.all()
    serializer_class = FacturaVentaSerializer
    permission_classes = [IsAuthenticated, IsEmployee | IsAdmin]
    # Adaptado: Filtros por fecha/cliente
    filter_backends = [filters.SearchFilter]
    search_fields = ['fecha', 'id_cliente__nombre']

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        factura = serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def mis_facturas(self, request):
        """Obtiene todas las facturas del cliente autenticado"""
        try:
            cliente = Cliente.objects.get(usuario=request.user)
        except Cliente.DoesNotExist:
            return Response({
                "detail": "Tu cuenta no estÃ¡ registrada como cliente.",
                "user_id": request.user.id,
                "username": request.user.username
            }, status=403)

        facturas = FacturaVenta.objects.filter(id_cliente=cliente)
        serializer = self.get_serializer(facturas, many=True)
        return Response(serializer.data)


class DetalleVentaViewset(viewsets.ModelViewSet):
    """Gestiona detalles de venta con permisos  y acciones para PDFs."""
    queryset = DetalleVenta.objects.all()
    serializer_class = DetalleVentaSerializer
    permission_classes = [IsAuthenticated,  IsAdmin | IsEmployee]

    @action(detail=True, methods=['get'])
    def pdf(self, request, pk=None):
        detalle_venta = self.get_object()
        pdf_file = build_detalle_venta_id_pdf(detalle_venta)

        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="detalle_venta_{detalle_venta.id}.pdf"'
        return response

    @action(detail=False, methods=['get'])
    def all_pdf(self, request):
        detalles_venta = self.get_queryset()
        pdf_file = build_todos_detalles_venta_pdf(detalles_venta)

        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="todos_detalles_venta.pdf"'
        return response

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def mis_detalles(self, request):
        """Obtiene los detalles de venta del cliente autenticado"""
        try:
            cliente = Cliente.objects.get(usuario=request.user)
        except Cliente.DoesNotExist:
            return Response({
                "detail": "Tu cuenta no estÃ¡ registrada como cliente.",
                "user_id": request.user.id,
                "username": request.user.username
            }, status=403)

        facturas_cliente = FacturaVenta.objects.filter(id_cliente=cliente)
        detalles_venta = self.get_queryset().filter(id_factura__in=facturas_cliente)

        serializer = self.get_serializer(detalles_venta, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def all_pdf_cliente(self, request):
        """Genera PDF de todas las compras del cliente autenticado"""
        try:
            cliente = Cliente.objects.get(usuario=request.user)
        except Cliente.DoesNotExist:
            return Response({
                "detail": "Tu cuenta no estÃ¡ registrada como cliente."
            }, status=403)

        # CORRECCIÃ“N: Usar id_factura en lugar de id_factura_venta
        facturas_cliente = FacturaVenta.objects.filter(id_cliente=cliente)
        detalles_venta = self.get_queryset().filter(id_factura__in=facturas_cliente)

        pdf_file = build_todos_detalles_venta_pdf(detalles_venta)

        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="mis_detalles_venta.pdf"'
        return response


class MovimientoViewset(viewsets.ModelViewSet):
    queryset = Movimiento.objects.all()
    serializer_class = MovimientoSerializer
    permission_classes = [IsAuthenticated, IsAdmin | IsEmployee]
    filter_backends = [filters.SearchFilter]
    search_fields = ['tipo', 'fecha', 'id_producto__nombre']

    @action(detail=True, methods=['get'])
    def pdf(self, request, pk=None):
        movimiento = self.get_object()
        pdf_file = build_movimiento_id_pdf(movimiento)
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="movimiento_{movimiento.id}.pdf"'
        return response
    
    @action(detail=False, methods=['get'])
    def all_pdf(self, request):
        movimientos = self.get_queryset()
        pdf_file = build_todos_movimientos_pdf(movimientos)
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="todos_movimientos.pdf"'
        return response
        


