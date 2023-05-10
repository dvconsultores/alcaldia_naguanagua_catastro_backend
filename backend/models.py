from django.db import models
from django.contrib.auth.models import *
from simple_history.models import HistoricalRecords
import datetime
from django.dispatch import receiver
from django.urls import reverse
from django_rest_passwordreset.signals import reset_password_token_created
from django.core.mail import send_mail 
from django.template.loader import render_to_string
from django.utils.html import strip_tags

class Ambito(models.Model):
    codigo = models.TextField(null=False,blank =False, unique=True, help_text="Codigo del ambito")
    descripcion = models.TextField(null=False,blank =False, unique=True, help_text="Descripcion del ambito")

class Sector(models.Model):
    CLASIFICACION = (
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D'),
        ('E', 'E'),
    )
    ambito=models.ForeignKey(Ambito,on_delete=models.PROTECT,help_text="ambito asociado")
    codigo = models.TextField(null=False,blank =False, unique=True, help_text="Codigo del Sector")
    descripcion = models.TextField(null=False,blank =False, unique=True, help_text="Descripcion del Sector")
    area = models.TextField(null=False,blank =False, unique=True, help_text="area del Sector")
    perimetro = models.TextField(null=False,blank =False, unique=True, help_text="Descripcion del Sector")
    clasificacion= models.CharField(max_length=1, choices=CLASIFICACION, default='A', help_text='clasificacion del Sector')

class Calle(models.Model):
    TIPO = (
        ('1', 'Colateral'),
        ('2', 'Via'),
        ('3', 'Doble Via')
    )
    codigo = models.TextField(null=False,blank =False, unique=True, help_text="Codigo de la calle")
    nombre = models.TextField(null=False,blank =False, unique=True, help_text="Nombre de la calle")
    tipo= models.CharField(max_length=1, choices=TIPO, default='1', help_text='tipo calle')

class Avenida(models.Model):
    TIPO = (
        ('1', 'Colateral'),
        ('2', 'Via'),
        ('3', 'Doble Via')
    )
    codigo = models.TextField(null=False,blank =False, unique=True, help_text="Codigo de la avenida")
    nombre = models.TextField(null=False,blank =False, unique=True, help_text="Nombre de la avenida")
    tipo= models.CharField(max_length=1, choices=TIPO, default='1', help_text='tipo de avenida')


class Urbanizacion(models.Model):
    TIPO = (
        ('P', 'Publica'),
        ('R', 'Privada'),
    )
    sector=models.ForeignKey(Sector,on_delete=models.PROTECT,help_text="Sector asociado")
    nombre = models.TextField(null=False,blank =False, unique=True, help_text="Nombre de la urbanizacion")
    tipo= models.CharField(max_length=1, choices=TIPO, default='P', help_text='tipo de la urbanizacion')

class Manzana(models.Model):
    sector=models.ForeignKey(Sector,on_delete=models.PROTECT,help_text="Sector asociado")
    codigo = models.TextField(null=False,blank =False, unique=True, help_text="Codigo de la Manzana")
    area = models.TextField(null=False,blank =False, unique=True, help_text="Area de la manzana")
    perimetro = models.TextField(null=False,blank =False, unique=True, help_text="Perimetro de la manzana")
    via_norte=models.ForeignKey(Calle,null=True,on_delete=models.PROTECT,help_text="Via cercana norte",related_name='manzana_via_norte')
    via_sur=models.ForeignKey(Calle,null=True,on_delete=models.PROTECT,help_text="Via cercana sur",related_name='manzana_via_sur')
    via_este=models.ForeignKey(Calle,null=True,on_delete=models.PROTECT,help_text="Via cercana este",related_name='manzana_via_este')
    via_oeste=models.ForeignKey(Calle,null=True,on_delete=models.PROTECT,help_text="Via cercana oeste",related_name='manzana_via_oeste')

class Parcela(models.Model):
    manzana=models.ForeignKey(Manzana,on_delete=models.PROTECT,help_text="Manzana asociado")
    codigo = models.TextField(null=False,blank =False, unique=True, help_text="Codigo de la Parcela")
    area = models.TextField(null=False,blank =False, unique=True, help_text="Area de la Parcela")
    perimetro = models.TextField(null=False,blank =False, unique=True, help_text="Perimetro de la Parcela")

class SubParcela(models.Model):
    parcela=models.ForeignKey(Parcela,on_delete=models.PROTECT,help_text="Parcela asociado")
    codigo = models.TextField(null=False,blank =False, unique=True, help_text="Codigo de la SubParcela")
    area = models.TextField(null=False,blank =False, unique=True, help_text="Area de la SubParcela")
    perimetro = models.TextField(null=False,blank =False, unique=True, help_text="Perimetro de la SubParcela")


class ConjuntoResidencial(models.Model):
    urbanizacion = models.ForeignKey(Urbanizacion,on_delete=models.PROTECT,help_text="Urbanizacion asociada")
    nombre = models.TextField(null=False,blank =False, unique=True, help_text="nombre del conjunto residencial")

class Edificio(models.Model):
    urbanizacion = models.ForeignKey(Urbanizacion,on_delete=models.PROTECT,help_text="Urbanizacion asociada")
    conjunto_residencial = models.ForeignKey(ConjuntoResidencial,null=True,on_delete=models.PROTECT,help_text="conjunto residencial asociado")
    nombre = models.TextField(null=False,blank =False, unique=True, help_text="nombre del conjunto residencial")

class Torre(models.Model):
    urbanizacion = models.ForeignKey(Urbanizacion,on_delete=models.PROTECT,help_text="Urbanizacion asociada")
    conjunto_residencial = models.ForeignKey(ConjuntoResidencial,null=True,on_delete=models.PROTECT,help_text="conjunto residencial asociado")
    nombre = models.TextField(null=False,blank =False, unique=True, help_text="nombre del conjunto residencial")

class Propietario(models.Model):
    tipo_documento = models.TextField(null=False,blank =False, unique=True, help_text="Tipo de documento")
    nacionalidad = models.TextField(null=False,blank =False, unique=True, help_text="nacionalidad del propietario")
    numero_documento = models.TextField(null=False,blank =False, unique=True, help_text="Numero del documento de identificacion")
    nombre = models.TextField(null=False,blank =False, unique=True, help_text="Nombre del propietario")
    apellido = models.TextField(null=False,blank =False, unique=True, help_text="Apellido del propietario")
    telefono_principal = models.TextField(null=False,blank =False, unique=True, help_text="telefono celular del propietario")
    email_principal = models.TextField(null=False,blank =False, unique=True, help_text="email principal del propietario")
    telefono_secundario = models.TextField(null=False,blank =False, unique=True, help_text="telefonos del propietario")
    email_secundario = models.TextField(null=False,blank =False, unique=True, help_text="email secundario del propietario")


class TipoInmueble(models.Model):
    codigo = models.TextField(null=False,blank =False, unique=True, help_text="Codigo del tipo de inmueble")
    descripcion = models.TextField(null=False,blank =False, unique=True, help_text="descripcion del tipo de inmueble")

class EstatusInmueble(models.Model):
    codigo = models.TextField(null=False,blank =False, unique=True, help_text="Codigo del estatus de inmueble")
    descripcion = models.TextField(null=False,blank =False, unique=True, help_text="descripcion del estatus de inmueble")

class NivelInmueble(models.Model):
    codigo = models.TextField(null=False,blank =False, unique=True, help_text="Codigo del nivel de inmueble")
    descripcion = models.TextField(null=False,blank =False, unique=True, help_text="descripcion del nivel de inmueble")

class UnidadInmueble(models.Model):
    codigo = models.TextField(null=False,blank =False, unique=True, help_text="Codigo de la unidad del inmueble")
    descripcion = models.TextField(null=False,blank =False, unique=True, help_text="descripcion de la unidad del inmueble")

class TipoDocumento(models.Model):
    codigo = models.TextField(null=False,blank =False, unique=True, help_text="Codigo del tipo de documento del inmueble")
    descripcion = models.TextField(null=False,blank =False, unique=True, help_text="descripcion del tipo de documento del inmueble")

class TipoEspecial(models.Model):
    codigo = models.TextField(null=False,blank =False, unique=True, help_text="Codigo del tipo especial del inmueble")
    descripcion = models.TextField(null=False,blank =False, unique=True, help_text="descripcion del tipo especial del inmueble")

class TipoTenencia(models.Model):
    codigo = models.TextField(null=False,blank =False, unique=True, help_text="Codigo del tipo tenecia del inmueble")
    descripcion = models.TextField(null=False,blank =False, unique=True, help_text="descripcion del tenecia especial del inmueble")

class Topografia(models.Model):
    codigo = models.TextField(null=False,blank =False, unique=True, help_text="Codigo de topografia")
    descripcion = models.TextField(null=False,blank =False, unique=True, help_text="descripcion de topografia")

class Acceso(models.Model):
    codigo = models.TextField(null=False,blank =False, unique=True, help_text="Codigo de Acceso")
    descripcion = models.TextField(null=False,blank =False, unique=True, help_text="descripcion de Acceso")

class Forma(models.Model):
    codigo = models.TextField(null=False,blank =False, unique=True, help_text="Codigo de Forma")
    descripcion = models.TextField(null=False,blank =False, unique=True, help_text="descripcion de Forma")

class Ubicacion(models.Model):
    codigo = models.TextField(null=False,blank =False, unique=True, help_text="Codigo de Ubicacion")
    descripcion = models.TextField(null=False,blank =False, unique=True, help_text="descripcion de Ubicacion")

class Uso(models.Model):
    codigo = models.TextField(null=False,blank =False, unique=True, help_text="Codigo de Uso")
    descripcion = models.TextField(null=False,blank =False, unique=True, help_text="descripcion de Uso")

class Regimen(models.Model):
    codigo = models.TextField(null=False,blank =False, unique=True, help_text="Codigo de Regimen")
    descripcion = models.TextField(null=False,blank =False, unique=True, help_text="descripcion de Regimen")

class Servicios(models.Model):
    codigo = models.TextField(null=False,blank =False, unique=True, help_text="Codigo de Servicio")
    descripcion = models.TextField(null=False,blank =False, unique=True, help_text="descripcion de Servicio")

class Tipologia(models.Model):
    codigo = models.TextField(null=False,blank =False, unique=True, help_text="Codigo de tipologia")
    descripcion = models.TextField(null=False,blank =False, unique=True, help_text="descripcion de tipologia")

class FinesFiscales(models.Model):
    codigo = models.TextField(null=False,blank =False, unique=True, help_text="Codigo de fines fiscales")
    descripcion = models.TextField(null=False,blank =False, unique=True, help_text="descripcion de fines fiscales")

class TipoDesincorporacion(models.Model):
    codigo = models.TextField(null=False,blank =False, unique=True, help_text="Codigo de tipo desincorporacion")
    descripcion = models.TextField(null=False,blank =False, unique=True, help_text="descripcion del tipo de desincorporacion")

class TipoTransaccion(models.Model):
    codigo = models.TextField(null=False,blank =False, unique=True, help_text="Codigo de tipo transaccion")
    descripcion = models.TextField(null=False,blank =False, unique=True, help_text="descripcion del tipo de transaccion")

class Inmueble(models.Model):
    numero_expediente = models.TextField(null=False,blank =False, unique=True, help_text="Numero de expediente")
    fecha_inscripcion = models.DateTimeField(default=datetime.now, blank=True, help_text="fecha de inscripcion")
    tipo=models.ForeignKey(TipoInmueble,on_delete=models.PROTECT,help_text="Sector asociado")
    status=models.ForeignKey(EstatusInmueble,on_delete=models.PROTECT,help_text="Sector asociado")
    ambito=models.ForeignKey(Ambito,on_delete=models.PROTECT,help_text="Sector asociado")
    sector=models.ForeignKey(Sector,on_delete=models.PROTECT,help_text="Sector asociado")
    manzana=models.ForeignKey(Manzana,on_delete=models.PROTECT,help_text="Sector asociado")
    parcela=models.ForeignKey(Parcela,on_delete=models.PROTECT,help_text="Sector asociado")
    subparcela=models.ForeignKey(SubParcela,on_delete=models.PROTECT,help_text="Sector asociado")
    nivel=models.ForeignKey(NivelInmueble,on_delete=models.PROTECT,help_text="Sector asociado")
    unidad=models.ForeignKey(UnidadInmueble,on_delete=models.PROTECT,help_text="Sector asociado")
    urbanizacion=models.ForeignKey(Urbanizacion,on_delete=models.PROTECT,help_text="urbanizacion")
    calle=models.ForeignKey(Calle,on_delete=models.PROTECT,help_text="Sector asociado")
    conjunto_residencial=models.ForeignKey(ConjuntoResidencial,on_delete=models.PROTECT,help_text="Sector asociado")
    edificio=models.ForeignKey(Edificio,on_delete=models.PROTECT,help_text="Sector asociado")
    avenida=models.ForeignKey(Avenida,on_delete=models.PROTECT,help_text="Sector asociado")
    torre=models.ForeignKey(Torre,on_delete=models.PROTECT,help_text="Sector asociado")
    numero_civico = models.TextField(null=False,blank =False, unique=True, help_text="Numero de expediente")
    numero_casa = models.TextField(null=False,blank =False, unique=True, help_text="Numero de expediente")
    numero_piso = models.TextField(null=False,blank =False, unique=True, help_text="Numero de expediente")
    telefono = models.TextField(null=False,blank =False, unique=True, help_text="Numero de expediente")
    zona = models.TextField(null=False,blank =False, unique=True, help_text="Numero de expediente")
    direccion = models.TextField(null=False,blank =False, unique=True, help_text="Numero de expediente")
    referencia = models.TextField(null=False,blank =False, unique=True, help_text="Numero de expediente")
    observaciones = models.TextField(null=False,blank =False, unique=True, help_text="Numero de expediente")
	






