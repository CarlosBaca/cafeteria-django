# Importa HttpResponse para devolver texto simple al navegador
# from django.http import HttpResponse

# (Opcional) render se usará más adelante para templates
from django.shortcuts import render
from .models import Producto, Pedido, DetallePedido
from django.contrib.auth.decorators import login_required
from .carrito import Carrito
from django.shortcuts import redirect
from django.http import HttpResponse
from django.contrib import messages
from django.db.models import Sum


# Vista básica que responde a una solicitud HTTP
def inicio(request):
    # Retorna texto simple al navegador
    # return HttpResponse("Bienvenido al sistema de cafetería")
    return render(request, "inicio.html")


def lista_productos(request):
    # Obtener el texto enviado desde la caja de búsqueda
    busqueda = request.GET.get("q", "")

    # Obtener solo productos activos
    productos = Producto.objects.filter(activo=True)

    # Si el usuario escribió algo, filtrar por nombre
    if busqueda:
        productos = productos.filter(nombre__icontains=busqueda)

    # Enviar productos y texto buscado al template
    return render(
        request,
        "productos/lista.html",
        {
            "productos": productos,
            "busqueda": busqueda,
        },
    )


@login_required
def mis_pedidos(request):
    pedidos = Pedido.objects.filter(usuario=request.user)
    return render(request, "pedidos/mis_pedidos.html", {"pedidos": pedidos})


@login_required
def detalle_pedido(request, pedido_id):
    detalles = DetallePedido.objects.filter(pedido_id=pedido_id)
    return render(request, "pedidos/detalle.html", {"detalles": detalles})


def agregar_producto(request, producto_id):
    carrito = Carrito(request)
    producto = Producto.objects.get(id=producto_id)

    carrito.agregar(producto)

    return redirect(request.META.get("HTTP_REFERER", "lista_productos"))


def eliminar_producto(request, producto_id):
    carrito = Carrito(request)
    producto = Producto.objects.get(id=producto_id)

    carrito.eliminar(producto)

    return redirect("ver_carrito")


def restar_producto(request, producto_id):
    carrito = Carrito(request)
    producto = Producto.objects.get(id=producto_id)

    carrito.restar(producto)

    return redirect("ver_carrito")


def limpiar_carrito(request):
    carrito = Carrito(request)
    carrito.limpiar()

    return redirect("ver_carrito")


def ver_carrito(request):
    carrito = request.session.get("carrito", {})
    return render(request, "carrito.html", {"carrito": carrito})


@login_required
def confirmar_pedido(request):
    carrito = request.session.get("carrito")

    if not carrito:
        return redirect("lista_productos")

    #  VALIDAR PRIMERO (SIN CREAR PEDIDO)
    for key, value in carrito.items():
        producto = Producto.objects.get(id=key)
        cantidad = value["cantidad"]

        if producto.stock < cantidad:
            messages.error(
                request,
                f"No hay suficiente stock para {producto.nombre}. Disponible: {producto.stock}",
            )
            return redirect("ver_carrito")

    # ✅ RECIÉN AQUÍ CREAS EL PEDIDO
    pedido = Pedido.objects.create(usuario=request.user, total=0)

    total = 0

    for key, value in carrito.items():
        producto = Producto.objects.get(id=key)
        cantidad = value["cantidad"]

        subtotal = producto.precio * cantidad

        DetallePedido.objects.create(
            pedido=pedido, producto=producto, cantidad=cantidad
        )

        producto.stock -= cantidad
        producto.save()

        total += subtotal

    pedido.total = total
    pedido.save()

    request.session["carrito"] = {}

    return redirect("mis_pedidos")


@login_required
def reporte_ventas(request):
    # Obtener todos los pedidos, del más reciente al más antiguo
    pedidos = Pedido.objects.all().order_by("-fecha")

    # Contar la cantidad total de pedidos
    cantidad_pedidos = pedidos.count()

    # Sumar el total de todos los pedidos
    total_vendido = pedidos.aggregate(Sum("total"))["total__sum"]

    # Si todavía no hay pedidos, mostrar cero
    if total_vendido is None:
        total_vendido = 0

    # Enviar datos al template del reporte
    return render(
        request,
        "pedidos/reporte_ventas.html",
        {
            "pedidos": pedidos,
            "cantidad_pedidos": cantidad_pedidos,
            "total_vendido": total_vendido,
        },
    )
