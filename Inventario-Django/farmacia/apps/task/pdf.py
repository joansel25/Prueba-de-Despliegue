# pdf.py

from reportlab.pdfgen import canvas
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle



def build_movimiento_id_pdf(movimiento):
    """Genera un PDF con los datos detallados de un movimiento de inventario."""
    buf = BytesIO()
    page = canvas.Canvas(buf, pagesize=letter)
    width, height = letter

    page.setTitle(f'Movimiento de Inventario - {movimiento.id}')
    page.drawString(50, height - 30, f"Movimiento de Inventario #{movimiento.id}")

    info = [
        ["Tipo de Movimiento:", movimiento.tipo],
        ["Fecha:", str(movimiento.fecha)],
        ["Producto:", movimiento.id_producto.nombre],
        ["Cantidad:", str(movimiento.cantidad)],
        ["Cliente:", movimiento.id_cliente.nombre],
    ]

    table = Table(info, colWidths=[150, 300])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    table.wrapOn(page, width, height)
    table.drawOn(page, 50, height - 150)

    page.showPage()
    page.save()

    buf.seek(0)
    return buf

# pdf.py - FUNCIONES DE MOVIMIENTOS CORREGIDAS

def build_movimiento_id_pdf(movimiento):
    """Genera un PDF con los datos detallados de un movimiento de inventario."""
    buf = BytesIO()
    page = canvas.Canvas(buf, pagesize=letter)
    width, height = letter

    page.setTitle(f'Movimiento de Inventario - {movimiento.id}')
    page.drawString(50, height - 30, f"Movimiento de Inventario #{movimiento.id}")

    # Manejar campos que pueden ser None
    cliente_nombre = movimiento.id_cliente.nombre if movimiento.id_cliente else "N/A"
    proveedor_nombre = movimiento.id_proveedor.nombre if movimiento.id_proveedor else "N/A"
    responsable_nombre = movimiento.responsable.nombre if movimiento.responsable else "Sistema"

    info = [
        ["Tipo de Movimiento:", movimiento.tipo],
        ["Fecha:", str(movimiento.fecha)],
        ["Producto:", movimiento.id_producto.nombre],
        ["Cantidad:", str(movimiento.cantidad)],
        ["Responsable:", responsable_nombre],
    ]

    # Agregar campo según el tipo de movimiento
    if movimiento.tipo == "entrada":
        info.append(["Proveedor:", proveedor_nombre])
    else:
        info.append(["Cliente:", cliente_nombre])

    table = Table(info, colWidths=[150, 300])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    table.wrapOn(page, width, height)
    table.drawOn(page, 50, height - 150)

    page.showPage()
    page.save()

    buf.seek(0)
    return buf

def build_todos_movimientos_pdf(movimientos):
    """Genera un PDF con todos los movimientos de inventario en formato tabular."""
    buf = BytesIO()
    page = canvas.Canvas(buf, pagesize=letter)
    width, height = letter

    page.setTitle('Todos los Movimientos de Inventario')
    page.drawString(50, height - 30, "Todos los Movimientos de Inventario")

    # Encabezado con ambos campos
    data = [["ID", "Tipo", "Fecha", "Producto", "Cantidad", "Proveedor", "Cliente", "Responsable"]]

    for movimiento in movimientos:
        # Manejar campos que pueden ser None
        cliente_nombre = movimiento.id_cliente.nombre if movimiento.id_cliente else "N/A"
        proveedor_nombre = movimiento.id_proveedor.nombre if movimiento.id_proveedor else "N/A"
        responsable_nombre = movimiento.responsable.nombre if movimiento.responsable else "Sistema"

        data.append([ 
            str(movimiento.id),
            movimiento.tipo,
            str(movimiento.fecha),
            movimiento.id_producto.nombre,
            str(movimiento.cantidad),
            proveedor_nombre,
            cliente_nombre,
            responsable_nombre,
        ])

    # Ajustar anchos de columnas
    table = Table(data, colWidths=[30, 50, 70, 90, 50, 80, 80, 80])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),  # Reducir tamaño de fuente
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    table.wrapOn(page, width, height)
    table.drawOn(page, 20, height - 100)  # Ajustar posición

    page.showPage()
    page.save()

    buf.seek(0)
    return buf

def build_producto_id_pdf(producto):
    """Crea PDF para un producto individual, enfocándose en detalles como precio y stock con un formato de tabla."""
    buf = BytesIO()
    page = canvas.Canvas(buf, pagesize=letter)
    width, height = letter

    page.setTitle(f'Producto - {producto.nombre}')
    page.drawString(50, height - 30, f"Ficha del Producto: {producto.nombre}")

    info = [
        ["Nombre:", producto.nombre],
        ["Precio:", str(producto.precio)],
        ["Stock:", str(producto.stock)],
        ["Categoría:", producto.id_categoria.nombre],
        ["Proveedor:", producto.id_proveedor.nombre],
    ]

    table = Table(info, colWidths=[150, 300])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey), #encabezado
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),#Color del texto del encabezado.
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),#Alineación izquierda de todo el contenido.
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),#Fuente en negrita para encabezado.
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),#Espacio inferior en la fila de encabezado.
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),#fondo beige para las filas de datos.
        ('GRID', (0, 0), (-1, -1), 1, colors.black),#Bordes negros en toda la tabla.
    ]))

    table.wrapOn(page, width, height)
    table.drawOn(page, 50, height - 150)

    page.showPage()
    page.save()

    buf.seek(0)
    return buf

def build_todos_productos_pdf(productos):
    """Produce PDF con tabla de todos los productos, """
    buf = BytesIO()
    page = canvas.Canvas(buf, pagesize=letter)
    width, height = letter

    page.setTitle('Todos los Productos')
    page.drawString(50, height - 30, "Todos los Productos")

    data = [["ID", "Nombre", "Precio", "Stock", "Categoría", "Proveedor"]]

    for producto in productos:
        data.append([
            str(producto.id),
            producto.nombre,
            str(producto.precio),
            str(producto.stock),
            producto.id_categoria.nombre,
            producto.id_proveedor.nombre,
        ])

    table = Table(data, colWidths=[40, 100, 60, 60, 100, 100])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    table.wrapOn(page, width, height)
    table.drawOn(page, 30, height - 100)

    page.showPage()
    page.save()

    buf.seek(0)
    return buf


def build_detalle_venta_id_pdf(detalle_venta):
    """Genera PDF para un detalle de venta, calculando subtotal dinámicamente en la tabla."""
    buf = BytesIO()
    page = canvas.Canvas(buf, pagesize=letter)
    width, height = letter

    page.setTitle(f'Detalle de Venta - {detalle_venta.id}')
    page.drawString(50, height - 30, f"Detalle de Venta #{detalle_venta.id}")

    info = [
        ["Factura:", str(detalle_venta.id_factura.id)],
        ["Producto:", detalle_venta.id_producto.nombre],
        ["Cantidad:", str(detalle_venta.cantidad)],
        ["Precio Unitario:", str(detalle_venta.precio_unitario)],
        ["Subtotal:", str(detalle_venta.cantidad * detalle_venta.precio_unitario)],
    ]

    table = Table(info, colWidths=[150, 300])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    table.wrapOn(page, width, height)
    table.drawOn(page, 50, height - 150)

    page.showPage()
    page.save()

    buf.seek(0)
    return buf

def build_todos_detalles_venta_pdf(detalles_venta):
    """Genera un PDF con el detalle de las ventas, mostrando subtotales por fila para facilitar revisiones rápidas."""

    buf = BytesIO()
    page = canvas.Canvas(buf, pagesize=letter)
    width, height = letter

    page.setTitle('Todos los Detalles de Venta')
    page.drawString(50, height - 30, "Todos los Detalles de Venta")

    data = [["Fecha","ID", "Factura", "Producto", "Cantidad", "Precio Unitario", "Subtotal"]]
    
    total_general = 0
    for detalle in detalles_venta:
        data.append([
            str(detalle.id_factura.fecha),
            str(detalle.id),
            str(detalle.id_factura.id),
            detalle.id_producto.nombre,
            str(detalle.cantidad),
            str(detalle.precio_unitario),
            str(detalle.cantidad * detalle.precio_unitario),
        ])
        total_general += detalle.cantidad * detalle.precio_unitario
    
    data.append(["", "", "", "","", "Total General:", str(total_general)])
    
       
    

    table = Table(data, colWidths=[95,40, 60, 100, 60, 80, 80, 100])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    table.wrapOn(page, width, height)
    table.drawOn(page, 30, height - 100)

    page.showPage()
    page.save()

    buf.seek(0)
    return buf