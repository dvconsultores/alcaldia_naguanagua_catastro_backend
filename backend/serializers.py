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

    #sector= serializers.SerializerMethodField('loadid_sector')
    #def loadid_sector(self, obj):
    #  return obj.sector.id

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
    
class ParcelaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parcela
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


class SubParcelaSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubParcela
        fields = '__all__'

    ambito= serializers.SerializerMethodField('loadid_ambito')
    def loadid_ambito(self, obj):
      return obj.parcela.sector.ambito.id
    
    descripcion_ambito= serializers.SerializerMethodField('loaddescripcion_ambito')
    def loaddescripcion_ambito(self, obj):
      return obj.parcela.sector.ambito.descripcion

    sector= serializers.SerializerMethodField('loadid_sector')
    def loadid_sector(self, obj):
      return obj.parcela.sector.id

    descripcion_sector= serializers.SerializerMethodField('loaddescripcion_sector')
    def loaddescripcion_sector(self, obj):
      return obj.parcela.sector.descripcion

    codigo_parcela= serializers.SerializerMethodField('loadcodigo_parcela')
    def loadcodigo_parcela(self, obj):
      return obj.parcela.codigo
    

class ConjuntoResidencialSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConjuntoResidencial
        fields = '__all__'

    ambito= serializers.SerializerMethodField('loadid_ambito')
    def loadid_ambito(self, obj):
      if obj.sector:
        return obj.sector.ambito.id
      return None
       
    descripcion_ambito= serializers.SerializerMethodField('loaddescripcion_ambito')
    def loaddescripcion_ambito(self, obj):
      if obj.sector:
        return obj.sector.ambito.descripcion
      return None
       
    descripcion_sector= serializers.SerializerMethodField('loaddescripcion_sector')
    def loaddescripcion_sector(self, obj):
      if obj.sector:
        return obj.sector.descripcion 
      return None           

class EdificioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Edificio
        fields = '__all__'

    ambito= serializers.SerializerMethodField('loadid_ambito')
    def loadid_ambito(self, obj):
      if obj.urbanizacion:
        return obj.urbanizacion.sector.ambito.id
      return None
        
    descripcion_ambito= serializers.SerializerMethodField('loaddescripcion_ambito')
    def loaddescripcion_ambito(self, obj):
      if obj.urbanizacion:
        return obj.urbanizacion.sector.ambito.descripcion
      return None
    
    sector= serializers.SerializerMethodField('loadid_sector')
    def loadid_sector(self, obj):
      if obj.urbanizacion:
        return obj.urbanizacion.sector.id
      return None

    descripcion_sector= serializers.SerializerMethodField('loaddescripcion_sector')
    def loaddescripcion_sector(self, obj):
      if obj.urbanizacion:
        return obj.urbanizacion.sector.descripcion 
      return None
    
    nombre_urbanizacion= serializers.SerializerMethodField('loadnombre_urbanizacion')
    def loadnombre_urbanizacion(self, obj):
      if obj.urbanizacion:
        return obj.urbanizacion.nombre 
      return None
      
class TorreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Torre
        fields = '__all__'

    ambito= serializers.SerializerMethodField('loadid_ambito')
    def loadid_ambito(self, obj):
      return obj.conjuntoresidencial.sector.ambito.id

    descripcion_ambito= serializers.SerializerMethodField('loaddescripcion_ambito')
    def loaddescripcion_ambito(self, obj):
      return obj.conjuntoresidencial.sector.ambito.descripcion

    sector= serializers.SerializerMethodField('loadid_sector')
    def loadid_sector(self, obj):
      return obj.conjuntoresidencial.sector.id

    descripcion_sector= serializers.SerializerMethodField('loaddescripcion_sector')
    def loaddescripcion_sector(self, obj):
      return obj.conjuntoresidencial.sector.descripcion   
    
    nombre_conjuntoresidencial= serializers.SerializerMethodField('loadnombre_conjuntoresidencial')
    def loadnombre_conjuntoresidencial(self, obj):
      return obj.conjuntoresidencial.nombre
    
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

class Tipologia_CategorizacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tipologia_Categorizacion
        fields = '__all__'

class ZonaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Zona
        fields = '__all__'

class CategorizacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categorizacion
        fields = '__all__'

class IC_PeriodoSerializer(serializers.ModelSerializer):
    class Meta:
        model = IC_Periodo
        fields = '__all__' 

class InmuebleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inmueble
        fields = '__all__'

    codigo_ambito= serializers.SerializerMethodField('loadcodigo_ambito')
    def loadcodigo_ambito(self, obj):
      if obj.ambito:
        return obj.ambito.codigo
      return None   
    descripcion_ambito= serializers.SerializerMethodField('loaddescripcion_ambito')
    def loaddescripcion_ambito(self, obj):
      if obj.ambito:
        return obj.ambito.descripcion
      return None

    descripcion_tipo= serializers.SerializerMethodField('loaddescripcion_tipo')
    def loaddescripcion_tipo(self, obj):
      if obj.tipo:
        return obj.tipo.descripcion
      return None

    descripcion_status= serializers.SerializerMethodField('loaddescripcion_status')
    def loaddescripcion_status(self, obj):
      if obj.status:
        return obj.status.descripcion
      return None
    
    inmueble_activo= serializers.SerializerMethodField('loadinmueble_activo')
    def loadinmueble_activo(self, obj):
      if obj.status:
        return obj.status.inmueble_activo
      return None


    descripcion_sector= serializers.SerializerMethodField('loaddescripcion_sector')
    def loaddescripcion_sector(self, obj):
      if obj.sector:
        return obj.sector.descripcion
      return None

    codigo_sector= serializers.SerializerMethodField('loadcodigo_sector')
    def loadcodigo_sector(self, obj):
      if obj.sector:
        return obj.sector.codigo
      return None

    codigo_manzana= serializers.SerializerMethodField('loadcodigo_manzana')
    def loadcodigo_manzana(self, obj):
      if obj.manzana:
        return obj.manzana.codigo
      return None

    codigo_parcela= serializers.SerializerMethodField('loadcodigo_parcela')
    def loadcodigo_parcela(self, obj):
      if obj.parcela:
        return obj.parcela.codigo
      return None

    codigo_subparcela= serializers.SerializerMethodField('loadcodigo_subparcela')
    def loadcodigo_subparcela(self, obj):
      if obj.subparcela:
        return obj.subparcela.codigo
      return None

    codigo_nivel= serializers.SerializerMethodField('loadcodigo_nivel')
    def loadcodigo_nivel(self, obj):
      if obj.nivel:
        return obj.nivel.codigo
      return None
    
    codigo_unidad= serializers.SerializerMethodField('loadcodigo_unidad')
    def loadcodigo_unidad(self, obj):
      if obj.unidad:
        return obj.unidad.codigo
      return None
    
    nombre_urbanizacion= serializers.SerializerMethodField('loadnombre_urbanizacion')
    def loadnombre_urbanizacion(self, obj):
      if obj.urbanizacion:
        return obj.urbanizacion.nombre
      return None

    #id_zona= serializers.SerializerMethodField('loadid_zona')
    #def loadid_zona(self, obj):
    #  if obj.zona:
    #    return obj.zona.id
    #  return None


    #id_zona= serializers.SerializerMethodField('loadid_zona')  activar cuando se valide la zona desde la urbanzacion
    #def loadid_zona(self, obj):
    #  if obj.urbanizacion:
    #    return obj.urbanizacion.zona.id
    #  return None

    nombre_calle= serializers.SerializerMethodField('loadnombre_calle')
    def loadnombre_calle(self, obj):
      if obj.calle:
          return obj.calle.nombre
      return None
    
    nombre_conjunto_residencial= serializers.SerializerMethodField('loadnombre_conjunto_residencial')
    def loadnombre_conjunto_residencial(self, obj):
      if obj.conjunto_residencial:
        return obj.conjunto_residencial.nombre
      return None    
    nombre_edificio= serializers.SerializerMethodField('loadnombre_edificio')
    def loadnombre_edificio(self, obj):
      if obj.edificio:
        return obj.edificio.nombre
      return None
        
    nombre_avenida= serializers.SerializerMethodField('loadnombre_avenida')
    def loadnombre_avenida(self, obj):
      if obj.avenida:
        return obj.avenida.nombre
      return None
        
    nombre_torre= serializers.SerializerMethodField('loadnombre_torre')
    def loadnombre_torre(self, obj):
      if obj.torre:
        return obj.torre.nombre
      return None

    codigo_zona= serializers.SerializerMethodField('loadcodigo_zona')
    def loadcodigo_zona(self, obj):
      if obj.zona:
        return obj.zona.codigo
      return None  
    
    descripcion_zona= serializers.SerializerMethodField('loaddescripcion_zona')
    def loaddescripcion_zona(self, obj):
      if obj.zona:
        return obj.zona.descripcion
      return None

    descripcion_categorizacion= serializers.SerializerMethodField('loaddescripcion_categorizacion')
    def loaddescripcion_categorizacion(self, obj):
      if obj.categorizacion:
        return obj.categorizacion.descripcion
      return None

    codigo_categorizacion= serializers.SerializerMethodField('loadcodigo_categorizacion')
    def loadcodigo_categorizacion(self, obj):
      if obj.categorizacion:
        return obj.categorizacion.codigo
      return None

    descripcion_comunidad= serializers.SerializerMethodField('loaddescripcion_comunidad')
    def loaddescripcion_comunidad(self, obj):
      if obj.comunidad:
        return obj.comunidad.comunidad
      return None




    codigo_periodo= serializers.SerializerMethodField('loadcodigo_periodo')
    def loadcodigo_periodo(self, obj):
      if obj.periodo:
        return obj.periodo.periodo
      return None
    
    id_periodo= serializers.SerializerMethodField('loadid_periodo')
    def loadid_periodo(self, obj):
      if obj.periodo:
        return obj.periodo.id
      return None
    
    descripcion_desincorporacion= serializers.SerializerMethodField('loaddescripcion_desincorporacion')
    def loaddescripcion_desincorporacion(self, obj):
      if obj.tipodesincorporacion:
        return obj.tipodesincorporacion.descripcion
      return None

class InmueblePropietariosSerializer(serializers.ModelSerializer):
    inmueble = InmuebleSerializer()
    propietario = PropietarioSerializer()
    class Meta:
        model = InmueblePropietarios
        fields = '__all__'
    fecha_de_compra = serializers.SerializerMethodField('get_fecha')
    def get_fecha(self, obj):
      if obj.fecha_compra is not None:
          formatted_date = obj.fecha_compra.strftime("%d/%m/%Y")
          return f"{formatted_date}"
      return "" 

class InmueblePropiedadSerializer(serializers.ModelSerializer):
    class Meta:
        model = InmueblePropiedad
        fields = '__all__'

    descripcion_tipodocumento= serializers.SerializerMethodField('loaddescripcion_tipodocumento')
    def loaddescripcion_tipodocumento(self, obj):
      if obj.tipo_documento:
        return obj.tipo_documento.descripcion
      return None
    

class InmuebleTerrenoSerializer(serializers.ModelSerializer):
    class Meta:
        model = InmuebleTerreno
        fields = '__all__'

class InmuebleTerrenoTopografiaSerializer(serializers.ModelSerializer):
    inmueble_terreno=InmuebleTerrenoSerializer()
    topografia=TopografiaSerializer()
    class Meta:
        model = InmuebleTerrenoTopografia
        fields = '__all__'

class InmuebleTerrenoAccesoSerializer(serializers.ModelSerializer):
    inmueble_terreno=InmuebleTerrenoSerializer()
    acceso=AccesoSerializer()
    class Meta:
        model = InmuebleTerrenoAcceso
        fields = '__all__'

class InmuebleTerrenoUsoSerializer(serializers.ModelSerializer):
    inmueble_terreno=InmuebleTerrenoSerializer()
    uso=UsoSerializer()
    class Meta:
        model = InmuebleTerrenoUso
        fields = '__all__'


class InmuebleTerrenoServicioSerializer(serializers.ModelSerializer):
    inmueble_terreno=InmuebleTerrenoSerializer()
    servicios=ServiciosSerializer()
    class Meta:
        model = InmuebleTerrenoServicio
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
    inmueble_construccion=InmuebleConstruccionSerializer()
    soporte=SoporteSerializer()
    class Meta:
        model = InmuebleConstruccionSoporte
        fields = '__all__'

class InmuebleConstruccionTechoSerializer(serializers.ModelSerializer):
    inmueble_construccion=InmuebleConstruccionSerializer()
    techo=TechoSerializer()
    class Meta:
        model = InmuebleConstruccionTecho
        fields = '__all__'

class InmuebleConstruccionCubiertaSerializer(serializers.ModelSerializer):
    inmueble_construccion=InmuebleConstruccionSerializer()
    cubierta=CubiertaSerializer()
    class Meta:
        model = InmuebleConstruccionCubierta
        fields = '__all__'

class InmuebleValoracionTerrenoSerializer(serializers.ModelSerializer):
    class Meta:
        model = InmuebleValoracionTerreno
        fields = '__all__'
    zona_codigo= serializers.SerializerMethodField('loadzona_codigo')
    def loadzona_codigo(self, obj):
        if obj.tipologia:
          return obj.tipologia.zona.codigo
        return None
    uso_codigo= serializers.SerializerMethodField('loaduso_codigo')
    def loaduso_codigo(self, obj):
        if obj.tipologia:
          return obj.tipologia.codigo
        return None
    uso_descripcion= serializers.SerializerMethodField('loaduso_descripcion')
    def loaduso_descripcion(self, obj):
        if obj.tipologia:
          return obj.tipologia.descripcion
        return None
    uso_valor= serializers.SerializerMethodField('loaduso_valor')
    def loaduso_valor(self, obj):
        if obj.tipologia:
          return obj.tipologia.tarifa
        return None
    uso_total= serializers.SerializerMethodField('loaduso_total')
    def loaduso_total(self, obj):
        if obj.tipologia:
          return obj.tipologia.tarifa*obj.area
        return None
    tipo_descripcion= serializers.SerializerMethodField('loadtipo_descripcion')
    def loadtipo_descripcion(self, obj):
        if obj.tipo:
          return obj.tipo.descripcion
        return None
 

class InmuebleValoracionConstruccionSerializer(serializers.ModelSerializer):
    class Meta:
        model = InmuebleValoracionConstruccion
        fields = '__all__'  
    zona_codigo= serializers.SerializerMethodField('loadzona_codigo')
    def loadzona_codigo(self, obj):
        if obj.tipologia:
          return obj.tipologia.zona.codigo
        return None
    uso_codigo= serializers.SerializerMethodField('loaduso_codigo')
    def loaduso_codigo(self, obj):
      return obj.tipologia.codigo
    uso_descripcion= serializers.SerializerMethodField('loaduso_descripcion')
    def loaduso_descripcion(self, obj):
      return obj.tipologia.descripcion
    uso_valor= serializers.SerializerMethodField('loaduso_valor')
    def loaduso_valor(self, obj):
      return obj.tipologia.tarifa
    uso_total= serializers.SerializerMethodField('loaduso_total')
    def loaduso_total(self, obj):
      return obj.tipologia.tarifa*obj.area
    tipo_descripcion= serializers.SerializerMethodField('loadtipo_descripcion')
    def loadtipo_descripcion(self, obj):
      return obj.tipo.descripcion
    fecha_construccion = serializers.SerializerMethodField('get_fecha_construccion')
    def get_fecha_construccion(self, obj):
      if obj.fecha_construccion is not None:
          formatted_date = obj.fecha_construccion.strftime("%d/%m/%Y")
          formatted_time = obj.fecha_construccion.strftime("%I:%M %p")
          return f"{formatted_date} {formatted_time}"
      return "" 



class InmuebleValoracionTerreno2024Serializer(serializers.ModelSerializer):
    class Meta:
        model = InmuebleValoracionTerreno2024
        fields = '__all__'
    categorizacion_codigo= serializers.SerializerMethodField('loadcategorizacion_codigo')
    def loadcategorizacion_codigo(self, obj):
        if obj.tipologia_categorizacion:
          return obj.tipologia_categorizacion.categorizacion.codigo
        return None
    uso_codigo= serializers.SerializerMethodField('loaduso_codigo')
    def loaduso_codigo(self, obj):
        if obj.tipologia_categorizacion:
          return obj.tipologia_categorizacion.codigo
        return None
    uso_descripcion= serializers.SerializerMethodField('loaduso_descripcion')
    def loaduso_descripcion(self, obj):
        if obj.tipologia_categorizacion:
          return obj.tipologia_categorizacion.descripcion
        return None
    uso_valor= serializers.SerializerMethodField('loaduso_valor')
    def loaduso_valor(self, obj):
        if obj.tipologia_categorizacion:
          return obj.tipologia_categorizacion.tarifa
        return None
    uso_total= serializers.SerializerMethodField('loaduso_total')
    def loaduso_total(self, obj):
        if obj.tipologia_categorizacion:
          return obj.tipologia_categorizacion.tarifa*obj.area
        return None
    tipo_descripcion= serializers.SerializerMethodField('loadtipo_descripcion')
    def loadtipo_descripcion(self, obj):
        if obj.tipo:
          return obj.tipo.descripcion
        return None
 

class InmuebleValoracionConstruccion2024Serializer(serializers.ModelSerializer):
    class Meta:
        model = InmuebleValoracionConstruccion2024
        fields = '__all__'  
    categorizacion_codigo= serializers.SerializerMethodField('loadcategorizacion_codigo')
    def loadcategorizacion_codigo(self, obj):
        if obj.tipologia_categorizacion:
          return obj.tipologia_categorizacion.categorizacion.codigo
        return None
    
    uso_codigo= serializers.SerializerMethodField('loaduso_codigo')
    def loaduso_codigo(self, obj):
        if obj.tipologia_categorizacion:
          return obj.tipologia_categorizacion.codigo
        return None
    
    uso_descripcion= serializers.SerializerMethodField('loaduso_descripcion')
    def loaduso_descripcion(self, obj):
        if obj.tipologia_categorizacion:
          return obj.tipologia_categorizacion.descripcion
        return None
        
    uso_valor= serializers.SerializerMethodField('loaduso_valor')
    def loaduso_valor(self, obj):
        if obj.tipologia_categorizacion:
          return obj.tipologia_categorizacion.tarifa
        return None
      
    uso_total= serializers.SerializerMethodField('loaduso_total')
    def loaduso_total(self, obj):
        if obj.tipologia_categorizacion:
          return obj.tipologia_categorizacion.tarifa*obj.area
        return None      

    tipo_descripcion= serializers.SerializerMethodField('loadtipo_descripcion')
    def loadtipo_descripcion(self, obj):
        if obj.tipo.descripcion:
          return obj.tipo.descripcion
        return None      

    fecha_construccion = serializers.SerializerMethodField('get_fecha_construccion')
    def get_fecha_construccion(self, obj):
      if obj.fecha_construccion is not None:
          formatted_date = obj.fecha_construccion.strftime("%d/%m/%Y")
          formatted_time = obj.fecha_construccion.strftime("%I:%M %p")
          return f"{formatted_date} {formatted_time}"
      return "" 



    # Define cómo manejar la asignación de claves foráneas
   # def to_representation(self, instance):
   #     representation = super().to_representation(instance)
   #     representation['tipologia'] = instance.tipologia.id if instance.tipologia else None
   #     representation['tipo'] = instance.tipo.id if instance.tipo else None
   #     return representation

    # Define cómo manejar la creación/actualización de claves foráneas
    #def to_internal_value(self, data):
    #    tipologia_id = data.pop('tipologia', None)
    #    tipo_id = data.pop('tipo', None)
    #    
    #    validated_data = super().to_internal_value(data)
    #    
    #    if tipologia_id is not None:
    #        validated_data['tipologia_id'] = tipologia_id
    #    
    #    if tipo_id is not None:
    #        validated_data['tipo_id'] = tipo_id
    #    
    #    return validated_data



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

class TipoFlujoDetalleSerializer(serializers.ModelSerializer):
    #tasamulta = TasaMultaSerializer()
    class Meta:
        model = TipoFlujoDetalle
        fields = '__all__'

class EstadoCuentaSerializer(serializers.ModelSerializer):
    tipoflujo_descripcion= serializers.SerializerMethodField('loaddescripcion_flujo')
    def loaddescripcion_flujo(self, obj):
      if obj.tipoflujo:
        return obj.tipoflujo.descripcion
      return None
    
    tipoflujo_vencimiento= serializers.SerializerMethodField('loaddescripcion_vcto')
    def loaddescripcion_vcto(self, obj):
      if obj.tipoflujo:
        return obj.tipoflujo.vencimiento
      return None
   
    propietario_nombre= serializers.SerializerMethodField('loadnombre_propietario')
    def loadnombre_propietario(self, obj):
      if obj.propietario:
        return obj.propietario.nombre
      return None

    propietario_direccion= serializers.SerializerMethodField('loadnombre_propietariodireccion')
    def loadnombre_propietariodireccion(self, obj):
      if obj.propietario:
        return obj.propietario.direccion
      return None
    
    propietario_telefono_principal= serializers.SerializerMethodField('loadnombre_propietariotelefono_principal')
    def loadnombre_propietariotelefono_principal(self, obj):
      if obj.propietario:
        return obj.propietario.telefono_principal
      return None

    propietario_nacionalidad= serializers.SerializerMethodField('loadnombre_propietariotnacionalidad')
    def loadnombre_propietariotnacionalidad(self, obj):
      if obj.propietario:
        return obj.propietario.nacionalidad
      return None
       
    propietario_numero_documento= serializers.SerializerMethodField('loadnombre_propietarionumero_documento')
    def loadnombre_propietarionumero_documento(self, obj):
      if obj.propietario:
        return obj.propietario.numero_documento
      return None   

    inmueble_numero_expediente= serializers.SerializerMethodField('loadpexpediente')
    def loadpexpediente(self, obj):
      if obj.inmueble:
        return obj.inmueble.numero_expediente
      return None
    
    fechaformato = serializers.SerializerMethodField('get_fecha')
    def get_fecha(self, obj):
      if obj.fecha is not None:
          formatted_date = obj.fecha.strftime("%d/%m/%Y")
          formatted_time = obj.fecha.strftime("%I:%M %p")
          return f"{formatted_date} {formatted_time}"
      return "" 
       
    class Meta:
        model = EstadoCuenta
        fields = '__all__' 

class EstadoCuentaDetalleSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstadoCuentaDetalle
        fields = '__all__'       

class LiquidacionSerializer(serializers.ModelSerializer):

    estadocuenta_numero= serializers.SerializerMethodField('loadestadocuenta_numero')
    def loadestadocuenta_numero(self, obj):
      if obj.estadocuenta:
        return obj.estadocuenta.numero
      return None

    tipoflujo_descripcion= serializers.SerializerMethodField('loaddescripcion_flujo')
    def loaddescripcion_flujo(self, obj):
      if obj.tipoflujo:
        return obj.tipoflujo.descripcion
      return None
    
    tipoflujo_vencimiento= serializers.SerializerMethodField('loaddescripcion_vcto')
    def loaddescripcion_vcto(self, obj):
      if obj.tipoflujo:
        return obj.tipoflujo.vencimiento
      return None
  
    propietario_nombre= serializers.SerializerMethodField('loadnombre_propietario')
    def loadnombre_propietario(self, obj):
      if obj.propietario:
        return obj.propietario.nombre
      return None

    propietario_direccion= serializers.SerializerMethodField('loadnombre_propietariodireccion')
    def loadnombre_propietariodireccion(self, obj):
      if obj.propietario:
        return obj.propietario.direccion
      return None
    
    propietario_telefono_principal= serializers.SerializerMethodField('loadnombre_propietariotelefono_principal')
    def loadnombre_propietariotelefono_principal(self, obj):
      if obj.propietario:
        return obj.propietario.telefono_principal
      return None

    propietario_nacionalidad= serializers.SerializerMethodField('loadnombre_propietariotnacionalidad')
    def loadnombre_propietariotnacionalidad(self, obj):
      if obj.propietario:
        return obj.propietario.nacionalidad
      return None
    
    propietario_numero_documento= serializers.SerializerMethodField('loadnombre_propietarionumero_documento')
    def loadnombre_propietarionumero_documento(self, obj):
      if obj.propietario:
        return obj.propietario.numero_documento
      return None 

    inmueble_numero_expediente= serializers.SerializerMethodField('loadpexpediente')
    def loadpexpediente(self, obj):
      if obj.inmueble:
        return obj.inmueble.numero_expediente
      return None

    inmueble_direccion= serializers.SerializerMethodField('loadpexpedientedireccion')
    def loadpexpedientedireccion(self, obj):
      if obj.inmueble:
        return obj.inmueble.direccion
      return None
        
    fechaformato = serializers.SerializerMethodField('get_fecha')
    def get_fecha(self, obj):
      if obj.fecha is not None:
          formatted_date = obj.fecha.strftime("%d/%m/%Y")
          formatted_time = obj.fecha.strftime("%I:%M %p")
          return f"{formatted_date} {formatted_time}"
      return "" 

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

class BancoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banco
        fields = '__all__'  

class BancoCuentaSerializer(serializers.ModelSerializer):
    class Meta:
        model = BancoCuenta
        fields = '__all__'  
    banco_nombre= serializers.SerializerMethodField('loadbanco_nombre')
    def loadbanco_nombre(self, obj):
      return obj.banco.descripcion+'-'+obj.numero

class PagoEstadoCuentaSerializer(serializers.ModelSerializer):
    #liquidacion = LiquidacionSerializer()

    liquidacion_numero= serializers.SerializerMethodField('load_numero')
    def load_numero(self, obj):
      if obj.liquidacion:
        return obj.liquidacion.numero
      return None

    liquidacion_estadocuenta_numero= serializers.SerializerMethodField('loadestadocuenta_numero')
    def loadestadocuenta_numero(self, obj):
      if obj.liquidacion:
        return obj.liquidacion.estadocuenta.numero
      return None

    liquidacion_tipoflujo_descripcion= serializers.SerializerMethodField('loaddescripcion_flujo')
    def loaddescripcion_flujo(self, obj):
      if obj.liquidacion:
        return obj.liquidacion.tipoflujo.descripcion
      return None
   
    liquidacion_propietario_nombre= serializers.SerializerMethodField('loadnombre_propietario')
    def loadnombre_propietario(self, obj):
      if obj.liquidacion:
        return obj.liquidacion.propietario.nombre
      return None
       
    liquidacion_inmueble_numero_expediente= serializers.SerializerMethodField('loadpexpediente')
    def loadpexpediente(self, obj):
      if obj.liquidacion:
        if obj.liquidacion.inmueble:
          return obj.liquidacion.inmueble.numero_expediente
      return None

    fecha_recibo= serializers.SerializerMethodField('loadfecha_recibo')
    def loadfecha_recibo(self, obj):
      if obj.fecha:
        return obj.fecha
      return None


    fecha = serializers.SerializerMethodField('get_fecha')
    def get_fecha(self, obj):
      if obj.fecha is not None:
          formatted_date = obj.fecha.strftime("%d/%m/%Y")
          formatted_time = obj.fecha.strftime("%I:%M %p")
          return f"{formatted_date} {formatted_time}"
      return "" 
    
    class Meta:
        model = PagoEstadoCuenta
        fields = '__all__' 

class PagoEstadoCuentaDetalleSerializer(serializers.ModelSerializer):
    class Meta:
        model = PagoEstadoCuentaDetalle
        fields = '__all__' 

    banco_nombre= serializers.SerializerMethodField('loadbanco_nombre')
    def loadbanco_nombre(self, obj):
      if obj.bancocuenta:
        return obj.bancocuenta.banco.descripcion
      return None

    banco_codigo= serializers.SerializerMethodField('loadbanco_codigo')
    def loadbanco_codigo(self, obj):
      if obj.bancocuenta:
        return obj.bancocuenta.banco.codigo
      return None
    
    banco_cuenta= serializers.SerializerMethodField('loadbanco_cuenta')
    def loadbanco_cuenta(self, obj):
      if obj.bancocuenta:
        return obj.bancocuenta.numero
      return None

    tipopago_nombre= serializers.SerializerMethodField('loadtipopago_nombre')
    def loadtipopago_nombre(self, obj):
      if obj.tipopago:
        return obj.tipopago.descripcion
      return None

    operacion_tipo= serializers.SerializerMethodField('loadoperacion_tipo')
    def loadoperacion_tipo(self, obj):
      if obj.tipopago:
        return obj.tipopago.operacion
      return None
    
    numero_recibo= serializers.SerializerMethodField('loadnumero_recibo')
    def loadnumero_recibo(self, obj):
      return obj.pagoestadocuenta.numero

    numero_caja= serializers.SerializerMethodField('loadnumero_caja')
    def loadnumero_caja(self, obj):
      if obj.pagoestadocuenta.caja:
        return obj.pagoestadocuenta.caja
      return None

    fecha_recibo= serializers.SerializerMethodField('loadfecha_recibo')
    def loadfecha_recibo(self, obj):
      if obj.pagoestadocuenta.fecha:
        return obj.pagoestadocuenta.fecha
      return None
    
    fecha = serializers.SerializerMethodField('get_fecha')
    def get_fecha(self, obj):
      if obj.pagoestadocuenta.fecha is not None:
          formatted_date = obj.pagoestadocuenta.fecha.strftime("%d/%m/%Y")
          formatted_time = obj.pagoestadocuenta.fecha.strftime("%I:%M %p")
          return f"{formatted_date} {formatted_time}"
      return "" 
    
   # fecha = serializers.SerializerMethodField('get_fechapago')
   # def get_fechapago(self, obj):
   #   if obj.fechapago is not None:
   #       formatted_date = obj.fechapago.strftime("%Y-%m-%d") 
   #       #formatted_date = obj.fechapago.strftime("%d/%m/%Y")
   #       formatted_time = obj.fechapago.strftime("%I:%M %p")
   #       #return f"{formatted_date} {formatted_time}"
   #       return f"{formatted_date}"
   #   return ""  


class CorrelativoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Correlativo
        fields = '__all__'       

class FlujoSerializer(serializers.ModelSerializer):
    #pagoestadocuenta = PagoEstadoCuentaSerializer()
    #inmueble = InmuebleSerializer()
    class Meta:
        model = Flujo
        fields = '__all__' 
    
    descripcion_flujo= serializers.SerializerMethodField('loaddescripcion_flujo')
    def loaddescripcion_flujo(self, obj):
      if obj.pagoestadocuenta:
        return obj.pagoestadocuenta.liquidacion.tipoflujo.descripcion
      return None

    nombre_propietario= serializers.SerializerMethodField('loadnombre_propietario')
    def loadnombre_propietario(self, obj):
      if obj.pagoestadocuenta:
        return obj.pagoestadocuenta.liquidacion.propietario.nombre
      return None
       
    estado_display = serializers.SerializerMethodField('get_estado_display')
    def get_estado_display(self, obj):
        return dict(Flujo.ESTADO)[obj.estado]
    
    expediente= serializers.SerializerMethodField('loadpexpediente')
    def loadpexpediente(self, obj):
      return obj.inmueble.numero_expediente
    
    fecha = serializers.SerializerMethodField('get_fecha')
    def get_fecha(self, obj):
      if obj.fecha is not None:
          formatted_date = obj.fecha.strftime("%d/%m/%Y")
          formatted_time = obj.fecha.strftime("%I:%M %p")
          return f"{formatted_date} {formatted_time}"
      return ""     

    
class FlujoDetalleSerializer(serializers.ModelSerializer):
    class Meta:
        model = FlujoDetalle
        fields = '__all__' 

    flujo_fecha = serializers.SerializerMethodField('get_flujo_fecha')   
    def get_flujo_fecha(self, obj):
      if obj.flujo.fecha is not None:
          formatted_date = obj.flujo.fecha.strftime("%d/%m/%Y")
          formatted_time = obj.flujo.fecha.strftime("%I:%M %p")
          return f"{formatted_date} {formatted_time}"
      return "" 
        
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
      if obj.envia_usuario:
          return obj.envia_usuario.username
      return None
    
    envia_fecha = serializers.SerializerMethodField('get_envia_fecha')
    def get_envia_fecha(self, obj):
      if obj.envia_fecha is not None:
          formatted_date = obj.envia_fecha.strftime("%d/%m/%Y")
          formatted_time = obj.envia_fecha.strftime("%I:%M %p")
          return f"{formatted_date} {formatted_time}"
      return ""

    recibe_usuario_nombre= serializers.SerializerMethodField('loadrecibe_usuario_nombre')
    def loadrecibe_usuario_nombre(self, obj):
      if obj.recibe_usuario:
          return obj.recibe_usuario.username
      return None
    
    recibe_fecha = serializers.SerializerMethodField('get_recibe_fecha')   
    def get_recibe_fecha(self, obj):
      if obj.recibe_fecha is not None:
          formatted_date = obj.recibe_fecha.strftime("%d/%m/%Y")
          formatted_time = obj.recibe_fecha.strftime("%I:%M %p")
          return f"{formatted_date} {formatted_time}"
      return ""  

    estado_display = serializers.SerializerMethodField('get_estado_display')
    def get_estado_display(self, obj):
        return dict(FlujoDetalle.ESTADO)[obj.estado]

    tarea_display = serializers.SerializerMethodField('get_tarea_display')
    def get_tarea_display(self, obj):
        return dict(FlujoDetalle.TAREA)[obj.tarea]
    
    procesa_fecha = serializers.SerializerMethodField('get_procesa_fecha')
    def get_procesa_fecha(self, obj):
      if obj.procesa_fecha is not None:
          formatted_date = obj.procesa_fecha.strftime("%d/%m/%Y")
          formatted_time = obj.procesa_fecha.strftime("%I:%M %p")
          return f"{formatted_date} {formatted_time}"
      return ""  

    procesa_usuario= serializers.SerializerMethodField('loadprocesa_usuario')
    def loadprocesa_usuario(self, obj):
      if obj.procesa_usuario:
          return obj.procesa_usuario.username
      return None

    fin_fecha = serializers.SerializerMethodField('get_fin_fecha')
    def get_fin_fecha(self, obj):
      if obj.fin_fecha is not None:
          formatted_date = obj.fin_fecha.strftime("%d/%m/%Y")
          formatted_time = obj.fin_fecha.strftime("%I:%M %p")
          return f"{formatted_date} {formatted_time}"
      return "" 

    fin_usuario= serializers.SerializerMethodField('loadfin_usuario')
    def loadfin_usuario(self, obj):
      if obj.fin_usuario:
          return obj.fin_usuario.username
      return None

    inicio_proceso_fecha = serializers.SerializerMethodField('get_inicio_proceso_fecha')
    def get_inicio_proceso_fecha(self, obj):
      if obj.inicio_proceso_fecha is not None:
          formatted_date = obj.inicio_proceso_fecha.strftime("%d/%m/%Y")
          formatted_time = obj.inicio_proceso_fecha.strftime("%I:%M %p")
          return f"{formatted_date} {formatted_time}"
      return "" 

    inicio_proceso_usuario= serializers.SerializerMethodField('loadinicio_proceso_usuario')
    def loadinicio_proceso_usuario(self, obj):
      if obj.inicio_proceso_usuario:
          return obj.inicio_proceso_usuario.username
      return None
    


class IC_ImpuestoCargosSerializer(serializers.ModelSerializer):
    class Meta:
        model = IC_ImpuestoCargos
        fields = '__all__' 

class IC_ImpuestoSerializer(serializers.ModelSerializer):
    class Meta:
        model = IC_Impuesto
        fields = '__all__' 

class IC_ImpuestoDetalleSerializer(serializers.ModelSerializer):
    class Meta:
        model = IC_ImpuestoDetalle
        fields = '__all__' 

class IC_ImpuestoCorreccionesSerializer(serializers.ModelSerializer):
    class Meta:
        model = IC_ImpuestoCorrecciones
        fields = '__all__' 

class IC_ImpuestoCorreccionesDetalleSerializer(serializers.ModelSerializer):
    class Meta:
        model = IC_ImpuestoCorreccionesDetalle
        fields = '__all__' 


class IC_ImpuestoPeriodoSerializer(serializers.ModelSerializer):
    class Meta:
        model = IC_ImpuestoPeriodo
        fields = '__all__' 

class IC_ImpuestoDescuentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = IC_ImpuestoDescuento
        fields = '__all__' 

class IC_ImpuestoExoneracionSerializer(serializers.ModelSerializer):
    class Meta:
        model = IC_ImpuestoExoneracion
        fields = '__all__' 
    zona_codigo= serializers.SerializerMethodField('loadzona_codigo')
    def loadzona_codigo(self, obj):
        if obj.tipologia:
          return obj.tipologia.zona.codigo
        return None
    uso_zona_codigo= serializers.SerializerMethodField('loaduso_codigo')
    def loaduso_codigo(self, obj):
        if obj.tipologia:
          return obj.tipologia.codigo
        return None
    uso_zona_descripcion= serializers.SerializerMethodField('loaduso_descripcion')
    def loaduso_descripcion(self, obj):
        if obj.tipologia:
          return obj.tipologia.descripcion
        return None
    categorizacion_codigo= serializers.SerializerMethodField('loadcategorizacion_codigoC')
    def loadcategorizacion_codigoC(self, obj):
        if obj.tipologia_categorizacion:
          return obj.tipologia_categorizacion.categorizacion.codigo
        return None
    
    uso_categorizacion_codigo= serializers.SerializerMethodField('loaduso_codigoC')
    def loaduso_codigoC(self, obj):
        if obj.tipologia_categorizacion:
          return obj.tipologia_categorizacion.codigo
        return None
    
    uso_categorizacion_descripcion= serializers.SerializerMethodField('loaduso_descripcionC')
    def loaduso_descripcionC(self, obj):
        if obj.tipologia_categorizacion:
          return obj.tipologia_categorizacion.descripcion
        return None    

class IC_ImpuestoDetalleDescuentosSerializer(serializers.ModelSerializer):
    class Meta:
        model = IC_ImpuestoDetalleDescuentos
        fields = '__all__' 

class IC_ImpuestoDetalleMoraSerializer(serializers.ModelSerializer):
    class Meta:
        model = IC_ImpuestoDetalleMora
        fields = '__all__' 

class AE_ActividadEconomicaSerializer(serializers.ModelSerializer):
    class Meta:
        model = AE_ActividadEconomica
        fields = '__all__' 

class AE_ActividadEconomicaDetalleSerializer(serializers.ModelSerializer):
    class Meta:
        model = AE_ActividadEconomicaDetalle
        fields = '__all__'
    codigo_general= serializers.SerializerMethodField('loadcodigo_general')
    def loadcodigo_general(self, obj):
      return obj.AE_actividadeconomica.codigo
    descripcion_general= serializers.SerializerMethodField('loaddescripcion_general')
    def loaddescripcion_general(self, obj):
      return obj.AE_actividadeconomica.descripcion


class AE_PatenteSerializer(serializers.ModelSerializer):
    class Meta:
        model = AE_Patente
        fields = '__all__'
    propietario_nombre= serializers.SerializerMethodField('loadpropietario_nombre')
    def loadpropietario_nombre(self, obj):
      return obj.propietario.nombre
    
    propietario_numero= serializers.SerializerMethodField('loadpropietario_numero')
    def loadpropietario_numero(self, obj):
      return obj.propietario.numero_documento

class AE_Patente_ActividadEconomicaSerializer(serializers.ModelSerializer):
    class Meta:
        model = AE_Patente_ActividadEconomica
        fields = '__all__'
    codigo_general= serializers.SerializerMethodField('loadcodigo_general')
    def loadcodigo_general(self, obj):
      return obj.AE_actividadeconomica.AE_actividadeconomica.codigo
    descripcion_general= serializers.SerializerMethodField('loaddescripcion_general')
    def loaddescripcion_general(self, obj):
      return obj.AE_actividadeconomica.AE_actividadeconomica.descripcion
    codigo_especifico= serializers.SerializerMethodField('loadcodigo_especifico')
    def loadcodigo_especifico(self, obj):
      return obj.AE_actividadeconomica.codigo
    descripcion_especifico= serializers.SerializerMethodField('loaddescripcion_especifico')
    def loaddescripcion_especifico(self, obj):
      return obj.AE_actividadeconomica.descripcion

class TasaInteresSerializer(serializers.ModelSerializer):
    class Meta:
        model = TasaInteres
        fields = '__all__'

class NotaCreditoSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotaCredito
        fields = '__all__'
    propietario_nombre= serializers.SerializerMethodField('loadpropietario_nombre')
    def loadpropietario_nombre(self, obj):
      return obj.propietario.nombre
    
    propietario_numero_documento= serializers.SerializerMethodField('loadpropietario_numero')
    def loadpropietario_numero(self, obj):
      return obj.propietario.numero_documento
      

    fecha = serializers.SerializerMethodField('get_procesa_fecha')
    def get_procesa_fecha(self, obj):
      if obj.fecha is not None:
          formatted_date = obj.fecha.strftime("%d/%m/%Y")
          formatted_time = obj.fecha.strftime("%I:%M %p")
          return f"{formatted_date} {formatted_time}"
      return ""    
    numero_recibo= serializers.SerializerMethodField('loadnumero_recibo')
    def loadnumero_recibo(self, obj):
      return obj.pagoestadocuenta.numero
        

class ExcelDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExcelDocument
        fields = '__all__'

class ExcelDocumentLOGSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExcelDocumentLOG
        fields = '__all__'

class CorridasBancariasSerializer(serializers.ModelSerializer):
    class Meta:
        model = CorridasBancarias
        fields = '__all__'  

    banco_nombre= serializers.SerializerMethodField('loadbanco_nombre')
    def loadbanco_nombre(self, obj):
      if obj.bancocuenta:
        return obj.bancocuenta.banco.descripcion
      return None

    banco_codigo= serializers.SerializerMethodField('loadbanco_codigo')
    def loadbanco_codigo(self, obj):
      if obj.bancocuenta:
        return obj.bancocuenta.banco.codigo
      return None
    
    banco_cuenta= serializers.SerializerMethodField('loadbanco_cuenta')
    def loadbanco_cuenta(self, obj):
      if obj.bancocuenta:
        return obj.bancocuenta.numero
      return None

    banco_cuenta_corta= serializers.SerializerMethodField('loadbanco_cuenta_corta')
    def loadbanco_cuenta_corta(self, obj):
      if obj.bancocuenta:
        cuentacorta = obj.bancocuenta.numero
        cuentacorta = cuentacorta.replace("-","")
        return cuentacorta[-4:]
      return None
    
    fecha_corrida = serializers.SerializerMethodField('get_procesa_fecha')
    def get_procesa_fecha(self, obj):
      if obj.fecha is not None:
          formatted_date = obj.fecha.strftime("%d/%m/%Y")
          return f"{formatted_date}"
      return "" 
    
class ComunidadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comunidad 
        fields = '__all__'

class InmuebleCategorizacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = InmuebleCategorizacion
        fields = '__all__'
        
#class Serializer(serializers.ModelSerializer):
#    class Meta:
#        model = 
#        fields = '__all__'