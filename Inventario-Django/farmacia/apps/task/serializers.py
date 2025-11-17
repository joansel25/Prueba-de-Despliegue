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
    usuario = serializers.DictField(write_only=True)

    class Meta:
        model = Cliente
        fields = ['id', 'nombre', 'telefono', 'correo', 'usuario']

    def create(self, validated_data):
        usuario_data = validated_data.pop('usuario')

        username = usuario_data.get('username')
        password = usuario_data.get('password')

        if not username or not password:
            raise serializers.ValidationError(
                {"usuario": "username y password son obligatorios"}
            )

        # Validar existencia del usuario
        if Usuario.objects.filter(username=username).exists():
            raise serializers.ValidationError(
                {"usuario": "El username ya existe."}
            )

        rol_cliente, _ = Rol.objects.get_or_create(name='cliente')

        # Crear usuario hijo
        usuario = Usuario.objects.create_user(
            username=username,
            password=password,
            rol=rol_cliente
        )

        # Crear cliente
        cliente = Cliente.objects.create(
            usuario=usuario,
            nombre=validated_data["nombre"],
            telefono=validated_data["telefono"],
            correo=validated_data["correo"]
        )

        return cliente



class EmpleadoSerializer(serializers.ModelSerializer):
    usuario = serializers.DictField(write_only=True)

    class Meta:
        model = Empleado
        fields = ['id', 'nombre', 'telefono', 'usuario']

    def create(self, validated_data):
        usuario_data = validated_data.pop('usuario')
        username = usuario_data.get('username')
        if Usuario.objects.filter(username=username).exists():
            raise serializers.ValidationError(
                {"usuario": "El username ya existe."})

        rol_empleado, _ = Rol.objects.get_or_create(name='empleado')
        usuario = Usuario.objects.create_user(
            username=username,
            password=usuario_data.get('password'),
            rol=rol_empleado
        )
        empleado = Empleado.objects.create(usuario=usuario, **validated_data)
        return empleado


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
