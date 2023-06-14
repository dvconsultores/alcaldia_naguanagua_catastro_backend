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
from django.utils import timezone

class Departamento(models.Model):
    nombre = models.CharField(max_length=255, null=False, blank=False, primary_key=True, help_text="Nombre Depatamento para usuario de catastro FLUJO")
    def __str__(self):
        return '%s' % (self.nombre)


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

class Perfil(models.Model):
    TIPO = (('S', 'Super'), 
            ('A', 'Admin'),
            ('U', 'Usuario'), 
            ('C', 'Catastro'), 
            ('T', 'Tributario'))
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, help_text="usuario asociado")
    activo = models.BooleanField(default=True, help_text="esta el usuario activo?")
    tipo = models.CharField(max_length=1, null=True, choices=TIPO, default='U', help_text="Tipo de usuario")
    departamento = models.ForeignKey(Departamento, null=True, blank=True,on_delete=models.CASCADE, help_text="Departamento del usuario")
    modulo = models.ForeignKey(Modulo, null=True, blank=True,on_delete=models.CASCADE, help_text="Modulo INICAL al entrar")
    def __str__(self):
        return '%s - %s - %s' % (self.usuario.username, self.tipo,self.departamento)

class Permiso(models.Model):
    modulo = models.ForeignKey(Modulo, null=False, blank=False,on_delete=models.CASCADE, help_text="Opcion de menu asociada")
    perfil = models.ForeignKey(Perfil, null=False, blank=False,on_delete=models.CASCADE, help_text="Usuario asociado")
    # Metodos
    leer = models.BooleanField(default=False, help_text="Tiene opcion de leer?")
    escribir = models.BooleanField(default=False, help_text="Tiene opcion de escribir?")
    borrar = models.BooleanField(default=False, help_text="Tiene opcion de borrar?")
    actualizar = models.BooleanField(default=False, help_text="Tiene opcion de actualizar?")

    def __str__(self):
        return '%s (Permiso: %s-%s-%s - Leer:%s Borrar:%s Actualizar:%s Escribir:%s)' % (self.perfil.usuario.username, self.modulo.es_menu, self.modulo.menu, self.modulo.nombre, self.leer, self.borrar, self.actualizar, self.escribir)


class Ambito(models.Model):
    codigo = models.TextField(null=False,blank =False, unique=True, help_text="Codigo del ambito")
    descripcion = models.TextField(null=False,blank =False, unique=False, help_text="Descripcion del ambito")
    def __str__(self):
        return '%s - %s' % (self.codigo, self.descripcion)
    
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
    perimetro = models.TextField(null=True,blank =True, help_text="Descripcion del Sector")
    clasificacion= models.CharField(max_length=1, choices=CLASIFICACION, default='A', help_text='clasificacion del Sector')
    def __str__(self):
        return '%s - %s' % (self.codigo, self.descripcion)
    
class Calle(models.Model):
    TIPO = (
        ('1', 'Colateral'),
        ('2', 'Via'),
        ('3', 'Doble Via')
    )
    codigo = models.TextField(null=False,blank =False, unique=True, help_text="Codigo de la calle")
    nombre = models.TextField(null=False,blank =False, unique=False, help_text="Nombre de la calle")
    tipo= models.CharField(max_length=1, choices=TIPO, default='1', help_text='tipo calle')
    def __str__(self):
        return '%s - %s' % (self.codigo, self.nombre)
    
class Avenida(models.Model):
    TIPO = (
        ('1', 'Colateral'),
        ('2', 'Via'),
        ('3', 'Doble Via')
    )
    codigo = models.TextField(null=False,blank =False, unique=True, help_text="Codigo de la avenida")
    nombre = models.TextField(null=False,blank =False, unique=False, help_text="Nombre de la avenida")
    tipo= models.CharField(max_length=1, choices=TIPO, default='1', help_text='tipo de avenida')
    def __str__(self):
        return '%s - %s' % (self.codigo, self.nombre)

class Urbanizacion(models.Model):
    TIPO = (
        ('P', 'Publica'),
        ('R', 'Privada'),
    )
    sector=models.ForeignKey(Sector,on_delete=models.PROTECT,help_text="Sector asociado")
    nombre = models.TextField(null=False,blank =False, unique=False, help_text="Nombre de la urbanizacion")
    tipo= models.CharField(max_length=1, choices=TIPO, default='P', help_text='tipo de la urbanizacion')
    def __str__(self):
        return '%s - %s' % (self.tipo, self.nombre)
    
class Manzana(models.Model):
    sector=models.ForeignKey(Sector,on_delete=models.PROTECT,help_text="Sector asociado")
    codigo = models.TextField(null=False,blank =False, unique=True, help_text="Codigo de la Manzana")
    area = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal(0.0), null=False, help_text="Area en m2")
    perimetro = models.TextField(null=True,blank =True, help_text="Perimetro de la manzana")
    via_norte=models.ForeignKey(Calle,null=True,on_delete=models.PROTECT,help_text="Via cercana norte",related_name='manzana_via_norte')
    via_sur=models.ForeignKey(Calle,null=True,on_delete=models.PROTECT,help_text="Via cercana sur",related_name='manzana_via_sur')
    via_este=models.ForeignKey(Calle,null=True,on_delete=models.PROTECT,help_text="Via cercana este",related_name='manzana_via_este')
    via_oeste=models.ForeignKey(Calle,null=True,on_delete=models.PROTECT,help_text="Via cercana oeste",related_name='manzana_via_oeste')
    def __str__(self):
        return '%s' % (self.codigo)
    
class Parcela(models.Model):
    manzana=models.ForeignKey(Manzana,on_delete=models.PROTECT,help_text="Manzana asociado")
    codigo = models.TextField(null=False,blank =False, unique=True, help_text="Codigo de la Parcela")
    area = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal(0.0), null=False, help_text="Area en m2")
    perimetro = models.TextField(null=True,blank =True, help_text="Perimetro de la Parcela")
    def __str__(self):
        return '%s' % (self.codigo)
    
class SubParcela(models.Model):
    parcela=models.ForeignKey(Parcela,on_delete=models.PROTECT,help_text="Parcela asociado")
    codigo = models.TextField(null=False,blank =False, unique=True, help_text="Codigo de la SubParcela")
    area = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal(0.0), null=False, help_text="Area en m2")
    perimetro = models.TextField(null=True,blank =True, help_text="Perimetro de la SubParcela")
    def __str__(self):
        return '%s' % (self.codigo)

class ConjuntoResidencial(models.Model):
    urbanizacion = models.ForeignKey(Urbanizacion,on_delete=models.PROTECT,help_text="Urbanizacion asociada")
    nombre = models.TextField(null=False,blank =False, unique=True, help_text="nombre del conjunto residencial")
    def __str__(self):
        return '%s' % (self.nombre)
    
class Edificio(models.Model):
    urbanizacion = models.ForeignKey(Urbanizacion,on_delete=models.PROTECT,help_text="Urbanizacion asociada")
    conjunto_residencial = models.ForeignKey(ConjuntoResidencial,null=True,on_delete=models.PROTECT,help_text="conjunto residencial asociado")
    nombre = models.TextField(null=False,blank =False, unique=True, help_text="nombre del conjunto residencial")
    def __str__(self):
        return '%s' % (self.nombre)
    
class Torre(models.Model):
    urbanizacion = models.ForeignKey(Urbanizacion,on_delete=models.PROTECT,help_text="Urbanizacion asociada")
    conjunto_residencial = models.ForeignKey(ConjuntoResidencial,null=True,on_delete=models.PROTECT,help_text="conjunto residencial asociado")
    nombre = models.TextField(null=False,blank =False, unique=True, help_text="nombre del conjunto residencial")
    def __str__(self):
        return '%s' % (self.nombre)
    
class TipoInmueble(models.Model):
    codigo = models.TextField(null=False,blank =False, unique=True, help_text="Codigo del tipo de inmueble")
    descripcion = models.TextField(null=False,blank =False, unique=True, help_text="descripcion del tipo de inmueble")
    def __str__(self):
        return '%s - %s' % (self.codigo, self.descripcion)
    
class EstatusInmueble(models.Model):
    codigo = models.TextField(null=False,blank =False, unique=True, help_text="Codigo del estatus de inmueble")
    descripcion = models.TextField(null=False,blank =False, unique=True, help_text="descripcion del estatus de inmueble")
    def __str__(self):
        return '%s - %s' % (self.codigo, self.descripcion)
    
class NivelInmueble(models.Model):
    codigo = models.TextField(null=False,blank =False, unique=True, help_text="Codigo del nivel de inmueble")
    descripcion = models.TextField(null=False,blank =False, unique=True, help_text="descripcion del nivel de inmueble")
    def __str__(self):
        return '%s - %s' % (self.codigo, self.descripcion)
    
class UnidadInmueble(models.Model):
    codigo = models.TextField(null=False,blank =False, unique=True, help_text="Codigo de la unidad del inmueble")
    descripcion = models.TextField(null=False,blank =False, unique=True, help_text="descripcion de la unidad del inmueble")
    def __str__(self):
        return '%s - %s' % (self.codigo, self.descripcion)
    
class TipoDocumento(models.Model):
    codigo = models.TextField(null=False,blank =False, unique=True, help_text="Codigo del tipo de documento del inmueble")
    descripcion = models.TextField(null=False,blank =False, unique=True, help_text="descripcion del tipo de documento del inmueble")
    def __str__(self):
        return '%s - %s' % (self.codigo, self.descripcion)
    
class TipoEspecial(models.Model):
    codigo = models.TextField(null=False,blank =False, unique=True, help_text="Codigo del tipo especial del inmueble")
    descripcion = models.TextField(null=False,blank =False, unique=True, help_text="descripcion del tipo especial del inmueble")
    def __str__(self):
        return '%s - %s' % (self.codigo, self.descripcion)
    
class TipoTenencia(models.Model):
    codigo = models.TextField(null=False,blank =False, unique=True, help_text="Codigo del tipo tenecia del inmueble")
    descripcion = models.TextField(null=False,blank =False, unique=True, help_text="descripcion del tenecia especial del inmueble")
    def __str__(self):
        return '%s - %s' % (self.codigo, self.descripcion)
    
class Topografia(models.Model):
    codigo = models.TextField(null=False,blank =False, unique=True, help_text="Codigo de topografia")
    descripcion = models.TextField(null=False,blank =False, unique=True, help_text="descripcion de topografia")
    def __str__(self):
        return '%s - %s' % (self.codigo, self.descripcion)
    
class Acceso(models.Model):
    codigo = models.TextField(null=False,blank =False, unique=True, help_text="Codigo de Acceso")
    descripcion = models.TextField(null=False,blank =False, unique=True, help_text="descripcion de Acceso")
    def __str__(self):
        return '%s - %s' % (self.codigo, self.descripcion)
    
class Forma(models.Model):
    codigo = models.TextField(null=False,blank =False, unique=True, help_text="Codigo de Forma")
    descripcion = models.TextField(null=False,blank =False, unique=True, help_text="descripcion de Forma")
    def __str__(self):
        return '%s - %s' % (self.codigo, self.descripcion)
    
class Ubicacion(models.Model):
    codigo = models.TextField(null=False,blank =False, unique=True, help_text="Codigo de Ubicacion")
    descripcion = models.TextField(null=False,blank =False, unique=True, help_text="descripcion de Ubicacion")
    def __str__(self):
        return '%s - %s' % (self.codigo, self.descripcion)
    
class Uso(models.Model):
    codigo = models.TextField(null=False,blank =False, unique=True, help_text="Codigo de Uso")
    descripcion = models.TextField(null=False,blank =False, unique=True, help_text="descripcion de Uso")
    def __str__(self):
        return '%s - %s' % (self.codigo, self.descripcion)
    
class Regimen(models.Model):
    codigo = models.TextField(null=False,blank =False, unique=True, help_text="Codigo de Regimen")
    descripcion = models.TextField(null=False,blank =False, unique=True, help_text="descripcion de Regimen")
    def __str__(self):
        return '%s - %s' % (self.codigo, self.descripcion)
    
class Servicios(models.Model):
    codigo = models.TextField(null=False,blank =False, unique=True, help_text="Codigo de Servicio")
    descripcion = models.TextField(null=False,blank =False, unique=True, help_text="descripcion de Servicio")
    def __str__(self):
        return '%s - %s' % (self.codigo, self.descripcion)
    
class Tipologia(models.Model):
    codigo = models.TextField(null=False,blank =False, unique=True, help_text="Codigo de tipologia")
    descripcion = models.TextField(null=False,blank =False, unique=True, help_text="descripcion de tipologia")
    def __str__(self):
        return '%s - %s' % (self.codigo, self.descripcion)
    
class FinesFiscales(models.Model):
    codigo = models.TextField(null=False,blank =False, unique=True, help_text="Codigo de fines fiscales")
    descripcion = models.TextField(null=False,blank =False, unique=True, help_text="descripcion de fines fiscales")
    def __str__(self):
        return '%s - %s' % (self.codigo, self.descripcion)
    
class TipoDesincorporacion(models.Model):
    codigo = models.TextField(null=False,blank =False, unique=True, help_text="Codigo de tipo desincorporacion")
    descripcion = models.TextField(null=False,blank =False, unique=True, help_text="descripcion del tipo de desincorporacion")
    def __str__(self):
        return '%s - %s' % (self.codigo, self.descripcion)
    
class TipoTransaccion(models.Model):
    codigo = models.TextField(null=False,blank =False, unique=True, help_text="Codigo de tipo transaccion")
    descripcion = models.TextField(null=False,blank =False, unique=True, help_text="descripcion del tipo de transaccion")
    def __str__(self):
        return '%s - %s' % (self.codigo, self.descripcion)
    
class Zona(models.Model):
    codigo = models.TextField(null=False,blank =False, unique=True, help_text="Codigo de Zona")
    descripcion = models.TextField(null=False,blank =False, unique=True, help_text="descripcion de la Zona")
    def __str__(self):
        return '%s - %s' % (self.codigo, self.descripcion)
    
# Maestro de Propietarios/Contribuyentes
class Propietario(models.Model):
    tipo_documento  = models.TextField(null=False,blank =False, unique=False, help_text="Numero de expediente")
    nacionalidad  = models.TextField(null=False,blank =False, unique=False, help_text="Numero de expediente")
    numero_documento  = models.TextField(null=False,blank =False, unique=True, help_text="Numero de expediente")
    nombre  = models.TextField(null=False,blank =False, unique=False, help_text="Numero de expediente")
    telefono_principal  = models.TextField(null=False,blank =False, unique=False, help_text="Numero de expediente")
    telefono_secundario   = models.TextField(null=True,blank =True, help_text="Numero de expediente")
    email_principal  = models.TextField(null=False,blank =False, unique=False, help_text="Numero de expediente")
    emaill_secundario  = models.TextField(null=True,blank =True, help_text="Numero de expediente")
    def __str__(self):
        return '%s - %s' % (self.numero_documento, self.nombre)
    
class Inmueble(models.Model):
    numero_expediente = models.TextField(null=False,blank =False, unique=True, help_text="Numero de expediente")
    fecha_inscripcion = models.DateField(blank=True,null=True, help_text="fecha de inscripcion")
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
    def __str__(self):
        return '%s' % (self.numero_expediente)

class InmueblePropiedad(models.Model):
    inmueble = models.ForeignKey (Inmueble, on_delete=models.PROTECT,help_text="Sector asociado")
    tipo_documento = models.ForeignKey (TipoDocumento, on_delete=models.PROTECT,help_text="Sector asociado")
    tipo_especial = models.ForeignKey (TipoEspecial, on_delete=models.PROTECT,help_text="Sector asociado")
    fecha_habitabilidad	= models.DateField(blank=True, help_text="fecha_habitabilidad")
    tipo_tenencia = models.ForeignKey (TipoTenencia, on_delete=models.PROTECT,help_text="tipo_tenencia asociado")
    fecha_vigencia = models.DateField(blank=True, help_text="fecha de inscripcion")
    fecha_documento	= models.DateField(blank=True, help_text="fecha de inscripcion")
    numero_documento = models.TextField(null=False,blank =False, unique=True, help_text="Numero de expediente")
    matricula_documento	= models.TextField(null=True,blank =True, help_text="Numero de expediente")
    anio_folio_documento = models.TextField(null=True,blank =True, help_text="Numero de expediente")
    fecha_terreno = models.DateField(blank=True, help_text="fecha de inscripcion")
    numero_terreno = models.TextField(null=True,blank =True, help_text="Numero de expediente")
    folio_terreno = models.TextField(null=True,blank =True, help_text="Numero de expediente")
    protocolo_terreno = models.TextField(null=True,blank =True, help_text="Numero de expediente")
    tomo_terreno = models.TextField(null=True,blank =True, help_text="Numero de expediente")
    area_terreno =  models.DecimalField(max_digits=14, decimal_places=2, default=Decimal(0.0), null=False, help_text="area_terreno en m2")
    valor_terreno = models.TextField(null=True,blank =True, help_text="Numero de expediente")
    fecha_construccion = models.DateField(blank=True, help_text="fecha de inscripcion")
    numero_construccion	= models.TextField(null=True,blank =True, help_text="Numero de expediente")
    folio_construccion = models.TextField(null=True,blank =True, help_text="Numero de expediente")
    protocolo_construccion = models.TextField(null=True,blank =True, help_text="Numero de expediente")
    tomo_construccion = models.TextField(null=True,blank =True, help_text="Numero de expediente")
    area_construccion =  models.DecimalField(max_digits=14, decimal_places=2, default=Decimal(0.0), null=False, help_text="area_construccion en m2")
    lindero_norte = models.TextField(null=True,blank =True, help_text="Numero de expediente")
    lindero_sur	= models.TextField(null=True,blank =True, help_text="Numero de expediente")
    lindero_este = models.TextField(null=True,blank =True, help_text="Numero de expediente")
    lindero_oeste = models.TextField(null=True,blank =True, help_text="Numero de expediente")
    def __str__(self):
        return '%s' % (self.inmueble.numero_expediente)

class InmueblePropietarios(models.Model):
    inmueble = models.ForeignKey (Inmueble, on_delete=models.PROTECT,help_text="Id Inmueble")
    propietario = models.ForeignKey (Propietario, on_delete=models.PROTECT,help_text="Id Propietario")
    def __str__(self):
        return '%s - %s' % (self.inmueble.numero_expediente,self.propietario.nombre)

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
    observaciones = models.TextField(null=True,blank =True, help_text="Observaciones")
    def __str__(self):
        return '%s' % (self.inmueble.numero_expediente)
    
class InmuebleTerrenoTopografia(models.Model):
    inmueble_terreno = models.ForeignKey (InmuebleTerreno, on_delete=models.PROTECT,help_text="Inmueble asociado")
    topografia = models.ForeignKey (Topografia, on_delete=models.PROTECT,help_text="Topografia asociado")
    
class InmuebleTerrenoAcceso(models.Model):
    inmueble_terreno = models.ForeignKey (InmuebleTerreno, on_delete=models.PROTECT,help_text="Inmueble asociado")
    acceso = models.ForeignKey (Acceso, on_delete=models.PROTECT,help_text="Acceso asociado")
    def __str__(self):
        return '%s' % (self.inmueble.numero_expediente)
    	
class InmuebleTerrenoUso(models.Model):
    inmueble_terreno = models.ForeignKey (InmuebleTerreno, on_delete=models.PROTECT,help_text="Inmueble asociado")
    uso = models.ForeignKey (Uso, on_delete=models.PROTECT,help_text="uso asociado")
    def __str__(self):
        return '%s' % (self.inmueble.numero_expediente)
    	
class InmuebleTerrenoRegimen(models.Model):
    inmueble_terreno = models.ForeignKey (InmuebleTerreno, on_delete=models.PROTECT,help_text="Inmueble asociado")
    regimen	= models.ForeignKey (Regimen, on_delete=models.PROTECT,help_text="regimen asociado")
    def __str__(self):
        return '%s' % (self.inmueble.numero_expediente)

class UsoConstruccion(models.Model):
    codigo = models.TextField(null=False,blank =False, unique=True, help_text="Codigo de UsoConstruccion")
    descripcion = models.TextField(null=False,blank =False, unique=True, help_text="descripcion de UsoConstruccion")
    def __str__(self):
        return '%s - %s' % (self.codigo, self.descripcion)
    
class Soporte(models.Model):
    codigo = models.TextField(null=False,blank =False, unique=True, help_text="Codigo de Soporte")
    descripcion = models.TextField(null=False,blank =False, unique=True, help_text="descripcion de Soporte")

class Techo(models.Model):
    codigo = models.TextField(null=False,blank =False, unique=True, help_text="Codigo de Techo")
    descripcion = models.TextField(null=False,blank =False, unique=True, help_text="descripcion de Techo")
    def __str__(self):
        return '%s - %s' % (self.codigo, self.descripcion)
    
class Cubierta(models.Model):
    codigo = models.TextField(null=False,blank =False, unique=True, help_text="Codigo de Cubierta")
    descripcion = models.TextField(null=False,blank =False, unique=True, help_text="descripcion de Cubierta")
    def __str__(self):
        return '%s - %s' % (self.codigo, self.descripcion)
    
class TipoPared(models.Model):
    codigo = models.TextField(null=False,blank =False, unique=True, help_text="Codigo de TipoPared")
    descripcion = models.TextField(null=False,blank =False, unique=True, help_text="descripcion de TipoPared")
    def __str__(self):
        return '%s - %s' % (self.codigo, self.descripcion)
    
class AcabadoPared(models.Model):
    codigo = models.TextField(null=False,blank =False, unique=True, help_text="Codigo de AcabadoPared")
    descripcion = models.TextField(null=False,blank =False, unique=True, help_text="descripcion de AcabadoPared")
    def __str__(self):
        return '%s - %s' % (self.codigo, self.descripcion)
    
class Conservacion(models.Model):
    codigo = models.TextField(null=False,blank =False, unique=True, help_text="Codigo de Conservacion")
    descripcion = models.TextField(null=False,blank =False, unique=True, help_text="descripcion de Conservacion")
    def __str__(self):
        return '%s - %s' % (self.codigo, self.descripcion)
    

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
    porcentaje_refaccion = models.TextField(null=True,blank =True, help_text="Numero de expediente")
    edad_efectiva = models.TextField(null=True,blank =True, help_text="edad_efectiva")
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
    observaciones = models.TextField(null=True,blank =True, help_text="observaciones")

class InmuebleValoracionConstruccion(models.Model):
    inmueble_terreno = models.ForeignKey (InmuebleValoracionTerreno, on_delete=models.PROTECT,help_text="Id inmueble_terreno asociado")
    tipologia = models.ForeignKey (Tipologia, on_delete=models.PROTECT,help_text="tipologia asociado")
    fecha_compra = models.DateField(blank=True, help_text="fecha_compra")
    trimestre = models.PositiveIntegerField(default=0,help_text="trimestre")
    anio = models.PositiveIntegerField(default=0, help_text="Numero de expediente")
    area = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal(0.0), null=False, help_text="Area en m2")
    valor = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal(0.0), null=False, help_text="valor")
    depreciacion = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal(0.0), null=False, help_text="depreciacion")
    observaciones = models.TextField(null=True,blank =True, help_text="observaciones")

class InmuebleUbicacion(models.Model):
    inmueble = models.ForeignKey (Inmueble, on_delete=models.PROTECT,help_text="Id Inmueble asociado")
    lindero_norte = models.TextField(null=True,blank =True, help_text="Numero de expediente")
    lindero_sur = models.TextField(null=True,blank =True, help_text="Numero de expediente")
    lindero_este = models.TextField(null=True,blank =True, help_text="Numero de expediente")
    lindero_oeste = models.TextField(null=True,blank =True, help_text="Numero de expediente")
    imagen_inmueble = models.ImageField(upload_to='media/paises', null=True, blank=True, help_text="Imagen asociado al pais")
    imagen_plano = models.ImageField(upload_to='media/paises', null=True, blank=True, help_text="Imagen asociado al pais")
    imagan_plano_mesura =models.ImageField(upload_to='media/paises', null=True, blank=True, help_text="Imagen asociado al pais")
    g1_norte = models.TextField(null=True,blank =True, help_text="Numero de expediente")
    g1_este = models.TextField(null=True,blank =True, help_text="Numero de expediente")
    g2_norte = models.TextField(null=True,blank =True, help_text="Numero de expediente")
    g2_este = models.TextField(null=True,blank =True, help_text="Numero de expediente")
    g3_norte = models.TextField(null=True,blank =True, help_text="Numero de expediente")
    g3_este = models.TextField(null=True,blank =True, help_text="Numero de expediente")
    g4_norte = models.TextField(null=True,blank =True, help_text="Numero de expediente")
    g4_este = models.TextField(null=True,blank =True, help_text="Numero de expediente")
    g5_norte = models.TextField(null=True,blank =True, help_text="Numero de expediente")
    g5_este = models.TextField(null=True,blank =True, help_text="Numero de expediente")
    g6_norte = models.TextField(null=True,blank =True, help_text="Numero de expediente")
    g6_este = models.TextField(null=True,blank =True, help_text="Numero de expediente")
    g7_norte = models.TextField(null=True,blank =True, help_text="Numero de expediente")
    g7_este = models.TextField(null=True,blank =True, help_text="Numero de expediente")
    g8_norte = models.TextField(null=True,blank =True, help_text="Numero de expediente")
    g8_este = models.TextField(null=True,blank =True, help_text="Numero de expediente")

class InmuebleFaltante(models.Model):
    inmueble = models.ForeignKey (Inmueble, on_delete=models.PROTECT,help_text="Id Inmueble asociado")
    cedula = models.TextField(null=True,blank =True,help_text="Numero de expediente")
    documentopropiedad = models.TextField(null=True,blank =True, help_text="Numero de expediente")
    observaciones = models.TextField(null=True,blank =True,help_text="observaciones")



## Histoial de Actualizacion de precios de Tasa BS
class TasaBCV(models.Model):
    fecha = models.DateField(blank=True, help_text="Fecha Actualizacion TASA")
    fecha_vigente= models.DateField(blank=True, help_text=" A partir de esta fecha se aplica los calculos")
    monto  = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal(0.0), null=False,  help_text="Monto TASA")
    habilitado = models.BooleanField(default=True, help_text="Esta activo?")
    def __str__(self):
        return '%s - %s' % (self.monto, self.fecha)
## Histoial de Actualizacion de precios de UT
class UnidadTributaria(models.Model):
    fecha = models.DateField(blank=True, help_text="Fecha Actualizacion Unidad Tributaria")
    fecha_vigente= models.DateField(blank=True, help_text=" A partir de esta fecha se aplica los calculos")
    monto  = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal(0.0), null=False,  help_text="Monto Unidad tributaria")
    habilitado = models.BooleanField(default=True, help_text="Esta activo?")
    def __str__(self):
        return '%s - %s' % (self.monto, self.fecha)
    
## moneda para calculo : ejemplo Petro
class Moneda(models.Model):
    descripcion  = models.TextField(null=False,blank =False, unique=True, help_text="Descripcion de la Moneda")
    habilitado = models.BooleanField(default=True, help_text="Esta activo?")
    def __str__(self):
        return '%s' % (self.descripcion)
    
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
    def __str__(self):
        return '%s - %s' % (self.tipo, self.descripcion)

#Maestro de tipos de pago
class TipoFlujo(models.Model):
    descripcion  = models.TextField(null=False,blank =False, unique=True, help_text="Descripcion Tipo de pago")
    def __str__(self):
        return '%s' % (self.descripcion)

class EstadoCuenta(models.Model):
    numero = models.TextField(null=False,blank =False, unique=True, help_text="Numero de Estado de Cuenta")
    inmueble = models.ForeignKey (Inmueble, null=True,blank =True,on_delete=models.PROTECT,help_text="Id Inmueble asociado")
    tipoflujo = models.ForeignKey(TipoFlujo, null=True,blank =True,on_delete=models.PROTECT,help_text="Tipo de flujo (solo catasrro: inscripcion, actualizacion o modificar propietario")
    fecha = models.DateTimeField(blank=True, help_text="Fecha Estado Cuenta")
    propietario=models.ForeignKey(Propietario, on_delete=models.PROTECT,help_text="Contribuyente/Propietario asociado")
    observaciones = models.TextField(null=True,blank =True, help_text="observaciones")
    valor_petro  = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal(0.0), null=False, help_text="total")
    valor_tasa_bs = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal(0.0), null=False, help_text="total")
    monto_total  = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal(0.0), null=False, help_text="monto total")
    habilitado = models.BooleanField(default=True, help_text="Esta activo?")
    def __str__(self):
        return '%s - %s - %s' % (self.numero,self.propietario.nombre,self.tipoflujo)
    
class EstadoCuentaDetalle(models.Model):
    estadocuenta = models.ForeignKey(EstadoCuenta, on_delete=models.PROTECT,help_text="ID Cabecera Estado de Cuenta")
    tasamulta = models.ForeignKey(TasaMulta, on_delete=models.PROTECT,help_text="Id Tasa Multa")
    monto_unidad_tributaria  = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal(0.0), null=False,  help_text="Monto Unidad tributaria")	
    monto_tasa  = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal(0.0), null=False,  help_text="Monto total del renglon tasa(monto_unidad_tributaria * cantidad)")	
    cantidad  = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal(0.0), null=False, help_text="Cantidad Unidad tributaria")
    def __str__(self):
        return '%s - %s' % (self.estadocuenta.numero,self.tasamulta)
class Liquidacion(models.Model):
    estadocuenta = models.ForeignKey(EstadoCuenta,null=True,blank=True, on_delete=models.PROTECT,help_text="ID Cabecera Estado de Cuenta")
    numero = models.TextField(null=False,blank =False, unique=True, help_text="Numero de Liquidacion")
    inmueble = models.ForeignKey (Inmueble, null=True,blank =True,on_delete=models.PROTECT,help_text="Id Inmueble asociado")
    tipoflujo = models.ForeignKey(TipoFlujo, null=True,blank =True,on_delete=models.PROTECT,help_text="Tipo de flujo solo catasrro: inscripcion, actualizacion o modificar propietario")
    fecha = models.DateTimeField(blank=True, help_text="Fecha Estado Cuenta")
    propietario=models.ForeignKey(Propietario, on_delete=models.PROTECT,help_text="Contribuyente/Propietario asociado")
    observaciones = models.TextField(null=True,blank =True, help_text="observaciones")
    valor_petro  = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal(0.0), null=False, help_text="total")
    valor_tasa_bs = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal(0.0), null=False, help_text="total")
    monto_total  = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal(0.0), null=False, help_text="total")
    habilitado = models.BooleanField(default=True, help_text="Se muestra la liquidacion?")

    def __str__(self):
        return '%s - %s - %s' % (self.numero,self.propietario.nombre,self.tipoflujo)
    
class LiquidacionDetalle(models.Model):
    liquidacion = models.ForeignKey(Liquidacion, on_delete=models.PROTECT,help_text="ID Cabecera liquidacion")
    tasamulta = models.ForeignKey(TasaMulta, on_delete=models.PROTECT,help_text="Id Tasa Multa")
    monto_unidad_tributaria  = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal(0.0), null=False,  help_text="Monto Unidad tributaria")	
    monto_tasa  = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal(0.0), null=False,  help_text="Monto total del renglon tasa(monto_unidad_tributaria * cantidad)")	
    cantidad  = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal(0.0), null=False, help_text="Cantidad Unidad tributaria")
    def __str__(self):
        return '%s - %s' % (self.liquidacion.numero,self.tasamulta)

#Maestro de tipos de pago
class TipoPago(models.Model):
    descripcion  = models.TextField(null=False,blank =False, unique=True, help_text="Descripcion Tipo de pago")
    def __str__(self):
        return '%s' % (self.descripcion)

   
class Banco(models.Model):
    descripcion  = models.TextField(null=False,blank =False, unique=True, help_text="Nombre del banco")
    def __str__(self):
        return '%s' % (self.descripcion)

class BancoCuenta(models.Model):
    banco = models.ForeignKey(Banco, on_delete=models.PROTECT,help_text="ID Banco")
    numero  = models.TextField(null=False,blank =False, unique=True, help_text="Numero de Cuenta")
    TIPO = (
        ('1', 'Corriente'),
        ('2', 'Ahorro'),
    )
    tipo= models.CharField(max_length=1, choices=TIPO, default='1', help_text='Tipo de Cuenta')
    def __str__(self):
        return '%s - %s - %s' % (self.banco.descripcion,self.numero,self.tipo)


#Maestro de recibo Pago
class PagoEstadoCuenta(models.Model):
    numero = models.TextField(null=False,blank =False, unique=True, help_text="Numero de pago")
    liquidacion = models.ForeignKey(Liquidacion, on_delete=models.PROTECT,help_text="ID Cabecera liquidacion")
    fecha = models.DateTimeField(blank=True, help_text="Fecha Estado Cuenta")
    observaciones = models.TextField(null=True,blank =True, help_text="observaciones")
    monto  = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal(0.0), null=False, help_text="total")
    def __str__(self):
        return '%s - %s' % (self.numero,self.liquidacion)
    
#Detalle de recibo Pago
class PagoEstadoCuentaDetalle(models.Model):
    pagoestadocuenta = models.ForeignKey(PagoEstadoCuenta, on_delete=models.PROTECT,help_text="ID Cabecera PAGO")
    tipopago = models.ForeignKey(TipoPago, on_delete=models.PROTECT,help_text="Id Tipo Pago")
    monto  = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal(0.0), null=False,  help_text="Monto del pago")	
    bancocuenta = models.ForeignKey(BancoCuenta,null=True,blank =True, on_delete=models.PROTECT,help_text="ID Banco")
    nro_referencia = models.TextField(null=True,blank =True,  help_text="numero de referencia")
    fechapago = models.DateTimeField(blank=True, help_text="Fecha pago")
    
# tabla dee control para manejo de correlativos
class Correlativo(models.Model):
    ExpedienteCatastro = models.PositiveIntegerField(null=True, blank=True,  help_text="Numero de Expediente de Catastro")	
    NumeroEstadoCuenta = models.PositiveIntegerField(null=True, blank=True,  help_text="Numero de Estado de Cuenta")
    NumeroLiquidacion = models.PositiveIntegerField(null=True, blank=True,  help_text="Numero de NumeroLiquidacion")
    NumeroPago = models.PositiveIntegerField(null=True, blank=True,  help_text="Numero de Recibo de pagos")

# Caranday ver 1.0
class Flujo(models.Model):
    inmueble=models.ForeignKey(Inmueble, on_delete=models.PROTECT,help_text="Inmueble")
    pagoestadocuenta = models.ForeignKey(PagoEstadoCuenta, on_delete=models.PROTECT,help_text="ID Cabecera PAGO")
    fecha = models.DateTimeField(blank=True,null=True, help_text="Fecha creacion")
    ESTADO = (
        ('1', 'En Proceso'),
        ('2', 'Cerrado'),
    )
    estado= models.CharField(max_length=1, choices=ESTADO, default='1', help_text='Estado dela solicitud')
    def __str__(self):
        return '%s - %s - %s' % (self.inmueble,self.pagoestadocuenta,self.estado)

class FlujoDetalle(models.Model):
    flujo = models.ForeignKey(Flujo, on_delete=models.PROTECT,help_text="ID Cabecera PAGO")
    ESTADO = (
        ('1', 'Pendiente por Recibir'),
        ('2', 'Recibido'),
        ('3', 'Pendiente por Procesar'),
        ('4', 'En proceso'),
        ('5', 'Proceso Culminado'),
        ('6', 'Pendiente por Enviar'),
        ('7', 'Enviado'),
        ('8', 'Finalizado'),
        ('9', 'Fin de la Solicitud'),
        ('0', 'Pendiente por Re-Enviar')
    )
    TAREA = (
        ('1', 'Pendiente por Recibir'),
        ('3', 'Pendiente por Procesar'),
        ('6', 'Pendiente por Enviar'),
        ('7', 'Devuelto'),
        ('8', 'Finalizado'),
    )
    estado= models.CharField(max_length=1, choices=ESTADO, default='1', help_text='Estado del proceso')
    tarea= models.CharField(max_length=1, choices=TAREA, default='1', help_text='Estado del proceso')
    
    envia_usuario  = models.ForeignKey(User, on_delete=models.CASCADE, help_text="usuario asociado",related_name='FujoDetalle_envia_usuario')
    envia_fecha = models.DateTimeField(blank=True,null=True, help_text="Fecha enviado")
    
    recibe_usuario  = models.ForeignKey(User,blank=True,null=True, on_delete=models.CASCADE, help_text="usuario asociado",related_name='FujoDetalle_recibe_usuario')
    recibe_fecha = models.DateTimeField(blank=True,null=True, help_text="Fecha recepcion")
    
    #usuario_envia   = models.ForeignKey(Perfil, blank=True,null=True,on_delete=models.CASCADE, help_text="usuario envia", related_name='FlujoDetalle_usuario_envia')
    #usuario_recibe  = models.ForeignKey(Perfil, blank=True,null=True,on_delete=models.CASCADE, help_text="usuario recibe",related_name='FlujoDetalle_usuario_recibe')
    departamento_envia   = models.ForeignKey(Departamento, blank=True,null=True,on_delete=models.CASCADE, help_text="Departamento envia", related_name='FlujoDetalle_departamento_envia')
    departamento_recibe  = models.ForeignKey(Departamento, blank=True,null=True,on_delete=models.CASCADE, help_text="Departamento recibe",related_name='FlujoDetalle_departamento_recibe')
    
    inicio_proceso_usuario  = models.ForeignKey(User,blank=True,null=True, on_delete=models.CASCADE, help_text="usuario asociado",related_name='FujoDetalle_inicio_proceso_usuario')
    inicio_proceso_fecha = models.DateTimeField(blank=True,null=True, help_text="Fecha Inicio de proceso")
    
    procesa_usuario  = models.ForeignKey(User,blank=True,null=True, on_delete=models.CASCADE, help_text="usuario asociado",related_name='FujoDetalle_procesa_usuario')
    procesa_fecha = models.DateTimeField(blank=True,null=True, help_text="Fecha FIN de proceso")
    
    fin_usuario  = models.ForeignKey(User, blank=True,null=True,on_delete=models.CASCADE, help_text="usuario asociado",related_name='FujoDetalle_fin_usuario')
    fin_fecha = models.DateTimeField(blank=True,null=True, help_text="Fecha FIN DE LA SOLICITUD")

    observaciones = models.TextField(null=True,blank =True, help_text="observaciones")

    def save(self, *args, **kwargs):
        if not self.procesa_fecha:
           self.procesa_fecha = timezone.now()
        if self.estado=='2':
           self.recibe_fecha = timezone.now()
        if self.estado=='4':
           self.inicio_proceso_fecha = timezone.now()
        if self.estado=='5':
           self.procesa_fecha = timezone.now()
        if self.estado=='7':
           self.envia_fecha = timezone.now()
        if self.estado=='9':
           self.fin_fecha = timezone.now()
        super().save(*args, **kwargs)
