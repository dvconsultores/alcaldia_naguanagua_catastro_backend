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
router.register(r'categorizacion', views.CategorizacionViewset,basename='categorizacion')
router.register(r'tipologia_categorizacion', views.Tipologia_CategorizacionViewset,basename='tipologia_categorizacion')
router.register(r'inmueble', views.InmuebleViewset,basename='inmueble')
router.register(r'inmueble_propiedad', views.InmueblePropiedadViewset,basename='inmueble_propiedad')
router.register(r'inmueble_propietarios', views.InmueblePropietariosViewset,basename='inmueble_propietarios')
router.register(r'inmueble_terreno', views.InmuebleTerrenoViewset,basename='inmueble_terreno')
router.register(r'inmueble_terreno_topografia', views.InmuebleTerrenoTopografiaViewset,basename='inmueble_terreno_topografia')
router.register(r'inmueble_terreno_acceso', views.InmuebleTerrenoAccesoViewset,basename='inmueble_terreno_acceso')
router.register(r'inmueble_terreno_uso', views.InmuebleTerrenoUsoViewset,basename='inmueble_terreno_uso')
router.register(r'inmueble_terreno_servicio', views.InmuebleTerrenoServicioViewset,basename='inmueble_terreno_servicio')
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

router.register(r'inmueble_valoracion_terreno2024', views.InmuebleValoracionTerreno2024Viewset,basename='inmueble_valoracion_terreno2024')
router.register(r'inmueble_valoracion_construccion2024', views.InmuebleValoracionConstruccion2024Viewset,basename='inmueble_valoracion_construccion2024')

router.register(r'inmueble_ubicacion', views.InmuebleUbicacionViewset,basename='inmueble_ubicacion')
router.register(r'inmueble_faltante', views.InmuebleFaltanteViewset,basename='inmueble_faltante')
router.register(r'propietario/', views.PropietarioViewset,basename='propietario')
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
router.register(r'ic_periodo', views.IC_PeriodoViewset,basename='ic_periodo')
router.register(r'ic_impuestocargos', views.IC_ImpuestoCargosViewset,basename='ic_impuestocargos')
router.register(r'ic_impuesto', views.IC_ImpuestoViewset,basename='ic_impuesto')
router.register(r'ic_impuestodetalle', views.IC_ImpuestoDetalleViewset,basename='ic_impuestodetalle')
router.register(r'ic_impuestocorrecciones', views.IC_ImpuestoCorreccionesViewset,basename='ic_impuestocorrecciones')
router.register(r'ic_impuestocorreccionesdetalle', views.IC_ImpuestoCorreccionesDetalleViewset,basename='ic_impuestocorreccionesDetalle')
router.register(r'ic_impuestoperiodo', views.IC_ImpuestoPeriodoViewset,basename='ic_impuestoperiodo')
router.register(r'ic_impuestodescuento', views.IC_ImpuestoDescuentoViewset,basename='ic_impuestodescuento')
router.register(r'ic_impuestoexoneracion', views.IC_ImpuestoExoneracionViewset,basename='ic_impuestoexoneracion')
router.register(r'ic_impuestodetalledescuentos', views.IC_ImpuestoDetalleDescuentosViewset,basename='ic_impuestodetalledescuentos')
router.register(r'ic_impuestodetallemora', views.IC_ImpuestoDetalleMoraViewset,basename='ic_impuestodetallemora')
router.register(r'ae_actividadeconomica', views.AE_ActividadEconomicaViewset,basename='ae_actividadeconomica')
router.register(r'ae_actividadeconomicadetalle', views.AE_ActividadEconomicaDetalleViewset,basename='ae_actividadeconomicadetalle') 
router.register(r'ae_patente', views.AE_PatenteViewset,basename='ae_patente')
router.register(r'ae_patente_actividadeconomica', views.AE_Patente_ActividadEconomicaViewset,basename='ae_patente_actividadeconomica') 
router.register(r'tasainteres', views.TasaInteresViewset,basename='tasainteres') 
router.register(r'notacredito', views.NotaCreditoViewset,basename='notacredito') 
router.register(r'ExcelDocument', views.ExcelDocumentViewset,basename='exceldocument') 
router.register(r'ExcelDocumentLOG', views.ExcelDocumentLOGViewset,basename='exceldocumentLOG') 
router.register(r'corridasbancarias', views.CorridasBancariasViewset,basename='corridasbancarias') 
router.register(r'comunidad', views.ComunidadViewset,basename='comunidad') 


urlpatterns = [
    # Base
    path('', include(router.urls)),
    path('signin/', views.SignIn),
    path('signup/', views.SignUp),
    path('changepassword/', views.ChangePassword),
    path('crearestadocuenta/', views.CrearEstadoCuenta),
    path('crearliquidacion/', views.CrearLiquidacion),
    path('crearPago/', views.CrearPago),
    path('crearperfil/', views.CrearPerfl),
    path('CrearInmueblePropietario/', views.CrearInmueblePropietario),
    path('MultaInmueble/', views.MultaInmueble),
    path('ImpuestoInmueble/', views.ImpuestoInmueble),
    path('ImpuestoInmueble2023/', views.ImpuestoInmueble2023),
    path('ImpuestoInmueblePublic/', views.ImpuestoInmueblePublic),
    path('ImpuestoInmueble2023Public/', views.ImpuestoInmueble2023Public),
    path('DatosInmueblesPublic/', views.DatosInmueblesPublic),
    path('CertificaFicha/', views.CertificaFicha),
    path('ImpuestoInmueblePago/', views.ImpuestoInmueblePago),
    path('ImpuestoInmuebleDetalle/', views.ImpuestoInmuebleDetalle),
    path('importardatosdesdeexcel', views.importardatosdesdeexcel),
    path('importarcorridabancaria', views.importarcorridabancaria),
    path('subir-archivo-excel2/', views.subir_archivo_excel),
    path('upload_excel/', views.upload_excel),
    path('filtrar_propietarios/', views.filtrar_propietarios, name='filtrar_propietarios'),
    path('filtrar_inmuebles/', views.filtrar_inmuebles, name='filtrar_inmuebles'),
    path('listar_inmuebles/', views.listar_inmuebles, name='listar_inmuebles'),

    path('filtrar_flujos/', views.filtrar_flujos, name='filtrar_flujos'),

    path('filtrar_patentes/', views.filtrar_patentes, name='filtrar_patentes'),
    path('crearpatente/', views.CrearPatente),
    path('estadisticaflujo/', views.EstadisticaFlujo),
    path('corridaancaria-sin-pago/', views.CorridasBancariaSinPagoView.as_view()),
    path('corridaancaria-sin-pago-recaudos/', views.CorridasBancariaSinPagoRecaudosView.as_view()),
 

]