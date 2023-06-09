from rest_framework.authtoken import views as vx
from rest_framework import routers
from django.urls import include, path
from . import views

router = routers.DefaultRouter()
router.register(r'departamento',views.DepartamentoViewset,basename='perfil')
router.register(r'perfil',views.PerfilViewset,basename='perfil')
router.register(r'usuarios',views.UserViewset,basename='user')
router.register(r'modulos',views.ModuloViewset,basename='modulo')
router.register(r'permiso',views.PermisoViewset,basename='permiso')
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
router.register(r'zona', views.ZonaViewset,basename='zona')
router.register(r'inmueble', views.InmuebleViewset,basename='inmueble')
router.register(r'inmueble_propiedad', views.InmueblePropiedadViewset,basename='inmueble_propiedad')
router.register(r'inmueble_propietarios', views.InmueblePropietariosViewset,basename='inmueble_propietarios')
router.register(r'inmueble_terreno', views.InmuebleTerrenoViewset,basename='inmueble_terreno')
router.register(r'inmueble_terreno_topografia', views.InmuebleTerrenoTopografiaViewset,basename='inmueble_terreno_topografia')
router.register(r'inmueble_terreno_acceso', views.InmuebleTerrenoAccesoViewset,basename='inmueble_terreno_acceso')
router.register(r'inmueble_terreno_uso', views.InmuebleTerrenoUsoViewset,basename='inmueble_terreno_uso')
router.register(r'inmueble_terreno_regimen', views.InmuebleTerrenoRegimenViewset,basename='inmueble_terreno_regimen')
router.register(r'uso_construccion', views.UsoConstruccionViewset,basename='uso_construccion')
router.register(r'soporte', views.SoporteViewset,basename='soporte')
router.register(r'techo', views.TechoViewset,basename='techo')
router.register(r'cubierta', views.CubiertaViewset,basename='cubierta')
router.register(r'tipo_pared', views.TipoParedViewset,basename='tipo_pared')
router.register(r'acabado_pared', views.AcabadoParedViewset,basename='acabado_pared')
router.register(r'conservacion', views.ConservacionViewset,basename='conservacion')
router.register(r'inmueble_construccion', views.InmuebleConstruccionViewset,basename='inmueble_construccion')
router.register(r'inmueble_construccion_soporte', views.InmuebleConstruccionSoporteViewset,basename='inmueble_construccion_soporte')
router.register(r'inmueble_construccion_techo', views.InmuebleConstruccionTechoViewset,basename='inmueble_construccion_techo')
router.register(r'inmueble_construccion_cubierta', views.InmuebleConstruccionCubiertaViewset,basename='inmueble_construccion_cubierta')
router.register(r'inmueble_valoracion_terreno', views.InmuebleValoracionTerrenoViewset,basename='inmueble_valoracion_terreno')
router.register(r'inmueble_valoracion_construccion', views.InmuebleValoracionConstruccionViewset,basename='inmueble_valoracion_construccion')
router.register(r'inmueble_ubicacion', views.InmuebleUbicacionViewset,basename='inmueble_ubicacion')
router.register(r'inmueble_faltante', views.InmuebleFaltanteViewset,basename='inmueble_faltante')
router.register(r'propietario', views.PropietarioViewset,basename='propietario')
router.register(r'tasabcv', views.TasaBCVViewset,basename='tasabcv')
router.register(r'unidadtributaria', views.UnidadTributariaViewset,basename='unidadtributaria')
router.register(r'moneda', views.MonedaViewset,basename='moneda')
router.register(r'tasamulta', views.TasaMultaViewset,basename='tasamulta')
router.register(r'tipoflujo', views.TipoFlujoViewset,basename='tipoflujo')
router.register(r'tipoflujodetalle', views.TipoFlujoDetalleViewset,basename='tipoflujodetalle')
router.register(r'estadocuenta', views.EstadoCuentaViewset,basename='estadocuenta')
router.register(r'estadocuentadetalle', views.EstadoCuentaDetalleViewset,basename='estadocuentadetalle')
router.register(r'liquidacion', views.LiquidacionViewset,basename='liquidacion')
router.register(r'liquidaciondetalle', views.LiquidacionDetalleViewset,basename='liquidaciondetalle')
router.register(r'tipopago', views.TipoPagoViewset,basename='tipopago')
router.register(r'banco', views.BancoViewset,basename='banco')
router.register(r'bancocuenta', views.BancoCuentaViewset,basename='bancocuenta')
router.register(r'pagoestadocuenta', views.PagoEstadoCuentaViewset,basename='pagoestadocuenta')
router.register(r'pagoestadocuentadetalle', views.PagoEstadoCuentaDetalleViewset,basename='pagoestadocuentadetalle')
router.register(r'correlativo', views.CorrelativoViewset,basename='correlativo')
router.register(r'flujo', views.FlujoViewset,basename='flujo')
router.register(r'flujodetalle', views.FlujoDetalleViewset,basename='flujodetalle')

urlpatterns = [
    # Base
    path('', include(router.urls)),
    path('signin/', views.SignIn),
    path('signup/', views.SignUp),
    path('changepassword/', views.ChangePassword),
    path('crearestadocuenta/', views.CrearEstadoCuenta),
    path('crearliquidacion/', views.CrearLiquidacion),
    path('crearPago/', views.CrearPago),
    path('CrearInmueblePropietario/', views.CrearInmueblePropietario),
    path('MuestraTasa', views.MuestraTasa),
]