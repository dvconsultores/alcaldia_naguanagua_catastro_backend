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

