from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import *
from .use_cases import *
from django.contrib.auth.models import *
from rest_framework.decorators import api_view,permission_classes
from django.views.decorators.csrf import csrf_exempt
from django_filters.rest_framework import DjangoFilterBackend


class MultiSerializerViewSet(viewsets.ModelViewSet):
    serializers = { 
        'default': None,
    }

    def get_serializer_class(self):
            return self.serializers.get(self.action,
                        self.serializers.get('default'))


@api_view(["POST"])
@csrf_exempt
@permission_classes([AllowAny])
def SignIn(request):
    return generate_token(request.data["username"],request.data["password"])

@api_view(["POST"])
@csrf_exempt
@permission_classes([AllowAny])
def SignUp(request):
    return create_user(request.data["username"],request.data["password"],request.data["email"])

@api_view(["POST"])
@csrf_exempt
@permission_classes([IsAuthenticated])
def ChangePassword(request):
    return change_password(request.user,request.data["password"])

@api_view(["POST"])
@csrf_exempt
@permission_classes([IsAuthenticated])
def CrearEstadoCuenta(request):
    datos=request.data
    return Crear_Estado_Cuenta(datos)

@api_view(["POST"])
@csrf_exempt
@permission_classes([IsAuthenticated])
def CrearLiquidacion(request):
    datos=request.data
    return Crear_Liquidacion(datos)

@api_view(["POST"])
@csrf_exempt
@permission_classes([IsAuthenticated])
def CrearPago(request):
    datos=request.data
    return Crear_Pago(datos)

@api_view(["POST"])
@csrf_exempt
@permission_classes([IsAuthenticated])
def CrearInmueblePropietario(request):
    datos=request.data
    return Crear_Inmueble_Propietario(datos)

class UserViewset(MultiSerializerViewSet):
    permission_classes = [IsAuthenticated]
    queryset=User.objects.all()
    serializers = {
        'default': UserSerializer
    }




class DepartamentoViewset(MultiSerializerViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Departamento.objects.all()
    serializers = {
        'default': DepartamentoSerializer
    }
    filter_backends = [DjangoFilterBackend]
# excluye el departamento de usuario actual.
# este filtro se usa cuando enviamos un documento en FLUJO. y con esto
# evitamos que se envie el doucmento al mismo departamento que envia.
    def get_queryset(self):
        queryset = super().get_queryset()
        nombre_a_excluir = self.request.query_params.get('nombre')
        if nombre_a_excluir:
            queryset = queryset.exclude(nombre=nombre_a_excluir)
        return queryset



class PerfilViewset(MultiSerializerViewSet):
    permission_classes = [IsAuthenticated]
    queryset=Perfil.objects.all()
    serializers = {
        'default': PerfilSerializer
    }

class ModuloViewset(MultiSerializerViewSet):
    permission_classes = [IsAuthenticated]
    queryset=Modulo.objects.all()
    serializers = {
        'default': ModuloSerializer
    }

class PermisoViewset(MultiSerializerViewSet):
    permission_classes = [IsAuthenticated]
    queryset=Permiso.objects.all()
    serializers = {
        'default': PermisoSerializer
    }

class AmbitoViewset(MultiSerializerViewSet):
    permission_classes = [IsAuthenticated]
    queryset=Ambito.objects.all()
    serializers = {
        'default': AmbitoSerializer,
        'create':CreateAmbitoSerializer
    }


class SectorViewset(MultiSerializerViewSet):
    permission_classes = [IsAuthenticated]
    queryset=Sector.objects.all()
    serializers = {
        'default': SectorSerializer
    }

class CalleViewset(MultiSerializerViewSet):
    permission_classes = [IsAuthenticated]
    queryset=Calle.objects.all()
    serializers = {
        'default': CalleSerializer
    }

class AvenidaViewset(MultiSerializerViewSet):
    permission_classes = [IsAuthenticated]
    queryset=Avenida.objects.all()
    serializers = {
        'default': AvenidaSerializer
    }

class UrbanizacionViewset(MultiSerializerViewSet):
    permission_classes = [IsAuthenticated]
    queryset=Urbanizacion.objects.all()
    serializers = {
        'default': UrbanizacionSerializer
    }
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
      'id':['exact'],
    }

class ManzanaViewset(MultiSerializerViewSet):
    permission_classes = [IsAuthenticated]
    queryset=Manzana.objects.all()
    serializers = {
        'default': ManzanaSerializer
    }

class ParcelaViewset(MultiSerializerViewSet):
    permission_classes = [IsAuthenticated]
    queryset=Parcela.objects.all()
    serializers = {
        'default': ParcelaSerializer
    }

class SubParcelaViewset(MultiSerializerViewSet):
    permission_classes = [IsAuthenticated]
    queryset=SubParcela.objects.all()
    serializers = {
        'default': SubParcelaSerializer
    }

class ConjuntoResidencialViewset(MultiSerializerViewSet):
    permission_classes = [IsAuthenticated]
    queryset=ConjuntoResidencial.objects.all()
    serializers = {
        'default': ConjuntoResidencialSerializer
    }

class EdificioViewset(MultiSerializerViewSet):
    permission_classes = [IsAuthenticated]
    queryset=Edificio.objects.all()
    serializers = {
        'default': EdificioSerializer
    }

class TorreViewset(MultiSerializerViewSet):
    permission_classes = [IsAuthenticated]
    queryset=Torre.objects.all()
    serializers = {
        'default': TorreSerializer
    }

class PropietarioViewset(MultiSerializerViewSet):
    permission_classes = [IsAuthenticated]
    queryset=Propietario.objects.all()
    serializers = {
        'default': PropietarioSerializer
    }

class TipoInmuebleViewset(MultiSerializerViewSet):
    permission_classes = [IsAuthenticated]
    queryset=TipoInmueble.objects.all()
    serializers = {
        'default': TipoInmuebleSerializer
    }


class EstatusInmuebleViewset(MultiSerializerViewSet):
    permission_classes = [IsAuthenticated]
    queryset=EstatusInmueble.objects.all()
    serializers = {
        'default': EstatusInmuebleSerializer
    }

class NivelInmuebleViewset(MultiSerializerViewSet):
    permission_classes = [IsAuthenticated]
    queryset=NivelInmueble.objects.all()
    serializers = {
        'default': NivelInmuebleSerializer
    }

class UnidadInmuebleViewset(MultiSerializerViewSet):
    permission_classes = [IsAuthenticated]
    queryset=UnidadInmueble.objects.all()
    serializers = {
        'default': UnidadInmuebleSerializer
    }        

class TipoDocumentoViewset(MultiSerializerViewSet):
    permission_classes = [IsAuthenticated]
    queryset=TipoDocumento.objects.all()
    serializers = {
        'default': TipoDocumentoSerializer
    }

class TipoEspecialViewset(MultiSerializerViewSet):
    permission_classes = [IsAuthenticated]
    queryset=TipoEspecial.objects.all()
    serializers = {
        'default': TipoEspecialSerializer
    }

class TipoTenenciaViewset(MultiSerializerViewSet):
    permission_classes = [IsAuthenticated]
    queryset=TipoTenencia.objects.all()
    serializers = {
        'default': TipoTenenciaSerializer
    }

class TopografiaViewset(MultiSerializerViewSet):
    permission_classes = [IsAuthenticated]
    queryset=Topografia.objects.all()
    serializers = {
        'default': TopografiaSerializer
    }

class AccesoViewset(MultiSerializerViewSet):
    permission_classes = [IsAuthenticated]
    queryset=Acceso.objects.all()
    serializers = {
        'default': AccesoSerializer
    }

class FormaViewset(MultiSerializerViewSet):
    permission_classes = [IsAuthenticated]
    queryset=Forma.objects.all()
    serializers = {
        'default': FormaSerializer
    }        

class UbicacionViewset(MultiSerializerViewSet):
    permission_classes = [IsAuthenticated]
    queryset=Ubicacion.objects.all()
    serializers = {
        'default': UbicacionSerializer
    }

class UsoViewset(MultiSerializerViewSet):
    permission_classes = [IsAuthenticated]
    queryset=Uso.objects.all()
    serializers = {
        'default': UsoSerializer
    }

class RegimenViewset(MultiSerializerViewSet):
    permission_classes = [IsAuthenticated]
    queryset=Regimen.objects.all()
    serializers = {
        'default': RegimenSerializer
    }

class ServiciosViewset(MultiSerializerViewSet):
    permission_classes = [IsAuthenticated]
    queryset=Servicios.objects.all()
    serializers = {
        'default': ServiciosSerializer
    }

class FinesFiscalesViewset(MultiSerializerViewSet):
    permission_classes = [IsAuthenticated]
    queryset=FinesFiscales.objects.all()
    serializers = {
        'default': FinesFiscalesSerializer
    }

class TipoDesincorporacionViewset(MultiSerializerViewSet):
    permission_classes = [IsAuthenticated]
    queryset=TipoDesincorporacion.objects.all()
    serializers = {
        'default': TipoDesincorporacionSerializer
    }        

class TipoTransaccionViewset(MultiSerializerViewSet):
    permission_classes = [IsAuthenticated]
    queryset=TipoTransaccion.objects.all()
    serializers = {
        'default': TipoTransaccionSerializer
    }

class TipologiaViewset(MultiSerializerViewSet):
    permission_classes = [IsAuthenticated]
    queryset=Tipologia.objects.all()
    serializers = {
        'default': TipologiaSerializer
    }

class ZonaViewset(MultiSerializerViewSet):
    permission_classes = [IsAuthenticated]
    queryset=Zona.objects.all()
    serializers = {
        'default': ZonaSerializer
    }

class InmuebleViewset(MultiSerializerViewSet):
    permission_classes = [IsAuthenticated]
    queryset=Inmueble.objects.all()
    serializers = {
        'default': InmuebleSerializer
    }

class InmueblePropiedadViewset(MultiSerializerViewSet):
    permission_classes = [IsAuthenticated]
    queryset= InmueblePropiedad.objects.all()
    serializers = {
        'default': InmueblePropiedadSerializer
    }


class InmueblePropietariosViewset(MultiSerializerViewSet):
    permission_classes = [IsAuthenticated]
    queryset= InmueblePropietarios.objects.all()
    serializers = {
        'default': InmueblePropietariosSerializer
    }
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
      'propietario':['exact'],
      'inmueble':['exact'],
    }

class InmuebleTerrenoViewset(MultiSerializerViewSet):
    permission_classes = [IsAuthenticated]
    queryset= InmuebleTerreno.objects.all()
    serializers = {
        'default': InmuebleTerrenoSerializer
    }

class InmuebleTerrenoTopografiaViewset(MultiSerializerViewSet):
    permission_classes = [IsAuthenticated]
    queryset= InmuebleTerrenoTopografia.objects.all()
    serializers = {
        'default': InmuebleTerrenoTopografiaSerializer
    }
class InmuebleTerrenoAccesoViewset(MultiSerializerViewSet):
    permission_classes = [IsAuthenticated]
    queryset= InmuebleTerrenoAcceso.objects.all()
    serializers = {
        'default': InmuebleTerrenoAccesoSerializer
    }
class InmuebleTerrenoUsoViewset(MultiSerializerViewSet):
    permission_classes = [IsAuthenticated]
    queryset= InmuebleTerrenoUso.objects.all()
    serializers = {
        'default': InmuebleTerrenoUsoSerializer
    }
class InmuebleTerrenoRegimenViewset(MultiSerializerViewSet):
    permission_classes = [IsAuthenticated]
    queryset= InmuebleTerrenoRegimen.objects.all()
    serializers = {
        'default': InmuebleTerrenoRegimenSerializer
    }

class UsoConstruccionViewset(MultiSerializerViewSet):
    permission_classes = [IsAuthenticated]
    queryset=UsoConstruccion.objects.all()
    serializers = {
        'default': UsoConstruccionSerializer
    }

class SoporteViewset(MultiSerializerViewSet):
    permission_classes = [IsAuthenticated]
    queryset=Soporte.objects.all()
    serializers = {
        'default': SoporteSerializer
    }

class TechoViewset(MultiSerializerViewSet):
    permission_classes = [IsAuthenticated]
    queryset=Techo.objects.all()
    serializers = {
        'default': TechoSerializer
    }

class CubiertaViewset(MultiSerializerViewSet):
    permission_classes = [IsAuthenticated]
    queryset=Cubierta.objects.all()
    serializers = {
        'default': CubiertaSerializer
    }

class TipoParedViewset(MultiSerializerViewSet):
    permission_classes = [IsAuthenticated]
    queryset=TipoPared.objects.all()
    serializers = {
        'default': TipoParedSerializer
    }

class AcabadoParedViewset(MultiSerializerViewSet):
    permission_classes = [IsAuthenticated]
    queryset=AcabadoPared.objects.all()
    serializers = {
        'default': AcabadoParedSerializer
    }

class ConservacionViewset(MultiSerializerViewSet):
    permission_classes = [IsAuthenticated]
    queryset=Conservacion.objects.all()
    serializers = {
        'default': ConservacionSerializer
    }

class InmuebleConstruccionViewset(MultiSerializerViewSet):
    permission_classes = [IsAuthenticated]
    queryset= InmuebleConstruccion.objects.all()
    serializers = {
        'default': InmuebleConstruccionSerializer
    }

class InmuebleConstruccionSoporteViewset(MultiSerializerViewSet):
    permission_classes = [IsAuthenticated]
    queryset=InmuebleConstruccionSoporte.objects.all()
    serializers = {
        'default': InmuebleConstruccionSoporteSerializer
    }

class InmuebleConstruccionTechoViewset(MultiSerializerViewSet):
    permission_classes = [IsAuthenticated]
    queryset=InmuebleConstruccionTecho.objects.all()
    serializers = {
        'default': InmuebleConstruccionTechoSerializer
    }

class InmuebleConstruccionCubiertaViewset(MultiSerializerViewSet):
    permission_classes = [IsAuthenticated]
    queryset=InmuebleConstruccionCubierta.objects.all()
    serializers = {
        'default': InmuebleConstruccionCubiertaSerializer
    }

class InmuebleValoracionTerrenoViewset(MultiSerializerViewSet):
    permission_classes = [IsAuthenticated]
    queryset= InmuebleValoracionTerreno.objects.all()
    serializers = {
        'default': InmuebleValoracionTerrenoSerializer
    }
    
class InmuebleValoracionConstruccionViewset(MultiSerializerViewSet):
    permission_classes = [IsAuthenticated]
    queryset= InmuebleValoracionConstruccion.objects.all()
    serializers = {
        'default': InmuebleValoracionConstruccionSerializer
    }

class InmuebleUbicacionViewset(MultiSerializerViewSet):
    permission_classes = [IsAuthenticated]
    queryset= InmuebleUbicacion.objects.all()
    serializers = {
        'default': InmuebleUbicacionSerializer
    }

class InmuebleFaltanteViewset(MultiSerializerViewSet):
    permission_classes = [IsAuthenticated]
    queryset= InmuebleFaltante.objects.all()
    serializers = {
        'default': InmuebleFaltanteSerializer
    }

class PropietarioViewset(MultiSerializerViewSet):
    permission_classes = [IsAuthenticated]
    queryset= Propietario.objects.all()
    serializers = {
        'default': PropietarioSerializer
    }



class TasaBCVViewset(MultiSerializerViewSet):
    permission_classes = [IsAuthenticated]
    queryset=TasaBCV.objects.all()
    serializers = {
        'default': TasaBCVSerializer
    }

class UnidadTributariaViewset(MultiSerializerViewSet):
    permission_classes = [IsAuthenticated]
    queryset=UnidadTributaria.objects.all()
    serializers = {
        'default': UnidadTributariaSerializer
    }

class MonedaViewset(MultiSerializerViewSet):
    permission_classes = [IsAuthenticated]
    queryset=Moneda.objects.all()
    serializers = {
        'default': MonedaSerializer
    }

class TasaMultaViewset(MultiSerializerViewSet):
    permission_classes = [IsAuthenticated]
    queryset=TasaMulta.objects.all()
    serializers = {
        'default': TasaMultaSerializer
    }

class TipoFlujoViewset(MultiSerializerViewSet):
    permission_classes = [IsAuthenticated]
    queryset=TipoFlujo.objects.all()
    serializers = {
        'default': TipoFlujoSerializer
    }

class EstadoCuentaViewset(MultiSerializerViewSet):
    permission_classes = [IsAuthenticated]
    queryset=EstadoCuenta.objects.all()
    serializers = {
        'default': EstadoCuentaSerializer
    }
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
      'propietario':['exact'],
      'habilitado':['exact'],
    }

class EstadoCuentaDetalleViewset(MultiSerializerViewSet):
    permission_classes = [IsAuthenticated]
    queryset=EstadoCuentaDetalle.objects.all()
    serializers = {
        'default': EstadoCuentaDetalleSerializer
    }
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
      'estadocuenta_id':['exact'],
    }

class LiquidacionViewset(MultiSerializerViewSet):
    permission_classes = [IsAuthenticated]
    queryset=Liquidacion.objects.all()
    serializers = {
        'default': LiquidacionSerializer
    }
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
      'propietario':['exact'],
      'habilitado':['exact'],
    }

class LiquidacionDetalleViewset(MultiSerializerViewSet):
    permission_classes = [IsAuthenticated]
    queryset=LiquidacionDetalle.objects.all()
    serializers = {
        'default': LiquidacionDetalleSerializer
    }

class TipoPagoViewset(MultiSerializerViewSet):
    permission_classes = [IsAuthenticated]
    queryset=TipoPago.objects.all()
    serializers = {
        'default': TipoPagoSerializer
    }


class BancoViewset(MultiSerializerViewSet):
    permission_classes = [IsAuthenticated]
    queryset=Banco.objects.all()
    serializers = {
        'default': BancoSerializer
    }

class BancoCuentaViewset(MultiSerializerViewSet):
    permission_classes = [IsAuthenticated]
    queryset=BancoCuenta.objects.all()
    serializers = {
        'default': BancoCuentaSerializer
    }


class PagoEstadoCuentaViewset(MultiSerializerViewSet):
    permission_classes = [IsAuthenticated]
    queryset=PagoEstadoCuenta.objects.all()
    serializers = {
        'default': PagoEstadoCuentaSerializer
    }

class PagoEstadoCuentaDetalleViewset(MultiSerializerViewSet):
    permission_classes = [IsAuthenticated]
    queryset=PagoEstadoCuentaDetalle.objects.all()
    serializers = {
        'default': PagoEstadoCuentaDetalleSerializer
    }

class CorrelativoViewset(MultiSerializerViewSet):
    permission_classes = [IsAuthenticated]
    queryset=Correlativo.objects.all()
    serializers = {
        'default': CorrelativoSerializer
    }

class FlujoViewset(MultiSerializerViewSet):
    permission_classes = [IsAuthenticated]
    queryset=Flujo.objects.all()
    serializers = {
        'default': FlujoSerializer
    }

class FlujoDetalleViewset(MultiSerializerViewSet):
    permission_classes = [IsAuthenticated]
    queryset=FlujoDetalle.objects.all()
    serializers = {
        'default': FlujoDetalleSerializer
    }
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
      'estado':['exact'],
      'recibe_usuario':['exact'],
      'departamento_recibe':['exact'],
      'flujo':['exact'],
      'tarea':['exact'],
    }
#    def get_queryset(self):
#        queryset = super().get_queryset()
#        user = self.request.user
#        queryset = queryset.filter(recibe_usuario=user)
#        return queryset
    
#class Viewset(MultiSerializerViewSet):
#    permission_classes = [IsAuthenticated]
#    queryset=.objects.all()
#    serializers = {
#        'default': Serializer
#    }

#class Viewset(MultiSerializerViewSet):
#    permission_classes = [IsAuthenticated]
#    queryset=.objects.all()
#    serializers = {
#        'default': Serializer
#    }

