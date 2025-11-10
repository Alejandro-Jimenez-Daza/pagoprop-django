from django.contrib import admin

# Register your models here.
from .models import Apartamento, PropietarioApartamento, Comprobante

# Registramos el modelo Apartamento
@admin.register(Apartamento)
class ApartamentoAdmin(admin.ModelAdmin):
    list_display = ['apartamentoID', 'numeroApartamento']
    search_fields = ['numeroApartamento']

# Registramos el modelo PropietarioApartamento
@admin.register(PropietarioApartamento)
class PropietarioApartamentoAdmin(admin.ModelAdmin):
    list_display = ['propietarioAptoID', 'copropietario', 'apartamento']
    list_filter = ['apartamento']
    search_fields = ['copropietario__username', 'apartamento__numeroApartamento']

# Registramos el modelo Comprobante
@admin.register(Comprobante)
class ComprobanteAdmin(admin.ModelAdmin):
    list_display = ['comprobanteID', 'copropietario', 'apartamento', 'monto', 'fecha_creacion']
    list_filter = ['fecha_creacion', 'apartamento']
    search_fields = ['copropietario__username', 'apartamento__numeroApartamento']