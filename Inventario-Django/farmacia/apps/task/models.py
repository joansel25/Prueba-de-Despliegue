from django.db import models
from model_utils.models import TimeStampedModel
from ..usuario.models import Usuario
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError

class Categoria(TimeStampedModel):
    nombre = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.nombre

class Proveedor(TimeStampedModel):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="proveedores")
    nombre = models.CharField(max_length=150)
    contacto = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre

class Producto(TimeStampedModel):
    nombre = models.CharField(max_length=150)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    id_categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name="productos")
    id_proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE, related_name="productos_proveedor")

    @property
    def valor_total_stock(self):
        return self.stock * self.precio

    @property
    def low_stock(self):
        return self.stock < 10 

    def __str__(self):
        return f"{self.nombre} ({self.id_categoria})"

class Cliente(TimeStampedModel):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="clientes")
    nombre = models.CharField(max_length=150)
    correo = models.EmailField(unique=True)
    telefono = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.nombre

class Empleado(TimeStampedModel):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="empleados")
    nombre = models.CharField(max_length=150)
    #correo = models.EmailField(unique=True)
    telefono = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.nombre

class FacturaVenta(TimeStampedModel):
    fecha = models.DateField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    id_cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name="facturas")
    id_empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE, related_name="facturas")

    def __str__(self):
        return f"Factura {self.id}"

class DetalleVenta(TimeStampedModel):
    cantidad = models.IntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    id_factura = models.ForeignKey(FacturaVenta, on_delete=models.CASCADE, related_name="detalles")
    id_producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name="detalles")
    
    def save(self, *args, **kwargs):
        if self.id_producto:
            self.precio_unitario = self.id_producto.precio  # Automatización: Toma precio actual del producto
        if self.precio_unitario is None:
            raise ValidationError("precio_unitario no puede ser nulo; asegúrese de que id_producto esté definido.")
        self.subtotal = self.cantidad * self.precio_unitario  # Cálculo automático
        super().save(*args, **kwargs)  # Ahora inserta con valores válidos

    def __str__(self):
        return f"Detalle {self.id} (Factura {self.id_factura})"

class Movimiento(TimeStampedModel):
    TIPOS_MOVIMIENTO = [('entrada', 'Entrada'), ('salida', 'Salida')]
    tipo = models.CharField(max_length=10, choices=TIPOS_MOVIMIENTO)
    cantidad = models.IntegerField(default=1)
    fecha = models.DateField(auto_now_add=True)
    id_producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name="movimiento")
    id_cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name="movimiento", null=True, blank=True)  # Para salidas
    id_proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE, related_name="movimiento", null=True, blank=True)  # Adaptado: Para entradas
    responsable = models.ForeignKey(Empleado, on_delete=models.SET_NULL, null=True, related_name="movimientos")  # Adaptado: Responsable

    def __str__(self):
        return f"Movimiento {self.id} ({self.tipo})"

# Signals para automatizaciones
@receiver(pre_save, sender=DetalleVenta)
def validar_stock_detalle(sender, instance, **kwargs):
    if instance.id_producto.stock < instance.cantidad:
        raise ValidationError(f"Stock insuficiente para {instance.id_producto.nombre}. Disponible: {instance.id_producto.stock}")

@receiver(post_save, sender=DetalleVenta)
def calcular_subtotal_detalle(sender, instance, created, **kwargs):
    if created:
        instance.precio_unitario = instance.id_producto.precio
        instance.subtotal = instance.cantidad * instance.precio_unitario
        instance.save(update_fields=['precio_unitario', 'subtotal'])

@receiver(post_save, sender=DetalleVenta)
def actualizar_total_factura(sender, instance, **kwargs):
    factura = instance.id_factura
    factura.total = sum(detalle.subtotal for detalle in factura.detalles.all())
    factura.save(update_fields=["total"])

@receiver(pre_save, sender=Movimiento)
def validar_movimiento(sender, instance, **kwargs):
    if instance.tipo == 'salida' and instance.id_producto.stock < instance.cantidad:
        raise ValidationError(f"Stock insuficiente para salida de {instance.id_producto.nombre}.")
    if instance.tipo == 'entrada' and not instance.id_proveedor:
        raise ValidationError("Para entradas, debe especificar un proveedor.")
    if instance.tipo == 'salida' and not instance.id_cliente:
        raise ValidationError("Para salidas, debe especificar un cliente.")

@receiver(post_save, sender=Movimiento)
def actualizar_stock_movimiento(sender, instance, created, **kwargs):
    if created:
        producto = instance.id_producto
        if instance.tipo == 'entrada':
            producto.stock += instance.cantidad
        elif instance.tipo == 'salida':
            producto.stock -= instance.cantidad
        producto.save()
        print(f"Stock actualizado: {producto.nombre} = {producto.stock}")  # Debug