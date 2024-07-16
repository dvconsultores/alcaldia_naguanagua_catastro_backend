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
from .storage_backends import PrivateMediaStorage


def logos_path(filename):
    return "logos/{0}".format(filename)

def excel_path(instance, filename):
    return "excel_files/{0}".format(filename)

def immuebles_path(instance, filename):
    return "immueble_{0}/imgs/{1}".format(instance.id, filename)

def immuebles_path_doc(instance, filename):
    return "immueble_{0}/docs/{1}".format(instance.id, filename)

def immuebles_path_ficha(instance, filename):
    return "immueble_{0}/ficha/{1}".format(instance.id, filename)
def immuebles_path_desincopora(instance, filename):
    return "immueble_{0}/desincopora/{1}".format(instance.id, filename)

def estadocuenta_path(instance, filename):
    return "estadocuenta_{0}/pdf/{1}".format(instance.id, filename)

def liquidacion_path(instance, filename):
    return "liquidacion_{0}/pdf/{1}".format(instance.id, filename)

def pagoestadocuenta_path(instance, filename):
    return "pagoestadocuenta_{0}/pdf/{1}".format(instance.id, filename)   

def correcciones_path(instance, filename):
    return "IC_impuestocorrecciones{0}/imgs/{1}".format(instance.id, filename)

def flujo_path(instance, filename):
    return "flujo_{0}/docs/{1}".format(instance.id, filename)

def flujoentrega_path(instance, filename):
    return "flujo_{0}/entrega/{1}".format(instance.id, filename)

class Departamento(models.Model):
    nombre = models.CharField(max_length=255, null=False, blank=False, primary_key=True, help_text="Nombre Depatamento para usuario de catastro FLUJO")
    APLICA = (
        ('C', 'Inmuebles Urbanos'),
        ('A', 'Actividades económicas'),
        ('V', 'Vehiculos'),
        ('P', 'Propaganda y publicidad'),
        ('X', 'Todos')
    )
    aplica= models.CharField(max_length=1, choices=APLICA, default='X', help_text='A que tipo de sector aplica')   
    finaliza_flujo = models.BooleanField(default=False, help_text="Es TRUE si finaliza flujos")
    imprime_recibo_entrega = models.BooleanField(default=False, help_text="Es TRUE si Imprime recibo de entrega a contribuyente (para expediente)")
  
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
    caja = models.PositiveIntegerField(null=True, blank=True,  help_text="Numero de Caja en caso que el perfil sea de cajero")
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
        return '%s (Permiso: %s-%s-%s-%s - Leer:%s Borrar:%s Actualizar:%s Escribir:%s)' % (self.perfil.usuario.username, self.modulo.es_menu, self.modulo.menu, self.modulo.titulo, self.modulo.nombre, self.leer, self.borrar, self.actualizar, self.escribir)
    class Meta:
         ordering = ['perfil__usuario__username','modulo__menu', '-modulo__es_menu', '-modulo__titulo']

class Ambito(models.Model):
    codigo = models.TextField(null=False,blank =False, unique=True, help_text="Codigo del ambito")
    descripcion = models.TextField(null=False,blank =False, unique=False, help_text="Descripcion del ambito")
    class Meta:
        indexes = [
            models.Index(fields=['codigo']),
        ]
    def __str__(self):
        return '%s - %s' % (self.codigo, self.descripcion)
    
class Sector(models.Model):
    CLASIFICACION = (
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D'),
        ('E', 'E')
    )
    ambito=models.ForeignKey(Ambito,on_delete=models.PROTECT,help_text="ambito asociado")
    codigo = models.TextField(null=False,blank =False, help_text="Codigo del Sector")
    descripcion = models.TextField(null=False,blank =False, unique=False, help_text="Descripcion del Sector")
    area = models.DecimalField(max_digits=22, decimal_places=8, default=Decimal(0.0), null=False, help_text="Area en m2")
    perimetro = models.TextField(null=True,blank =True, help_text="Descripcion del Sector")
    clasificacion= models.CharField(max_length=1, choices=CLASIFICACION, default='A', help_text='clasificacion del Sector')
    def __str__(self):
        return '%s - %s - %s' % (self.ambito.codigo,self.codigo, self.descripcion)

    class Meta:
        unique_together = ('ambito', 'codigo')
        ordering = ['ambito','codigo']
        indexes = [
            models.Index(fields=['codigo']),
        ]

class Calle(models.Model):
    TIPO = (
        ('1', 'Una Via'),
        ('2', 'Doble Via'),
        ('3', 'Colateral'),
        ('4', 'Arterial')
    )
    nombre = models.TextField(null=False,blank =False, unique=False, help_text="Nombre de la calle")
    tipo= models.CharField(max_length=1, choices=TIPO, default='1', help_text='tipo calle')
    class Meta:
        indexes = [
            models.Index(fields=['nombre']),
        ]
    def __str__(self):
        return '%s - %s' % (self.tipo, self.nombre)
    
class Avenida(models.Model):
    TIPO = (
        ('1', 'Una Via'),
        ('2', 'Doble Via'),
        ('3', 'Colateral'),
        ('4', 'Arterial')
    )
    nombre = models.TextField(null=False,blank =False, help_text="Nombre de la avenida")
    tipo= models.CharField(max_length=1, choices=TIPO, default='1', help_text='tipo de avenida')
    class Meta:
        indexes = [
            models.Index(fields=['nombre']),
        ]
    def __str__(self):
        return '%s - %s' % (self.tipo, self.nombre)
    
class Zona(models.Model):
    codigo = models.TextField(null=False,blank =False, unique=True, help_text="Codigo de Zona")
    descripcion = models.TextField(null=False,blank =False, unique=True, help_text="descripcion de la Zona")
    class Meta:
        indexes = [
            models.Index(fields=['codigo']),
        ]
    def __str__(self):
        return '%s - %s' % (self.codigo, self.descripcion)

class Categorizacion(models.Model):
    codigo = models.TextField(null=False,blank =False, unique=True, help_text="Codigo de Categorizacion Ordenanza 2024")
    descripcion = models.TextField(null=False,blank =False, unique=True, help_text="descripcion de la Categorizacion Ordenanza 2024")
    class Meta:
        indexes = [
            models.Index(fields=['codigo']),
        ]
    def __str__(self):
        return '%s - %s' % (self.codigo, self.descripcion)

class Urbanizacion(models.Model):
    TIPO = (
        ('P', 'Publica'),
        ('R', 'Privada'),
    )
    sector=models.ForeignKey(Sector,on_delete=models.PROTECT,help_text="Sector asociado")
    nombre = models.TextField(null=False,blank =False, help_text="Nombre de la urbanizacion")
    tipo= models.CharField(max_length=1, choices=TIPO, default='P', help_text='tipo de la urbanizacion')
    zona = models.ForeignKey(Zona,on_delete=models.PROTECT, null=True,blank =True,help_text="Zona !! Base para calculo")      
    def __str__(self):
        return '%s -%s - %s' % (self.nombre,self.sector.codigo,self.sector.ambito.codigo)
    class Meta:
        unique_together = ('sector', 'nombre')
        ordering = ['sector','nombre']
        indexes = [
            models.Index(fields=['nombre']),
        ]

class Manzana(models.Model):
    sector=models.ForeignKey(Sector,on_delete=models.PROTECT,help_text="Sector asociado")
    codigo = models.TextField(null=False,blank =False, help_text="Codigo de la Manzana")
    def __str__(self):
        return '%s - %s' % (self.sector.codigo,self.codigo)  
    class Meta:
        unique_together = ('sector', 'codigo')
        ordering = ['sector','codigo']
        indexes = [
            models.Index(fields=['codigo']),
        ]
   
class Parcela(models.Model):
    sector=models.ForeignKey(Sector,null=True,blank =True,on_delete=models.PROTECT,help_text="Sector asociado.")
    codigo = models.TextField(null=False,blank =False, help_text="Codigo de la Parcela")
    def __str__(self):
        return '%s - %s - %s ' % (self.sector.codigo,self.sector.ambito.codigo,self.codigo)
    class Meta:
        unique_together = ('sector', 'codigo')
        ordering = ['sector','codigo'] 
        indexes = [
            models.Index(fields=['codigo']),
        ]

class SubParcela(models.Model):
    parcela=models.ForeignKey(Parcela,on_delete=models.PROTECT,help_text="Parcela asociado")
    codigo = models.TextField(null=False,blank =False, help_text="Codigo de la SubParcela")
    def __str__(self):
        return '%s - %s - %s - %s ' % (self.parcela.codigo,self.parcela.sector.codigo,self.parcela.sector.ambito.codigo,self.codigo)
    class Meta:
        unique_together = ('parcela', 'codigo')
        ordering = ['parcela','codigo']
        indexes = [
            models.Index(fields=['codigo']),
        ]

class ConjuntoResidencial(models.Model):
    urbanizacion = models.ForeignKey(Urbanizacion,null=True,blank =True,on_delete=models.PROTECT,help_text="Urbanizacion/barrio asociada")
    sector=models.ForeignKey(Sector,null=True,blank =True,on_delete=models.PROTECT,help_text="Sector asociado.")
    #codigo = models.TextField(null=False,blank =False,  default='S-N',help_text="Codigo ConjuntoResidencial")
    nombre = models.TextField(null=False,blank =False, help_text="nombre del conjunto residencial")
    def __str__(self):
        return '%s -%s' % (self.sector.codigo,self.nombre) 
    class Meta:
        unique_together = ('sector', 'nombre')
        ordering = ['sector','nombre']
        indexes = [
            models.Index(fields=['nombre']),
        ]

class Edificio(models.Model):
    conjuntoresidencial = models.ForeignKey(ConjuntoResidencial,null=True,blank =True, on_delete=models.PROTECT,help_text="conjunto residencial asociado")
    urbanizacion = models.ForeignKey(Urbanizacion,null=True,blank =True, on_delete=models.PROTECT,help_text="Urbanizacion/barrio asociada")
    nombre = models.TextField(null=False,blank =False, help_text="nombre del Edificio")
    def __str__(self):
        return '%s -%s' % (self.urbanizacion.nombre,self.nombre)
    
    class Meta:
        unique_together = ('urbanizacion', 'nombre')
        ordering = ['urbanizacion','nombre']
        indexes = [
            models.Index(fields=['nombre']),
        ]
    
class Torre(models.Model):
    conjuntoresidencial = models.ForeignKey(ConjuntoResidencial,null=True,on_delete=models.PROTECT,help_text="conjunto residencial asociado")
    nombre = models.TextField(null=False,blank =False, help_text="nombre de la Torre")
    def __str__(self):
        return '%s -%s' % (self.conjuntoresidencial.nombre,self.nombre)
    class Meta:
        unique_together = ('conjuntoresidencial', 'nombre')
        ordering = ['conjuntoresidencial','nombre']
        indexes = [
            models.Index(fields=['nombre']),
        ]

class TipoInmueble(models.Model):
    codigo = models.TextField(null=False,blank =False, unique=True, help_text="Codigo del tipo de inmueble")
    descripcion = models.TextField(null=False,blank =False, unique=True, help_text="descripcion del tipo de inmueble")
    TIPO = (('U', 'Unifamiliar Residencial'), 
            ('M', 'Multifamiliar No residencial'))
    tipo = models.CharField(max_length=1, null=True, choices=TIPO, default='U', help_text="Requerido para cálculo de multas artículo 99 y 101")
    class Meta:
        indexes = [
            models.Index(fields=['codigo']),
        ]      
    def __str__(self):
        return 'Id:%s - Codigo:%s- Descripcion:%s- Tipo:%s' % (self.id,self.codigo,self.descripcion, self.tipo)
    
class EstatusInmueble(models.Model):
    codigo = models.TextField(null=False,blank =False, unique=True, help_text="Codigo del estatus de inmueble")
    descripcion = models.TextField(null=False,blank =False, unique=True, help_text="descripcion del estatus de inmueble")
    inmueble_activo = models.BooleanField(default=True, help_text="si es tru, este estatus permite procesar el inmueble para calculo de impuestos")
    class Meta:
        indexes = [
            models.Index(fields=['codigo']),
        ]
    def __str__(self):
        return '%s - %s' % (self.codigo, self.descripcion)
    
class NivelInmueble(models.Model):
    codigo = models.TextField(null=False,blank =False, unique=True, help_text="Codigo del nivel de inmueble")
    descripcion = models.TextField(null=False,blank =False, unique=True, help_text="descripcion del nivel de inmueble")
    def __str__(self):
        return '%s - %s' % (self.codigo, self.descripcion)
    class Meta:
        indexes = [
            models.Index(fields=['codigo']),
        ]
    
class UnidadInmueble(models.Model):
    codigo = models.TextField(null=False,blank =False, unique=True, help_text="Codigo de la unidad del inmueble")
    descripcion = models.TextField(null=False,blank =False, unique=True, help_text="descripcion de la unidad del inmueble")
    def __str__(self):
        return '%s - %s' % (self.codigo, self.descripcion)
    class Meta:
        indexes = [
            models.Index(fields=['codigo']),
        ]
    
class TipoDocumento(models.Model):
    codigo = models.TextField(null=False,blank =False, unique=True, help_text="Codigo del tipo de documento del inmueble")
    descripcion = models.TextField(null=False,blank =False, unique=True, help_text="descripcion del tipo de documento del inmueble")
    def __str__(self):
        return '%s - %s' % (self.codigo, self.descripcion)
    class Meta:
        indexes = [
            models.Index(fields=['codigo']),
        ]
    
class TipoEspecial(models.Model):
    codigo = models.TextField(null=False,blank =False, unique=True, help_text="Codigo del tipo especial del inmueble")
    descripcion = models.TextField(null=False,blank =False, unique=True, help_text="descripcion del tipo especial del inmueble")
    def __str__(self):
        return '%s - %s' % (self.codigo, self.descripcion)
    class Meta:
        indexes = [
            models.Index(fields=['codigo']),
        ]
    
class TipoTenencia(models.Model):
    codigo = models.TextField(null=False,blank =False, unique=True, help_text="Codigo del tipo tenecia del inmueble")
    descripcion = models.TextField(null=False,blank =False, unique=True, help_text="descripcion del tenecia especial del inmueble")
    def __str__(self):
        return '%s - %s' % (self.codigo, self.descripcion)
    class Meta:
        indexes = [
            models.Index(fields=['codigo']),
        ]
    
class Topografia(models.Model):
    codigo = models.TextField(null=False,blank =False, unique=True, help_text="Codigo de topografia")
    descripcion = models.TextField(null=False,blank =False, unique=True, help_text="descripcion de topografia")
    def __str__(self):
        return '%s - %s' % (self.codigo, self.descripcion)
    class Meta:
        indexes = [
            models.Index(fields=['codigo']),
        ]
    
class Acceso(models.Model):
    codigo = models.TextField(null=False,blank =False, unique=True, help_text="Codigo de Acceso")
    descripcion = models.TextField(null=False,blank =False, unique=True, help_text="descripcion de Acceso")
    def __str__(self):
        return '%s - %s' % (self.codigo, self.descripcion)
    class Meta:
        indexes = [
            models.Index(fields=['codigo']),
        ]
    
class Forma(models.Model):
    codigo = models.TextField(null=False,blank =False, unique=True, help_text="Codigo de Forma")
    descripcion = models.TextField(null=False,blank =False, unique=True, help_text="descripcion de Forma")
    def __str__(self):
        return '%s - %s' % (self.codigo, self.descripcion)
    class Meta:
        indexes = [
            models.Index(fields=['codigo']),
        ]
    
class Ubicacion(models.Model):
    codigo = models.TextField(null=False,blank =False, unique=True, help_text="Codigo de Ubicacion")
    descripcion = models.TextField(null=False,blank =False, unique=True, help_text="descripcion de Ubicacion")
    def __str__(self):
        return '%s - %s' % (self.codigo, self.descripcion)
    class Meta:
        indexes = [
            models.Index(fields=['codigo']),
        ]
    
class Uso(models.Model):
    codigo = models.TextField(null=False,blank =False, unique=True, help_text="Codigo de Uso")
    descripcion = models.TextField(null=False,blank =False, unique=True, help_text="descripcion de Uso")
    def __str__(self):
        return '%s - %s' % (self.codigo, self.descripcion)
    class Meta:
        indexes = [
            models.Index(fields=['codigo']),
        ]
    
class Regimen(models.Model):
    codigo = models.TextField(null=False,blank =False, unique=True, help_text="Codigo de Regimen")
    descripcion = models.TextField(null=False,blank =False, unique=True, help_text="descripcion de Regimen")
    def __str__(self):
        return '%s - %s' % (self.codigo, self.descripcion)
    class Meta:
        indexes = [
            models.Index(fields=['codigo']),
        ]
    
class Servicios(models.Model):
    codigo = models.TextField(null=False,blank =False, unique=True, help_text="Codigo de Servicio")
    descripcion = models.TextField(null=False,blank =False, unique=True, help_text="descripcion de Servicio")
    def __str__(self):
        return '%s - %s' % (self.codigo, self.descripcion)
    class Meta:
        indexes = [
            models.Index(fields=['codigo']),
        ]
    

#las tipologias USOS no se deben eliminar nunca, forman parte de la trazabilidad de los cálculos, tampoco de puede modificar
#los montos, si existe un cambio de cuota por una nueva ordenanza. se debe INHABILITAR y crear uno nuevo. y el deshabilitado
# se lo coloca la observacion de que pertenecia a la ordenza de fecha xxxx vigende hasta la fecha xx-xx-xxx
class Tipologia(models.Model):
    codigo = models.TextField(null=False,blank =False, unique=True, help_text="Codigo de tipologia")
    descripcion = models.TextField(null=False,blank =False, help_text="descripcion de tipologia")
    zona = models.ForeignKey(Zona,on_delete=models.PROTECT, null=True,blank =True,help_text="Zona !! Base para calculo")
    tarifa = models.DecimalField(max_digits=22, decimal_places=8, default=Decimal(0.0), null=False, help_text="Tarifa o Alicuota")
    habilitado = models.BooleanField(default=True, help_text="Esta activo?")
    observaciones = models.TextField(null=True,blank =True, help_text="observaciones en caso de no esar hablita por que cambio el valor a causa de una ordenanza nueva.")    
    FinesFiscales = models.BooleanField(default=False, help_text="True es para fines fiscales(para impresion de cedula catastral)")
    def __str__(self):
        return 'Id:%s - Zona:%s - Codigo:%s - Descripcion:%s' % (self.id,self.zona,self.codigo, self.descripcion)
    class Meta:
        indexes = [
            models.Index(fields=['codigo']),
        ]
    
class Tipologia_Categorizacion(models.Model):
    codigo = models.TextField(null=False,blank =False, unique=True, help_text="Codigo de tipologia")
    descripcion = models.TextField(null=False,blank =False, help_text="descripcion de tipologia")
    categorizacion = models.ForeignKey(Categorizacion,on_delete=models.PROTECT, null=True,blank =True,help_text="Categorizacion ORDENANZA 2024!! Base para calculo")
    tarifa = models.DecimalField(max_digits=22, decimal_places=8, default=Decimal(0.0), null=False, help_text="Tarifa o Alicuota")
    habilitado = models.BooleanField(default=True, help_text="Esta activo?")
    observaciones = models.TextField(null=True,blank =True, help_text="observaciones en caso de no esar hablita por que cambio el valor a causa de una ordenanza nueva.")    
    FinesFiscales = models.BooleanField(default=False, help_text="True es para fines fiscales(para impresion de cedula catastral)")
    def __str__(self):
        return 'Id:%s - Zona:%s - Codigo:%s - Descripcion:%s - Alicuota:%s' % (self.id,self.categorizacion,self.codigo, self.descripcion, self.tarifa)
    class Meta:
        indexes = [
            models.Index(fields=['codigo']),
        ]

    #!!! ojo es posible se elimine etste modelo!!!!!!!!!!!!!!!!!!!!!!
class FinesFiscales(models.Model):
    codigo = models.TextField(null=False,blank =False, unique=True, help_text="Codigo de fines fiscales")
    descripcion = models.TextField(null=False,blank =False, unique=True, help_text="descripcion de fines fiscales")
    def __str__(self):
        return '%s - %s' % (self.codigo, self.descripcion)
    class Meta:
        indexes = [
            models.Index(fields=['codigo']),
        ]
    
class TipoDesincorporacion(models.Model):
    codigo = models.TextField(null=False,blank =False, unique=True, help_text="Codigo de tipo desincorporacion")
    descripcion = models.TextField(null=False,blank =False, unique=True, help_text="descripcion del tipo de desincorporacion (cuando se desincorpora un propietario de un inmueble)")
    def __str__(self):
        return '%s - %s' % (self.codigo, self.descripcion)
    class Meta:
        indexes = [
            models.Index(fields=['codigo']),
        ]
    
class TipoTransaccion(models.Model):
    codigo = models.TextField(null=False,blank =False, unique=True, help_text="Codigo de tipo transaccion")
    descripcion = models.TextField(null=False,blank =False, unique=True, help_text="descripcion del tipo de transaccion")
    def __str__(self):
        return '%s - %s' % (self.codigo, self.descripcion)
    class Meta:
        indexes = [
            models.Index(fields=['codigo']),
        ]
    

    
# Maestro de Propietarios/Contribuyentes
class Propietario(models.Model):
    tipo_documento  = models.TextField(null=False,blank =False,default='R',  help_text="Tipo de documento: R=RIF")
    nacionalidad  = models.TextField(null=False,blank =False, default='V', help_text="Nacinalidad")
    numero_documento  = models.TextField(null=False,blank =False, unique=True, help_text="Numero de documento (RIF)")
    nombre  = models.TextField(null=False,blank =False, unique=False, help_text="Nombre o razon social")
    telefono_principal  = models.TextField(null=False,blank =False, unique=False, help_text="Numero de teléfono principal")
    telefono_secundario   = models.TextField(null=True,blank =True, help_text="Numero de teléfono secundario")
    email_principal  = models.TextField(null=False,blank =False, unique=False, help_text="correo 1")
    emaill_secundario  = models.TextField(null=True,blank =True, help_text="correo 2")
    direccion = models.TextField(null=True,blank =True, help_text="Direccion")
    def __str__(self):
        return '%s - %s - %s' % (self.id,self.numero_documento, self.nombre)
    class Meta:
        indexes = [
            models.Index(fields=['numero_documento']),
        ]

# Periodos
class IC_Periodo(models.Model):
    descripcion = models.TextField(null=False,blank =False, unique=True, help_text="descripcion del Periodo")
    periodo = models.PositiveIntegerField(null=True, blank=True,  help_text="Numero del periodo")
    fechadesde  = models.DateField(blank=True,null=True,help_text="fecha Desde donde valida si aplica el descuento")
    fechahasta  = models.DateField(blank=True,null=True, help_text="fecha Hasta donde valida si aplica el descuento")
    dias_gracia=models.PositiveIntegerField(null=True, blank=True,  help_text="Dias a partir del diainicio que no paga multa")
    APLICA = (
        ('C', 'Inmuebles Urbanos'),
        ('A', 'Actividades económicas'),
        ('V', 'Vehiculos'),
        ('P', 'Propaganda y publicidad'),
        ('X', 'Todos')
    )
    aplica= models.CharField(max_length=1, choices=APLICA, default='X', help_text='A que tipo de sector aplica')  
    def __str__(self):
        return '%s - %s- %s' % (self.id,self.periodo,self.aplica)
    class Meta:
        indexes = [
            models.Index(fields=['periodo']),
        ]

class Comunidad(models.Model):
    comunidad = models.TextField(null=False,blank =False, unique=True,  help_text="numero_civico de expediente")
    categoria = models.TextField(null=True,blank =True, help_text="numero_civico de expediente")
    clave = models.TextField(null=True,blank =True, help_text="numero_civico de expediente.")

    history = HistoricalRecords()

    class Meta:
        indexes = [
            models.Index(fields=['comunidad']),
        ]


class Inmueble(models.Model):
    numero_expediente = models.TextField(null=False,blank =False, unique=True, help_text="Numero de expediente.Correlativo.ExpedienteCatastro")
    fecha_inscripcion = models.DateField(blank=True,null=True, help_text="fecha de inscripcion")
    fecha_creacion = models.DateField(blank=True,null=True, help_text="fecha de creacion en el modelo")
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
    numero_civico = models.TextField(null=True,blank =True, help_text="numero_civico de expediente")
    numero_casa = models.TextField(null=True,blank =True, help_text="numero_casa de expediente")
    numero_piso = models.TextField(null=True,blank =True, help_text="numero_piso de expediente")
    telefono = models.TextField(null=True,blank =True, help_text="telefono de expediente")
    zona = models.ForeignKey(Zona,on_delete=models.PROTECT, null=True,blank =True,help_text="Zona !! Base para calculo")
    categorizacion = models.ForeignKey(Categorizacion,on_delete=models.PROTECT, null=True,blank =True,help_text="Categorizacion !! Base para calculo")
    direccion = models.TextField(null=True,blank =True, help_text="direccion")
    referencia = models.TextField(null=True,blank =True, help_text="referencia")
    observaciones = models.TextField(null=True,blank =True, help_text="observaciones")
    inscripcion_paga = models.BooleanField(default=False, help_text="True desde use_case de crear pago cuando se cancele el flujo de Inscripcion de Inmueble")
    habilitado = models.BooleanField(default=True, help_text="Esta activo?")
    periodo=models.ForeignKey(IC_Periodo, null=True,blank =True,on_delete=models.PROTECT,help_text="Periodo que adeuda")
    tipodesincorporacion=models.ForeignKey(TipoDesincorporacion, null=True,blank =True,on_delete=models.PROTECT,help_text="Motivo Desincorporacion")
    anio = models.PositiveIntegerField(null=True, blank=True,  help_text="Año que adeuda")
    ReportePdfDesincorporacion = models.FileField(upload_to=immuebles_path_desincopora,help_text="PDF Desincorporacion", null=True,blank =True)
    ReportePdfCedulaCatastral = models.FileField(upload_to=immuebles_path_ficha,help_text="PDF Cedula catastral", null=True,blank =True)
    comunidad = models.ForeignKey(Comunidad, null=True,blank =True,on_delete=models.PROTECT,help_text="comunidad")

    history = HistoricalRecords()

    class Meta:
        indexes = [
            models.Index(fields=['numero_expediente']),
        ]

    
    def __str__(self):
        return '%s - %s' % (self.id,self.numero_expediente)

class InmueblePropiedad(models.Model): 
    inmueble = models.ForeignKey (Inmueble, on_delete=models.PROTECT,help_text="Sector asociado")
    tipo_documento = models.ForeignKey (TipoDocumento, null=True,blank =True,on_delete=models.PROTECT,help_text="tipo_documento asociado")
    tipo_especial = models.ForeignKey (TipoEspecial, null=True,blank =True,on_delete=models.PROTECT,help_text="tipo_especial asociado")
    fecha_habitabilidad	= models.DateField(null=True,blank =True, help_text="fecha_habitabilidad")
    tipo_tenencia = models.ForeignKey (TipoTenencia, null=True,blank =True,on_delete=models.PROTECT,help_text="tipo_tenencia asociado")
    fecha_vigencia = models.DateField(null=True,blank =True, help_text="fecha de inscripcion")
    fecha_documento	= models.DateField(null=True,blank =True, help_text="fecha de inscripcion")
    numero_documento = models.TextField(null=True,blank =True, help_text="Numero de expediente")
    matricula_documento	= models.TextField(null=True,blank =True, help_text="Numero de expediente")
    anio_folio_documento = models.TextField(null=True,blank =True, help_text="Numero de expediente")
    fecha_terreno = models.DateField(null=True,blank =True, help_text="fecha de inscripcion")
    numero_terreno = models.TextField(null=True,blank =True, help_text="Numero de expediente")
    folio_terreno = models.TextField(null=True,blank =True, help_text="Numero de expediente")
    protocolo_terreno = models.TextField(null=True,blank =True, help_text="Numero de expediente")
    tomo_terreno = models.TextField(null=True,blank =True, help_text="Numero de expediente")
    area_terreno =  models.DecimalField(max_digits=22, decimal_places=8, default=Decimal(0.0), null=True,blank =True, help_text="area_terreno en m2")
    valor_terreno = models.TextField(null=True,blank =True, help_text="Numero de expediente")
    fecha_construccion = models.DateField(null=True,blank =True, help_text="fecha de inscripcion")
    numero_construccion	= models.TextField(null=True,blank =True, help_text="Numero de expediente")
    folio_construccion = models.TextField(null=True,blank =True, help_text="Numero de expediente")
    protocolo_construccion = models.TextField(null=True,blank =True, help_text="Numero de expediente")
    tomo_construccion = models.TextField(null=True,blank =True, help_text="Numero de expediente")
    area_construccion =  models.DecimalField(max_digits=22, decimal_places=8, default=Decimal(0.0), null=True,blank =True, help_text="area_construccion en m2")
    valor_construccion = models.TextField(null=True,blank =True, help_text="valor construccion")
    lindero_norte = models.TextField(null=True,blank =True, help_text="Numero de expediente")
    lindero_sur	= models.TextField(null=True,blank =True, help_text="Numero de expediente")
    lindero_este = models.TextField(null=True,blank =True, help_text="Numero de expediente")
    lindero_oeste = models.TextField(null=True,blank =True, help_text="Numero de expediente")
    pdf_documento = models.FileField(upload_to=immuebles_path_doc, null=True, blank=True, help_text="Pdf del documento de registro")

    history = HistoricalRecords()

    def __str__(self):
        return '%s' % (self.inmueble.numero_expediente)
    class Meta:
        indexes = [
            models.Index(fields=['inmueble']),
        ]

class InmueblePropietarios(models.Model):
    inmueble = models.ForeignKey (Inmueble, on_delete=models.PROTECT,help_text="Id Inmueble")
    propietario = models.ForeignKey (Propietario, on_delete=models.PROTECT,help_text="Id Propietario")
    fecha_compra = models.DateField(null=True,blank =True, help_text="fecha de compra del inmueble")
    modificacion_paga = models.BooleanField(default=False, help_text="True desde use_case de crear pago cuando se cancele el flujo de cambio de propietario")

    history = HistoricalRecords()
    # def save(self, *args, **kwargs):
    #     user = kwargs.pop('user', None)  # Extrae el usuario de los kwargs
    #     super().save(*args, **kwargs)
    #     if user:
    #         history_instance = self.history.most_recent()  # Obtiene la instancia histórica
    #         history_instance.user = user
    #         history_instance.save()

    def __str__(self):
        return '%s - %s' % (self.inmueble.numero_expediente,self.propietario.nombre)
    class Meta:
        indexes = [
            models.Index(fields=['inmueble']),
        ]

class InmuebleTerreno(models.Model):
    inmueble = models.ForeignKey (Inmueble, on_delete=models.PROTECT,help_text="Id Inmueble asociado")
    #topografia	= models.ForeignKey (Topografia, on_delete=models.PROTECT,help_text="Topografia asociado")
    #acceso = models.ForeignKey (Acceso, on_delete=models.PROTECT,help_text="Acceso asociado")
    forma = models.ForeignKey (Forma,null=True,blank =True, on_delete=models.PROTECT,help_text="Forma asociado")
    ubicacion = models.ForeignKey (Ubicacion,null=True,blank =True, on_delete=models.PROTECT,help_text="Ubicacion asociado")
    tenencia = models.ForeignKey (TipoTenencia,null=True,blank =True, on_delete=models.PROTECT,help_text="tenencia asociado")
    #uso	= models.ForeignKey (Uso, on_delete=models.PROTECT,help_text="uso asociado")
    regimen	= models.ForeignKey (Regimen,null=True,blank =True, on_delete=models.PROTECT,help_text="regimen asociado")
    #servicios = models.ForeignKey (Servicios,null=True,blank =True, on_delete=models.PROTECT,help_text="Servicios Asociado")
    observaciones = models.TextField(null=True,blank =True, help_text="Observaciones")
    def __str__(self):
        return '%s' % (self.inmueble.numero_expediente)
    class Meta:
        indexes = [
            models.Index(fields=['inmueble']),
        ]
    
class InmuebleTerrenoTopografia(models.Model):
    inmueble_terreno = models.ForeignKey (InmuebleTerreno, on_delete=models.PROTECT,help_text="Inmueble asociado")
    topografia = models.ForeignKey (Topografia, on_delete=models.PROTECT,help_text="Topografia asociado")
    def __str__(self):
        return '%s' % (self.inmueble_terreno.inmueble.numero_expediente)
    class Meta:
        indexes = [
            models.Index(fields=['inmueble_terreno']),
        ]
    	    
class InmuebleTerrenoAcceso(models.Model):
    inmueble_terreno = models.ForeignKey (InmuebleTerreno, on_delete=models.PROTECT,help_text="Inmueble asociado")
    acceso = models.ForeignKey (Acceso, on_delete=models.PROTECT,help_text="Acceso asociado")
    def __str__(self):
        return '%s' % (self.inmueble_terreno.inmueble.numero_expediente)
    class Meta:
        indexes = [
            models.Index(fields=['inmueble_terreno']),
        ]
    	
class InmuebleTerrenoUso(models.Model):
    inmueble_terreno = models.ForeignKey (InmuebleTerreno, on_delete=models.PROTECT,help_text="Inmueble asociado")
    uso = models.ForeignKey (Uso, on_delete=models.PROTECT,help_text="uso asociado")
    def __str__(self):
        return '%s' % (self.inmueble_terreno.inmueble.numero_expediente)
    class Meta:
        indexes = [
            models.Index(fields=['inmueble_terreno']),
        ]

class InmuebleTerrenoServicio(models.Model):
    inmueble_terreno = models.ForeignKey (InmuebleTerreno, on_delete=models.PROTECT,help_text="Inmueble asociado")
    servicio	= models.ForeignKey (Servicios, on_delete=models.PROTECT,help_text="regimen asociado")
    def __str__(self):
        return '%s' % (self.inmueble_terreno.inmueble.numero_expediente)
    class Meta:
        indexes = [
            models.Index(fields=['inmueble_terreno']),
        ]

class UsoConstruccion(models.Model):
    codigo = models.TextField(null=False,blank =False, unique=True, help_text="Codigo de UsoConstruccion")
    descripcion = models.TextField(null=False,blank =False, unique=True, help_text="descripcion de UsoConstruccion")
    def __str__(self):
        return '%s - %s' % (self.codigo, self.descripcion)
    class Meta:
        indexes = [
            models.Index(fields=['codigo']),
        ]
    
class Soporte(models.Model):
    codigo = models.TextField(null=False,blank =False, unique=True, help_text="Codigo de Soporte")
    descripcion = models.TextField(null=False,blank =False, unique=True, help_text="descripcion de Soporte")
    def __str__(self):
        return '%s - %s' % (self.codigo, self.descripcion)
    class Meta:
        indexes = [
            models.Index(fields=['codigo']),
        ]

class Techo(models.Model):
    codigo = models.TextField(null=False,blank =False, unique=True, help_text="Codigo de Techo")
    descripcion = models.TextField(null=False,blank =False, unique=True, help_text="descripcion de Techo")
    def __str__(self):
        return '%s - %s' % (self.codigo, self.descripcion)
    class Meta:
        indexes = [
            models.Index(fields=['codigo']),
        ]
    
class Cubierta(models.Model):
    codigo = models.TextField(null=False,blank =False, unique=True, help_text="Codigo de Cubierta")
    descripcion = models.TextField(null=False,blank =False, unique=True, help_text="descripcion de Cubierta")
    def __str__(self):
        return '%s - %s' % (self.codigo, self.descripcion)
    class Meta:
        indexes = [
            models.Index(fields=['codigo']),
        ]
    
class TipoPared(models.Model):
    codigo = models.TextField(null=False,blank =False, unique=True, help_text="Codigo de TipoPared")
    descripcion = models.TextField(null=False,blank =False, unique=True, help_text="descripcion de TipoPared")
    def __str__(self):
        return '%s - %s' % (self.codigo, self.descripcion)
    class Meta:
        indexes = [
            models.Index(fields=['codigo']),
        ]
    
class AcabadoPared(models.Model):
    codigo = models.TextField(null=False,blank =False, unique=True, help_text="Codigo de AcabadoPared")
    descripcion = models.TextField(null=False,blank =False, unique=True, help_text="descripcion de AcabadoPared")
    def __str__(self):
        return '%s - %s' % (self.codigo, self.descripcion)
    class Meta:
        indexes = [
            models.Index(fields=['codigo']),
        ]
    
class Conservacion(models.Model):
    codigo = models.TextField(null=False,blank =False, unique=True, help_text="Codigo de Conservacion")
    descripcion = models.TextField(null=False,blank =False, unique=True, help_text="descripcion de Conservacion")
    def __str__(self):
        return '%s - %s' % (self.codigo, self.descripcion)
    class Meta:
        indexes = [
            models.Index(fields=['codigo']),
        ]
    

class InmuebleConstruccion(models.Model):
    inmueble = models.ForeignKey (Inmueble, on_delete=models.PROTECT,help_text="Id Inmueble asociado")
    tipo=models.ForeignKey(TipoInmueble,null=True,blank =True,on_delete=models.PROTECT,help_text="TipoInmueble asociado")
    uso_construccion = models.ForeignKey(UsoConstruccion,null=True,blank =True,on_delete=models.PROTECT,help_text="uso_construccion asociado")
    tenencia = models.ForeignKey (TipoTenencia, null=True,blank =True,on_delete=models.PROTECT,help_text="tenencia asociado")
    regimen	= models.ForeignKey (Regimen,null=True,blank =True, on_delete=models.PROTECT,help_text="regimen asociado")
    #soporte = models.ForeignKey (Soporte, on_delete=models.PROTECT,help_text="Soporte asociado")
    #techo = models.ForeignKey (Techo, on_delete=models.PROTECT,help_text="Techo asociado")
    #cubierta = models.ForeignKey (Cubierta, on_delete=models.PROTECT,help_text="Cubierta asociado")
    tipo_pared = models.ForeignKey (TipoPared,null=True,blank =True, on_delete=models.PROTECT,help_text="TipoPared asociado")
    acabado_pared = models.ForeignKey (AcabadoPared, null=True,blank =True,on_delete=models.PROTECT,help_text="AcabadoPared asociado")
    conservacion = models.ForeignKey (Conservacion, null=True,blank =True,on_delete=models.PROTECT,help_text="Conservacion asociado")
    anio_construccion = models.PositiveIntegerField(default=0, help_text="anio_construccion")
    anio_refaccion = models.PositiveIntegerField(default=0, help_text="anio_refaccion")
    porcentaje_refaccion = models.TextField(null=True,blank =True, help_text="Numero de expediente")
    edad_efectiva = models.TextField(null=True,blank =True, help_text="edad_efectiva")
    numero_niveles = models.PositiveIntegerField(default=0, help_text="Numero de niveles")
    numero_edificaciones = models.PositiveIntegerField(default=0, help_text="numero de edificaciones")
    observaciones = models.TextField(null=True,blank =True, help_text="observaciones")
    def __str__(self):
        return '%s - %s' % (self.inmueble.id, self.observaciones)
    class Meta:
        indexes = [
            models.Index(fields=['inmueble']),
        ]
    
class InmuebleConstruccionSoporte(models.Model):
    inmueble_construccion = models.ForeignKey (InmuebleConstruccion, on_delete=models.PROTECT,help_text="Inmueble asociado")
    soporte = models.ForeignKey(Soporte, on_delete=models.PROTECT,help_text="Soporte asociado")
    class Meta:
        indexes = [
            models.Index(fields=['inmueble_construccion']),
        ]

class InmuebleConstruccionTecho(models.Model):
    inmueble_construccion = models.ForeignKey (InmuebleConstruccion, on_delete=models.PROTECT,help_text="Inmueble asociado")
    techo = models.ForeignKey(Techo, on_delete=models.PROTECT,help_text="Techo asociado")
    class Meta:
        indexes = [
            models.Index(fields=['inmueble_construccion']),
        ]

class InmuebleConstruccionCubierta(models.Model):
    inmueble_construccion = models.ForeignKey (InmuebleConstruccion, on_delete=models.PROTECT,help_text="Inmueble asociado")
    cubierta = models.ForeignKey(Cubierta, on_delete=models.PROTECT,help_text="Cubierta asociado") 
    class Meta:
        indexes = [
            models.Index(fields=['inmueble_construccion']),
        ]


class InmuebleValoracionTerreno(models.Model):
    inmueble = models.ForeignKey (Inmueble, on_delete=models.PROTECT,help_text="Id Inmueble asociado")
    area = models.DecimalField(max_digits=22, decimal_places=8, default=Decimal(0.0), null=False, help_text="Area en m2")
    tipologia = models.ForeignKey (Tipologia, null=True,blank =True,on_delete=models.PROTECT,help_text="tipologia asociado")
    tipo=models.ForeignKey(TipoInmueble, null=True,blank =True,on_delete=models.PROTECT,help_text="Tipo de Inmueble asociado para determinar si unifamiliar o multifamiliar")    
    fines_fiscales	= models.ForeignKey (FinesFiscales,null=True,blank =True, on_delete=models.PROTECT,help_text="fines_fiscales asociado")
    valor_unitario = models.DecimalField(max_digits=22, decimal_places=8, default=Decimal(0.0), null=False, help_text="valor_unitario")
    area_factor_ajuste =  models.DecimalField(max_digits=22, decimal_places=8, default=Decimal(0.0), null=False, help_text="Area en m2 del factor de ajuste")
    forma_factor_ajuste	= models.ForeignKey (Forma,null=True,blank =True, on_delete=models.PROTECT,help_text="Forma del factor de ajuste")
    valor_ajustado = models.DecimalField(max_digits=22, decimal_places=8, default=Decimal(0.0), null=False, help_text="Valor Ajustado")
    valor_total = models.DecimalField(max_digits=22, decimal_places=8, default=Decimal(0.0), null=False, help_text="Valor Total")
    observaciones = models.TextField(null=True,blank =True, help_text="observaciones")
    aplica= models.CharField(max_length=1, default='T', help_text='TERRENO')
    
    history = HistoricalRecords()

    def __str__(self):
        return '%s - %s' % (self.inmueble.id, self.observaciones)
    class Meta:
        indexes = [
            models.Index(fields=['inmueble']),
        ]
    
class InmuebleValoracionConstruccion(models.Model):
    inmueblevaloracionterreno = models.ForeignKey (InmuebleValoracionTerreno, on_delete=models.PROTECT,help_text="Id inmueble_terreno asociado")
    tipologia = models.ForeignKey (Tipologia, on_delete=models.PROTECT,help_text="tipologia asociado")
    sub_utilizado = models.BooleanField(default=False, help_text="subutilizado si o no")
    tipo=models.ForeignKey(TipoInmueble,on_delete=models.PROTECT,help_text="Tipo de Inmueble asociado para determinar si unifamiliar o multifamiliar")    
    fecha_construccion = models.DateField(blank=True,  null=True, help_text="fecha construccion")
    area = models.DecimalField(max_digits=22, decimal_places=8, default=Decimal(0.0), null=False, help_text="Area en m2")
    valor = models.DecimalField(max_digits=22, decimal_places=8, default=Decimal(0.0), null=False, help_text="valor")
    depreciacion = models.DecimalField(max_digits=22, decimal_places=8, default=Decimal(0.0), null=False, help_text="depreciacion")
    valor_actual = models.DecimalField(max_digits=22, decimal_places=8, default=Decimal(0.0), null=False, help_text="valor")
    aplica= models.CharField(max_length=1, default='C', help_text='CONSTRUCCION')  

    history = HistoricalRecords()

    def __str__(self):
        return '%s - %s ' % (self.inmueblevaloracionterreno.inmueble.id, self.inmueblevaloracionterreno.id) 
    class Meta:
        indexes = [
            models.Index(fields=['inmueblevaloracionterreno']),
        ]


class InmuebleValoracionTerreno2024(models.Model):
    inmueble = models.ForeignKey (Inmueble, on_delete=models.PROTECT,help_text="Id Inmueble asociado")
    area = models.DecimalField(max_digits=22, decimal_places=8, default=Decimal(0.0), null=False, help_text="Area en m2")
    tipologia_categorizacion = models.ForeignKey (Tipologia_Categorizacion, null=True,blank =True,on_delete=models.PROTECT,help_text="tipologia asociado ORDENANZA 2024")
    tipo=models.ForeignKey(TipoInmueble, null=True,blank =True,on_delete=models.PROTECT,help_text="Tipo de Inmueble asociado para determinar si unifamiliar o multifamiliar")    
    fines_fiscales	= models.ForeignKey (FinesFiscales,null=True,blank =True, on_delete=models.PROTECT,help_text="fines_fiscales asociado")
    valor_unitario = models.DecimalField(max_digits=22, decimal_places=8, default=Decimal(0.0), null=False, help_text="valor_unitario")
    area_factor_ajuste =  models.DecimalField(max_digits=22, decimal_places=8, default=Decimal(0.0), null=False, help_text="Area en m2 del factor de ajuste")
    forma_factor_ajuste	= models.ForeignKey (Forma,null=True,blank =True, on_delete=models.PROTECT,help_text="Forma del factor de ajuste")
    valor_ajustado = models.DecimalField(max_digits=22, decimal_places=8, default=Decimal(0.0), null=False, help_text="Valor Ajustado")
    valor_total = models.DecimalField(max_digits=22, decimal_places=8, default=Decimal(0.0), null=False, help_text="Valor Total")
    observaciones = models.TextField(null=True,blank =True, help_text="observaciones")
    aplica= models.CharField(max_length=1, default='T', help_text='TERRENO')

    history = HistoricalRecords()
    
    def __str__(self):
        return '%s - %s' % (self.inmueble.id, self.observaciones)
    class Meta:
        indexes = [
            models.Index(fields=['inmueble']),
        ]
    
class InmuebleValoracionConstruccion2024(models.Model): 
    inmueblevaloracionterreno = models.ForeignKey (InmuebleValoracionTerreno2024, on_delete=models.PROTECT,help_text="Id inmueble_terreno asociado")
    tipologia_categorizacion = models.ForeignKey (Tipologia_Categorizacion,null=True,blank =True, on_delete=models.PROTECT,help_text="tipologia asociado ORDENANZA 2024")
    sub_utilizado = models.BooleanField(default=False, help_text="subutilizado si o no")
    tipo=models.ForeignKey(TipoInmueble,on_delete=models.PROTECT,help_text="Tipo de Inmueble asociado para determinar si unifamiliar o multifamiliar")    
    fecha_construccion = models.DateField(blank=True,  null=True, help_text="fecha construccion")
    area = models.DecimalField(max_digits=22, decimal_places=8, default=Decimal(0.0), null=False, help_text="Area en m2")
    valor = models.DecimalField(max_digits=22, decimal_places=8, default=Decimal(0.0), null=False, help_text="valor")
    depreciacion = models.DecimalField(max_digits=22, decimal_places=8, default=Decimal(0.0), null=False, help_text="depreciacion")
    valor_actual = models.DecimalField(max_digits=22, decimal_places=8, default=Decimal(0.0), null=False, help_text="valor")
    aplica= models.CharField(max_length=1, default='C', help_text='CONSTRUCCION')  
    
    history = HistoricalRecords()

    def __str__(self):
        return '%s - %s ' % (self.inmueblevaloracionterreno.inmueble.id, self.inmueblevaloracionterreno.id)
    class Meta:
        indexes = [
            models.Index(fields=['inmueblevaloracionterreno']),
        ]



class InmuebleUbicacion(models.Model):
    inmueble = models.ForeignKey (Inmueble, on_delete=models.PROTECT,help_text="Id Inmueble asociado")
    lindero_norte = models.TextField(null=True,blank =True, help_text="Numero de expediente")
    lindero_sur = models.TextField(null=True,blank =True, help_text="Numero de expediente")
    lindero_este = models.TextField(null=True,blank =True, help_text="Numero de expediente")
    lindero_oeste = models.TextField(null=True,blank =True, help_text="Numero de expediente")
    imagen_inmueble = models.ImageField(upload_to=immuebles_path, null=True, blank=True, help_text="Imagen asociado al Inmueble")
    imagen_plano = models.ImageField(upload_to=immuebles_path, null=True, blank=True, help_text="Imagen asociado al Plano")
    imagan_plano_mesura =models.ImageField(upload_to=immuebles_path, null=True, blank=True, help_text="Imagen asociado al Plano Mesura")
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
    class Meta:
        indexes = [
            models.Index(fields=['inmueble']),
        ]

class InmuebleFaltante(models.Model):
    inmueble = models.ForeignKey (Inmueble, on_delete=models.PROTECT,help_text="Id Inmueble asociado")
    cedula = models.TextField(null=True,blank =True,help_text="Numero de cedula")
    documentopropiedad = models.TextField(null=True,blank =True, help_text="Numero de documentopropiedad")
    observaciones = models.TextField(null=True,blank =True,help_text="observaciones")
    class Meta:
        indexes = [
            models.Index(fields=['inmueble']),
        ]

## Histoial de Actualizacion de tasas para calculo de interes moratorio
class TasaInteres(models.Model):
    anio = models.PositiveIntegerField(null=True, blank=True,  help_text="Año")
    mes = models.PositiveIntegerField(null=True, blank=True,  help_text="Mes")
    tasa  = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal(0.0), null=False,  help_text="Tasa")
    habilitado = models.BooleanField(default=True, help_text="Esta activo?")
    def __str__(self):
        return '%s - %s - %s' % (self.anio, self.mes, self.tasa)

## Histoial de Actualizacion de precios de Tasa BS
class TasaBCV(models.Model):
    fecha = models.DateField(blank=True, help_text="Fecha Actualizacion TASA")
    fecha_vigente= models.DateField(blank=True, help_text=" A partir de esta fecha se aplica los calculos")
    monto  = models.DecimalField(max_digits=22, decimal_places=8, default=Decimal(0.0), null=False,  help_text="Monto TASA")
    habilitado = models.BooleanField(default=True, help_text="Esta activo?")
    def __str__(self):
        return '%s - %s' % (self.monto, self.fecha)
    def save(self, *args, **kwargs):
        self.fecha = timezone.now().date() 
        super().save(*args, **kwargs)

## Histoial de Actualizacion de precios de UT/petro u otro definido por la ley
class UnidadTributaria(models.Model):
    fecha = models.DateField(blank=True, help_text="Fecha Actualizacion Unidad Tributaria")
    fecha_vigente= models.DateField(blank=True, help_text=" A partir de esta fecha se aplica los calculos")
    monto  = models.DecimalField(max_digits=22, decimal_places=8, default=Decimal(0.0), null=False,  help_text="Monto Unidad tributaria")
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
    codigo = models.TextField(null=True,blank =True, unique=True, help_text="Codigo de la Tasa Multa")
    TIPO = (
        ('I', 'Impuesto'),
        ('T', 'Tasa'),
        ('M', 'Multa'),
        ('R', 'Recaudacion'),
        ('O', 'Otro')
    )
    descripcion  = models.TextField(null=False,blank =False, unique=True, help_text="Descripcion")
    detalle  = models.TextField(null=True,blank =True, help_text="Información extra. en caso de un artoculo especifico de la ordenanza")
    unidad_tributaria  = models.TextField(null=False,blank =False, unique=False, help_text="Cantidad Unidad tributaria")
    tipo= models.CharField(max_length=1, choices=TIPO, default='O', help_text='tipo de recaudacion')
    APLICA = (
        ('C', 'Inmuebles Urbanos'),
        ('I', 'Catastro'),
        ('A', 'Actividades económicas'),
        ('V', 'Vehiculos'),
        ('P', 'Propaganda y publicidad'),
        ('R', 'Recaudacion'),
        ('X', 'Todos')
    )
    aplica= models.CharField(max_length=1, choices=APLICA, default='X', help_text='A que tipo de sector aplica')  
    def __str__(self):
        return '%s - %s - %s' % (self.codigo,self.tipo, self.descripcion)
        
    class Meta:
        indexes = [
            models.Index(fields=['codigo']),
        ]

#Maestro de tipos de pago (sirce para validar los conceptos de catastro, dias de vencimiento, pre-carga items que regulamente se cargan en ese tipo de flujo)
class TipoFlujo(models.Model):
    """
    Una clase típica definiendo un modelo, derivado desde la clase Model.
    """
    codigo = models.TextField(null=True,blank =True, unique=True,help_text="Codigo del Tipo de Flujo")
    descripcion  = models.TextField(null=False,blank =False, unique=True, help_text="Descripcion Tipo de pago")
    vencimiento = models.PositiveIntegerField(null=True, blank=True,  help_text="dias vencimiento pra validar el estado de cuenta")
    APLICA = (
        ('C', 'Inmuebles Urbanos'),
        ('I', 'Catastro'),
        ('A', 'Actividades económicas'),
        ('V', 'Vehiculos'),
        ('P', 'Propaganda y publicidad'),
        ('R', 'Recaudacion'),
        ('X', 'Todos')
    )
    aplica= models.CharField(max_length=1, choices=APLICA, default='X', help_text='A que tipo de sector aplica')
    carandai = models.BooleanField(default=True, help_text="genera flujo?")
    crea_expediente = models.BooleanField(default=False, help_text="genera un nuevo numero de expediente?")
    def __str__(self):
        return '%s - %s - %s - %s - %s - crea flujo:%s - crea expediente:%s' % (self.id,self.codigo,self.descripcion,self.aplica,self.vencimiento,self.carandai,self.crea_expediente)
    class Meta:
        indexes = [
            models.Index(fields=['codigo']),
        ]   
class TipoFlujoDetalle(models.Model):
    tipoflujo = models.ForeignKey (TipoFlujo, null=True,blank =True,on_delete=models.PROTECT,help_text="Id TipoFlujo")
    tasamulta = models.ForeignKey(TasaMulta, on_delete=models.PROTECT,help_text="Id Tasa Multa")
    def __str__(self):
        return '%s - %s' % (self.tipoflujo.descripcion,self.tasamulta)
    class Meta:
        indexes = [
            models.Index(fields=['tipoflujo']),
        ]

class EstadoCuenta(models.Model):
    numero = models.TextField(null=False,blank =False, unique=True, help_text="Numero de Estado de Cuenta. Correlativo.NumeroEstadoCuenta")
    inmueble = models.ForeignKey (Inmueble, null=True,blank =True,on_delete=models.PROTECT,help_text="Id Inmueble asociado")
    tipoflujo = models.ForeignKey(TipoFlujo, null=True,blank =True,on_delete=models.PROTECT,help_text="Tipo de flujo (solo catasrro: inscripcion, actualizacion o modificar propietario")
    fecha = models.DateTimeField(blank=True, help_text="Fecha Estado Cuenta")
    propietario=models.ForeignKey(Propietario, on_delete=models.PROTECT,help_text="Contribuyente/Propietario asociado")
    observaciones = models.TextField(null=True,blank =True, help_text="observaciones")
    valor_petro  = models.DecimalField(max_digits=22, decimal_places=8, default=Decimal(0.0), null=False, help_text="total")
    valor_tasa_bs = models.DecimalField(max_digits=22, decimal_places=8, default=Decimal(0.0), null=False, help_text="total")
    monto_total  = models.DecimalField(max_digits=22, decimal_places=8, default=Decimal(0.0), null=False, help_text="monto total")
    habilitado = models.BooleanField(default=True, help_text="Esta activo?")
    fecha_compra = models.DateField(null=True,blank =True, help_text="Fecha de compra del inmueble (SOLO SE PIDE PARA INSCRIPCION DE INMUEBLES NUEVOS)")
    area = models.DecimalField(max_digits=22, decimal_places=8, default=Decimal(0.0), null=False, help_text="Area en m2 (SOLO SE PIDE PARA INSCRIPCION DE INMUEBLES NUEVOS)")
    tipo=models.ForeignKey(TipoInmueble,null=True,blank =True,on_delete=models.PROTECT,help_text="TipoInmueble asociado (SOLO SE PIDE PARA INSCRIPCION DE INMUEBLES NUEVOS)")
    ReportePdf = models.FileField(upload_to=estadocuenta_path,help_text="PDF EstadoCuenta", null=True,blank =True)
    def __str__(self):
        return '%s - %s - %s - %s' % (self.id,self.numero,self.propietario.nombre,self.tipoflujo)
    class Meta:
        indexes = [
            models.Index(fields=['numero']),
        ]
    
class EstadoCuentaDetalle(models.Model):
    estadocuenta = models.ForeignKey(EstadoCuenta, on_delete=models.PROTECT,help_text="ID Cabecera Estado de Cuenta")
    tasamulta = models.ForeignKey(TasaMulta, on_delete=models.PROTECT,help_text="Id Tasa Multa")
    monto_unidad_tributaria  = models.DecimalField(max_digits=22, decimal_places=8, default=Decimal(0.0), null=False,  help_text="Monto Unidad tributaria")	
    monto_tasa  = models.DecimalField(max_digits=22, decimal_places=8, default=Decimal(0.0), null=False,  help_text="Monto total del renglon tasa(monto_unidad_tributaria * cantidad)")	
    cantidad  = models.DecimalField(max_digits=22, decimal_places=8, default=Decimal(0.0), null=False, help_text="Cantidad Unidad tributaria")
    observaciones = models.TextField(null=True,blank =True, help_text="observaciones")
    def __str__(self):
        return '%s - %s' % (self.estadocuenta.numero,self.tasamulta)
    class Meta:
        indexes = [
            models.Index(fields=['estadocuenta']),
        ]

class Liquidacion(models.Model):
    estadocuenta = models.ForeignKey(EstadoCuenta,null=True,blank=True, on_delete=models.PROTECT,help_text="ID Cabecera Estado de Cuenta")
    numero = models.TextField(null=False,blank =False, unique=True, help_text="Numero de Liquidacion. Correlativo.NumeroLiquidacion")
    inmueble = models.ForeignKey (Inmueble, null=True,blank =True,on_delete=models.PROTECT,help_text="Id Inmueble asociado")
    tipoflujo = models.ForeignKey(TipoFlujo, null=True,blank =True,on_delete=models.PROTECT,help_text="Tipo de flujo solo catasrro: inscripcion, actualizacion o modificar propietario")
    fecha = models.DateTimeField(blank=True, help_text="Fecha Estado Cuenta")
    propietario=models.ForeignKey(Propietario, on_delete=models.PROTECT,help_text="Contribuyente/Propietario asociado")
    observaciones = models.TextField(null=True,blank =True, help_text="observaciones")
    valor_petro  = models.DecimalField(max_digits=22, decimal_places=8, default=Decimal(0.0), null=False, help_text="total")
    valor_tasa_bs = models.DecimalField(max_digits=22, decimal_places=8, default=Decimal(0.0), null=False, help_text="total")
    monto_total  = models.DecimalField(max_digits=22, decimal_places=8, default=Decimal(0.0), null=False, help_text="total")
    habilitado = models.BooleanField(default=True, help_text="Se muestra la liquidacion?")
    fecha_compra = models.DateField(null=True,blank =True, help_text="Fecha de compra del inmueble (SOLO SE PIDE PARA INSCRIPCION DE INMUEBLES NUEVOS)")
    area = models.DecimalField(max_digits=22, decimal_places=8, default=Decimal(0.0), null=False, help_text="Area en m2 (SOLO SE PIDE PARA INSCRIPCION DE INMUEBLES NUEVOS)")
    tipo=models.ForeignKey(TipoInmueble,null=True,blank =True,on_delete=models.PROTECT,help_text="TipoInmueble asociado (SOLO SE PIDE PARA INSCRIPCION DE INMUEBLES NUEVOS)")
    ReportePdf = models.FileField(upload_to=liquidacion_path,help_text="PDF PreFactura", null=True,blank =True)
    def __str__(self):
        return '%s - %s - %s' % (self.numero,self.propietario.nombre,self.tipoflujo)
    class Meta:
        indexes = [
            models.Index(fields=['numero']),
        ]
    
class LiquidacionDetalle(models.Model):
    liquidacion = models.ForeignKey(Liquidacion, on_delete=models.PROTECT,help_text="ID Cabecera liquidacion")
    tasamulta = models.ForeignKey(TasaMulta, on_delete=models.PROTECT,help_text="Id Tasa Multa")
    monto_unidad_tributaria  = models.DecimalField(max_digits=22, decimal_places=8, default=Decimal(0.0), null=False,  help_text="Monto Unidad tributaria")	
    monto_tasa  = models.DecimalField(max_digits=22, decimal_places=8, default=Decimal(0.0), null=False,  help_text="Monto total del renglon tasa(monto_unidad_tributaria * cantidad)")	
    cantidad  = models.DecimalField(max_digits=22, decimal_places=8, default=Decimal(0.0), null=False, help_text="Cantidad Unidad tributaria")
    observaciones = models.TextField(null=True,blank =True, help_text="observaciones")
    def __str__(self):
        return '%s - %s' % (self.liquidacion.numero,self.tasamulta)
    class Meta:
        indexes = [
            models.Index(fields=['liquidacion']),
        ]

#Maestro de tipos de pago
class TipoPago(models.Model):
    descripcion  = models.TextField(null=False,blank =False, unique=True, help_text="Descripcion Tipo de pago")
    codigo  = models.TextField(null=True,blank =True,  help_text="codigo Tipo de pago")
    lstar = models.BooleanField(default=True, help_text="se lista en los formularios?")
    #(
    #    ('3', 'TRANSFERENCIA'),
    #    ('5', 'DEPOSITO'),
    #    ('11', 'DEBITO'),
#        ('14', 'SITUADO'),
#        ('4', 'INTERESES'),
#        ('12', 'FCI'),
#        ('X', 'Todos')
#    )
    operacion  = models.TextField(null=True,blank =True,  help_text="codigo Tipo de operacion")


    def __str__(self):
        return '%s - %s - %s - %s' % (self.id,self.descripcion,self.codigo,self.operacion)
    class Meta:
        indexes = [
            models.Index(fields=['descripcion']),
        ]

   
class Banco(models.Model):
    descripcion  = models.TextField(null=False,blank =False, unique=True, help_text="Nombre del banco")
    codigo  = models.TextField(null=True,blank =True, help_text="Codigo del banco")
    def __str__(self):
        return '%s' % (self.descripcion)
    class Meta:
        indexes = [
            models.Index(fields=['descripcion']),
        ]

class BancoCuenta(models.Model):
    banco = models.ForeignKey(Banco, on_delete=models.PROTECT,help_text="ID Banco")
    numero  = models.TextField(null=False,blank =False, unique=True, help_text="Numero de Cuenta")
    codigocuenta  = models.TextField(null=True,blank =True, help_text="codigo de Cuenta")
    TIPO = (
        ('1', 'Corriente'),
        ('2', 'Ahorro'),
    )
    tipo= models.CharField(max_length=1, choices=TIPO, default='1', help_text='Tipo de Cuenta')
    def __str__(self):
        return '%s - %s - %s' % (self.banco.descripcion,self.numero,self.tipo)
    
class MotivoAnulacionPago(models.Model):
    descripcion  = models.TextField(null=False,blank =False, unique=True, help_text="Descripcion del motivo")
    def __str__(self):
        return '%s' % (self.descripcion)
    


#Maestro de recibo Pago
class PagoEstadoCuenta(models.Model):
    numero = models.TextField(null=False,blank =False, unique=True, help_text="Numero de pago. Correlativo.NumeroPago")
    liquidacion = models.ForeignKey(Liquidacion, null=True,blank =True,on_delete=models.PROTECT,help_text="ID Cabecera liquidacion")
    fecha = models.DateTimeField(blank=True, help_text="Fecha Estado Cuenta")
    caja = models.PositiveIntegerField(null=True, blank=True,  help_text="Numero de Caja . Viene del modelo Perfil")
    observaciones = models.TextField(null=True,blank =True, help_text="observaciones")
    monto  = models.DecimalField(max_digits=22, decimal_places=8, default=Decimal(0.0), null=False, help_text="total pagado")
    monto_cxc = models.DecimalField(max_digits=22, decimal_places=8, default=Decimal(0.0), null=False, help_text="monto de la factura, la diferencia de lo pagado de mas se usa para crear la nota de crédito")
    habilitado = models.BooleanField(default=True, help_text="Esta activo?")
    anula_usuario = models.TextField(null=True,blank =True, help_text="usuario que anula")
    anula_fecha = models.DateTimeField(blank=True, null=True,help_text="Fecha Anulacion")
    anula_observaciones = models.TextField(null=True,blank =True, help_text="observaciones por la anulacion")
    motivoanulacionpago = models.ForeignKey(MotivoAnulacionPago,null=True,blank =True, on_delete=models.PROTECT,help_text="ID MotivoAnulacionPago")
    ReportePdf = models.FileField(upload_to=pagoestadocuenta_path,help_text="PDF PagoEstadoCuenta", null=True,blank =True)
    def __str__(self):
        return '%s - %s - %s' % (self.id,self.numero,self.liquidacion)
    def save(self, *args, **kwargs):
        self.fecha = timezone.now()
        super().save(*args, **kwargs) 
    class Meta:
        indexes = [
            models.Index(fields=['numero']),
        ]

#Detalle de recibo Pago
class PagoEstadoCuentaDetalle(models.Model):
    pagoestadocuenta = models.ForeignKey(PagoEstadoCuenta, on_delete=models.PROTECT,help_text="ID Cabecera PAGO")
    tipopago = models.ForeignKey(TipoPago, on_delete=models.PROTECT,help_text="Id Tipo Pago")
    monto  = models.DecimalField(max_digits=22, decimal_places=8, default=Decimal(0.0), null=False,  help_text="Monto del pago")	
    bancocuenta = models.ForeignKey(BancoCuenta,null=True,blank =True, on_delete=models.PROTECT,help_text="ID Banco")
    nro_aprobacion = models.TextField(null=True,blank =True,  help_text="numero de aprobacion (debito)")
    nro_lote = models.TextField(null=True,blank =True,  help_text="numero de lote (debito)")
    nro_referencia = models.TextField(null=True,blank =True,  help_text="numero de referencia (debito, trasferencia y nota de credito)")
    fechapago = models.DateTimeField(blank=True, help_text="Fecha pago")
    class Meta:
        indexes = [
            models.Index(fields=['pagoestadocuenta']),
        ]



# tabla dee control para manejo de correlativos
class Correlativo(models.Model):
    ExpedienteCatastro = models.PositiveIntegerField(null=True, blank=True,  help_text="Numero de Expediente de Catastro")	
    NumeroEstadoCuenta = models.PositiveIntegerField(null=True, blank=True,  help_text="Numero de Estado de Cuenta")
    NumeroLiquidacion = models.PositiveIntegerField(null=True, blank=True,  help_text="Numero de NumeroLiquidacion")
    NumeroPago = models.PositiveIntegerField(null=True, blank=True,  help_text="Numero de Recibo de pagos")
    NumeroNotaCredito = models.PositiveIntegerField(null=True, blank=True,  help_text="Numero de nota de credito")
    NumeroSolicitud = models.PositiveIntegerField(null=True, blank=True,  help_text="Numero de Solicitud FLUJO")
    NumeroCalculoMulta = models.PositiveIntegerField(null=True, blank=True,  help_text="Numero de calculo de multa")
    NumeroCalculoImpuesto = models.PositiveIntegerField(null=True, blank=True,  help_text="Numero calculo de impuesto")
    NumeroCorreccionImpuesto = models.PositiveIntegerField(null=True, blank=True,  help_text="Numero correccion impuesto Catastro")
    NumeroIC_Impuesto = models.PositiveIntegerField(null=True, blank=True,  help_text="Numero Impuesto Catastro")
    NumeroAE_Patente = models.PositiveIntegerField(null=True, blank=True,  help_text="Numero de licencia o patente de Indistria y comercio")
    NumeroAE_Patente_Generica = models.PositiveIntegerField(null=True, blank=True,  help_text="Numero de licencia o patente de Indistria y comercio genérica")
    Logo1 = models.ImageField(upload_to=logos_path,help_text="Logo 1 para reporte", null=True,blank =True)
    Logo2 = models.ImageField(upload_to=logos_path,help_text="Logo 2 para reporte", null=True,blank =True)




# Caranday ver 1.0
class Flujo(models.Model):
    numero = models.TextField(null=False,blank =False, unique=True, help_text="Numero de Solicitud. Correlativo.NumeroSolicitud")
    inmueble=models.ForeignKey(Inmueble, on_delete=models.PROTECT,help_text="Inmueble")
    pagoestadocuenta = models.ForeignKey(PagoEstadoCuenta, on_delete=models.PROTECT,help_text="ID Cabecera PAGO")
    fecha = models.DateTimeField(blank=True,null=True, help_text="Fecha creacion")
    ESTADO = (
        ('1', 'En Proceso'),
        ('2', 'Cerrado'),
    )
    estado= models.CharField(max_length=1, choices=ESTADO, default='1', help_text='Estado dela solicitud')
    ReportePdf = models.FileField(upload_to=flujoentrega_path,help_text="PDF soporte entrega de documentos", null=True,blank =True)
    class Meta:
        indexes = [
            models.Index(fields=['numero']),
        ]
    def __str__(self):
        return '%s - %s - %s' % (self.inmueble,self.pagoestadocuenta,self.estado)
    def save(self, *args, **kwargs):
        self.fecha = timezone.now()
        super().save(*args, **kwargs)


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
        ('0', 'Pendiente por Re-Enviar'),
        ('A', 'Imprimir Soporte Entrega Expediente')

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
    class Meta:
        indexes = [
            models.Index(fields=['flujo']),
        ]
    def save(self, *args, **kwargs):
        if self.estado=='1':
           self.envia_fecha = timezone.now()
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

################################ Impuesto Catastro
# MAESTRO 

    
# MAESTRO
# Porcentajes a aplicar al momento de calcular los TOTALES de impuesto en IC_Impuesto
class IC_ImpuestoCargos(models.Model):
    codigo = models.TextField(null=False,blank =False, unique=True, help_text="Codigo: multa, recargo, impuesto ") 
    descripcion = models.TextField(null=False,blank =False, unique=True, help_text="Descripcion")
    porcentaje  =  models.DecimalField(max_digits=22, decimal_places=8, default=Decimal(0.0), null=True,blank =True, help_text="Porcentaje")  
    habilitado = models.BooleanField(default=True, help_text="Esta activo?")
    APLICA = (
        ('C', 'Inmuebles Urbanos'),
        ('A', 'Actividades económicas'),
        ('V', 'Vehiculos'),
        ('P', 'Propaganda y publicidad'),
        ('X', 'Todos')
    )
    aplica= models.CharField(max_length=1, choices=APLICA, default='X', help_text='A que tipo de sector aplica')  
    def __str__(self):
        return '%s - %s - %s' % (self.codigo,self.porcentaje,self.aplica)
    

# Las correcciones son ajustes que hacen a cada periodo porque aunque estén por pagar, el contribuyente demuestra que se pago. 
# Las correcciones de deben hacer por cada soporte(foto del pago). 
# Ejemplo, si la foto del recibo hace referencia a dos periodos entonces se crea una corrección por esos dos periodos.
class IC_ImpuestoCorrecciones(models.Model):
    numero = models.TextField(null=False,blank =False, unique=True, help_text="Numero de Solicitud. Correlativo.NumeroCorreccionImpuesto")
    observaciones = models.TextField(null=True,blank =True, help_text="observaciones")
    fecha = models.DateTimeField(default=timezone.now, blank=True, help_text="fecha de registro")
    numerorecibo = models.TextField(null=True,blank =True, help_text="numero del recibo de pago como referencia")
    total =  models.DecimalField(max_digits=22, decimal_places=8, default=Decimal(0.0), null=True,blank =True, help_text="monto cancelado según el recibo de pago")  
    inmueble=models.ForeignKey(Inmueble, on_delete=models.PROTECT,help_text="Inmueble")

#Ese modelo permite corregir periodos ya cargados por deuda de un inmueble para no se cobrados
class IC_ImpuestoCorreccionesDetalle(models.Model):
    IC_impuestocorrecciones  = models.ForeignKey(IC_ImpuestoCorrecciones, on_delete=models.PROTECT,help_text="ID Impuesto Correcciones")  
    imagensoporte = models.ImageField(upload_to=correcciones_path, null=True, blank=True, help_text="Imagen de soporte")   

# MAESTRO
# Este modelo controla todos los periodos por inmueble pagados y  no pagados (por pagos o por correcciones)
class IC_ImpuestoPeriodo(models.Model):
    inmueble=models.ForeignKey(Inmueble, on_delete=models.PROTECT,help_text="Inmueble")
    periodo=models.ForeignKey(IC_Periodo, on_delete=models.PROTECT,help_text="Periodo")
    anio = models.PositiveIntegerField(null=True, blank=True,  help_text="Año")
    IC_impuestocorrecciones  = models.ForeignKey(IC_ImpuestoCorrecciones, null=True,blank =True,on_delete=models.PROTECT,help_text="ID Impuesto Correcciones. Sin dato es no se ha pagado con ninguna correccion")   
    pagoestadocuenta = models.ForeignKey(PagoEstadoCuenta, null=True,blank =True,on_delete=models.PROTECT,help_text="ID Cabecera PAGO, Sin dato es no se ha pagado") 
    def __str__(self):
        return '%s - %s - %s' % (self.inmueble.numero_expediente,self.periodo.periodo,self.anio)

class IC_Impuesto(models.Model):
    numero = models.TextField(null=False,blank =False, unique=True, help_text="Correlativo.NumeroIC_Impuesto")
    estadocuenta = models.ForeignKey(EstadoCuenta, null=True, blank=True,on_delete=models.PROTECT,help_text="ID Cabecera Estado de Cuenta")
    liquidacion = models.ForeignKey(Liquidacion, null=True, blank=True,on_delete=models.PROTECT,help_text="ID Cabecera liquidacion")
    zona = models.ForeignKey(Zona,on_delete=models.PROTECT, null=True,blank =True,help_text="Zona !! Base para calculo")
    basecalculobs =  models.DecimalField(max_digits=22, decimal_places=8, default=Decimal(0.0), null=True,blank =True, help_text="base imponible del tributo en referencia") 
    subtotal =  models.DecimalField(max_digits=22, decimal_places=8, default=Decimal(0.0), null=True,blank =True, help_text="suma de total_uso de ImpuestoDetalle") 
    multa =  models.DecimalField(max_digits=22, decimal_places=8, default=Decimal(0.0), null=True,blank =True, help_text="IC_ImpuestoCargos.porcentaje donde codigo=multa") 
    recargo =  models.DecimalField(max_digits=22, decimal_places=8, default=Decimal(0.0), null=True,blank =True, help_text="IC_ImpuestoCargos.porcentaje donde codigo=recargo") 
    interes =  models.DecimalField(max_digits=22, decimal_places=8, default=Decimal(0.0), null=True,blank =True, help_text="IC_ImpuestoCargos.porcentaje donde codigo=interes") 
    total =  models.DecimalField(max_digits=22, decimal_places=8, default=Decimal(0.0), null=True,blank =True, help_text="Total") 
    descuento  =  models.DecimalField(max_digits=22, decimal_places=8, default=Decimal(0.0), null=True,blank =True, help_text="descuento????") 
    grantotal =  models.DecimalField(max_digits=22, decimal_places=8, default=Decimal(0.0), null=True,blank =True, help_text="gran total")
    aniopagoini=models.PositiveIntegerField(null=True, blank=True,  help_text="Año hasta donde se calculo el impuesto")
    periodopagoini=models.PositiveIntegerField(null=True, blank=True,  help_text="Periodo  hasta donde se calculo el impuesto")
    aniopagofin=models.PositiveIntegerField(null=True, blank=True,  help_text="Año hasta donde se calculo el impuesto")
    periodopagofin=models.PositiveIntegerField(null=True, blank=True,  help_text="Periodo  hasta donde se calculo el impuesto")
    def __str__(self):
        return '%s - %s - %s - %s - %s - %s - %s - %s' % (self.numero,self.estadocuenta.numero,self.estadocuenta.inmueble.numero_expediente,self.total,self.aniopagoini,self.periodopagoini,self.aniopagofin,self.periodopagofin)
    
class IC_ImpuestoDetalle(models.Model):
    IC_impuesto  = models.ForeignKey(IC_Impuesto, on_delete=models.PROTECT,help_text="ID IC_Impuesto") 
    periodo=models.ForeignKey(IC_Periodo, on_delete=models.PROTECT,null=True,blank =True,help_text="Periodo de proceso")
    anio=models.PositiveIntegerField(null=True, blank=True,  help_text="Año de proceso")
    tipologia = models.ForeignKey (Tipologia, null=True,blank =True,on_delete=models.PROTECT,help_text="tipologia asociado") 
    area = models.DecimalField(max_digits=22, decimal_places=8, default=Decimal(0.0), null=False, help_text="Area en m2") 
    alicuota_articulo41=models.DecimalField(max_digits=22, decimal_places=8, default=Decimal(0.0), null=False, help_text="Alicuota") 
    base=models.DecimalField(max_digits=22, decimal_places=8, default=Decimal(0.0), null=False, help_text="area x aliuota_articulo41") 
    descuento=models.DecimalField(max_digits=22, decimal_places=8, default=Decimal(0.0), null=False, help_text="suma de descuentos (detalle en IC_ImpuestoDescuento)") 
    total=models.DecimalField(max_digits=22, decimal_places=8, default=Decimal(0.0), null=False, help_text="(area x alicuota_articulo41)-descuento") 
    sub_utilizado = models.BooleanField(default=False, help_text="subutilizado si o no") 
    multa = models.BooleanField(default=False, help_text="Aplico multa?") 
    tipo=models.ForeignKey(TipoInmueble,on_delete=models.PROTECT,null=True,blank =True,help_text="Tipo de Inmueble asociado para determinar si unifamiliar o multifamiliar")     
    def __str__(self):
        return '%s - %s - %s - %s - %s - %s' % (self.IC_impuesto.numero,self.anio,self.periodo.periodo,self.tipologia.descripcion,self.area,self.alicuota_articulo41) 

class IC_ImpuestoDetalleMora(models.Model):
    IC_impuesto  = models.ForeignKey(IC_Impuesto, on_delete=models.PROTECT,help_text="ID IC_Impuesto") 
    anio=models.PositiveIntegerField(null=True, blank=True,  help_text="Año de proceso")
    mes=models.PositiveIntegerField(null=True, blank=True,  help_text="Mes de proceso")
    tasa=models.DecimalField(max_digits=22, decimal_places=8, default=Decimal(0.0), null=False, help_text="tasa") 
    dias=models.PositiveIntegerField(null=True, blank=True,  help_text="dias")
    moramensual=models.DecimalField(max_digits=22, decimal_places=8, default=Decimal(0.0), null=False, help_text="moramensual") 
    interesmensual=models.DecimalField(max_digits=22, decimal_places=8, default=Decimal(0.0), null=False, help_text="interesmensual") 
    def __str__(self):
        return '%s - %s - %s - %s - %s - %s - %s' % (self.IC_impuesto.numero,self.anio,self.mes,self.tasa,self.dias,self.moramensual,self.interesmensual) 


# MAESTRO Configuración de descuentos por impuestos si la fecha del pago del impuesto esta contenida entra fechadesde y fecha 
# hasta aplica es descuento, si no tiene tipologia aplica a cualquier uso, si tiene tipologia solo aplica a ese uso. 
# Si seccion es detalle aplica a los usos pero si es total, aplica a la cabecera y en este caso si el registro 
class IC_ImpuestoDescuento(models.Model):
    descripcion = models.TextField(null=False,blank =False, unique=True, help_text="Descripcion")
    fechadesde  = models.DateField(blank=True,null=True,help_text="fecha Desde donde valida si aplica el descuento")
    fechahasta  = models.DateField(blank=True,null=True, help_text="fecha Hasta donde valida si aplica el descuento")
    porcentaje =  models.DecimalField(max_digits=22, decimal_places=8, default=Decimal(0.0), null=True,blank =True, help_text="Porcentaje de descuento") 
    tipologia = models.ForeignKey (Tipologia, null=True,blank =True,on_delete=models.PROTECT,help_text="tipologia asociado. Solo para Inmuebles. Si no tiene aplica a cualquier uso") 
    tipologia_categorizacion = models.ForeignKey (Tipologia_Categorizacion, null=True,blank =True,on_delete=models.PROTECT,help_text="tipologia asociado. Solo para Inmuebles. Si no tiene aplica a cualquier uso") 
    habilitado = models.BooleanField(default=True, help_text="Esta activo?")
    prontopago = models.BooleanField(default=False, help_text="Es de pronto pago?, True si y valida la fecha con la fecha de sistema, false aplica por fecha y periododo")
    inmueble=models.ForeignKey(Inmueble,blank=True,null=True, on_delete=models.PROTECT,help_text="Inmueble")

    APLICA = (
        ('C', 'Inmuebles Urbanos'),
        ('A', 'Actividades económicas'),
        ('V', 'Vehiculos'),
        ('P', 'Propaganda y publicidad'),
        ('X', 'Todos')
    )
    aplica= models.CharField(max_length=1, choices=APLICA, default='X', help_text='A que tipo de sector aplica')  
    def __str__(self):
        return '%s - %s - %s - %s - %s - %s' % (self.id,self.fechadesde,self.fechahasta,self.porcentaje,self.tipologia,self.descripcion)
    
# Descuentos aplicados por cada IC_ImpuestoDetalle
class IC_ImpuestoDetalleDescuentos(models.Model):
    IC_impuesto  = models.ForeignKey(IC_Impuesto, on_delete=models.PROTECT,null=True,blank =True,help_text="ID IC_Impuesto") 
    IC_impuestodescuento  = models.ForeignKey(IC_ImpuestoDescuento, on_delete=models.PROTECT,null=True,blank =True,help_text="ID Impuesto Inmueble")
    periodo=models.ForeignKey(IC_Periodo, on_delete=models.PROTECT,null=True,blank =True,help_text="Periodo de proceso")
    anio=models.PositiveIntegerField(null=True, blank=True,  help_text="Año de proceso")
    tipologia = models.ForeignKey (Tipologia, null=True,blank =True,on_delete=models.PROTECT,help_text="tipologia asociado")
    base =  models.DecimalField(max_digits=22, decimal_places=8, default=Decimal(0.0), null=True,blank =True, help_text="Base de calculo") 
    porcentaje =  models.DecimalField(max_digits=22, decimal_places=8, default=Decimal(0.0), null=True,blank =True, help_text="Porcentaje de descuento") 
    total =  models.DecimalField(max_digits=22, decimal_places=8, default=Decimal(0.0), null=True,blank =True, help_text="Total. Segun la tipologia:IC_ImpuestoDetalle.base * TC_ImpuestoDescuentos.porcentaje")  
    def __str__(self):
        return '%s - %s - %s - %s - %s - %s' % (self.IC_impuesto.numero,self.anio,self.periodo.periodo,self.tipologia.descripcion,self.IC_impuestodescuento.descripcion,self.porcentaje) 

class IC_Multa(models.Model):
    numero = models.TextField(null=False,blank =False, unique=True, help_text="Numero de pago")
    estadocuenta = models.ForeignKey(EstadoCuenta, null=True, blank=True,on_delete=models.PROTECT,help_text="ID Cabecera Estado de Cuenta")
    liquidacion = models.ForeignKey(Liquidacion, null=True, blank=True,on_delete=models.PROTECT,help_text="ID Cabecera liquidacion")
    #ActividadEconomica
    zona = models.ForeignKey(Zona,on_delete=models.PROTECT, null=True,blank =True,help_text="Zona !! Base para calculo")
    basecalculobs =  models.DecimalField(max_digits=22, decimal_places=8, default=Decimal(0.0), null=True,blank =True, help_text="base imponible del tributo en referencia") 
    subtotal =  models.DecimalField(max_digits=22, decimal_places=8, default=Decimal(0.0), null=True,blank =True, help_text="suma de total_uso de ImpuestoDetalle") 
    multa =  models.DecimalField(max_digits=22, decimal_places=8, default=Decimal(0.0), null=True,blank =True, help_text="IC_ImpuestoCargos.porcentaje donde codigo=multa") 
    recargo =  models.DecimalField(max_digits=22, decimal_places=8, default=Decimal(0.0), null=True,blank =True, help_text="IC_ImpuestoCargos.porcentaje donde codigo=recargo") 
    interes =  models.DecimalField(max_digits=22, decimal_places=8, default=Decimal(0.0), null=True,blank =True, help_text="IC_ImpuestoCargos.porcentaje donde codigo=interes") 
    total =  models.DecimalField(max_digits=22, decimal_places=8, default=Decimal(0.0), null=True,blank =True, help_text="Total") 
    descuento  =  models.DecimalField(max_digits=22, decimal_places=8, default=Decimal(0.0), null=True,blank =True, help_text="descuento????") 
    grantotal =  models.DecimalField(max_digits=22, decimal_places=8, default=Decimal(0.0), null=True,blank =True, help_text="gran total")
    aniopago=models.PositiveIntegerField(null=True, blank=True,  help_text="Año hasta donde se calculo el impuesto")
    periodopago=models.PositiveIntegerField(null=True, blank=True,  help_text="Periodo  hasta donde se calculo el impuesto")
    #Factor= models.DecimalField(max_digits=5, decimal_places=2, default=Decimal(0.0), null=True,blank =True, help_text="si es 1 es todo el año (4 periodos). Si es un periodo, el factor=0.75") 
    inmueble=models.ForeignKey(Inmueble, on_delete=models.PROTECT,help_text="Inmueble")

class IC_MultaDetalle(models.Model):
    IC_impuesto  = models.ForeignKey(IC_Impuesto, on_delete=models.PROTECT,help_text="ID IC_Impuesto") 
    IC_ImpuestoPeriodo  = models.ForeignKey(IC_ImpuestoPeriodo,null=True,blank =True, on_delete=models.PROTECT,help_text="ID IC_ImpuestoPeriodo. Por este D al momento de pagar esta Liquidacion entonces marco el periodo en IC_ImpuestoPeriodo como cancelado") 
    tipologia = models.ForeignKey (Tipologia, null=True,blank =True,on_delete=models.PROTECT,help_text="tipologia asociado") 
    area = models.DecimalField(max_digits=22, decimal_places=8, default=Decimal(0.0), null=False, help_text="Area en m2") 
    alicuota_articulo41=models.DecimalField(max_digits=22, decimal_places=8, default=Decimal(0.0), null=False, help_text="Alicuota") 
    base=models.DecimalField(max_digits=22, decimal_places=8, default=Decimal(0.0), null=False, help_text="area x aliuota_articulo41") 
    descuento=models.DecimalField(max_digits=22, decimal_places=8, default=Decimal(0.0), null=False, help_text="suma de descuentos (detalle en IC_ImpuestoDescuento)") 
    total=models.DecimalField(max_digits=22, decimal_places=8, default=Decimal(0.0), null=False, help_text="(area x alicuota_articulo41)-descuento") 
    sub_utilizado = models.BooleanField(default=False, help_text="subutilizado si o no") 
    tipo=models.ForeignKey(TipoInmueble,on_delete=models.PROTECT,null=True,blank =True,help_text="Tipo de Inmueble asociado para determinar si unifamiliar o multifamiliar")     


#********************************************************************************************************************
################################ Impuesto Actividades Economicas
#********************************************************************************************************************

#Maestro de tipos Actividades económicas
class AE_ActividadEconomica(models.Model):
    """
    Ramo
    """
    codigo = models.TextField(null=False,blank =False, unique=False,help_text="Código de clasificación actividad económica")
    descripcion  = models.TextField(null=False,blank =False, unique=True, help_text="Descripcion")
    alicuota=models.DecimalField(max_digits=22, decimal_places=8, default=Decimal(0.0), null=False, help_text="Alicuota") 
    minimo_tributable_mensual=models.DecimalField(max_digits=22, decimal_places=8, default=Decimal(0.0), null=False, help_text="") 
    minimo_tributable_anual=models.DecimalField(max_digits=22, decimal_places=8, default=Decimal(0.0), null=False, help_text="") 
    porcentaje_maximo_ingresos=models.DecimalField(max_digits=22, decimal_places=8, default=Decimal(0.0), null=False, 
                                                   help_text="este  impuesto no puede ser superior a este % de los ingresos brutos obtenidos en el mes") 
    observaciones = models.TextField(null=True,blank =True, help_text="observaciones")
    def __str__(self):
        return '%s - %s - %s' % (self.id,self.codigo,self.descripcion)
    
#Maestro de específico de Actividades económicas    
class AE_ActividadEconomicaDetalle(models.Model):
    AE_actividadeconomica = models.ForeignKey (AE_ActividadEconomica, null=True,blank =True,on_delete=models.PROTECT,help_text="Id AE_ActividadEconomica")
    codigo = models.TextField(null=False,blank =False, unique=False,help_text="Código de clasificación actividad económica")
    descripcion  = models.TextField(null=False,blank =False, unique=True, help_text="Descripcion")
    alicuota=models.DecimalField(max_digits=22, decimal_places=8, default=Decimal(0.0), null=False, help_text="Alicuota") 
    minimo_tributable_mensual=models.DecimalField(max_digits=22, decimal_places=8, default=Decimal(0.0), null=False, help_text="") 
    minimo_tributable_anual=models.DecimalField(max_digits=22, decimal_places=8, default=Decimal(0.0), null=False, help_text="") 
    porcentaje_maximo_ingresos=models.DecimalField(max_digits=22, decimal_places=8, default=Decimal(0.0), null=False, 
                                                   help_text="este  impuesto no puede ser superior a este % de los ingresos brutos obtenidos en el mes") 
    observaciones = models.TextField(null=True,blank =True, help_text="observaciones")
    def __str__(self):
        return '%s - %s - %s' % (self.AE_actividadeconomica.descripcion,self.codigo,self.descripcion)

# Maestro de Patente
class AE_Patente(models.Model):
    numero = models.TextField(null=False,blank =False, unique=True, help_text="Correlativo.NumeroAE_Patente para tipo_patente T o D, Correlativo.NumeroAE_Patente_Generica para tipo_patente G")
    propietario = models.ForeignKey(Propietario, null=True, blank=True,on_delete=models.PROTECT,help_text="ID Propietario")
    TIPO_PATENTE = (
        ('T', 'Temporal'),
        ('D', 'Definitiva'),
        ('G', 'Genérica')
    )
    tipo_patente= models.CharField(max_length=1, choices=TIPO_PATENTE, default='T', help_text='Tpo de patente o licencia')  
    numero_documento_representante  = models.TextField(null=False,blank =False,  help_text="Numero de documento (RIF)")
    nombre_representante  = models.TextField(null=False,blank =False,  help_text="Nombre o razon social")
    cargo_representante  = models.TextField(null=False,blank =False,  help_text="Cargo")
    telefono   = models.TextField(null=True,blank =True, help_text="Numero de teléfono secundario")
    periodo=models.ForeignKey(IC_Periodo, on_delete=models.PROTECT,help_text="Periodo de inscripcion")
    anio = models.PositiveIntegerField(null=True, blank=True,  help_text="Año")
    horario_desde  = models.TextField(null=False,blank =False, help_text="horario de trabajo desde formato militar")
    horario_hasta= models.TextField(null=False,blank =False,  help_text="horario de trabajo hasta: formato militar")
    nro_inmuebles=models.PositiveIntegerField(null=True, blank=True,  help_text="Numero de inmuebles")
    nro_solicitud=models.PositiveIntegerField(null=True, blank=True,  help_text="Numero de solicitud")
    nro_tomo=models.PositiveIntegerField(null=True, blank=True,  help_text="Numero de tomo")
    inmueble=models.ForeignKey(Inmueble, null=True,blank =True,on_delete=models.PROTECT,help_text="Inmueble")
    habilitado = models.BooleanField(default=True, help_text="Licencia activa si o no") 

    def __str__(self):
        return '%s - %s - %s - %s - %s' % (self.id,self.tipo_patente,self.numero,self.nombre_representante, self.cargo_representante) 

# Detalle de activiades econimicas por patente    
class AE_Patente_ActividadEconomica(models.Model):
    AE_patente = models.ForeignKey (AE_Patente, null=True,blank =True,on_delete=models.PROTECT,help_text="Id AE_patente")
    AE_actividadeconomica = models.ForeignKey (AE_ActividadEconomicaDetalle, null=True,blank =True,on_delete=models.PROTECT,help_text="Id AE_ActividadEconomica")
    def __str__(self):
        return '%s - %s - %s - %s - %s' % (self.id,self.AE_patente.tipo_patente,self.AE_patente.numero,self.AE_patente.propietario.nombre,self.AE_actividadeconomica.descripcion)


class NotaCredito(models.Model):
    numeronotacredito  = models.TextField(null=False,blank =False, unique=True, help_text="Numero de nota de credito")
    propietario = models.ForeignKey (Propietario, on_delete=models.PROTECT,help_text="Id Propietario")
    tipopago = models.ForeignKey(TipoPago,null=True,blank =True, on_delete=models.PROTECT,help_text="Id Tipo Pago")
    observacion  = models.TextField(null=True,blank =True, help_text="observacion")
    fecha = models.DateTimeField(blank=True,null=True, help_text="Fecha creacion")
    monto=models.DecimalField(max_digits=22, decimal_places=8, default=Decimal(0.0), null=False, help_text="monto original de la nota de credito")     
    saldo=models.DecimalField(max_digits=22, decimal_places=8, default=Decimal(0.0), null=False, help_text="saldo de la nota de credito")
    pagoestadocuenta = models.ForeignKey(PagoEstadoCuenta,null=True,blank =True, on_delete=models.PROTECT,help_text="Id Pago Liquidacion")
    observaciones = models.TextField(null=True,blank =True, help_text="observaciones")
    habilitado = models.BooleanField(default=True, help_text="Esta activo?")
    anula_usuario = models.TextField(null=True,blank =True, help_text="usuario que anula")
    anula_fecha = models.DateTimeField(blank=True, null=True,help_text="Fecha Anulacion")
    anula_observaciones = models.TextField(null=True,blank =True, help_text="observaciones por la anulacion")
    motivoanulacionpago = models.ForeignKey(MotivoAnulacionPago,null=True,blank =True, on_delete=models.PROTECT,help_text="ID MotivoAnulacionPago")

    def __str__(self):
        return '%s - %s - %s - %s - %s - %s' % (self.id,self.numeronotacredito,self.propietario.nombre,self.monto,self.saldo,self.pagoestadocuenta)  
     
    def save(self, *args, **kwargs):
        self.fecha = timezone.now()
        super().save(*args, **kwargs)


class ExcelDocument(models.Model):
    title = models.CharField(max_length=255)
    excel_file = models.FileField(upload_to=excel_path)

    def __str__(self):
        return self.title

class ExcelDocumentLOG(models.Model):
    pestana = models.TextField( help_text="Pestaña del archivo de excel")
    codigo = models.TextField( help_text="id del registro con error")
    error = models.TextField( help_text="codigo del error")
    fecha = models.DateTimeField(blank=False, help_text="Fecha registro error")
    def __str__(self):
        return '%s - %s - %s - %s' % (self.pestana,self.codigo,self.error,self.fecha)

    def save(self, *args, **kwargs):
        self.fecha = timezone.now()
        super().save(*args, **kwargs)



class CorridasBancarias(models.Model):
    """
    CorridasBancaria
    """
    bancocuenta = models.ForeignKey(BancoCuenta, on_delete=models.PROTECT,help_text="ID Banco")
    fecha = models.DateField(blank=False,null=False, help_text="Fecha creacion")
    referencia = models.TextField(null=False,blank =False, help_text="referencia")
    descripcion = models.TextField(null=False,blank =False, help_text="descripcion")
    monto=models.DecimalField(max_digits=22, decimal_places=8, default=Decimal(0.0), null=False, help_text="monto original de la nota de credito") 
    SITUADO = (
    ('R', 'Situado Regional'),
    ('N', 'Situado Nacional'),
    ('I', 'Interes'),
    ('D', 'Deposito'),
    ('T', 'Transferencia')
    )
    situado= models.CharField(max_length=1, choices=SITUADO, default='T', help_text='Tipo de transaccion')
    fechacreacion = models.DateTimeField(null=True,blank =True,  help_text="Fecha registro error")

    def __str__(self):
        return '%s - %s - %s - %s - %s - %s' % (self.bancocuenta.codigocuenta,self.fecha,self.referencia,self.descripcion,self.monto,self.situado)
    class Meta:
        unique_together = ('bancocuenta', 'fecha','referencia','descripcion','monto')
        ordering = ['bancocuenta','fecha','referencia','descripcion','monto'] 

    def save(self, *args, **kwargs):
        self.fechacreacion = timezone.now()
        super().save(*args, **kwargs)


class InmuebleCategorizacion(models.Model):
    id_inmueble = models.TextField(null=False,blank =False, unique=True,  help_text="numero_civico de expediente")
    tipo_inmueble = models.TextField(null=True,blank =True, help_text="numero_civico de expediente")
    id_ambito = models.TextField(null=True,blank =True, help_text="numero_civico de expediente")
    sector = models.TextField(null=True,blank =True, help_text="numero_civico de expediente")
    id_manzana = models.TextField(null=True,blank =True, help_text="numero_civico de expediente")
    id_parcela = models.TextField(null=True,blank =True, help_text="numero_civico de expediente")
    id_sub_parcela = models.TextField(null=True,blank =True, help_text="numero_civico de expediente")
    urb_barrio = models.TextField(null=True,blank =True, help_text="numero_civico de expediente")
    con_residencial = models.TextField(null=True,blank =True, help_text="numero_civico de expediente")
    edificio = models.TextField(null=True,blank =True, help_text="numero_civico de expediente")
    avenida = models.TextField(null=True,blank =True, help_text="numero_civico de expediente")
    via = models.TextField(null=True,blank =True, help_text="numero_civico de expediente")
    referencia = models.TextField(null=True,blank =True, help_text="numero_civico de expediente")
    telefono = models.TextField(null=True,blank =True, help_text="numero_civico de expediente")
    observaciones = models.TextField(null=True,blank =True, help_text="numero_civico de expediente")
    direccion = models.TextField(null=True,blank =True, help_text="numero_civico de expediente")
    total_construccion = models.TextField(null=True,blank =True, help_text="numero_civico de expediente")
    total_terreno = models.TextField( help_text="numero_civico de expediente")
    comunidad = models.ForeignKey(Comunidad, null=True,blank =True,on_delete=models.PROTECT,help_text="comunidad")





