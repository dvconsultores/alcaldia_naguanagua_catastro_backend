from .models import *
from .serializers import *
from django.contrib.auth import authenticate
from knox.models import AuthToken
from rest_framework.response import Response
from rest_framework import viewsets, status, generics
import re

def generate_token(username,password):
    user = authenticate(username=username, password=password)
    if user is not None:
        perfil = Perfil.objects.get(usuario=user)
        permisos = Permiso.objects.filter(perfil=perfil)
        dataPermisos = PermisoSerializer(instance=permisos, many=True).data
        return Response({'token':AuthToken.objects.create(user)[1],
                         'user_id': user.pk,
                         'email':user.email,
                         'username':user.username,
                         'modulo':perfil.modulo.nombre,
                         'permisos': dataPermisos
                        }, status=status.HTTP_200_OK)
    else:
        return Response('invalid credentials', status=status.HTTP_400_BAD_REQUEST)

def create_user(username,password,email):
    if(User.objects.filter(username=username,email=email).count() > 0):
        return Response('the username/email is already in use', status=status.HTTP_400_BAD_REQUEST)
    else:
        user = User.objects.create_user(username=username,
                                 email=email,
                                 password=password)
        user.save()
        return generate_token(username,password)
    
def change_password(user,password):
    if re.fullmatch(re.compile(r"[A-Za-z0-9]+"), password):
        user.set_password(password)
        return Response('the password updated', status=status.HTTP_200_OK)
    else:
        return Response('The new password not match the security pattern', status=status.HTTP_400_BAD_REQUEST)
    

def Crear_Estado_Cuenta(request):
    if (True):
        print('ĺucas')
        print(request)
        return Response('the password updated', status=status.HTTP_200_OK)
    else:
        return Response('The new password not match the security pattern', status=status.HTTP_400_BAD_REQUEST)