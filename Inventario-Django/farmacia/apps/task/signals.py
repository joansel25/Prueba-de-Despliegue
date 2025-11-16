
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from .models import DetalleVenta, Movimiento, FacturaVenta

# ==================== SEÑALES PARA DETALLE VENTA ====================

@receiver(pre_save, sender=DetalleVenta)
def validar_stock_detalle(sender, instance, **kwargs):
    """
    Valida que haya stock suficiente antes de guardar un detalle de venta
    """
    if instance.id_producto.stock < instance.cantidad:
        raise ValidationError(
            f"Stock insuficiente para {instance.id_producto.nombre}. "
            f"Disponible: {instance.id_producto.stock}, Solicitado: {instance.cantidad}"
        )

@receiver(post_save, sender=DetalleVenta)
def calcular_subtotal_detalle(sender, instance, created, **kwargs):
    """
    Calcula automáticamente el subtotal después de guardar un detalle
    """
    if created:
        instance.precio_unitario = instance.id_producto.precio
        instance.subtotal = instance.cantidad * instance.precio_unitario
        instance.save(update_fields=['precio_unitario', 'subtotal'])

@receiver(post_save, sender=DetalleVenta)
def actualizar_total_factura(sender, instance, **kwargs):
    """
    Actualiza el total de la factura cuando se modifica un detalle
    """
    factura = instance.id_factura
    factura.total = sum(detalle.subtotal for detalle in factura.detalles.all())
    factura.save(update_fields=["total"])

@receiver(post_save, sender=DetalleVenta)
def actualizar_stock_venta(sender, instance, created, **kwargs):
    """
    Actualiza el stock del producto cuando se crea un detalle de venta
    """
    if created:
        producto = instance.id_producto
        producto.stock -= instance.cantidad
        producto.save()

# ==================== SEÑALES PARA MOVIMIENTOS ====================

@receiver(pre_save, sender=Movimiento)
def validar_movimiento(sender, instance, **kwargs):
    """
    Valida reglas de negocio antes de guardar un movimiento
    """
    # Validar stock para salidas
    if instance.tipo == 'salida' and instance.id_producto.stock < instance.cantidad:
        raise ValidationError(
            f"Stock insuficiente para salida de {instance.id_producto.nombre}. "
            f"Disponible: {instance.id_producto.stock}, Solicitado: {instance.cantidad}"
        )
    
    # Validar proveedor para entradas
    if instance.tipo == 'entrada' and not instance.id_proveedor:
        raise ValidationError("Para entradas, debe especificar un proveedor.")
    
    # Validar cliente para salidas
    if instance.tipo == 'salida' and not instance.id_cliente:
        raise ValidationError("Para salidas, debe especificar un cliente.")

@receiver(post_save, sender=Movimiento)
def actualizar_stock_movimiento(sender, instance, created, **kwargs):
    """
    Actualiza el stock del producto cuando se crea un movimiento
    """
    if created:
        producto = instance.id_producto
        if instance.tipo == 'entrada':
            producto.stock += instance.cantidad
        elif instance.tipo == 'salida':
            producto.stock -= instance.cantidad
        producto.save()

@receiver(post_delete, sender=Movimiento)
def revertir_stock_movimiento(sender, instance, **kwargs):
    """
    Revierte el stock si se elimina un movimiento
    """
    producto = instance.id_producto
    if instance.tipo == 'entrada':
        producto.stock -= instance.cantidad
    elif instance.tipo == 'salida':
        producto.stock += instance.cantidad
    producto.save()

# ==================== SEÑALES PARA FACTURA ====================

@receiver(post_delete, sender=FacturaVenta)
def actualizar_total_factura_eliminada(sender, instance, **kwargs):
    """
    Actualiza el total si se elimina una factura (aunque debería manejarse por CASCADE)
    """
    # Esta señal podría ser útil para lógica adicional
    pass

@receiver(pre_save, sender=FacturaVenta)
def validar_factura(sender, instance, **kwargs):
    """
    Validaciones adicionales para facturas
    """
    # Por ejemplo: validar que el empleado esté activo
    if instance.id_empleado and not instance.id_empleado.usuario.is_active:
        raise ValidationError("No se puede asignar una factura a un empleado inactivo")