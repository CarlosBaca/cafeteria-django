from django.urls import path
from . import views

urlpatterns = [
    path("productos/", views.lista_productos, name="lista_productos"),
    path("mis-pedidos/", views.mis_pedidos, name="mis_pedidos"),
    path("pedido/<int:pedido_id>/", views.detalle_pedido),
    path("carrito/", views.ver_carrito, name="ver_carrito"),
    path("agregar/<int:producto_id>/", views.agregar_producto, name="agregar"),
    path("eliminar/<int:producto_id>/", views.eliminar_producto, name="eliminar"),
    path("restar/<int:producto_id>/", views.restar_producto, name="restar"),
    path("limpiar/", views.limpiar_carrito, name="limpiar"),
    path("confirmar/", views.confirmar_pedido, name="confirmar_pedido"),
    path("reporte-ventas/", views.reporte_ventas, name="reporte_ventas"),
]
