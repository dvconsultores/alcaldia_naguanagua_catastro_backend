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
from decimal import Decimal


class Perfil(models.Model):
    TIPO = (('S', 'Super'), 
            ('A', 'Admin'),
            ('U', 'Usuario'), 
            ('C', 'Catastro'), 
            ('T', 'Tributario'))
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, help_text="usuario asociado")
    activo = models.BooleanField(default=True, help_text="esta el usuario activo?")
    tipo = models.CharField(max_length=1, null=True, choices=TIPO, default='U', help_text="Tipo de usuario")

    def __str__(self):
        return '%s - %s' % (self.usuario.username, self.tipo)

class Modulo(models.Model):
    nombre = models.CharField(max_length=255, null=False, blank=False, primary_key=True, help_text="Nombre exacto del archivo .VUE (a excepcion de los menues)")
    titulo = models.TextField(null=True,blank =True, help_text="Nombre que muestra en el Menu")
    menu = models.TextField(null=True,blank =True, help_text="Se coloca el valor del campo NOMBRE correpondiente al menu.")
    icono = models.TextField(null=True,blank =True, help_text="Icono a mostrar")
    es_menu = models.BooleanField(default=False, help_text="Es TRUE si pertenece a un titulo de menu. En valor que contenga su campo NOMBRE lo debe contener cada campo MENU de sus opciones")
    orden = models.PositiveIntegerField(null=True, blank=True,  help_text="Orden del menu y de la opcion dentro de menu")
    def __str__(self):
        return '%s - %s - %s - %s - %s'  % (self.es_menu,self.menu,self.orden, self.titulo,self.nombre)
        
    class Meta:
        ordering = ['menu','-es_menu','orden']


class Permiso(models.Model):
    modulo = models.ForeignKey(Modulo, null=False, blank=False,on_delete=models.CASCADE, help_text="Opcion de menu asociada")
    perfil = models.ForeignKey(Perfil, null=False, blank=False,on_delete=models.CASCADE, help_text="Usuario asociado")
    # Metodos
    leer = models.BooleanField(default=False, help_text="Tiene opcion de leer?")
    escribir = models.BooleanField(default=False, help_text="Tiene opcion de escribir?")
    borrar = models.BooleanField(default=False, help_text="Tiene opcion de borrar?")
    actualizar = models.BooleanField(default=False, help_text="Tiene opcion de actualizar?")

    def __str__(self):
        return '%s (Permiso: %s - Leer:%s Borrar:%s Actualizar:%s Escribir:%s)' % (self.perfil.usuario.username, self.modulo.nombre, self.leer, self.borrar, self.actualizar, self.escribir)




class Ambito(models.Model):
    codigo = models.TextField(null=False,blank =False, unique=True, help_text="Codigo del ambito")
    descripcion = models.TextField(null=False,blank =False, unique=False, help_text="Descripcion del ambito")

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
    descripcion = models.TextField(null=False,blank =False, unique=False, help_text="Descripcion del Sector")
    area = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal(0.0), null=False, help_text="Area en m2")
    perimetro = models.TextField(null=False,blank =False, unique=False, help_text="Descripcion del Sector")
    clasificacion= models.CharField(max_length=1, choices=CLASIFICACION, default='A', help_text='clasificacion del Sector')

class Calle(models.Model):
    TIPO = (
        ('1', 'Colateral'),
        ('2', 'Via'),
        ('3', 'Doble Via')
    )
    codigo = models.TextField(null=False,blank =False, unique=True, help_text="Codigo de la calle")
    nombre = models.TextField(null=False,blank =False, unique=False, help_text="Nombre de la calle")
    tipo= models.CharField(max_length=1, choices=TIPO, default='1', help_text='tipo calle')

class Avenida(models.Model):
    TIPO = (
        ('1', 'Colateral'),
        ('2', 'Via'),
        ('3', 'Doble Via')
    )
    codigo = models.TextField(null=False,blank =False, unique=True, help_text="Codigo de la avenida")
    nombre = models.TextField(null=False,blank =False, unique=False, help_text="Nombre de la avenida")
    tipo= models.CharField(max_length=1, choices=TIPO, default='1', help_text='tipo de avenida')


class Urbanizacion(models.Model):
    TIPO = (
        ('P', 'Publica'),
        ('R', 'Privada'),
    )
    sector=models.ForeignKey(Sector,on_delete=models.PROTECT,help_text="Sector asociado")
    nombre = models.TextField(null=False,blank =False, unique=False, help_text="Nombre de la urbanizacion")
    tipo= models.CharField(max_length=1, choices=TIPO, default='P', help_text='tipo de la urbanizacion')

class Manzana(models.Model):
    sector=models.ForeignKey(Sector,on_delete=models.PROTECT,help_text="Sector asociado")
    codigo = models.TextField(null=False,blank =False, unique=True, help_text="Codigo de la Manzana")
    area = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal(0.0), null=False, help_text="Area en m2")
    perimetro = models.TextField(null=False,blank =False, unique=False, help_text="Perimetro de la manzana")
    via_norte=models.ForeignKey(Calle,null=True,on_delete=models.PROTECT,help_text="Via cercana norte",related_name='manzana_via_norte')
    via_sur=models.ForeignKey(Calle,null=True,on_delete=models.PROTECT,help_text="Via cercana sur",related_name='manzana_via_sur')
    via_este=models.ForeignKey(Calle,null=True,on_delete=models.PROTECT,help_text="Via cercana este",related_name='manzana_via_este')
    via_oeste=models.ForeignKey(Calle,null=True,on_delete=models.PROTECT,help_text="Via cercana oeste",related_name='manzana_via_oeste')

class Parcela(models.Model):
    manzana=models.ForeignKey(Manzana,on_delete=models.PROTECT,help_text="Manzana asociado")
    codigo = models.TextField(null=False,blank =False, unique=True, help_text="Codigo de la Parcela")
    area = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal(0.0), null=False, help_text="Area en m2")
    perimetro = models.TextField(null=False,blank =False, unique=False, help_text="Perimetro de la Parcela")

class SubParcela(models.Model):
    parcela=models.ForeignKey(Parcela,on_delete=models.PROTECT,help_text="Parcela asociado")
    codigo = models.TextField(null=False,blank =False, unique=True, help_text="Codigo de la SubParcela")
    area = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal(0.0), null=False, help_text="Area en m2")
    perimetro = models.TextField(null=False,blank =False, unique=False, help_text="Perimetro de la SubParcela")


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

class Zona(models.Model):
    codigo = models.TextField(null=False,blank =False, unique=True, help_text="Codigo de Zona")
    descripcion = models.TextField(null=False,blank =False, unique=True, help_text="descripcion de la Zona")

# Maestro de Propietarios/Contribuyentes
class Propietario(models.Model):
    tipo_documento  = models.TextField(null=False,blank =False, unique=False, help_text="Numero de expediente")
    nacionalidad  = models.TextField(null=False,blank =False, unique=False, help_text="Numero de expediente")
    numero_documento  = models.TextField(null=False,blank =False, unique=True, help_text="Numero de expediente")
    nombre  = models.TextField(null=False,blank =False, unique=False, help_text="Numero de expediente")
    telefono_principal  = models.TextField(null=False,blank =False, unique=False, help_text="Numero de expediente")
    telefono_secundario   = models.TextField(null=False,blank =False, unique=False, help_text="Numero de expediente")
    email_principal  = models.TextField(null=False,blank =False, unique=False, help_text="Numero de expediente")
    emaill_secundario  = models.TextField(null=False,blank =False, unique=False, help_text="Numero de expediente")

class Inmueble(models.Model):
    numero_expediente = models.TextField(null=False,blank =False, unique=True, help_text="Numero de expediente")
    fecha_inscripcion = models.DateField(blank=True, help_text="fecha de inscripcion")
    tipo=models.ForeignKey(TipoInmueble,on_delete=models.PROTECT,null=True,blank =True,help_text="TipoInmueble asociado")
    status=models.ForeignKey(EstatusInmueble,on_delete=models.PROTECT,null=True,blank =True,help_text="status asociado")
    ambito=models.ForeignKey(Ambito,on_delete=models.PROTECT,null=True,blank =True,help_text="ambito asociado")
    sector=models.ForeignKey(Sector,on_delete=models.PROTECT,null=True,blank =True,help_text="Sector asociado")
    manzana=models.ForeignKey(Manzana,on_delete=models.PROTECT,null=True,blank =True,help_text="manzana asociado")
    parcela=models.ForeignKey(Parcela,on_delete=models.PROTECT,null=True,blank =True,help_text="parcela asociado")
    subparcela=models.ForeignKey(SubParcela,on_delete=models.PROTECT,null=True,blank =True,help_text="subparcela asociado")
    nivel=models.ForeignKey(NivelInmueble,on_delete=models.PROTECT,null=True,blank =True,help_text="nivel asociado")
    unidad=models.ForeignKey(UnidadInmueble,on_delete=models.PROTECT,null=True,blank =True,help_text="unidad asociado")
    urbanizacion=models.ForeignKey(Urbanizacion,on_delete=models.PROTECT,null=True,blank =True,help_text="urbanizacion")
    calle=models.ForeignKey(Calle,on_delete=models.PROTECT,null=True,blank =True,help_text="calle asociado")
    conjunto_residencial=models.ForeignKey(ConjuntoResidencial,on_delete=models.PROTECT,null=True,blank =True,help_text="Sector asociado")
    edificio=models.ForeignKey(Edificio,on_delete=models.PROTECT,null=True,blank =True,help_text="edificio asociado")
    avenida=models.ForeignKey(Avenida,on_delete=models.PROTECT,null=True,blank =True,help_text="avenida asociado")
    torre=models.ForeignKey(Torre,on_delete=models.PROTECT,null=True,blank =True,help_text="Sector asociado")
    numero_civico = models.TextField(null=True,blank =True, help_text="Numero de expediente")
    numero_casa = models.TextField(null=True,blank =True, help_text="Numero de expediente")
    numero_piso = models.TextField(null=True,blank =True, help_text="Numero de expediente")
    telefono = models.TextField(null=True,blank =True, help_text="Numero de expediente")
    zona = models.ForeignKey(Zona,on_delete=models.PROTECT, null=True,blank =True,help_text="Zona !! Base para calculo")
    direccion = models.TextField(null=True,blank =True, help_text="direccion")
    referencia = models.TextField(null=True,blank =True, help_text="referencia")
    observaciones = models.TextField(null=True,blank =True, help_text="observaciones")
	
class InmueblePropiedad(models.Model):
    inmueble = models.ForeignKey (Inmueble, on_delete=models.PROTECT,help_text="Sector asociado")
    tipo_documento = models.ForeignKey (TipoDocumento, on_delete=models.PROTECT,help_text="Sector asociado")
    tipo_especial = models.ForeignKey (TipoEspecial, on_delete=models.PROTECT,help_text="Sector asociado")
    fecha_habitabilidad	= models.DateField(blank=True, help_text="fecha_habitabilidad")
    tipo_tenencia = models.ForeignKey (TipoTenencia, on_delete=models.PROTECT,help_text="tipo_tenencia asociado")
    fecha_vigencia = models.DateField(blank=True, help_text="fecha de inscripcion")
    fecha_documento	= models.DateField(blank=True, help_text="fecha de inscripcion")
    numero_documento = models.TextField(null=False,blank =False, unique=True, help_text="Numero de expediente")
    matricula_documento	= models.TextField(null=False,blank =False, unique=False, help_text="Numero de expediente")
    anio_folio_documento = models.TextField(null=False,blank =False, unique=False, help_text="Numero de expediente")
    fecha_terreno = models.DateField(blank=True, help_text="fecha de inscripcion")
    numero_terreno = models.TextField(null=False,blank =False, unique=False, help_text="Numero de expediente")
    folio_terreno = models.TextField(null=False,blank =False, unique=False, help_text="Numero de expediente")
    protocolo_terreno = models.TextField(null=False,blank =False, unique=False, help_text="Numero de expediente")
    tomo_terreno = models.TextField(null=False,blank =False, unique=False, help_text="Numero de expediente")
    area_terreno =  models.DecimalField(max_digits=14, decimal_places=2, default=Decimal(0.0), null=False, help_text="area_terreno en m2")
    valor_terreno = models.TextField(null=False,blank =False, unique=False, help_text="Numero de expediente")
    fecha_construccion = models.DateField(blank=True, help_text="fecha de inscripcion")
    numero_construccion	= models.TextField(null=False,blank =False, unique=False, help_text="Numero de expediente")
    folio_construccion = models.TextField(null=False,blank =False, unique=False, help_text="Numero de expediente")
    protocolo_construccion = models.TextField(null=False,blank =False, unique=False, help_text="Numero de expediente")
    tomo_construccion = models.TextField(null=False,blank =False, unique=False, help_text="Numero de expediente")
    area_construccion =  models.DecimalField(max_digits=14, decimal_places=2, default=Decimal(0.0), null=False, help_text="area_construccion en m2")
    lindero_norte = models.TextField(null=False,blank =False, unique=False, help_text="Numero de expediente")
    lindero_sur	= models.TextField(null=False,blank =False, unique=False, help_text="Numero de expediente")
    lindero_este = models.TextField(null=False,blank =False, unique=False, help_text="Numero de expediente")
    lindero_oeste = models.TextField(null=False,blank =False, unique=False, help_text="Numero de expediente")

class InmueblePropietarios(models.Model):
    inmueble = models.ForeignKey (Inmueble, on_delete=models.PROTECT,help_text="Id Inmueble")
    propietario = models.ForeignKey (Propietario, on_delete=models.PROTECT,help_text="Id Propietario")

class InmuebleTerreno(models.Model):
    inmueble = models.ForeignKey (Inmueble, on_delete=models.PROTECT,help_text="Id Inmueble asociado")
    #topografia	= models.ForeignKey (Topografia, on_delete=models.PROTECT,help_text="Topografia asociado")
    #acceso = models.ForeignKey (Acceso, on_delete=models.PROTECT,help_text="Acceso asociado")
    forma = models.ForeignKey (Forma, on_delete=models.PROTECT,help_text="Forma asociado")
    ubicacion = models.ForeignKey (Ubicacion, on_delete=models.PROTECT,help_text="Ubicacion asociado")
    tenencia = models.ForeignKey (TipoTenencia, on_delete=models.PROTECT,help_text="tenencia asociado")
    #uso	= models.ForeignKey (Uso, on_delete=models.PROTECT,help_text="uso asociado")
    #regimen	= models.ForeignKey (Regimen, on_delete=models.PROTECT,help_text="regimen asociado")
    servicios = models.ForeignKey (Servicios, on_delete=models.PROTECT,help_text="Servicios Asociado")
    observaciones = models.TextField(null=False,blank =False, unique=False, help_text="Observaciones")

class InmuebleTerrenoTopografia(models.Model):
    inmueble_terreno = models.ForeignKey (InmuebleTerreno, on_delete=models.PROTECT,help_text="Inmueble asociado")
    topografia = models.ForeignKey (Topografia, on_delete=models.PROTECT,help_text="Topografia asociado")

class InmuebleTerrenoAcceso(models.Model):
    inmueble_terreno = models.ForeignKey (InmuebleTerreno, on_delete=models.PROTECT,help_text="Inmueble asociado")
    acceso = models.ForeignKey (Acceso, on_delete=models.PROTECT,help_text="Acceso asociado")
	
class InmuebleTerrenoUso(models.Model):
    inmueble_terreno = models.ForeignKey (InmuebleTerreno, on_delete=models.PROTECT,help_text="Inmueble asociado")
    uso = models.ForeignKey (Uso, on_delete=models.PROTECT,help_text="uso asociado")
	
class InmuebleTerrenoRegimen(models.Model):
    inmueble_terreno = models.ForeignKey (InmuebleTerreno, on_delete=models.PROTECT,help_text="Inmueble asociado")
    regimen	= models.ForeignKey (Regimen, on_delete=models.PROTECT,help_text="regimen asociado")


class UsoConstruccion(models.Model):
    codigo = models.TextField(null=False,blank =False, unique=True, help_text="Codigo de UsoConstruccion")
    descripcion = models.TextField(null=False,blank =False, unique=True, help_text="descripcion de UsoConstruccion")

class Soporte(models.Model):
    codigo = models.TextField(null=False,blank =False, unique=True, help_text="Codigo de Soporte")
    descripcion = models.TextField(null=False,blank =False, unique=True, help_text="descripcion de Soporte")

class Techo(models.Model):
    codigo = models.TextField(null=False,blank =False, unique=True, help_text="Codigo de Techo")
    descripcion = models.TextField(null=False,blank =False, unique=True, help_text="descripcion de Techo")

class Cubierta(models.Model):
    codigo = models.TextField(null=False,blank =False, unique=True, help_text="Codigo de Cubierta")
    descripcion = models.TextField(null=False,blank =False, unique=True, help_text="descripcion de Cubierta")

class TipoPared(models.Model):
    codigo = models.TextField(null=False,blank =False, unique=True, help_text="Codigo de TipoPared")
    descripcion = models.TextField(null=False,blank =False, unique=True, help_text="descripcion de TipoPared")

class AcabadoPared(models.Model):
    codigo = models.TextField(null=False,blank =False, unique=True, help_text="Codigo de AcabadoPared")
    descripcion = models.TextField(null=False,blank =False, unique=True, help_text="descripcion de AcabadoPared")

class Conservacion(models.Model):
    codigo = models.TextField(null=False,blank =False, unique=True, help_text="Codigo de Conservacion")
    descripcion = models.TextField(null=False,blank =False, unique=True, help_text="descripcion de Conservacion")


class InmuebleConstruccion(models.Model):
    inmueble = models.ForeignKey (Inmueble, on_delete=models.PROTECT,help_text="Id Inmueble asociado")
    tipo=models.ForeignKey(TipoInmueble,on_delete=models.PROTECT,help_text="TipoInmueble asociado")
    uso_construccion = models.ForeignKey(UsoConstruccion,on_delete=models.PROTECT,help_text="uso_construccion asociado")
    tenencia = models.ForeignKey (TipoTenencia, on_delete=models.PROTECT,help_text="tenencia asociado")
    regimen	= models.ForeignKey (Regimen, on_delete=models.PROTECT,help_text="regimen asociado")
    #soporte = models.ForeignKey (Soporte, on_delete=models.PROTECT,help_text="Soporte asociado")
    #techo = models.ForeignKey (Techo, on_delete=models.PROTECT,help_text="Techo asociado")
    #cubierta = models.ForeignKey (Cubierta, on_delete=models.PROTECT,help_text="Cubierta asociado")
    tipo_pared = models.ForeignKey (TipoPared, on_delete=models.PROTECT,help_text="TipoPared asociado")
    acabado_pared = models.ForeignKey (AcabadoPared, on_delete=models.PROTECT,help_text="AcabadoPared asociado")
    conservacion = models.ForeignKey (Conservacion, on_delete=models.PROTECT,help_text="Conservacion asociado")
    anio_construccion = models.PositiveIntegerField(default=0, help_text="anio_construccion")
    anio_refaccion = models.PositiveIntegerField(default=0, help_text="anio_refaccion")
    porcentaje_refaccion = models.TextField(null=False,blank =False, unique=False, help_text="Numero de expediente")
    edad_efectiva = models.TextField(null=False,blank =False, unique=False, help_text="edad_efectiva")
    numero_niveles = models.PositiveIntegerField(default=0, help_text="Numero de niveles")
    numero_edificaciones = models.PositiveIntegerField(default=0, help_text="numero de edificaciones")
    observaciones = models.TextField(null=True,blank =True, help_text="observaciones")

class InmuebleConstruccionSoporte(models.Model):
    inmueble_construccion = models.ForeignKey (InmuebleConstruccion, on_delete=models.PROTECT,help_text="Inmueble asociado")
    soporte = models.ForeignKey(Soporte, on_delete=models.PROTECT,help_text="Soporte asociado")

class InmuebleConstruccionTecho(models.Model):
    inmueble_construccion = models.ForeignKey (InmuebleConstruccion, on_delete=models.PROTECT,help_text="Inmueble asociado")
    techo = models.ForeignKey(Techo, on_delete=models.PROTECT,help_text="Techo asociado")

class InmuebleConstruccionCubierta(models.Model):
    inmueble_construccion = models.ForeignKey (InmuebleConstruccion, on_delete=models.PROTECT,help_text="Inmueble asociado")
    cubierta = models.ForeignKey(Cubierta, on_delete=models.PROTECT,help_text="Cubierta asociado") 


class InmuebleValoracionTerreno(models.Model):
    inmueble = models.ForeignKey (Inmueble, on_delete=models.PROTECT,help_text="Id Inmueble asociado")
    area = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal(0.0), null=False, help_text="Area en m2")
    tipologia = models.ForeignKey (Tipologia, on_delete=models.PROTECT,help_text="tipologia asociado")
    fines_fiscales	= models.ForeignKey (FinesFiscales, on_delete=models.PROTECT,help_text="fines_fiscales asociado")
    valor_unitario = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal(0.0), null=False, help_text="valor_unitario")
    area_factor_ajuste =  models.DecimalField(max_digits=14, decimal_places=2, default=Decimal(0.0), null=False, help_text="Area en m2 del factor de ajuste")
    forma_factor_ajuste	= models.ForeignKey (Forma, on_delete=models.PROTECT,help_text="Forma del factor de ajuste")
    valor_ajustado = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal(0.0), null=False, help_text="Valor Ajustado")
    valor_total = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal(0.0), null=False, help_text="Valor Total")
    observaciones = models.TextField(null=False,blank =False, unique=False, help_text="observaciones")

class InmuebleValoracionConstruccion(models.Model):
    inmueble_terreno = models.ForeignKey (InmuebleValoracionTerreno, on_delete=models.PROTECT,help_text="Id inmueble_terreno asociado")
    tipologia = models.ForeignKey (Tipologia, on_delete=models.PROTECT,help_text="tipologia asociado")
    fecha_compra = models.DateField(blank=True, help_text="fecha_compra")
    trimestre = models.PositiveIntegerField(default=0,help_text="trimestre")
    anio = models.PositiveIntegerField(default=0, help_text="Numero de expediente")
    area = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal(0.0), null=False, help_text="Area en m2")
    valor = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal(0.0), null=False, help_text="valor")
    depreciacion = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal(0.0), null=False, help_text="depreciacion")
    observaciones = models.TextField(null=False,blank =False, unique=False, help_text="observaciones")

class InmuebleUbicacion(models.Model):
    inmueble = models.ForeignKey (Inmueble, on_delete=models.PROTECT,help_text="Id Inmueble asociado")
    lindero_norte = models.TextField(null=False,blank =False, unique=False, help_text="Numero de expediente")
    lindero_sur = models.TextField(null=False,blank =False, unique=False, help_text="Numero de expediente")
    lindero_este = models.TextField(null=False,blank =False, unique=False, help_text="Numero de expediente")
    lindero_oeste = models.TextField(null=False,blank =False, unique=False, help_text="Numero de expediente")
    imagen_inmueble = models.ImageField(upload_to='media/paises', null=True, blank=True, help_text="Imagen asociado al pais")
    imagen_plano = models.ImageField(upload_to='media/paises', null=True, blank=True, help_text="Imagen asociado al pais")
    imagan_plano_mesura =models.ImageField(upload_to='media/paises', null=True, blank=True, help_text="Imagen asociado al pais")
    g1_norte = models.TextField(null=False,blank =False, unique=False, help_text="Numero de expediente")
    g1_este = models.TextField(null=False,blank =False, unique=False, help_text="Numero de expediente")
    g2_norte = models.TextField(null=False,blank =False, unique=False, help_text="Numero de expediente")
    g2_este = models.TextField(null=False,blank =False, unique=False, help_text="Numero de expediente")
    g3_norte = models.TextField(null=False,blank =False, unique=False, help_text="Numero de expediente")
    g3_este = models.TextField(null=False,blank =False, unique=False, help_text="Numero de expediente")
    g4_norte = models.TextField(null=False,blank =False, unique=False, help_text="Numero de expediente")
    g4_este = models.TextField(null=False,blank =False, unique=False, help_text="Numero de expediente")
    g5_norte = models.TextField(null=False,blank =False, unique=False, help_text="Numero de expediente")
    g5_este = models.TextField(null=False,blank =False, unique=False, help_text="Numero de expediente")
    g6_norte = models.TextField(null=False,blank =False, unique=False, help_text="Numero de expediente")
    g6_este = models.TextField(null=False,blank =False, unique=False, help_text="Numero de expediente")
    g7_norte = models.TextField(null=False,blank =False, unique=False, help_text="Numero de expediente")
    g7_este = models.TextField(null=False,blank =False, unique=False, help_text="Numero de expediente")
    g8_norte = models.TextField(null=False,blank =False, unique=False, help_text="Numero de expediente")
    g8_este = models.TextField(null=False,blank =False, unique=False, help_text="Numero de expediente")

class InmuebleFaltante(models.Model):
    inmueble = models.ForeignKey (Inmueble, on_delete=models.PROTECT,help_text="Id Inmueble asociado")
    cedula = models.TextField(null=False,blank =False, unique=False, help_text="Numero de expediente")
    doumento_propiedad = models.TextField(null=False,blank =False, unique=False, help_text="Numero de expediente")
    observaciones = models.TextField(null=False,blank =False, unique=False, help_text="observaciones")



## Histoial de Actualizacion de precios de Tasa BS
class TasaBCV(models.Model):
    fecha = models.DateField(blank=True, help_text="Fecha Actualizacion TASA")
    fecha_vigente= models.DateField(blank=True, help_text=" A partir de esta fecha se aplica los calculos")
    monto  = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal(0.0), null=False,  help_text="Monto TASA")
    habilitado = models.BooleanField(default=True, help_text="Esta activo?")

## Histoial de Actualizacion de precios de UT
class UnidadTributaria(models.Model):
    fecha = models.DateField(blank=True, help_text="Fecha Actualizacion Unidad Tributaria")
    fecha_vigente= models.DateField(blank=True, help_text=" A partir de esta fecha se aplica los calculos")
    monto  = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal(0.0), null=False,  help_text="Monto Unidad tributaria")
    habilitado = models.BooleanField(default=True, help_text="Esta activo?")

## moneda para calculo : ejemplo Petro
class Moneda(models.Model):
    descripcion  = models.TextField(null=False,blank =False, unique=True, help_text="Descripcion de la Moneda")
    habilitado = models.BooleanField(default=True, help_text="Esta activo?")

# Maestro de de Impuestos/Tasas/Multas
class TasaMulta(models.Model):
    TIPO = (
        ('I', 'Impuesto'),
        ('T', 'Tasa'),
        ('M', 'Multa'),
        ('O', 'Otro')
    )
    APLICA = (
        ('C', 'Catastro'),
        ('V', 'Vehiculo'),
        ('P', 'Patente'),
        ('I', 'Industria y Comercio'),
        ('O', 'Otro')
    )
    descripcion  = models.TextField(null=False,blank =False, unique=True, help_text="Descripcion")
    unidad_tributaria  = models.TextField(null=False,blank =False, unique=False, help_text="Cantidad Unidad tributaria")
    tipo= models.CharField(max_length=1, choices=TIPO, default='O', help_text='tipo de recaudacion')
    aplica= models.CharField(max_length=1, choices=APLICA, default='O', help_text='A que tipo de sector aplica')   

class EstadoCuenta(models.Model):
    numero = models.TextField(null=False,blank =False, unique=True, help_text="Numero de Estado de Cuenta")
    fecha = models.DateTimeField(blank=True, help_text="Fecha Estado Cuenta")
    propietario=models.ForeignKey(Propietario, on_delete=models.PROTECT,help_text="Contribuyente/Propietario asociado")
    observaciones = models.TextField(null=False,blank =False, unique=False, help_text="observaciones")
    valor_petro  = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal(0.0), null=False, help_text="total")
    valor_tasa_bs = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal(0.0), null=False, help_text="total")
    monto_total  = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal(0.0), null=False, help_text="total")

class EstadoCuentaDetalle(models.Model):
    estadocuenta = models.ForeignKey(EstadoCuenta, on_delete=models.PROTECT,help_text="ID Cabecera Estado de Cuenta")
    tasamulta = models.ForeignKey(TasaMulta, on_delete=models.PROTECT,help_text="Id Tasa Multa")
    monto_unidad_tributaria  = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal(0.0), null=False,  help_text="Monto Unidad tributaria")	
    monto_tasa  = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal(0.0), null=False,  help_text="Monto total del renglon tasa(monto_unidad_tributaria * cantidad)")	
    cantidad  = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal(0.0), null=False, help_text="Cantidad Unidad tributaria")

class Liquidacion(models.Model):
    estadocuenta = models.ForeignKey(EstadoCuenta,null=True, on_delete=models.PROTECT,help_text="ID Cabecera Estado de Cuenta")
    numero = models.TextField(null=False,blank =False, unique=True, help_text="Numero de Liquidacion")
    fecha = models.DateTimeField(blank=True, help_text="Fecha Estado Cuenta")
    propietario=models.ForeignKey(Propietario, on_delete=models.PROTECT,help_text="Contribuyente/Propietario asociado")
    observaciones = models.TextField(null=False,blank =False, unique=False, help_text="observaciones")
    valor_petro  = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal(0.0), null=False, help_text="total")
    valor_tasa_bs = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal(0.0), null=False, help_text="total")
    monto_total  = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal(0.0), null=False, help_text="total")

class LiquidacionDetalle(models.Model):
    liquidacion = models.ForeignKey(Liquidacion, on_delete=models.PROTECT,help_text="ID Cabecera liquidacion")
    tasamulta = models.ForeignKey(TasaMulta, on_delete=models.PROTECT,help_text="Id Tasa Multa")
    monto_unidad_tributaria  = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal(0.0), null=False,  help_text="Monto Unidad tributaria")	
    monto_tasa  = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal(0.0), null=False,  help_text="Monto total del renglon tasa(monto_unidad_tributaria * cantidad)")	
    cantidad  = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal(0.0), null=False, help_text="Cantidad Unidad tributaria")


#Maestro de tipos de pago
class TipoPago(models.Model):
    descripcion  = models.TextField(null=False,blank =False, unique=True, help_text="Descripcion Tipo de pago")

#Maestro de recibo Pago
class PagoEstadoCuenta(models.Model):
    numero = models.TextField(null=False,blank =False, unique=True, help_text="Numero de pago")
    estadocuenta = models.ForeignKey(EstadoCuenta, on_delete=models.PROTECT,help_text="ID Cabecera Estado de Cuenta")
    fecha = models.DateTimeField(blank=True, help_text="Fecha Estado Cuenta")
    propietario=models.ForeignKey(Propietario, on_delete=models.PROTECT,help_text="Contribuyente/Propietario asociado")
    observaciones = models.TextField(null=False,blank =False, unique=False, help_text="observaciones")
    monto  = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal(0.0), null=False, help_text="total")

#Detalle de recibo Pago
class PagoEstadoCuentaDetalle(models.Model):
    estadocuenta = models.ForeignKey(EstadoCuenta, on_delete=models.PROTECT,help_text="ID Cabecera Estado de Cuenta")
    tipopago = models.ForeignKey(TipoPago, on_delete=models.PROTECT,help_text="Id Tipo Pago")
    monto  = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal(0.0), null=False,  help_text="Monto del pago")	
    nro_cuenta = models.TextField(null=False,blank =False, unique=False, help_text="nro_cuenta")
    fecha = models.TextField(null=False,blank =False, unique=False, help_text="fecha")
    telefono = models.TextField(null=False,blank =False, unique=False, help_text="telefono")
    banco = models.TextField(null=False,blank =False, unique=False, help_text="banco")
    cedula = models.TextField(null=False,blank =False, unique=False, help_text="cedula")
    
# tabla dee control para manejo de correlativos
class Correlativo(models.Model):
    ExpedienteCatastro = models.PositiveIntegerField(null=True, blank=True,  help_text="Numero de Expediente de Catastro")	
    NumeroEstadoCuenta = models.PositiveIntegerField(null=True, blank=True,  help_text="Numero de Estado de Cuenta")
    NumeroLiquidacion = models.PositiveIntegerField(null=True, blank=True,  help_text="Numero de NumeroLiquidacion")
    NumeroPago = models.PositiveIntegerField(null=True, blank=True,  help_text="Numero de Recibo de pagos")

# Caranday ver 1.0
class Flujo(models.Model):
    inmueble=models.ForeignKey(Inmueble, on_delete=models.PROTECT,help_text="Inmueble")
    estadocuenta = models.ForeignKey(EstadoCuenta, on_delete=models.PROTECT,help_text="ID Cabecera Estado de Cuenta")
    