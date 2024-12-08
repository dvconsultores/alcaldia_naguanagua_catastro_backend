from django.contrib import admin
from .models import *
from django.apps import apps

myapp = apps.get_app_config('backend')
for model in myapp.get_models():
    if model != Inmueble and model != Permiso:    # Exclude Inmueble from the loop
        admin.site.register(model)

# Register your models here.

class InmuebleAdmin(admin.ModelAdmin):
    list_display=(
    "numero_expediente",
    "fecha_inscripcion",
    "fecha_creacion",
    #"tipo",
    "status",
    #"nivel",
    #"unidad",
    "urbanizacion",
    #"calle",
    "conjunto_residencial",
    "edificio",
    "avenida",
    "torre",
    "numero_civico",
    "numero_casa",
    "numero_piso",
    "telefono",
    "zona",
    "categorizacion",
    "direccion",
    "referencia",
    "observaciones",
    "habilitado",
    #"periodo",
    #"tipodesincorporacion",
    #"anio",
    "comunidad",)
    list_filter=("habilitado","categorizacion","status","urbanizacion") 
    search_fields=("numero_expediente",)
admin.site.register(Inmueble,InmuebleAdmin) 

class PermisoAdmin(admin.ModelAdmin):
    list_display=("modulo","perfil")
    list_filter=("modulo","perfil")
admin.site.register(Permiso,PermisoAdmin) 