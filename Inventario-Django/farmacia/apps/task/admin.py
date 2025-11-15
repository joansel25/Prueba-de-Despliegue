from django.contrib import admin
from .models import Categoria, Proveedor, Producto, Cliente, Empleado, FacturaVenta, DetalleVenta, Movimiento
from ..usuario import *


admin.site.register(Categoria)
admin.site.register(Proveedor)
admin.site.register(Producto)
admin.site.register(Cliente)
admin.site.register(Empleado)
admin.site.register(FacturaVenta)
admin.site.register(DetalleVenta)
admin.site.register(Movimiento)

