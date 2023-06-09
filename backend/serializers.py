from rest_framework import fields, serializers
from .models import *

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class PerfilSerializer(serializers.ModelSerializer):
    class Meta:
        model = Perfil
        fields = '__all__'  

class PermisoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permiso
        fields = '__all__'  
    titulo_modulo= serializers.SerializerMethodField('loadtitulo_modulo')
    def loadtitulo_modulo(self, obj):
      return obj.modulo.titulo 
    menu_modulo= serializers.SerializerMethodField('loadmenu_modulo')
    def loadmenu_modulo(self, obj):
      return obj.modulo.menu
    es_menu_modulo= serializers.SerializerMethodField('loades_menu_modulo')
    def loades_menu_modulo(self, obj):
      return obj.modulo.es_menu
    orden_modulo= serializers.SerializerMethodField('loadorden_modulo')
    def loadorden_modulo(self, obj):
      return obj.modulo.orden
    icono_modulo= serializers.SerializerMethodField('loadicono_modulo')
    def loadicono_modulo(self, obj):
      return obj.modulo.icono

class DepartamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Departamento
        fields = '__all__'  

class ModuloSerializer(serializers.ModelSerializer):
    class Meta:
        model = Modulo
        fields = '__all__'  

class AmbitoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ambito
        fields = ['id','codigo','descripcion']

class CreateAmbitoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ambito
        fields = '__all__'

class SectorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sector
        fields = '__all__'
    descripcion_ambito= serializers.SerializerMethodField('loaddescripcion_ambito')
    def loaddescripcion_ambito(self, obj):
      return obj.ambito.descripcion 

class CalleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Calle
        fields = '__all__'

class AvenidaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Avenida
        fields = '__all__'

class UrbanizacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Urbanizacion
        fields = '__all__'

    ambito= serializers.SerializerMethodField('loadid_ambito')
    def loadid_ambito(self, obj):
      return obj.sector.ambito.id

    descripcion_ambito= serializers.SerializerMethodField('loaddescripcion_ambito')
    def loaddescripcion_ambito(self, obj):
      return obj.sector.ambito.descripcion

    sector= serializers.SerializerMethodField('loadid_sector')
    def loadid_sector(self, obj):
      return obj.sector.id

    descripcion_sector= serializers.SerializerMethodField('loaddescripcion_sector')
    def loaddescripcion_sector(self, obj):
      return obj.sector.descripcion        

class ManzanaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manzana
        fields = '__all__'

    ambito= serializers.SerializerMethodField('loadid_ambito')
    def loadid_ambito(self, obj):
      return obj.sector.ambito.id
    
    descripcion_ambito= serializers.SerializerMethodField('loaddescripcion_ambito')
    def loaddescripcion_ambito(self, obj):
      return obj.sector.ambito.descripcion
    
    descripcion_sector= serializers.SerializerMethodField('loaddescripcion_sector')
    def loaddescripcion_sector(self, obj):
      return obj.sector.descripcion
    
    descripcion_via_norte= serializers.SerializerMethodField('loaddescripcion_via_norte')
    def loaddescripcion_via_norte(self, obj):
      return obj.via_norte.nombre
    
    descripcion_via_sur= serializers.SerializerMethodField('loaddescripcion_via_sur')
    def loaddescripcion_via_sur(self, obj):
      return obj.via_sur.nombre
    
    descripcion_via_este= serializers.SerializerMethodField('loaddescripcion_via_este')
    def loaddescripcion_via_este(self, obj):
      return obj.via_este.nombre
    
    descripcion_via_oeste= serializers.SerializerMethodField('loaddescripcion_via_oeste')
    def loaddescripcion_via_oeste(self, obj):
      return obj.via_oeste.nombre

class ParcelaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parcela
        fields = '__all__'

    ambito= serializers.SerializerMethodField('loadid_ambito')
    def loadid_ambito(self, obj):
      return obj.manzana.sector.ambito.id
        
    descripcion_ambito= serializers.SerializerMethodField('loaddescripcion_ambito')
    def loaddescripcion_ambito(self, obj):
      return obj.manzana.sector.ambito.descripcion

    sector= serializers.SerializerMethodField('loadid_sector')
    def loadid_sector(self, obj):
      return obj.manzana.sector.id

    descripcion_sector= serializers.SerializerMethodField('loaddescripcion_sector')
    def loaddescripcion_sector(self, obj):
      return obj.manzana.sector.descripcion

    manzana= serializers.SerializerMethodField('loadid_manzana')
    def loadid_manzana(self, obj):
      return obj.manzana.id

    codigo_manzana= serializers.SerializerMethodField('loadcodigo_manzana')
    def loadcodigo_manzana(self, obj):
      return obj.manzana.codigo


class SubParcelaSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubParcela
        fields = '__all__'

    ambito= serializers.SerializerMethodField('loadid_ambito')
    def loadid_ambito(self, obj):
      return obj.parcela.manzana.sector.ambito.id
    
    descripcion_ambito= serializers.SerializerMethodField('loaddescripcion_ambito')
    def loaddescripcion_ambito(self, obj):
      return obj.parcela.manzana.sector.ambito.descripcion

    sector= serializers.SerializerMethodField('loadid_sector')
    def loadid_sector(self, obj):
      return obj.parcela.manzana.sector.id

    descripcion_sector= serializers.SerializerMethodField('loaddescripcion_sector')
    def loaddescripcion_sector(self, obj):
      return obj.parcela.manzana.sector.descripcion

    manzana= serializers.SerializerMethodField('loadid_manzana')
    def loadid_manzana(self, obj):
      return obj.parcela.manzana.id

    codigo_manzana= serializers.SerializerMethodField('loadcodigo_manzana')
    def loadcodigo_manzana(self, obj):
      return obj.parcela.manzana.codigo
            
    codigo_parcela= serializers.SerializerMethodField('loadcodigo_parcela')
    def loadcodigo_parcela(self, obj):
      return obj.parcela.codigo
    

class ConjuntoResidencialSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConjuntoResidencial
        fields = '__all__'

    ambito= serializers.SerializerMethodField('loadid_ambito')
    def loadid_ambito(self, obj):
      return obj.urbanizacion.sector.ambito.id
    
    descripcion_ambito= serializers.SerializerMethodField('loaddescripcion_ambito')
    def loaddescripcion_ambito(self, obj):
      return obj.urbanizacion.sector.ambito.descripcion

    sector= serializers.SerializerMethodField('loadid_sector')
    def loadid_sector(self, obj):
      return obj.urbanizacion.sector.id

    descripcion_sector= serializers.SerializerMethodField('loaddescripcion_sector')
    def loaddescripcion_sector(self, obj):
      return obj.urbanizacion.sector.descripcion  

    urbanizacion= serializers.SerializerMethodField('loadid_urbanizacion')
    def loadid_urbanizacion(self, obj):
      return obj.urbanizacion.id

    nombre_urbanizacion= serializers.SerializerMethodField('loadnombre_urbanizacion')
    def loadnombre_urbanizacion(self, obj):
      return obj.urbanizacion.nombre             

class EdificioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Edificio
        fields = '__all__'

    ambito= serializers.SerializerMethodField('loadid_ambito')
    def loadid_ambito(self, obj):
      return obj.urbanizacion.sector.ambito.id
    
    descripcion_ambito= serializers.SerializerMethodField('loaddescripcion_ambito')
    def loaddescripcion_ambito(self, obj):
      return obj.urbanizacion.sector.ambito.descripcion

    sector= serializers.SerializerMethodField('loadid_sector')
    def loadid_sector(self, obj):
      return obj.urbanizacion.sector.id

    descripcion_sector= serializers.SerializerMethodField('loaddescripcion_sector')
    def loaddescripcion_sector(self, obj):
      return obj.urbanizacion.sector.descripcion   

    nombre_urbanizacion= serializers.SerializerMethodField('loadnombre_urbanizacion')
    def loadnombre_urbanizacion(self, obj):
      return obj.urbanizacion.nombre 
    
    nombre_conjuntoresidencial= serializers.SerializerMethodField('loadnombre_conjuntoresidencial')
    def loadnombre_conjuntoresidencial(self, obj):
      return obj.conjunto_residencial.nombre   
      
class TorreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Torre
        fields = '__all__'

    ambito= serializers.SerializerMethodField('loadid_ambito')
    def loadid_ambito(self, obj):
      return obj.urbanizacion.sector.ambito.id

    descripcion_ambito= serializers.SerializerMethodField('loaddescripcion_ambito')
    def loaddescripcion_ambito(self, obj):
      return obj.urbanizacion.sector.ambito.descripcion

    sector= serializers.SerializerMethodField('loadid_sector')
    def loadid_sector(self, obj):
      return obj.urbanizacion.sector.id

    descripcion_sector= serializers.SerializerMethodField('loaddescripcion_sector')
    def loaddescripcion_sector(self, obj):
      return obj.urbanizacion.sector.descripcion   

    nombre_urbanizacion= serializers.SerializerMethodField('loadnombre_urbanizacion')
    def loadnombre_urbanizacion(self, obj):
      return obj.urbanizacion.nombre 
    
    nombre_conjuntoresidencial= serializers.SerializerMethodField('loadnombre_conjuntoresidencial')
    def loadnombre_conjuntoresidencial(self, obj):
      return obj.conjunto_residencial.nombre
    
class PropietarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Propietario
        fields = '__all__'

class TipoInmuebleSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoInmueble
        fields = '__all__'

class EstatusInmuebleSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstatusInmueble
        fields = '__all__'

class NivelInmuebleSerializer(serializers.ModelSerializer):
    class Meta:
        model = NivelInmueble
        fields = '__all__'

class UnidadInmuebleSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnidadInmueble
        fields = '__all__'

class TipoDocumentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoDocumento
        fields = '__all__'

class TipoEspecialSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoEspecial
        fields = '__all__'

class TipoTenenciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoTenencia
        fields = '__all__'

class TopografiaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topografia
        fields = '__all__'

class AccesoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Acceso
        fields = '__all__'

class FormaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Forma
        fields = '__all__'

class UbicacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ubicacion
        fields = '__all__'

class UsoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Uso
        fields = '__all__'

class RegimenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Regimen
        fields = '__all__'

class ServiciosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Servicios
        fields = '__all__'

class FinesFiscalesSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinesFiscales
        fields = '__all__'

class TipoDesincorporacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoDesincorporacion
        fields = '__all__'

class TipoTransaccionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoTransaccion
        fields = '__all__'

class TipologiaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tipologia
        fields = '__all__'

class ZonaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Zona
        fields = '__all__'



class InmuebleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inmueble
        fields = '__all__'
     

    descripcion_ambito= serializers.SerializerMethodField('loaddescripcion_ambito')
    def loaddescripcion_ambito(self, obj):
      return obj.ambito.descripcion 

    descripcion_tipo= serializers.SerializerMethodField('loaddescripcion_tipo')
    def loaddescripcion_tipo(self, obj):
      return obj.tipo.descripcion

    descripcion_status= serializers.SerializerMethodField('loaddescripcion_status')
    def loaddescripcion_status(self, obj):
      return obj.status.descripcion

    descripcion_sector= serializers.SerializerMethodField('loaddescripcion_sector')
    def loaddescripcion_sector(self, obj):
      return obj.sector.descripcion

    descripcion_manzana= serializers.SerializerMethodField('loaddescripcion_manzana')
    def loaddescripcion_manzana(self, obj):
      return obj.manzana.codigo

    codigo_parcela= serializers.SerializerMethodField('loadcodigo_parcela')
    def loadcodigo_parcela(self, obj):
      return obj.parcela.codigo

    codigo_subparcela= serializers.SerializerMethodField('loadcodigo_subparcela')
    def loadcodigo_subparcela(self, obj):
      return obj.subparcela.codigo

    descripcion_nivel= serializers.SerializerMethodField('loaddescripcion_nivel')
    def loaddescripcion_nivel(self, obj):
      return obj.nivel.descripcion

    descripcion_unidad= serializers.SerializerMethodField('loaddescripcion_unidad')
    def loaddescripcion_unidad(self, obj):
      return obj.unidad.descripcion

    nombre_urbanizacion= serializers.SerializerMethodField('loadnombre_urbanizacion')
    def loadnombre_urbanizacion(self, obj):
      return obj.urbanizacion.nombre


    nombre_calle= serializers.SerializerMethodField('loadnombre_calle')
    def loadnombre_calle(self, obj):
      return obj.calle.nombre
    
    nombre_conjunto_residencial= serializers.SerializerMethodField('loadnombre_conjunto_residencial')
    def loadnombre_conjunto_residencial(self, obj):
      return obj.conjunto_residencial.nombre
    
    nombre_edificio= serializers.SerializerMethodField('loadnombre_edificio')
    def loadnombre_edificio(self, obj):
      return obj.edificio.nombre
    
    nombre_avenida= serializers.SerializerMethodField('loadnombre_avenida')
    def loadnombre_avenida(self, obj):
      return obj.avenida.nombre
    
    nombre_torre= serializers.SerializerMethodField('loadnombre_torre')
    def loadnombre_torre(self, obj):
      return obj.torre.nombre

    descripcion_zona= serializers.SerializerMethodField('loaddescripcion_zona')
    def loaddescripcion_zona(self, obj):
      return obj.zona.descripcion



class InmueblePropietariosSerializer(serializers.ModelSerializer):
    inmueble = InmuebleSerializer()
    propietario = PropietarioSerializer()
    class Meta:
        model = InmueblePropietarios
        fields = '__all__'




class InmueblePropiedadSerializer(serializers.ModelSerializer):
    class Meta:
        model = InmueblePropiedad
        fields = '__all__'


class InmuebleTerrenoSerializer(serializers.ModelSerializer):
    class Meta:
        model = InmuebleTerreno
        fields = '__all__'

class InmuebleTerrenoTopografiaSerializer(serializers.ModelSerializer):
    class Meta:
        model = InmuebleTerrenoTopografia
        fields = '__all__'

class InmuebleTerrenoAccesoSerializer(serializers.ModelSerializer):
    class Meta:
        model = InmuebleTerrenoAcceso
        fields = '__all__'

class InmuebleTerrenoUsoSerializer(serializers.ModelSerializer):
    class Meta:
        model = InmuebleTerrenoUso
        fields = '__all__'

class InmuebleTerrenoRegimenSerializer(serializers.ModelSerializer):
    class Meta:
        model = InmuebleTerrenoRegimen
        fields = '__all__'

class UsoConstruccionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsoConstruccion
        fields = '__all__'

class SoporteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Soporte
        fields = '__all__'

class TechoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Techo
        fields = '__all__'

class CubiertaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cubierta
        fields = '__all__'

class TipoParedSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoPared
        fields = '__all__'

class AcabadoParedSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcabadoPared
        fields = '__all__'

class ConservacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conservacion
        fields = '__all__'

class InmuebleConstruccionSerializer(serializers.ModelSerializer):
    class Meta:
        model = InmuebleConstruccion
        fields = '__all__'


class InmuebleConstruccionSoporteSerializer(serializers.ModelSerializer):
    class Meta:
        model = InmuebleConstruccionSoporte
        fields = '__all__'

class InmuebleConstruccionTechoSerializer(serializers.ModelSerializer):
    class Meta:
        model = InmuebleConstruccionTecho
        fields = '__all__'

class InmuebleConstruccionCubiertaSerializer(serializers.ModelSerializer):
    class Meta:
        model = InmuebleConstruccionCubierta
        fields = '__all__'

class InmuebleValoracionTerrenoSerializer(serializers.ModelSerializer):
    class Meta:
        model = InmuebleValoracionTerreno
        fields = '__all__'

class InmuebleValoracionConstruccionSerializer(serializers.ModelSerializer):
    class Meta:
        model = InmuebleValoracionConstruccion
        fields = '__all__' 

class InmuebleUbicacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = InmuebleUbicacion
        fields = '__all__' 

class InmuebleFaltanteSerializer(serializers.ModelSerializer):
    class Meta:
        model = InmuebleFaltante
        fields = '__all__' 

class PropietarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Propietario
        fields = '__all__' 



class TasaBCVSerializer(serializers.ModelSerializer):
    class Meta:
        model = TasaBCV
        fields = '__all__'

class UnidadTributariaSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnidadTributaria
        fields = '__all__'   

class MonedaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Moneda
        fields = '__all__'   

class TasaMultaSerializer(serializers.ModelSerializer):
    class Meta:
        model = TasaMulta
        fields = '__all__' 


class TipoFlujoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoFlujo
        fields = '__all__' 

class EstadoCuentaSerializer(serializers.ModelSerializer):
    inmueble = InmuebleSerializer()
    tipoflujo = TipoFlujoSerializer()
    propietario = PropietarioSerializer()
    class Meta:
        model = EstadoCuenta
        fields = '__all__' 

class EstadoCuentaDetalleSerializer(serializers.ModelSerializer):
    #estadocuenta=EstadoCuentaSerializer()
    class Meta:
        model = EstadoCuentaDetalle
        fields = '__all__'       

class LiquidacionSerializer(serializers.ModelSerializer):
    inmueble = InmuebleSerializer()
    tipoflujo = TipoFlujoSerializer()
    propietario = PropietarioSerializer()
    estadocuenta = EstadoCuentaSerializer()
    class Meta:
        model = Liquidacion
        fields = '__all__' 

class LiquidacionDetalleSerializer(serializers.ModelSerializer):
    class Meta:
        model = LiquidacionDetalle
        fields = '__all__'            

class TipoPagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoPago
        fields = '__all__'  

class PagoEstadoCuentaSerializer(serializers.ModelSerializer):
    liquidacion = LiquidacionSerializer()
    class Meta:
        model = PagoEstadoCuenta
        fields = '__all__' 

class PagoEstadoCuentaDetalleSerializer(serializers.ModelSerializer):
    class Meta:
        model = PagoEstadoCuentaDetalle
        fields = '__all__' 

class CorrelativoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Correlativo
        fields = '__all__'       

class FlujoSerializer(serializers.ModelSerializer):
    pagoestadocuenta = PagoEstadoCuentaSerializer()
    class Meta:
        model = Flujo
        fields = '__all__' 


class FlujoDetalleSerializer(serializers.ModelSerializer):
    class Meta:
        model = FlujoDetalle
        fields = '__all__' 

    flujo_fecha = serializers.SerializerMethodField('get_flujo_fecha')
    def get_flujo_fecha(self, obj):
        formatted_date = obj.flujo.fecha.strftime("%d/%m/%Y")
        formatted_time = obj.flujo.fecha.strftime("%I:%M %p")
        return f"{formatted_date} {formatted_time}"  

    tipoflujo_descripcion= serializers.SerializerMethodField('loadtipoflujo_descripcion')
    def loadtipoflujo_descripcion(self, obj):
      return obj.flujo.pagoestadocuenta.liquidacion.tipoflujo.descripcion
    
    propietario_nombre= serializers.SerializerMethodField('loadpropietario_nombre')
    def loadpropietario_nombre(self, obj):
      return obj.flujo.pagoestadocuenta.liquidacion.propietario.nombre
    
    propietario_numero= serializers.SerializerMethodField('loadpropietario_numero')
    def loadpropietario_numero(self, obj):
      return obj.flujo.pagoestadocuenta.liquidacion.propietario.numero_documento

    expediente= serializers.SerializerMethodField('loadpexpediente')
    def loadpexpediente(self, obj):
      return obj.flujo.inmueble.numero_expediente

    envia_usuario_nombre= serializers.SerializerMethodField('loadenvia_usuario_nombre')
    def loadenvia_usuario_nombre(self, obj):
      return obj.envia_usuario.username

    recibe_usuario_nombre= serializers.SerializerMethodField('loadrecibe_usuario_nombre')
    def loadrecibe_usuario_nombre(self, obj):
      return obj.recibe_usuario.username
    
    usuario_envia_nombre= serializers.SerializerMethodField('loadusuario_envia_nombre')
    def loadusuario_envia_nombre(self, obj):
      return obj.usuario_envia.usuario.username
    
    usuario_envia_departamento= serializers.SerializerMethodField('loadusuario_envia_departamento')
    def loadusuario_envia_departamento(self, obj):
      return obj.usuario_envia.departamento.nombre
    
    usuario_recibe_nombre= serializers.SerializerMethodField('loadusuario_recibe_nombre')
    def loadusuario_recibe_nombre(self, obj):
      return obj.usuario_recibe.usuario.username    

    usuario_recibe_departamento= serializers.SerializerMethodField('loadusuario_recibe_departamento')    
    def loadusuario_recibe_departamento(self, obj):
      return obj.usuario_recibe.departamento.nombre    

    estado_display = serializers.SerializerMethodField('get_estado_display')
    def get_estado_display(self, obj):
        return dict(FlujoDetalle.ESTADO)[obj.estado]

    tarea_display = serializers.SerializerMethodField('get_tarea_display')
    def get_tarea_display(self, obj):
        return dict(FlujoDetalle.TAREA)[obj.tarea]
    
    recibe_fecha = serializers.SerializerMethodField('get_recibe_fecha')
    def get_recibe_fecha(self, obj):
        formatted_date = obj.recibe_fecha.strftime("%d/%m/%Y")
        formatted_time = obj.recibe_fecha.strftime("%I:%M %p")
        return f"{formatted_date} {formatted_time}"

    envia_fecha = serializers.SerializerMethodField('get_envia_fecha')
    def get_envia_fecha(self, obj):
        formatted_date = obj.envia_fecha.strftime("%d/%m/%Y")
        formatted_time = obj.envia_fecha.strftime("%I:%M %p")
        return f"{formatted_date} {formatted_time}"
    
    procesa_fecha = serializers.SerializerMethodField('get_procesa_fecha')
    def get_procesa_fecha(self, obj):
        formatted_date = obj.procesa_fecha.strftime("%d/%m/%Y")
        formatted_time = obj.procesa_fecha.strftime("%I:%M %p")
        return f"{formatted_date} {formatted_time}"    