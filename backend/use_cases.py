from .models import *
from .serializers import *
from django.contrib.auth import authenticate
from knox.models import AuthToken
from rest_framework.response import Response
from rest_framework import viewsets, status, generics
import re
from datetime import datetime,timedelta,date
from pyDolarVenezuela import price
import pyBCV
import datetime
from django.db.models import Max,Min,Sum,Q
import pandas as pd
import os
import calendar
from decimal import Decimal
import math  # Importa la biblioteca math
from django.db import IntegrityError

# obtener la cantidad de dias que tiene un mes en un año especifico
def obtener_cantidad_dias(year, month):
    cantidad_dias = calendar.monthrange(year, month)[1]
    return cantidad_dias


# calcula los meses trascurridos ente dos fechas
def meses_transcurridos(fecha_desde, fecha_hasta):
    diff = fecha_hasta.year - fecha_desde.year
    diff_months = fecha_hasta.month - fecha_desde.month
    total_meses = (diff * 12 + diff_months) +0 # le sumo un mes mas considerando que el mes en curso se considera moroso
    return total_meses


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
                         'caja':perfil.caja,
                         'departamento':perfil.departamento.nombre,
                         'aplica':perfil.departamento.aplica,
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
        tipoflujo = None if request['flujo']==None else TipoFlujo.objects.get(codigo=request['flujo'])
        inmueble = None if request['inmueble']==None else Inmueble.objects.get(id=request['inmueble'])
        propietario = Propietario.objects.get(id=request['propietario'])
        Cabacera=EstadoCuenta(
            numero=correlativo.NumeroEstadoCuenta,
            tipoflujo=tipoflujo,
            inmueble=inmueble,
            fecha=str(date.today()),
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
            fecha=str(date.today()),
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
        #liquidacion = None if request['liquidacion']==None else Liquidacion.objects.get(id=request['liquidacion'])
        liquidacion = Liquidacion.objects.get(id=request['liquidacion'])
        Cabacera=PagoEstadoCuenta(
            numero=correlativo.NumeroPago,
            liquidacion=liquidacion,
            fecha=str(date.today()),
            observaciones=request['observacion'],
            caja=request['caja'],
            monto=request['monto'],
            monto_cxc=request['monto_cxc']
        )
        # evalua si se pago de mas para crear la nota de credito a favor del contribuyente
        print(request['monto'],request['monto_cxc'])
        monto_credito= float(request['monto'])-float(request['monto_cxc'])
        if monto_credito>0:
            tipopago = TipoPago.objects.get(codigo='N')
            notacredito=NotaCredito(
                numeronotacredito  = correlativo.NumeroNotaCredito,
                tipopago = tipopago,
                propietario = propietario,
                observacion  = '',
                fecha=str(date.today()),
                monto=   monto_credito, 
                saldo=    monto_credito
            )
            notacredito.save()
            correlativo.NumeroNotaCredito=correlativo.NumeroNotaCredito+1
            correlativo.save()
        Cabacera.save()
        for detalle in items:
            tipopago = None if detalle['tipopago']==None else TipoPago.objects.get(codigo=detalle['tipopago'])
            bancocuenta = None if detalle['bancocuenta']==None else BancoCuenta.objects.get(id=detalle['bancocuenta'])
            Detalle=PagoEstadoCuentaDetalle(
                pagoestadocuenta=Cabacera,
                tipopago = tipopago,
                bancocuenta=bancocuenta,
                monto  = float(detalle['monto']),
                fechapago =  str(date.today()),#detalle['fechapago'],
                nro_referencia = detalle['nro_referencia'],
                nro_aprobacion = detalle['nro_aprobacion'],
                nro_lote = detalle['nro_lote']
            )
            if detalle['tipopago']=='N':
                notacredito=NotaCredito.objects.get(propietario = propietario,numeronotacredito=detalle['nro_referencia'])
                notacredito.saldo=float(notacredito.saldo)-float(detalle['monto'])
                notacredito.save()
                print('nota de credito',float(notacredito.saldo),float(detalle['monto']),float(notacredito.saldo)-float(detalle['monto']))
            Detalle.save()
        #actualiza el correlativo de numero de pagos
        correlativo.NumeroPago=correlativo.NumeroPago+1  
        # solo aplica cuando la peticion viene de catastro y es una de esas 3 opciones
        if liquidacion.tipoflujo.codigo in ['1', '2', '3']:
            #solo aplica cuanbdo es inscripcion, el inmueble se debe crear nuevo
            if liquidacion.tipoflujo.codigo=='1':
                #crear inmuebles
                InmuebleNew=Inmueble(numero_expediente=correlativo.ExpedienteCatastro,
                                     fecha_inscripcion=date.today())
                InmuebleNew.save()
                InmueblePropietariosNew=InmueblePropietarios(inmueble=InmuebleNew,
                                                            propietario=propietario,
                                                            fecha_compra=date.today())
                InmueblePropietariosNew.save()
                InmueblePropiedadNew=InmueblePropiedad(inmueble=InmuebleNew)
                InmueblePropiedadNew.save()
                InmuebleTerrenoNew=InmuebleTerreno(inmueble=InmuebleNew)
                InmuebleTerrenoNew.save()
                InmuebleConstruccionNew=InmuebleConstruccion(inmueble=InmuebleNew)
                InmuebleConstruccionNew.save()
                InmuebleValoracionTerrenoNew=InmuebleValoracionTerreno(inmueble=InmuebleNew)
                InmuebleValoracionTerrenoNew.save()
                InmuebleUbicacionNew=InmuebleUbicacion(inmueble=InmuebleNew)
                InmuebleUbicacionNew.save()
                InmuebleFaltanteNew=InmuebleFaltante(inmueble=InmuebleNew)
                InmuebleFaltanteNew.save()
                #actualiza en correlativo del expediente 
                correlativo.ExpedienteCatastro=correlativo.ExpedienteCatastro+1
            else:
                #seleciona el inmueble ya seleccionado desde la liquidacion
                InmuebleNew=Inmueble.objects.get(id=liquidacion.inmueble.id)
            #crear flujo
            FlujoNew=Flujo(numero=correlativo.NumeroSolicitud,
                           inmueble=InmuebleNew,
                           pagoestadocuenta=Cabacera,
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
            #actualiza en correlativo del expediente 
            correlativo.NumeroSolicitud=correlativo.NumeroSolicitud+1
        #actualiza corrrelativo de pago
        correlativo.save()
        #marca la liquidacion como procesada
        liquidacion.habilitado=False
        liquidacion.save()

        return Response('Insert Pago OK', status=status.HTTP_200_OK)
    else:
        return Response('Insert Pago NOT Ok', status=status.HTTP_400_BAD_REQUEST)

def Crear_Inmueble_Propietario(request):
    if (request):
        inmueble = Inmueble.objects.get(id=request['inmueble'])
        propietario = Propietario.objects.get(id=request['propietario'])
        inmubelepropietario=InmueblePropietarios(
            inmueble=inmueble,
            propietario=propietario,
            fecha_compra=request['fecha_compra']
        )
        inmubelepropietario.save()
        return Response('Insert OK', status=status.HTTP_200_OK)
    else:
        return Response('Insert NOT Ok', status=status.HTTP_400_BAD_REQUEST)
    
# Verificación y Cálculo de multas y mora aplicando los Artículos 99 y 101 de la
# ORDENANZA DE REFORMA PARCIAL A LA ORDENANZA DE IMPUESTO SOBRE INMUEBLES URBANOS
# Año MMXX República Bolivariana de Venezuela-Estado Carabobo - Municipio Naguanagua .N° 225 Extraordinario.de Fecha 15/SEPTIEMBRE/2020
# con ajustes en las alicuotas y criterios segun Oficina Legal de la alcaldia de Naguanagua
#   Creado por:Jorge Cuauro
# Fecha creado:07-2023
def Multa_Inmueble(request):
    if (request):
        data = []
        if (request['inmueble']):
            today = date.today()
            #Ubicar la fecha de compra

            oInmueblePropietarios = InmueblePropietarios.objects.get(propietario=request['propietario'],inmueble=request['inmueble'])
            bmodificacion_paga=oInmueblePropietarios.modificacion_paga #si esta en true es que el proceso de modificacion de porpietario se culminó en su momento
            fecha_compra =oInmueblePropietarios.fecha_compra
            bModifica=True if (((today-fecha_compra).days)>90 and bmodificacion_paga==False) else False

            oInmueble = Inmueble.objects.get(id=request['inmueble'])
            binscripcion_paga=oInmueble.inscripcion_paga #si esta en true es que el proceso de incripción se cuminó en su momento
            fecha_inscripcion = oInmueble.fecha_inscripcion
            bInscripcion=True if (((today-fecha_inscripcion).days)>90 and binscripcion_paga==False) else False
            
            diferenciac=today-fecha_compra
            diferenciai=today-fecha_inscripcion
            print('fecha_inscripcion:',fecha_inscripcion,'today:',today,'diferencia:',diferenciai.days,'bInscripcion:',bInscripcion)

            print('fecha_compra:',fecha_compra,'today:',today,'diferencia:',diferenciac.days,'bModifica:',bModifica)

            if (bModifica or bInscripcion): # Artículo 20
                baseCalculo = UnidadTributaria.objects.get(habilitado=True)
                baseCalculoBs= float(baseCalculo.monto)
                if bInscripcion:
                    fechaVencidaI=fecha_inscripcion+ datetime.timedelta(days=90) # Sumar los 90 dias de plazo a la fecha vencida para determinar el periodo vencido
                    mesesVencidosI = meses_transcurridos(fechaVencidaI, today)
                    print("Meses Vencidos Inscripcion:", mesesVencidosI)
                    #Artículo 99
                    MultaMinInscripcionUni=0 * baseCalculoBs  #Si no maneja una multa mínima, coloque 0 !!!!! No implementado!!!
                    alicuotaMultaInscripcionUni=0.011111111
                    alicuotaMoraInscripcionUni=0.05 # por año de mora hasta 10 años

                    MultaMinInscripcionMULTI=0 * baseCalculoBs #Si no maneja una multa mínima, coloque 0 !!!!! No implementado!!!
                    alicuotaMultaInscripcionMULTI=0.02
                    alicuotaMoraInscripcionMULTI=0.033333333  # por año de mora hasta 10 años


                if bModifica:
                    fechaVencidaM=fecha_compra+ datetime.timedelta(days=90) # Sumar los 90 dias de plazo a la fecha vencida para determinar el periodo vencido
                    mesesVencidosM= meses_transcurridos(fechaVencidaM, today)
                    print("Meses Vencidos Modificacion:", mesesVencidosM)
                    #Artículo 101
                    MultaMinModificaUni=0 * baseCalculoBs #Si no maneja una multa mínima, coloque 0 !!!!! No implementado!!!
                    alicuotaMultaModificaUni=0.033
                    alicuotaMoraModificaUni=0.025 # por año de mora hasta 10 años
                    
                    MultaMinModificaMULTI=0 * baseCalculoBs #Si no maneja una multa mínima, coloque 0 !!!!! No implementado!!!
                    alicuotaMultaModificaMULTI=0.033
                    alicuotaMoraModificaMULTI=0.05 # por año de mora hasta 10 años (ojo por m2)
                
                terreno=InmuebleValoracionTerreno.objects.get(inmueble=request['inmueble'])
                ocupacion=InmuebleValoracionConstruccion.objects.filter(inmueblevaloracionterreno=terreno.id)
                print(terreno)
                #print(ocupacion)
                for dato in ocupacion:
                    # Validar la multa por los m2 del inmueble si esa multa es menor al mínimo, la multa final sera el mínimo
                    metrosCuadrados=float(dato.area)
                    if (dato.tipo.tipo=='U'): #Unifamiliar
                        if bInscripcion:
                            multa=metrosCuadrados*alicuotaMultaInscripcionUni
                            if MultaMinInscripcionUni: # Aca valida si es diferente de 0 osea que tendrá un mínimo, de lo contrario la multa es la calculada segun los m2
                                multa=multa if multa>MultaMinInscripcionUni else MultaMinInscripcionUni
                            moraFraccionada=alicuotaMoraInscripcionUni/12  # determinar la fraccion, Ya que la multa se calcula por mes en mora y este el multipica por la multa/12
                            mora=moraFraccionada*mesesVencidosI*metrosCuadrados
                            item = {
                                'codigo':'IC_MIU',
                                'aplica':'Multa Inscripcion Uni  Art.99',
                                #'tipologia':dato.tipologia.id,
                                #'sub_utilizado':dato.sub_utilizado,
                                #'tipo':dato.tipo.id,
                                'Uso':dato.tipologia.descripcion,
                                'tipo':dato.tipo.descripcion,
                                'Unifamiliar':dato.tipo.tipo,
                                #'fecha_construccion':dato.fecha_construccion,
                                '(a) area':dato.area,
                                '(b) multa Art.99':alicuotaMultaInscripcionUni,
                                '(c) multa Petro (a * b)':multa,
                                '(d) BASE FISCAL BS':baseCalculoBs, 
                                'MULTA Bs A PAGAR (c * d)':multa*baseCalculoBs,
                                '(e) mora Art.99':alicuotaMoraInscripcionUni,
                                '(f) moraFraccionada (e / 12)':moraFraccionada,
                                'fecha compra ':fecha_inscripcion,
                                'fecha vencida':fechaVencidaI,
                                'fecha hoy    ':today,
                                '(h) meses vencido':mesesVencidosI,
                                '(g) mora Petro (f * h * a)':mora,
                                'MORA  Bs A PAGAR (g * d)':mora*baseCalculoBs,
                            }
                            data.append(item)
                        if bModifica:
                            multa=metrosCuadrados*alicuotaMultaModificaUni
                            if MultaMinModificaUni: # Aca valida si es diferente de 0 osea que tendrá un mínimo, de lo contrario la multa es la calculada segun los m2
                                multa=multa if multa>MultaMinModificaUni else MultaMinModificaUni
                            moraFraccionada=alicuotaMoraModificaUni/12  # determinar la fraccion, Ya que la multa se calcula por mes en mora y este el multipica por la multa/12
                            mora=moraFraccionada*mesesVencidosM*metrosCuadrados
                            item = {
                                'codigo':'IC_MMU',
                                'aplica':'Multa Modifica Uni Art.101',
                                #'tipologia':dato.tipologia.id,
                                #'sub_utilizado':dato.sub_utilizado,
                                #'tipo':dato.tipo.id,
                                'Uso':dato.tipologia.descripcion,
                                'tipo':dato.tipo.descripcion,
                                'Unifamiliar':dato.tipo.tipo,
                                #'fecha_construccion':dato.fecha_construccion,
                                '(a) area':dato.area,
                                '(b) multa Art.101':alicuotaMultaModificaUni,
                                '(c) multa Petro (a * b)':multa,
                                '(d) BASE FISCAL BS':baseCalculoBs, 
                                'MULTA Bs A PAGAR (c * d)':multa*baseCalculoBs,
                                '(e) mora Art.101':alicuotaMoraModificaUni,
                                '(f) moraFraccionada (e / 12)':moraFraccionada,
                                'fecha compra ':fecha_compra,
                                'fecha vencida':fechaVencidaM,
                                'fecha hoy    ':today,
                                '(h) meses vencido':mesesVencidosM,
                                '(g) mora Petro (f * h * a)':mora,
                                'MORA  Bs A PAGAR (g * d)':mora*baseCalculoBs,
                            }
                            data.append(item)

                    else: #MULTIfamiliar
                        if bInscripcion:
                            multa=metrosCuadrados*alicuotaMultaInscripcionMULTI
                            if MultaMinInscripcionMULTI: # Aca valida si es diferente de 0 osea que tendrá un mínimo, de lo contrario la multa es la calculada segun los m2
                                multa=multa if multa>MultaMinInscripcionMULTI else MultaMinInscripcionMULTI
                            moraFraccionada=alicuotaMoraInscripcionMULTI/12  # determinar la fraccion, Ya que la multa se calcula por mes en mora y este el multipica por la multa/12
                            mora=moraFraccionada*mesesVencidosI*metrosCuadrados
                            item = {
                                'codigo':'IC_MMU',
                                'aplica':'Multa Inscripcion MULTI  Art.99',
                                #'tipologia':dato.tipologia.id,
                                #'sub_utilizado':dato.sub_utilizado,
                                #'tipo':dato.tipo.id,
                                'Uso':dato.tipologia.descripcion,
                                'tipo':dato.tipo.descripcion,
                                'Unifamiliar':dato.tipo.tipo,
                                #'fecha_construccion':dato.fecha_construccion,
                                '(a) area':dato.area,
                                '(b) multa Art.99':alicuotaMultaInscripcionMULTI,
                                '(c) multa Petro (a * b)':multa,
                                '(d) BASE FISCAL BS':baseCalculoBs, 
                                'MULTA Bs A PAGAR (c * d)':multa*baseCalculoBs,
                                '(e) mora Art.99':alicuotaMoraInscripcionMULTI,
                                '(f) moraFraccionada (e / 12)':moraFraccionada,
                                'fecha compra ':fecha_inscripcion,
                                'fecha vencida':fechaVencidaI,
                                'fecha hoy    ':today,
                                '(h) meses vencido':mesesVencidosI,
                                '(g) mora Petro (f * h * a)':mora,
                                'MORA  Bs A PAGAR (g * d)':mora*baseCalculoBs,
                            }
                            data.append(item)
                        if bModifica:
                            multa=metrosCuadrados*alicuotaMultaModificaMULTI
                            if MultaMinModificaMULTI: # Aca valida si es diferente de 0 osea que tendrá un mínimo, de lo contrario la multa es la calculada segun los m2
                                multa=multa if multa>MultaMinModificaMULTI else MultaMinModificaMULTI
                            moraFraccionada=alicuotaMoraModificaMULTI/12  # determinar la fraccion, Ya que la multa se calcula por mes en mora y este el multipica por la multa/12
                            mora=moraFraccionada*mesesVencidosM*metrosCuadrados
                            item = {
                                'codigo':'IC_MIM',
                                'aplica':'Multa Modifica MULTI  Art.101',
                                'Uso':dato.tipologia.descripcion,
                                #'sub_utilizado':dato.sub_utilizado,
                                #'tipo':dato.tipo.id,
                                'tipo':dato.tipo.descripcion,
                                'Unifamiliar':dato.tipo.tipo,
                                #'fecha_construccion':dato.fecha_construccion,
                                '(a) area':dato.area,
                                '(b) multa Art.101':alicuotaMultaModificaMULTI,
                                '(c) multa Petro (a * b)':multa,
                                '(d) BASE FISCAL BS':baseCalculoBs, 
                                'MULTA Bs A PAGAR (c * d)':multa*baseCalculoBs,
                                '(e) mora Art.101':alicuotaMoraModificaMULTI,
                                '(f) moraFraccionada (e / 12)':moraFraccionada,
                                'fecha compra ':fecha_compra,
                                'fecha vencida':fechaVencidaM,
                                'fecha hoy    ':today,
                                '(h) meses vencido':mesesVencidosM,
                                '(g) mora Petro (f * h * a)':mora,
                                'MORA  Bs A PAGAR (g * d)':mora*baseCalculoBs,
                            }
                            data.append(item)
                #cabecera = {
                #    'aplica':'Multa Modifica MULTI  Art.101',
                #    #'tipologia':dato.tipologia.id,
                #    #'sub_utilizado':dato.sub_utilizado,
                #    #'tipo':dato.tipo.id,
                #    'tipo':dato.tipo.descripcion,
                #    'Unifamiliar':dato.tipo.tipo,
                #    #'fecha_construccion':dato.fecha_construccion,
                #                '(a) area':dato.area,
                #                '(b) multa Art.101':alicuotaMultaModificaMULTI,
                #                '(c) multa Petro (a * b)':multa,
                #                '(d) BASE FISCAL BS':baseCalculoBs, 
                #                'MULTA Bs A PAGAR (c * d)':multa*baseCalculoBs,
                #                '(e) mora Art.101':alicuotaMoraModificaMULTI,
                #                '(f) moraFraccionada (e / 12)':moraFraccionada,
                #                'fecha compra ':fecha_compra,
                #                'fecha vencida':fechaVencidaM,
                #                'fecha hoy    ':today,
                #                '(h) meses vencido':mesesVencidosM,
                #                '(g) mora Petro (f * h * a)':mora,
                #                'MORA  Bs A PAGAR (g * d)':mora*baseCalculoBs,
                #}
                #data.append(item)
            return Response(data, status=status.HTTP_200_OK)
        return Response('Insert OK', status=status.HTTP_200_OK)
    else:
        return Response('Insert NOT Ok', status=status.HTTP_400_BAD_REQUEST)
    



#****************************************************************************************************
#ARTÍCULO 49: El impuesto autoliquidado sobre la base de la declaración del valor fiscal del
#inmueble realizada por los obligados al pago, se pagará en la forma siguiente:
#1.- Cuando el monto del impuesto autoliquidado no exceda de uno centésimo de Petro (0,01 Petro)
#el impuesto se pagará totalmente, en una sola porción, dentro del plazo concedido para hacer la
#declaración prevista en el artículo 31 y previamente a la presentación de esta.
#2.- Cuando el monto del impuesto autoliquidado exceda de uno centésimo de Petro (0,01 Petro) el
#impuesto se hará exigible trimestralmente y se pagará en forma fraccionada en cuatro porciones del
#igual monto.
#ARTÍCULO 50: En el caso del pago fraccionado previsto en el artículo anterior los pagos se harán
#trimestralmente, salvo las excepciones previstas en esta Ordenanza la primera porción se pagará dentro del
#plazo concedido para hacer la declaración prevista en el artículo 31 y previamente a la presentación de
#ésta. Las tres (3) restantes porciones del pago fraccionado se pagará dentro del primer (01) mes contado a
#partir de la fecha en que comience cada uno de los trimestres subsiguientes al primero. Los trimestres
#comenzarán a contarse desde el 1 ° de enero de cada año.
def Impuesto_Inmueble(request):
    if (request):
        data = []
        aDetalle = []
        aDescuento = []
        aInteres = []
        if (request['inmueble']):

            ## esto contruye la tabla de periodos por inmueble para mantener el historico
            # esto permite saber si esta pendientes por cancelar
            ############## inicio
            today = date.today()
            oInmueble = Inmueble.objects.get(id=request['inmueble'])
            Zona = Urbanizacion.objects.get(id=oInmueble.urbanizacion.id)
            oPeriodo = IC_Periodo.objects.filter(aplica='C')
            ano_fin=today.year
            dAnio=oInmueble.anio
            while dAnio<=ano_fin:
                for aPeriodo in oPeriodo:
                    existe=IC_ImpuestoPeriodo.objects.filter(inmueble=oInmueble,periodo=aPeriodo,anio=dAnio).count()
                    if existe == 0: # si no existe, crea el periodo
                        ic_impuestoperiodo=IC_ImpuestoPeriodo(
                            inmueble=oInmueble,
                            periodo=aPeriodo,
                            anio=dAnio
                        )
                        ic_impuestoperiodo.save()
                dAnio=dAnio+1
            ############# fin

            #Periodos Pendientes por Cobrar al Inmueble
            oImpuestoPeriodo = IC_ImpuestoPeriodo.objects.filter(inmueble=request['inmueble']).order_by('anio', 'periodo')
            if oImpuestoPeriodo:
                oBaseCalculo = UnidadTributaria.objects.get(habilitado=True)
                baseCalculoBs= float(oBaseCalculo.monto)
                #Crear lista con los años presentes en la cxc
                oAnio = IC_ImpuestoPeriodo.objects.filter(inmueble=request['inmueble']).values('anio').distinct().order_by('anio')
                maximo_ano = oAnio.aggregate(Max('anio'))['anio__max']
                minimo_ano = oAnio.aggregate(Min('anio'))['anio__min']
                
                # Contar la cantidad de periodos configurados para C atastro
                tPeriodo= IC_Periodo.objects.filter(aplica='C')
                CountPeriodo= tPeriodo.count()

                terreno=InmuebleValoracionTerreno.objects.get(inmueble=request['inmueble'])
                ocupacion=InmuebleValoracionConstruccion.objects.filter(inmueblevaloracionterreno=terreno.id)
                print('antes',ocupacion)
                
                total_area_terreno = terreno.area
                total_area_construcion = ocupacion.aggregate(Sum('area'))['area__sum']

                print('total_area_construcion',total_area_construcion,'total_area_terreno',total_area_terreno)
                if total_area_construcion < total_area_terreno:
                    sumar_terreno=True

                    # Crear una nueva instancia de InmuebleValoracionConstruccion
                    nuevo_objeto_construccion = ocupacion(
                        # Configura los campos de acuerdo a tus necesidades
                        tipologia=terreno.tipologia,
                        tipo=terreno.tipo,
                        area=terreno.area,
                        aplica=terreno.aplica,
                    )

                    # Asignar la relación con el objeto terreno
                    nuevo_objeto_construccion.ocupacion = terreno

                    # Guardar el nuevo objeto en la base de datos
                    nuevo_objeto_construccion.save()

                    # Agregar el nuevo objeto a la lista ocupacion
                print('despues',ocupacion)

                ZonaInmueble=Zona.zona
                oTipologia=Tipologia.objects.filter(zona=ZonaInmueble)

                #Ubicar la fecha de compra
                oPropietario = InmueblePropietarios.objects.get(propietario=request['propietario'],inmueble=request['inmueble'])
                fechaCompra=oPropietario.fecha_compra
                diferencia=today-fechaCompra
                print(fechaCompra,today,diferencia.days)
                # valida si aplica descuentos por pronto pago.
                oDescuento=0 # Bandera que valida si aplica descuento o no
                #if (diferencia.days<=90):
                #if (diferencia.days<=90 and minimo_ano==today.year):
                try:
                    oDescuento=IC_ImpuestoDescuento.objects.filter(habilitado=True,aplica='C')
                except:
                    oDescuento=0
                bMulta=True
                oCargos=IC_ImpuestoCargos.objects.filter(habilitado=True,aplica='C')
                fMulta=float(oCargos.get(codigo='multa').porcentaje)
                fRecargo=float(oCargos.get(codigo='recargo').porcentaje)
                tBaseMultaRecargoInteres=0
                tMulta=0
                tRecargo=0
                tInteres=0
                tTotal=0
                tTotalMora=0
                while minimo_ano<=maximo_ano:
                    #para los años menores al actual, toma los periodos pendientes segun el historico
                    PeriodosCxc=oImpuestoPeriodo.filter(anio=minimo_ano).order_by('periodo')
                    if minimo_ano==today.year:
                        # para el año en curso, solo procesa hasta el periodo que el contribuyente decide cancelar
                        PeriodosCxc=oImpuestoPeriodo.filter(anio=minimo_ano,periodo__lte=request['periodo']).order_by('periodo')

                    iAlicuota=(1/CountPeriodo)
                    for aPeriodo in PeriodosCxc:
                        if minimo_ano==today.year:
                            #ARTÍCULO 50: En el caso del pago fraccionado previsto en el artículo anterior los pagos se harán
                            #trimestralmente, salvo las excepciones previstas en esta Ordenanza la primera porción se pagará dentro del
                            #plazo concedido para hacer la declaración prevista en el artículo 31 y previamente a la presentación de
                            #ésta. Las tres (3) restantes porciones del pago fraccionado se pagará dentro del primer (01) mes contado a
                            #partir de la fecha en que comience cada uno de los trimestres subsiguientes al primero. Los trimestres
                            #comenzarán a contarse desde el 1 ° de enero de cada año.
                            fDiasGracia=tPeriodo.get(periodo=aPeriodo.periodo.periodo)
                            # Para el año en curso, evaluamos si dentro del rango de periodos va a cancelar, 
                            # existe un periodo que sumando los dias de gracia al inicio del periodo, la fecha de pago esta contenida
                            if today>= fDiasGracia.fechadesde and  \
                            today <= fDiasGracia.fechadesde+datetime.timedelta(days=fDiasGracia.dias_gracia) :
                                # La fecha actual está entre las fechas del modelo
                                print("La fecha actual está entre fecha_desde y fecha_hasta.",fDiasGracia)
                                bMulta=False
                            else:
                                if today<= fDiasGracia.fechadesde and  \
                                    today <= fDiasGracia.fechadesde+datetime.timedelta(days=fDiasGracia.dias_gracia) :
                                    # La fecha actual es menor a las fechas del modelo (periodos proximos)
                                    print("La fecha actual es menor a las fechas del modelo (periodos proximos).",fDiasGracia)
                                    bMulta=False

                                # La fecha actual NO está entre las fechas del modelo
                                print("La fecha actual NO está entre fecha_desde y fecha_hasta.")
                        for dato in ocupacion:
                            #Zona 1: Terrenos sin edificar mayores de 2.000 m2 en
                            #posesión por 5 años o más por el mismo propietario
                            if dato.tipologia.codigo=='17' and ZonaInmueble.codigo=='1':
                                mesesTrascurridos = meses_transcurridos(fechaCompra, today)
                                if mesesTrascurridos>=60: # tiene 5 años de antiguedad
                                    Alicuota=float(oTipologia.get(id=dato.tipologia.id).tarifa)
                                else:
                                    # si no se cumple aplico Otros Usos=5
                                    Alicuota=float(oTipologia.get(codigo='15').tarifa)
                            else:
                                Alicuota=float(oTipologia.get(id=dato.tipologia.id).tarifa)
                            Monto=float(dato.area)*(Alicuota*iAlicuota)*baseCalculoBs
                            mDescuento=0
                            if oDescuento: # and minimo_ano==today.year:
                                # Valida que aplique descuento solamente con el año actual
                                try:
                                    pDescuento=oDescuento.filter(Q(tipologia__isnull=True) | Q(tipologia=dato.tipologia.id,))
                                    #registros_validos = pDescuento.filter(
                                    #    fechadesde__year__lte=today.year,
                                    #    fechahasta__year__gte=today.year,
                                    #    fechadesde__month__lte=today.month,
                                    #    fechahasta__month__gte=today.month,
                                    #    fechadesde__day__lte=today.day,
                                    #    fechahasta__day__gte=today.day)
                                    print('descuento',pDescuento)
                                    print('registros',aPeriodo.periodo.fechadesde,aPeriodo.periodo.fechahasta) 
                                    registros_validos = pDescuento.filter(
                                        fechadesde__year__lte=minimo_ano,
                                        fechahasta__year__gte=minimo_ano,
                                        fechadesde__month__lte=aPeriodo.periodo.fechadesde.month,
                                        fechahasta__month__gte=aPeriodo.periodo.fechahasta.month,
                                        fechadesde__day__lte=aPeriodo.periodo.fechadesde.day,
                                        fechahasta__day__gte=aPeriodo.periodo.fechahasta.day) 
                                    #print('registros_validos',registros_validos)  
                                                                

                                    mDescuento=float(registros_validos.aggregate(Sum('porcentaje'))['porcentaje__sum'])
                                except:
                                    mDescuento=0
                                for DescuentoAplicado in registros_validos:
                                    ImpuestoDetalleDescuentos={
                                        'IC_impuestodetalle':'',
                                        'IC_impuestodescuento':DescuentoAplicado.id,
                                        'fechadesde':DescuentoAplicado.fechadesde,
                                        'fechahasta':DescuentoAplicado.fechahasta,
                                        'descripcion':DescuentoAplicado.descripcion,
                                        'base':Monto,
                                        'descuento':float(DescuentoAplicado.porcentaje),
                                        'total':Monto*(float(DescuentoAplicado.porcentaje/100)),
                                        'IC_impuestoperiodo':aPeriodo.id,
                                        'uso_id':dato.tipologia.id,
                                        'uso_descripcion':dato.tipologia.descripcion,
                                        'apica':dato.aplica,
                                        'anio': minimo_ano,
                                        'periodo': aPeriodo.periodo.periodo,
                                    }
                                    aDescuento.append(ImpuestoDetalleDescuentos)
                                    #print('ImpuestoDetalleDescuentos',ImpuestoDetalleDescuentos)                                
                            Total=float(Monto-(Monto*(mDescuento/100)))

                            ImpuestoDetalle = {
                                'IC_impuestoperiodo':aPeriodo.id,
                                'anio': minimo_ano,
                                'periodo': aPeriodo.periodo.periodo,
                                'multa':bMulta,
                                'uso_id':dato.tipologia.id,
                                'uso_descripcion':dato.tipologia.descripcion,
                                'apica':dato.aplica,
                                'tipo':dato.tipo.id,
                                'tipo_descripcion':dato.tipo.descripcion,
                                'area_m2':dato.area,
                                'factor':iAlicuota,
                                'alicuota_full':Alicuota,
                                'alicuota':Alicuota*iAlicuota,
                                'basecalculobs':baseCalculoBs, 
                                'sub_total':Monto,
                                'mdescuento':mDescuento,
                                'total':Total,
                            }
                            aDetalle.append(ImpuestoDetalle)
                            tTotal=tTotal+Total
                            if bMulta:
                                tTotalMora=tTotalMora+Total
                                tBaseMultaRecargoInteres=tBaseMultaRecargoInteres+Total
                                tMulta=tMulta+(Total*(fMulta/100))
                                tRecargo=tRecargo+(Total*(fRecargo/100))
                        #EndFor ocupacion
                    #EndFor PeriodosCxc
                    if tTotalMora: #minimo_ano==today.year:
                        oTasaInteres=TasaInteres.objects.filter(anio=minimo_ano).order_by('mes')
                        tTotalMora=(tTotalMora/12)
                        for aTasa in oTasaInteres:
                            if (aTasa.mes<=today.month and minimo_ano==today.year) or minimo_ano!=today.year:
                            #if (aTasa.mes<=5 and minimo_ano==today.year) or minimo_ano!=today.year:
                                cantidad_dias = obtener_cantidad_dias(aTasa.anio, aTasa.mes)
                                tasa_porcentaje=float(aTasa.tasa/100)
                                monto=((tTotalMora*tasa_porcentaje)/360)*cantidad_dias
                                ImpuestoInteresMoratorio={
                                        'anio':aTasa.anio,
                                        'mes':aTasa.mes,
                                        'tasa':tasa_porcentaje*100,
                                        'dias':cantidad_dias,
                                        'moramensual':tTotalMora,
                                        'interesmensual':monto,
                                    }
                                aInteres.append(ImpuestoInteresMoratorio)
                                tInteres=tInteres+monto
                            #end If
                        # end For oTasaInteres                    
                        tTotalMora=0
                    minimo_ano=minimo_ano+1
                #EndWhile
                correlativo=Correlativo.objects.get(id=1)
                numero=correlativo.NumeroIC_Impuesto
                Impuesto={
                    'numero':numero,
                    'zona':ZonaInmueble.id,
                    'basecalculobs':baseCalculoBs,
                    'inmueble':oInmueble.id,
                    'subtotal':tTotal,
                    'multa':tMulta,
                    'recargo':tRecargo,
                    'interes':tInteres,
                    'fmulta':fMulta,
                    'frecargo':fRecargo,
                    'total':tTotal+tMulta+tRecargo+tInteres,
                    'BaseMultaRecargoInteres':tBaseMultaRecargoInteres,
                }
                datos={
                    'cabacera':Impuesto,
                    'detalle':aDetalle,
                    'descuento':aDescuento,
                    'interes':aInteres,
                }
                data.append(datos)
            return Response(data, status=status.HTTP_200_OK)
        return Response('Insert OK', status=status.HTTP_200_OK)
    else:
        return Response('Insert NOT Ok', status=status.HTTP_400_BAD_REQUEST)


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
    
def Muestra_Tasa(request):
    precios = price()
    print(precios,request)  
    tasa=precios['$bcv']
    return Response('Tasa BCV al dia: '+tasa,status=status.HTTP_200_OK)

def Muestra_Tasa_New(request):
    currency = pyBCV.Currency()
    all_rates = currency.get_rate() # obtener todas las tasas de cambio de moneda
    usd_rate = currency.get_rate(currency_code='USD', prettify=False) # obtener la tasa de cambio del dólar estadounidense sin símbolo de moneda
    last_update = currency.get_rate(currency_code='Fecha') # obtener la hora de la última actualización

    rate_values = [float(value) for key, value in all_rates.items() if key != "Fecha"]
    print(rate_values)
    # Encontrar el valor máximo

    rate_values = {key: float(value) for key, value in all_rates.items() if key != "Fecha"}

    # Encontrar el key correspondiente al valor máximo
    max_rate_key = max(rate_values, key=lambda key: rate_values[key])
    max_rate_value = rate_values[max_rate_key]

    print(all_rates)
    print("El valor más alto de las tasas de cambio es:", max_rate_value)
    print("El key correspondiente es:", max_rate_key)

    result = {
        "max_rate_key": max_rate_key,
        "max_rate_value": max_rate_value
    }

    return Response(result,status=status.HTTP_200_OK) 




def importar_datos_desde_excel():
    importar='inmueble'

    if importar=='tasas':
        ruta_archivo_excel = os.path.join('media', 'archivos_excel/tasa.xlsx')
        datos_excel = pd.read_excel(ruta_archivo_excel)
        for index, row in datos_excel.iterrows():
            anio = row['anio']
            mes = row['mes']
            tasa = row['tasa']
            print(row)
            
            # Crea un nuevo objeto TasaInteres y guárdalo en la base de datos
            TasaInteres.objects.create(anio=anio, mes=mes, tasa=tasa)
        print("Datos importados exitosamente.")
    if importar=='ambito':
        ruta_archivo_excel = os.path.join('media', 'archivos_excel/maestros_dir_estructurada.xlsx')
        datos_excel = pd.read_excel(ruta_archivo_excel, sheet_name='ambito')
        for index, row in datos_excel.iterrows():
            codigo = row['id_ambito']
            descripcion = row['nombre']
            try:
                # Intenta obtener un registro existente o crear uno nuevo si no existe
                ambito, creado = Ambito.objects.get_or_create(
                    codigo=codigo,
                    defaults={
                        'descripcion': descripcion,
                    }
                )
                if not creado:
                    print(f"El registro con código {codigo} ya existe y no se creó uno nuevo.")
            except IntegrityError as e:
                # Maneja cualquier error de integridad si es necesario
                print(f"Error de integridad al crear el registro: {e}")
        print("Ambito importados exitosamente.")
    if importar=='sector':
        ruta_archivo_excel = os.path.join('media', 'archivos_excel/maestros_dir_estructurada.xlsx')
        datos_excel = pd.read_excel(ruta_archivo_excel, sheet_name='sector')
        for index, row in datos_excel.iterrows():
            ambito=Ambito.objects.get(codigo=row['id_ambito']) # integridad con ambito
            codigo = row['id_sector']
            descripcion = row['nombre'] #if not '' else 'falta nombre '+str(row['id_sector'])
            clasificacion = row['clasificacion']
            area = row['area'] if not math.isnan(row['area']) else Decimal('0')
            perimetro = row['perimetro'] if not math.isnan(row['perimetro']) else Decimal('0')
            #print(ambito,descripcion,row)
            try:
                # Intenta obtener un registro existente o crear uno nuevo si no existe
                sector, creado = Sector.objects.get_or_create(
                    codigo=codigo,
                    ambito=ambito,
                    defaults={
                        'descripcion': descripcion,
                        'clasificacion': clasificacion,
                        'area': Decimal(area),
                        'perimetro': Decimal(perimetro),
                    }
                )
                if not creado:
                    print(f"El registro con código {codigo} y ámbito {ambito} ya existe y no se creó uno nuevo.")
            except IntegrityError as e:
                # Maneja cualquier error de integridad si es necesario
                print(f"Error de integridad al crear el registro: {e}")
                print(ambito,descripcion,row)
        print("Sector importados exitosamente.")  
    if importar=='manzana':
        ruta_archivo_excel = os.path.join('media', 'archivos_excel/maestros_dir_estructurada.xlsx')
        datos_excel = pd.read_excel(ruta_archivo_excel, sheet_name='manzana')
        for index, row in datos_excel.iterrows():
            ambito=Ambito.objects.get(codigo=row['id_ambito']) # integridad con ambito
            sector=Sector.objects.get(codigo=row['id_sector'],ambito=ambito) # integridad con ambito
            codigo = row['id_manzana']
            area = row['area'] if not math.isnan(row['area']) else Decimal('0')
            perimetro = row['perimetro'] if not math.isnan(row['perimetro']) else Decimal('0')
            print(row)
            try:
                # Intenta obtener un registro existente o crear uno nuevo si no existe
                manzana, creado = Manzana.objects.get_or_create(
                    codigo=codigo,
                    sector=sector,
                    defaults={
                        'area': Decimal(area),
                        'perimetro': Decimal(perimetro),
                    }
                )
                if not creado:
                    print(f"El registro con código {codigo} y sector {sector} ya existe y no se creó uno nuevo.")
            except IntegrityError as e:
                # Maneja cualquier error de integridad si es necesario
                print(f"Error de integridad al crear el registro: {e}")
        print("manzana importados exitosamente.")
    if importar=='parcela':
        ruta_archivo_excel = os.path.join('media', 'archivos_excel/maestros_dir_estructurada.xlsx')
        datos_excel = pd.read_excel(ruta_archivo_excel, sheet_name='parcela')
        for index, row in datos_excel.iterrows():
            ambito=Ambito.objects.get(codigo=row['id_ambito']) # integridad con ambito
            sector=Sector.objects.get(codigo=row['id_sector'],ambito=ambito) # integridad con sector
            manzana=Manzana.objects.get(codigo=row['id_manzana'],sector=sector) # integridad con manzana
            codigo = row['id_parcela']
            area = row['area'] if not math.isnan(row['area']) else Decimal('0')
            perimetro = row['perimetro'] if not math.isnan(row['perimetro']) else Decimal('0')
            print(row)
            try:
                # Intenta obtener un registro existente o crear uno nuevo si no existe
                parcela, creado = Parcela.objects.get_or_create(
                    codigo=codigo,
                    manzana=manzana,
                    defaults={
                        'area': Decimal(area),
                        'perimetro': Decimal(perimetro),
                    }
                )
                if not creado:
                    print(f"El registro con código {codigo} y sector {sector} ya existe y no se creó uno nuevo.")
            except IntegrityError as e:
                # Maneja cualquier error de integridad si es necesario
                print(f"Error de integridad al crear el registro: {e}")
        print("parcela importados exitosamente.")  
    if importar=='sub-parcela':
        ruta_archivo_excel = os.path.join('media', 'archivos_excel/maestros_dir_estructurada.xlsx')
        datos_excel = pd.read_excel(ruta_archivo_excel, sheet_name='sub_parcela')
        for index, row in datos_excel.iterrows():
            ambito=Ambito.objects.get(codigo=row['id_ambito']) # integridad con ambito
            sector=Sector.objects.get(codigo=row['id_sector'],ambito=ambito) # integridad con sector
            manzana=Manzana.objects.get(codigo=row['id_manzana'],sector=sector) # integridad con manzana
            parcela=Parcela.objects.get(codigo=row['id_parcela'],manzana=manzana) # integridad con parcela
            codigo = row['id_sub_parcela']
            area = row['area'] if not math.isnan(row['area']) else Decimal('0')
            perimetro = row['perimetro'] if not math.isnan(row['perimetro']) else Decimal('0')
            print(row)
            try:
                # Intenta obtener un registro existente o crear uno nuevo si no existe
                subparcela, creado = SubParcela.objects.get_or_create(
                    codigo=codigo,
                    parcela=parcela,
                    defaults={
                        'area': Decimal(area),
                        'perimetro': Decimal(perimetro),
                    }
                )
                
                if not creado:
                    print(f"El registro con código {codigo} y sector {sector} ya existe y no se creó uno nuevo.")
            except IntegrityError as e:
                # Maneja cualquier error de integridad si es necesario
                print(f"Error de integridad al crear el registro: {e}")
        print("SubParcela importados exitosamente.")  
    if importar=='barrios': #Urbanizacion
        ruta_archivo_excel = os.path.join('media', 'archivos_excel/maestros_dir_estructurada.xlsx')
        datos_excel = pd.read_excel(ruta_archivo_excel, sheet_name='barrioss')
        for index, row in datos_excel.iterrows():
            ambito=Ambito.objects.get(codigo=row['id_ambito']) # integridad con ambito
            sector=Sector.objects.get(codigo=row['id_sector'],ambito=ambito) # integridad con ambito
            codigo = row['id_urb_barrio']
            #print(row)
            try:
                # Intenta obtener un registro existente o crear uno nuevo si no existe
                urbanizacion, creado = Urbanizacion.objects.get_or_create(
                    codigo=codigo,
                    sector=sector,
                    defaults={
                        'nombre': row['nombre'],
                    }
                )
                if not creado:
                    True
                    print(f"El registro con código {codigo} y sector {sector} ya existe y no se creó uno nuevo.")
            except IntegrityError as e:
                # Maneja cualquier error de integridad si es necesario
                print(f"Error de integridad al crear el registro: {e}")
        print("barrios importados exitosamente.")
    if importar=='contribuyente':
        ruta_archivo_excel = os.path.join('media', 'archivos_excel/maestros_dir_estructurada.xlsx')
        datos_excel = pd.read_excel(ruta_archivo_excel, sheet_name='persona')
        for index, row in datos_excel.iterrows():
            numero_documento = row['id_persona']
            nombre = row['nombre']
            telefono_principal = row['telefono']
            direccion = row['direccion']
            telefono_secundario = row['telefono2']
            email_principal = row['correo']
            emaill_secundario = row['correo2']
            try:
                # Intenta obtener un registro existente o crear uno nuevo si no existe
                ambito, creado = Propietario.objects.get_or_create(
                    numero_documento=numero_documento,
                    defaults={
                        'nombre': nombre,
                        'telefono_principal':telefono_principal,
                        'direccion':direccion,
                        'telefono_secundario':telefono_secundario,
                        'email_principal':email_principal,
                        'emaill_secundario':emaill_secundario,
                    }
                )
                if not creado:
                    print(f"El registro con código {numero_documento} ya existe y no se creó uno nuevo.")
            except IntegrityError as e:
                # Maneja cualquier error de integridad si es necesario
                print(f"Error de integridad al crear el registro: {e}")
        print("Persona/contribuyente importados exitosamente.")
    if importar=='conj_resinden':
        ruta_archivo_excel = os.path.join('media', 'archivos_excel/maestros_dir_estructurada.xlsx')
        datos_excel = pd.read_excel(ruta_archivo_excel, sheet_name='conj_resinden')
        for index, row in datos_excel.iterrows():
            urbanizacion=Urbanizacion.objects.get(codigo=row['id_urb_barrio']) # integridad con urbanizacion
            codigo = row['id_conj_residencial']
            nombre = row['nombre']
            try:
                # Intenta obtener un registro existente o crear uno nuevo si no existe
                creado = ConjuntoResidencial.objects.get_or_create(
                    codigo=codigo,
                    urbanizacion=urbanizacion,
                    defaults={
                        'nombre': nombre,
                    }
                )
                if not creado:
                    print(f"El registro con código {codigo} ya existe y no se creó uno nuevo.")
            except IntegrityError as e:
                # Maneja cualquier error de integridad si es necesario
                print(f"Error de integridad al crear el registro: {e}")
        print("conj_resinden importados exitosamente.")

    if importar=='edificio':
        ruta_archivo_excel = os.path.join('media', 'archivos_excel/maestros_dir_estructurada.xlsx')
        datos_excel = pd.read_excel(ruta_archivo_excel, sheet_name='edificio')
        for index, row in datos_excel.iterrows():
            try:
                conjuntoresidencial=ConjuntoResidencial.objects.get(codigo=row['id_conj_residencial']) # integridad con urbanizacion
                codigo = row['id_edificio']
                nombre = row['nombre']
                try:
                    # Intenta obtener un registro existente o crear uno nuevo si no existe
                    creado = Edificio.objects.get_or_create(
                        codigo=codigo,
                        conjuntoresidencial=conjuntoresidencial,
                        defaults={
                            'nombre': nombre,
                        }
                    )
                    if not creado:
                        print(f"El registro con código {codigo} ya existe y no se creó uno nuevo.")
                except IntegrityError as e:
                    # Maneja cualquier error de integridad si es necesario
                    print(f"Error de integridad al crear el registro: {e}")
            except ConjuntoResidencial.DoesNotExist:
                print("Conjunto residencial  no existe.")
        print("edificio importados exitosamente.")
    if importar=='torre':
        ruta_archivo_excel = os.path.join('media', 'archivos_excel/maestros_dir_estructurada.xlsx')
        datos_excel = pd.read_excel(ruta_archivo_excel, sheet_name='torre')
        for index, row in datos_excel.iterrows():
            try:
                conjuntoresidencial=ConjuntoResidencial.objects.get(codigo=row['id_conj_residencial']) # integridad con urbanizacion
                codigo = row['id_torre']
                nombre = row['nombre']
                try:
                    # Intenta obtener un registro existente o crear uno nuevo si no existe
                    creado = Torre.objects.get_or_create(
                        codigo=codigo,
                        conjuntoresidencial=conjuntoresidencial,
                        defaults={
                            'nombre': nombre,
                        }
                    )
                    if not creado:
                        print(f"El registro con código {codigo} ya existe y no se creó uno nuevo.")
                except IntegrityError as e:
                    # Maneja cualquier error de integridad si es necesario
                    print(f"Error de integridad al crear el registro: {e}")
            except ConjuntoResidencial.DoesNotExist:
                print("Conjunto residencial  no existe.")
        print("Torre importados exitosamente.")
    if importar=='avenida':
        ruta_archivo_excel = os.path.join('media', 'archivos_excel/maestros_dir_estructurada.xlsx')
        datos_excel = pd.read_excel(ruta_archivo_excel, sheet_name='avenida')
        for index,row in datos_excel.iterrows():
            codigo = row['id_avenida']
            nombre = row['nombre']
            tipo = int(row['id_tipo_avenida'])
            print(row)
            try:
                # Intenta obtener un registro existente o crear uno nuevo si no existe
                creado = Avenida.objects.get_or_create(
                    codigo=codigo,
                    defaults={
                        'tipo': tipo,
                        'nombre':nombre,
                    }
                )
                if not creado:
                    print(f"El registro con código {codigo} ya existe y no se creó uno nuevo.")
            except IntegrityError as e:
                # Maneja cualquier error de integridad si es necesario
                print(f"Error de integridad al crear el registro: {e}")
        print("avenida importados exitosamente.")

    if importar=='inmueble':
        ruta_archivo_excel = os.path.join('media', 'archivos_excel/maestros_dir_estructurada.xlsx')
        datos_excel = pd.read_excel(ruta_archivo_excel, sheet_name='inmueble')
        for index, row in datos_excel.iterrows():
            strZona= row['id_zona2004']
            if not math.isnan(strZona):
                parte_entera = int(strZona)
            else:
                parte_entera = 0 

            if  len(str(row['id_inmueble']))<6: 

                try:
                    zona=Zona.objects.get(codigo=parte_entera) # integridad con urbanizacion
                    numero_expediente = row['id_inmueble']
                    #zona = row['id_zona2004']
                    try:
                        # Intenta obtener un registro existente o crear uno nuevo si no existe
                        creado = Inmueble.objects.get_or_create(
                            numero_expediente=numero_expediente,
                            defaults={
                                'zona': zona,
                            }
                        )
                        if not creado:
                            print(f"El registro con código {numero_expediente} ya existe y no se creó uno nuevo.")
                        else:
                            print(f"El registro con código {numero_expediente} SE CREO.")

                    except IntegrityError as e:
                        # Maneja cualquier error de integridad si es necesario
                        print(f"Error de integridad al crear el registro: {e}")
                except Zona.DoesNotExist:
                    print("Zona no existe.")
 
        print("edificio importados exitosamente.")




    return Response('Datos importados exitosamente.',status=status.HTTP_200_OK) 