from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Movimiento, Producto

@receiver(post_save, sender=Movimiento)
def actualizar_stock(sender, instance, created, **kwargs):
    """
    Actualiza automáticamente el stock del producto
    según el tipo de movimiento (entrada, salida o ajuste).
    """
    if created:  # Solo cuando el movimiento es nuevo
        producto = instance.id_producto

        if instance.tipo == 'entrada':
            producto.stock += instance.cantidad
        elif instance.tipo == 'salida':
            producto.stock -= instance.cantidad
        elif instance.tipo == 'ajuste':
            # Si agregas el tipo 'ajuste', puedes definir su comportamiento
            # Por ejemplo: simplemente asignar la cantidad directamente
            producto.stock = instance.cantidad

        producto.save()