from rest_framework.authtoken import views as vx
from rest_framework import routers
from django.urls import include, path
from . import views

router = routers.DefaultRouter()
router.register(r'ambito', views.AmbitoViewset,basename='ambito')
router.register(r'sector', views.SectorViewset,basename='sector')
router.register(r'calle', views.CalleViewset,basename='calle')
router.register(r'avenida', views.AvenidaViewset,basename='avenida')
router.register(r'urbanizacion', views.UrbanizacionViewset,basename='urbanizacion')
router.register(r'manzana', views.ManzanaViewset,basename='manzana')
router.register(r'parcela', views.ParcelaViewset,basename='parcela')
router.register(r'subparcela', views.SubParcelaViewset,basename='subparcela')
router.register(r'conjuntoresidencial', views.ConjuntoResidencialViewset,basename='conjuntoresidencial')
router.register(r'edificio', views.EdificioViewset,basename='edificio')
router.register(r'torre', views.TorreViewset,basename='torre')
router.register(r'propietario', views.PropietarioViewset,basename='propietario')
router.register(r'tipoinmueble', views.TipoInmuebleViewset,basename='tipoinmueble')
router.register(r'estatusinmueble', views.EstatusInmuebleViewset,basename='estatusinmueble')
router.register(r'nivelinmueble', views.NivelInmuebleViewset,basename='nivelinmueble')
router.register(r'unidadinmueble', views.UnidadInmuebleViewset,basename='unidadinmueble')
router.register(r'tipodocumento', views.TipoDocumentoViewset,basename='tipodocumento')
router.register(r'tipoespecial', views.TipoEspecialViewset,basename='tipoespecial')
router.register(r'tipotenencia', views.TipoTenenciaViewset,basename='tipotenencia')
router.register(r'topografia', views.TopografiaViewset,basename='topografia')
router.register(r'acceso', views.AccesoViewset,basename='acceso')
router.register(r'forma', views.FormaViewset,basename='forma')
router.register(r'ubicacion', views.UbicacionViewset,basename='ubicacion')
router.register(r'uso', views.UsoViewset,basename='uso')
router.register(r'regimen', views.RegimenViewset,basename='regimen')
router.register(r'servicios', views.ServiciosViewset,basename='servicios')
router.register(r'finesfiscales', views.FinesFiscalesViewset,basename='finesfiscales')
router.register(r'tipodesincorporacion', views.TipoDesincorporacionViewset,basename='tipodesincorporacion')
router.register(r'tipotransaccion', views.TipoTransaccionViewset,basename='tipotransaccion')
router.register(r'tipologia', views.TipologiaViewset,basename='tipologia')
router.register(r'inmueble', views.InmuebleViewset,basename='inmueble')
router.register(r'inmueble_propiedad', views.InmueblePropiedadViewset,basename='inmueble_propiedad')
router.register(r'inmueble_propietarios', views.InmueblePropietariosViewset,basename='inmueble_propietarios')
router.register(r'inmueble_terreno', views.InmuebleTerrenoViewset,basename='inmueble_terreno')
router.register(r'inmueble_construccion', views.InmuebleConstruccionViewset,basename='inmueble_construccion')
router.register(r'inmueble_valoracion_terreno', views.InmuebleValoracionTerrenoViewset,basename='inmueble_valoracion_terreno')
router.register(r'inmueble_valoracion_construccion', views.InmuebleValoracionConstruccionViewset,basename='inmueble_valoracion_construccion')
router.register(r'inmueble_ubicacion', views.InmuebleUbicacionViewset,basename='inmueble_ubicacion')
router.register(r'inmueble_faltante', views.InmuebleFaltanteViewset,basename='inmueble_faltante')
router.register(r'propietario', views.PropietarioViewset,basename='propietario')


urlpatterns = [
    # Base
    path('', include(router.urls)),
    path('signin/', views.SignIn),
]