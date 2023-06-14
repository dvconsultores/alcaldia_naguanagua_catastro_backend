from .models import *
from .serializers import *
from django.contrib.auth import authenticate
from knox.models import AuthToken
from rest_framework.response import Response
from rest_framework import viewsets, status, generics
import re
from datetime import datetime,timedelta

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
                         'departamento':perfil.departamento.nombre,
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
        perfil=Perfil(usuario=user,
                      tipo='U',
                      activo=True)
        perfil.save()
        return generate_token(username,password)
    
def change_password(user,password):
    if re.fullmatch(re.compile(r"[A-Za-z0-9]+"), password):
        user.set_password(password)
        return Response('the password updated', status=status.HTTP_200_OK)
    else:
        return Response('The new password not match the security pattern', status=status.HTTP_400_BAD_REQUEST)
    
def Crear_Estado_Cuenta(request):
    if (request):
        items=request['detalle']
        correlativo=Correlativo.objects.get(id=1)
        valor_petro=UnidadTributaria.objects.get(habilitado=True).monto
        valor_tasabcv=TasaBCV.objects.get(habilitado=True).monto
        tipoflujo = None if request['flujo']==None else TipoFlujo.objects.get(id=request['flujo'])
        inmueble = None if request['inmueble']==None else Inmueble.objects.get(id=request['inmueble'])
        propietario = Propietario.objects.get(id=request['propietario'])
        Cabacera=EstadoCuenta(
            numero=correlativo.NumeroEstadoCuenta,
            tipoflujo=tipoflujo,
            inmueble=inmueble,
            fecha=str(datetime.now()),
            propietario=propietario,
            observaciones=request['observacion'],
            valor_petro=valor_petro,
            valor_tasa_bs=valor_tasabcv,
            monto_total=request['monto_total']
        )
        Cabacera.save()
        for detalle in items:
            tasa_multa_id = TasaMulta.objects.get(id=detalle['tasa_multa_id'])

            Detalle=EstadoCuentaDetalle(
                estadocuenta=Cabacera,
                tasamulta=tasa_multa_id,               
                monto_unidad_tributaria=detalle['monto_unidad_tributaria'],
                monto_tasa=detalle['calculo'],
                cantidad=detalle['cantidad']                     
            )
            Detalle.save()
        correlativo.NumeroEstadoCuenta=correlativo.NumeroEstadoCuenta+1
        correlativo.save()
        return Response('Insert EstadoCuenta OK', status=status.HTTP_200_OK)
    else:
        return Response('Insert EstadoCuenta NOT Ok', status=status.HTTP_400_BAD_REQUEST)
    
def Crear_Liquidacion(request):
    if (request):
        items=request['detalle']
        correlativo=Correlativo.objects.get(id=1)
        valor_petro=UnidadTributaria.objects.get(habilitado=True).monto
        valor_tasabcv=TasaBCV.objects.get(habilitado=True).monto
        tipoflujo = None if request['flujo']==None else TipoFlujo.objects.get(id=request['flujo'])
        inmueble = None if request['inmueble']==None else Inmueble.objects.get(id=request['inmueble'])
        propietario = Propietario.objects.get(id=request['propietario'])
        estadocuenta = None if request['estadocuenta']==None else EstadoCuenta.objects.get(id=request['estadocuenta'])
        Cabacera=Liquidacion(
            numero=correlativo.NumeroLiquidacion,
            tipoflujo=tipoflujo,
            estadocuenta=estadocuenta,
            inmueble=inmueble,
            fecha=str(datetime.now()),
            propietario=propietario,
            observaciones=request['observacion'],
            valor_petro=valor_petro,
            valor_tasa_bs=valor_tasabcv,
            monto_total=request['monto_total']
        )
        Cabacera.save()
        for detalle in items:
            tasa_multa_id = TasaMulta.objects.get(id=detalle['tasamulta'])
            Detalle=LiquidacionDetalle(
                liquidacion=Cabacera,
                tasamulta=tasa_multa_id,               
                monto_unidad_tributaria=detalle['monto_unidad_tributaria'],
                monto_tasa=detalle['monto_tasa'],
                cantidad=detalle['cantidad']                     
            )
            Detalle.save()
            # actualizamos 
        correlativo.NumeroLiquidacion=correlativo.NumeroLiquidacion+1
        correlativo.save()

        #marco el estado de cuenta para que no aparezca denuevo en las listas de estados de cuenta disponibles
        # con eso validamos que no se genere dos liquidaciones con el mismo estado de cuenta.
        estadocuenta.habilitado=False
        estadocuenta.save()
        return Response('Insert Liquidacion OK', status=status.HTTP_200_OK)
    else:
        return Response('Insert Liquidacion NOT Ok', status=status.HTTP_400_BAD_REQUEST)


def Crear_Pago(request):
    if (request):
        items=request['detalle']
        correlativo=Correlativo.objects.get(id=1)
        propietario = Propietario.objects.get(id=request['propietario'])
        liquidacion = None if request['liquidacion']==None else Liquidacion.objects.get(id=request['liquidacion'])
        Cabacera=PagoEstadoCuenta(
            numero=correlativo.NumeroPago,
            liquidacion=liquidacion,
            fecha=str(datetime.now()),
            observaciones=request['observacion'],
            monto=request['monto']
        )
        Cabacera.save()
        for detalle in items:
            tipopago = None if detalle['tipopago']==None else TipoPago.objects.get(id=detalle['tipopago'])
            bancocuenta = None if detalle['bancocuenta']==None else BancoCuenta.objects.get(id=detalle['bancocuenta'])
            Detalle=PagoEstadoCuentaDetalle(
                pagoestadocuenta=Cabacera,
                tipopago = tipopago,
                bancocuenta=bancocuenta,
                monto  = detalle['monto'],
                fechapago =  str(datetime.now()),#detalle['fechapago'],
                nro_referencia = detalle['referencia']
            )
            Detalle.save()
        #crear inmuebles
        InmuebleNew=Inmueble(numero_expediente=correlativo.ExpedienteCatastro)
        InmuebleNew.save()
        InmueblePropietariosNew=InmueblePropietarios(inmueble=InmuebleNew,
                                                     propietario=propietario)
        InmueblePropietariosNew.save()        
        #crear flujo
        FlujoNew=Flujo(inmueble=InmuebleNew,
                       pagoestadocuenta=Cabacera,
                       fecha=str(datetime.now()),
                       estado='1')
        FlujoNew.save()
        departamentoenvia=Departamento.objects.get(nombre='Admin')
        usuarioenvia=User.objects.get(username='Admin')
        departamentorecibe=Departamento.objects.get(nombre='Taquilla Catastro')
        FlujoDetalleNew=FlujoDetalle(
            flujo=FlujoNew,
            estado='1',
            tarea='1',
            departamento_envia=departamentoenvia,
            envia_usuario=usuarioenvia,
            departamento_recibe=departamentorecibe
        )
        FlujoDetalleNew.save()
        #actualiza corrrelativo de pago
        correlativo.NumeroPago=correlativo.NumeroPago+1
        correlativo.ExpedienteCatastro=correlativo.ExpedienteCatastro+1
        correlativo.save()
        #marca la liquidacion como procesada
        liquidacion.habilitado=False
        liquidacion.save()

        return Response('Insert Pago OK', status=status.HTTP_200_OK)
    else:
        return Response('Insert Pago NOT Ok', status=status.HTTP_400_BAD_REQUEST)


def Crear_Estado_Cuenta1(request):
    if (request):
        items=request['detalle']
        correlativo=Correlativo.objects.get(id=1)
        valor_petro=UnidadTributaria.objects.get(habilitado=True).monto
        valor_tasabcv=TasaBCV.objects.get(habilitado=True).monto
        #print('todo')
        #print(request)
        #print('detalle')
        #print(items)

        print('numero',correlativo.NumeroEstadoCuenta)
        print('tipoflujo',request['flujo'])
        print('fecha',str(datetime.now()))
        print('propietario',request['propietario'])
        print('observaciones',request['observacion'])
        print('valor_petro',valor_petro)
        print('valor_tasa_bs',valor_tasabcv)
        print('monto_total',request['monto_total'])
        Cabacera=EstadoCuenta(
            numero=correlativo,
            tipoflujo=request['flujo'],
            fecha=str(datetime.now()),
            propietario=request['propietario'],
            observaciones=request['observacion'],
            valor_petro=valor_petro,
            valor_tasa_bs=valor_tasabcv,
            monto_total=request['monto_total']
        )
        Cabacera.save()
        

        for detalle in items:
            #print('estadocuenta')
            print('tasamulta',detalle['tasa_multa_id'])

            #monto_unidad_tributaria=TasaMulta.objects.get(id=detalle['tasa_multa_id']).unidad_tributaria
            #print('monto_unidad_tributaria',monto_unidad_tributaria)
            #print('monto_tasa',monto_unidad_tributaria*detalle['cantidad']*valor_petro*valor_tasabcv)
            ##print('monto_tasa',detalle['monto_unidad_tributaria']*detalle['cantidad']*valor_petro*valor_tasabcv)

            print('monto_unidad_tributaria',detalle['monto_unidad_tributaria'])
            print('monto_tasa',detalle['calculo'])
            print('cantidad',detalle['cantidad'])
            Detalle=EstadoCuentaDetalle(
                estadocuenta=Cabacera,
                tasamulta=detalle['tasa_multa_id'],                     
                monto_unidad_tributaria=detalle['monto_unidad_tributaria'],
                monto_tasa=detalle['calculo'],
                cantidad=detalle['cantidad']                     
            )
            Detalle.save()
        correlativo.NumeroEstadoCuenta=correlativo.NumeroEstadoCuenta+1
        correlativo.save()
        return Response('Insert OK', status=status.HTTP_200_OK)
    else:
        return Response('Insert NOT Ok', status=status.HTTP_400_BAD_REQUEST)
    
