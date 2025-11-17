from rest_framework import serializers
from .models import *
from ..usuario.models import Usuario, Rol

# -----------------------------
# CATEGORÍA
# -----------------------------


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = '__all__'


# -----------------------------
# PRODUCTO
# -----------------------------
class ProductoSerializer(serializers.ModelSerializer):
    low_stock = serializers.ReadOnlyField()

    class Meta:
        model = Producto
        fields = '__all__'


# -----------------------------
# PROVEEDOR
# -----------------------------
class ProveedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proveedor
        fields = '__all__'


class ClienteSerializer(serializers.ModelSerializer):
    usuario = serializers.PrimaryKeyRelatedField(
        queryset=Usuario.objects.all()
    )

    class Meta:
        model = Cliente
        fields = ['id', 'nombre', 'telefono', 'correo', 'usuario']
class EmpleadoSerializer(serializers.ModelSerializer):
    usuario = serializers.PrimaryKeyRelatedField(
        queryset=Usuario.objects.all()
    )

    class Meta:
        model = Empleado
        fields = ['id', 'nombre', 'telefono', 'usuario']



# -----------------------------
# DETALLE VENTA
# -----------------------------
class DetalleVentaSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(
        source='id_producto.nombre', read_only=True)
    factura_fecha = serializers.DateField(
        source='id_factura.fecha', read_only=True)

    class Meta:
        model = DetalleVenta
        fields = '__all__'


# -----------------------------
# FACTURA VENTA
# -----------------------------
class FacturaVentaSerializer(serializers.ModelSerializer):
    detalles = DetalleVentaSerializer(many=True)

    class Meta:
        model = FacturaVenta
        fields = ['id', 'fecha', 'total',
                  'id_cliente', 'id_empleado', 'detalles']
        read_only_fields = ['fecha', 'total']

    def create(self, validated_data):
        detalles_data = validated_data.pop('detalles')
        factura = FacturaVenta.objects.create(**validated_data)

        total_factura = 0

        for item in detalles_data:
            detalle = DetalleVenta.objects.create(id_factura=factura, **item)
            total_factura += detalle.subtotal

        factura.total = total_factura
        factura.save()

        return factura


# -----------------------------
# MOVIMIENTO
# -----------------------------
class MovimientoSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(
        source='id_producto.nombre', read_only=True)
    proveedor_nombre = serializers.CharField(
        source='id_proveedor.nombre', read_only=True)
    cliente_nombre = serializers.CharField(
        source='id_cliente.nombre', read_only=True)
    responsable_nombre = serializers.CharField(
        source='responsable.nombre', read_only=True)

    class Meta:
        model = Movimiento
        fields = '__all__'

    def validate(self, data):

        if data['tipo'] == 'entrada' and not data.get('id_proveedor'):
            raise serializers.ValidationError(
                "Para entradas, debe especificar un proveedor."
            )

        if data['tipo'] == 'salida' and not data.get('id_cliente'):
            raise serializers.ValidationError(
                "Para salidas, debe especificar un cliente."
            )

        return data
