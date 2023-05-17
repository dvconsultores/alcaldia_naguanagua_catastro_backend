from rest_framework import fields, serializers
from .models import *

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
    descripcion_ambito= serializers.SerializerMethodField('loaddescripcion_ambito')
    def loaddescripcion_ambito(self, obj):
      return obj.sector.ambito.descripcion
    
    descripcion_sector= serializers.SerializerMethodField('loaddescripcion_sector')
    def loaddescripcion_sector(self, obj):
      return obj.sector.descripcion        

class ManzanaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manzana
        fields = '__all__'
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
    descripcion_ambito= serializers.SerializerMethodField('loaddescripcion_ambito')
    def loaddescripcion_ambito(self, obj):
      return obj.sector.ambito.descripcion
    
    descripcion_sector= serializers.SerializerMethodField('loaddescripcion_sector')
    def loaddescripcion_sector(self, obj):
      return obj.sector.descripcion
    
    codigo_manzana= serializers.SerializerMethodField('loadcodigo_manzana')
    def loadcodigo_manzana(self, obj):
      return obj.manzana.codigo


class SubParcelaSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubParcela
        fields = '__all__'
    descripcion_ambito= serializers.SerializerMethodField('loaddescripcion_ambito')
    def loaddescripcion_ambito(self, obj):
      return obj.sector.ambito.descripcion
    
    descripcion_sector= serializers.SerializerMethodField('loaddescripcion_sector')
    def loaddescripcion_sector(self, obj):
      return obj.sector.descripcion
    
    codigo_manzana= serializers.SerializerMethodField('loadcodigo_manzana')
    def loadcodigo_manzana(self, obj):
      return obj.manzana.codigo
            
    codigo_parcela= serializers.SerializerMethodField('loadcodigo_parcela')
    def loadcodigo_parcela(self, obj):
      return obj.parcela.codigo
    

class ConjuntoResidencialSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConjuntoResidencial
        fields = '__all__'
    descripcion_ambito= serializers.SerializerMethodField('loaddescripcion_ambito')
    def loaddescripcion_ambito(self, obj):
      return obj.sector.ambito.descripcion
    
    descripcion_sector= serializers.SerializerMethodField('loaddescripcion_sector')
    def loaddescripcion_sector(self, obj):
      return obj.sector.descripcion  

    nombre_urbanizacion= serializers.SerializerMethodField('loadnombre_urbanizacion')
    def loadnombre_urbanizacion(self, obj):
      return obj.urbanizacion.nombre             

class EdificioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Edificio
        fields = '__all__'
    descripcion_ambito= serializers.SerializerMethodField('loaddescripcion_ambito')
    def loaddescripcion_ambito(self, obj):
      return obj.sector.ambito.descripcion
    
    descripcion_sector= serializers.SerializerMethodField('loaddescripcion_sector')
    def loaddescripcion_sector(self, obj):
      return obj.sector.descripcion  

    nombre_urbanizacion= serializers.SerializerMethodField('loadnombre_urbanizacion')
    def loadnombre_urbanizacion(self, obj):
      return obj.urbanizacion.nombre 
    
    nombre_conjuntoresidencial= serializers.SerializerMethodField('loadnombre_conjuntoresidencial')
    def loadnombre_conjuntoresidencial(self, obj):
      return obj.conjuntoresidencial.nombre   
      
class TorreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Torre
        fields = '__all__'
    descripcion_ambito= serializers.SerializerMethodField('loaddescripcion_ambito')
    def loaddescripcion_ambito(self, obj):
      return obj.sector.ambito.descripcion
    
    descripcion_sector= serializers.SerializerMethodField('loaddescripcion_sector')
    def loaddescripcion_sector(self, obj):
      return obj.sector.descripcion  

    nombre_urbanizacion= serializers.SerializerMethodField('loadnombre_urbanizacion')
    def loadnombre_urbanizacion(self, obj):
      return obj.urbanizacion.nombre 
    
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

class ZonaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Zona
        fields = '__all__'

class InmuebleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inmueble
        fields = '__all__'


class InmueblePropiedadSerializer(serializers.ModelSerializer):
    class Meta:
        model = InmueblePropiedad
        fields = '__all__'


class InmueblePropietariosSerializer(serializers.ModelSerializer):
    class Meta:
        model = InmueblePropietarios
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



class TasaMultaSerializer(serializers.ModelSerializer):
    class Meta:
        model = TasaMulta
        fields = '__all__' 

class EstadoCuentaSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstadoCuenta
        fields = '__all__' 

class EstadoCuentaDetalleSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstadoCuentaDetalle
        fields = '__all__'         