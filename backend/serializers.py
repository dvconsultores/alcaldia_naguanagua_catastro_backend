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

class ManzanaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manzana
        fields = '__all__'

class ParcelaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parcela
        fields = '__all__'

class SubParcelaSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubParcela
        fields = '__all__'

class ConjuntoResidencialSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConjuntoResidencial
        fields = '__all__'

class EdificioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Edificio
        fields = '__all__'

class TorreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Torre
        fields = '__all__'

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

class InmuebleConstruccionSerializer(serializers.ModelSerializer):
    class Meta:
        model = InmuebleConstruccion
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