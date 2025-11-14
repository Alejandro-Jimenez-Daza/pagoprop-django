from django.urls import path
from . import views

urlpatterns = [
    path('registro/', views.registro_view, name='registro'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('mis-apartamentos/', views.mis_apartamentos_view, name='mis_apartamentos'),
    path('subir-comprobante/', views.subir_comprobante_view, name='subir_comprobante'),  # 👈 NUEVA
    path('mis-comprobantes/', views.mis_comprobantes_view, name='mis_comprobantes'),      # 👈 NUEVA
    path('eliminar-comprobante/<int:comprobante_id>/', views.eliminar_comprobante_view, name='eliminar_comprobante'),  # 👈 NUEVA
    path('editar-comprobante/<int:comprobante_id>/', views.editar_comprobante_view, name='editar_comprobante'),  # 👈 NUEVA

]