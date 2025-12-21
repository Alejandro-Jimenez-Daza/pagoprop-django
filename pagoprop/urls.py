from django.urls import path
from . import views

urlpatterns = [
    # Autenticación
    path('registro/', views.registro_view, name='registro'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Usuario normal
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('perfil/', views.perfil_view, name='perfil'),  # 👈 NUEVA
    path('editar-perfil/', views.editar_perfil_view, name='editar_perfil'),  # 👈 NUEVA
    path('cambiar-password/', views.cambiar_password_view, name='cambiar_password'),  # 👈 NUEVA
    path('mis-apartamentos/', views.mis_apartamentos_view, name='mis_apartamentos'),
    path('apartamento/<int:apartamento_id>/', views.detalle_apartamento_view, name='detalle_apartamento'),
    path('subir-comprobante/', views.subir_comprobante_view, name='subir_comprobante'),
    path('mis-comprobantes/', views.mis_comprobantes_view, name='mis_comprobantes'),
    path('editar-comprobante/<int:comprobante_id>/', views.editar_comprobante_view, name='editar_comprobante'),
    path('eliminar-comprobante/<int:comprobante_id>/', views.eliminar_comprobante_view, name='eliminar_comprobante'),
    
    # Administrador
    path('admin-dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
    path('admin-comprobantes/', views.admin_todos_comprobantes_view, name='admin_todos_comprobantes'),
    path('admin-asignar/', views.admin_asignar_apartamento_view, name='admin_asignar_apartamento'),
    path('admin-eliminar-asignacion/<int:asignacion_id>/', views.admin_eliminar_asignacion_view, name='admin_eliminar_asignacion'),
]