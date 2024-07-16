from .models import *
from .serializers import *
from django.contrib.auth import authenticate
from knox.models import AuthToken
from rest_framework.response import Response
from rest_framework import viewsets, status, generics
import re
from django.db.models import Max,Min,Sum,Q 
import pandas as pd
import os
import calendar
from decimal import Decimal
import math  # Importa la biblioteca math
from django.db import IntegrityError,transaction
from django.http import JsonResponse
from datetime import datetime, timedelta, date
from django.core.serializers.json import DjangoJSONEncoder
import json
import urllib.parse
from django.http import HttpResponse
from django.db.models import Count, CharField, Value, When, Case
#from django.db.models import Count, F
from django.db.models.functions import ExtractYear, ExtractMonth
from .storage_backends import PrivateMediaStorage

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
                         'nombre':user.first_name,
                         'apellido':user.last_name,
                         'modulo':perfil.modulo.nombre,
                         'caja':perfil.caja,
                         'departamento':perfil.departamento.nombre,
                         'finaliza_flujo':perfil.departamento.finaliza_flujo,
                         'imprime_recibo_entrega':perfil.departamento.imprime_recibo_entrega,
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
        nNumero=correlativo.NumeroEstadoCuenta
        correlativo.NumeroEstadoCuenta=correlativo.NumeroEstadoCuenta+1
        correlativo.save()
        valor_petro=TasaBCV.objects.get(habilitado=True).monto
        valor_tasabcv=TasaBCV.objects.get(habilitado=True).monto
        tipoflujo = None if request['flujo']==None else TipoFlujo.objects.get(codigo=request['flujo'])
        inmueble = None if request['inmueble']==None else Inmueble.objects.get(id=request['inmueble'])
        propietario = Propietario.objects.get(id=request['propietario'])
        Cabacera=EstadoCuenta(
            numero=nNumero,
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

        result = {
        "documento": Cabacera.numero,
        "id": Cabacera.id

        }
        return Response(result, status=status.HTTP_200_OK)
    else:
        result = {
        "documento": 'Insert EstadoCuenta NOT Ok'
 
        }
        return Response(result, status=status.HTTP_400_BAD_REQUEST)
    
def Crear_Liquidacion(request):
    if (request):
        items=request['detalle']
        correlativo=Correlativo.objects.get(id=1)
        nNumero=correlativo.NumeroLiquidacion
        correlativo.NumeroLiquidacion=correlativo.NumeroLiquidacion+1
        correlativo.save()
        valor_petro=TasaBCV.objects.get(habilitado=True).monto
        valor_tasabcv=TasaBCV.objects.get(habilitado=True).monto
        tipoflujo = None if request['flujo']==None else TipoFlujo.objects.get(id=request['flujo'])
        inmueble = None if request['inmueble']==None else Inmueble.objects.get(id=request['inmueble'])
        propietario = Propietario.objects.get(id=request['propietario'])
        estadocuenta = None if request['estadocuenta']==None else EstadoCuenta.objects.get(id=request['estadocuenta'])
        Cabacera=Liquidacion(
            numero=nNumero,
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
        result = {
        "documento": Cabacera.numero,
        "id": Cabacera.id,
        "idedocuenta":Cabacera.estadocuenta.numero
        }

        #marco el estado de cuenta para que no aparezca denuevo en las listas de estados de cuenta disponibles
        # con eso validamos que no se genere dos liquidaciones con el mismo estado de cuenta.
        estadocuenta.habilitado=False
        estadocuenta.save()
        return Response(result, status=status.HTTP_200_OK)
    else:
        result = {
        "documento": 'Insert Pre-Factura NOT Ok'
 
        }
        return Response(result, status=status.HTTP_400_BAD_REQUEST)


def Crear_Pago(request):
    if (request):
        notacredito=[]
        items=request['detalle']
        correlativo=Correlativo.objects.get(id=1)
        NroPlanilla=correlativo.NumeroPago 
        ##print('NroPlanilla',NroPlanilla)
        correlativo.NumeroPago=correlativo.NumeroPago+1
        correlativo.save()
        #propietario = Propietario.objects.get(id=request['propietario'])
        propietario = None if request['propietario']==None else Propietario.objects.get(id=request['propietario'])
        liquidacion = None if request['liquidacion']==None else Liquidacion.objects.get(id=request['liquidacion'])
        #liquidacion = Liquidacion.objects.get(id=request['liquidacion'])
        ##print('liquidaciones',liquidacion.id)
        ##print('estado de cuenta',liquidacion.estadocuenta.id)
        # valida si el pago corresponde a un impuesto de inmueble.
        
        #PagaImpuestoInmueble=False
        #AnioPago=0
        #PeriodoPago=0
        #InmueblePago=0
        #try:
        #    oIC_Impuesto = IC_Impuesto.objects.get(estadocuenta__id=liquidacion.estadocuenta.id)  #tabla de detalle de impuesto del estado de cuenta
        #    PagaImpuestoInmueble=True
        #    tPeriodo= IC_Periodo.objects.filter(aplica='C')             # maestro de periodos
        #    CountPeriodo= tPeriodo.count()                              # cuenta el total de periodos de cayastro para saber cual es el ultimo
        #    oPeriodoPago=tPeriodo.get(id=oIC_Impuesto.periodopagofin)   #ubica el numero de periodo pagado 
        #    AnioPago=oIC_Impuesto.aniopagofin                           #año ultimo pago
        #    ##print('CountPeriodo',CountPeriodo,oPeriodoPago.periodo)
        #    if oPeriodoPago.periodo==CountPeriodo:                      #evalua si el "periodo" pagado es el ultimo segun el maestro de periodos de catastro
        #        oPeriodoPago= tPeriodo.get(periodo=1)
        #        AnioPago=AnioPago+1
        #    else:
        #        oPeriodoPago= tPeriodo.get(periodo=oPeriodoPago.periodo+1)          
        #    InmueblePago=Inmueble.objects.get(id=oIC_Impuesto.estadocuenta.inmueble.id)
        #    InmueblePago.anio=AnioPago
        #    InmueblePago.periodo=oPeriodoPago
        #    InmueblePago.save()
        #except IC_Impuesto.DoesNotExist:
        #    PagaImpuestoInmueble=False


        print('liquidacion1',liquidacion)
        ##print('PagaImpuestoInmueble',PagaImpuestoInmueble,AnioPago,PeriodoPago,InmueblePago)  
        Cabacera=PagoEstadoCuenta(
            numero=NroPlanilla,
            liquidacion=liquidacion,
            fecha=str(date.today()),
            observaciones=request['observacion'],
            caja=request['caja'],
            monto=request['monto'],
            monto_cxc=request['monto_cxc']
        )
        Cabacera.save()
        # evalua si se pago de mas para crear la nota de credito a favor del contribuyente
        ##print(request['monto'],request['monto_cxc'])

        if liquidacion:
            monto_credito= float(request['monto'])-float(request['monto_cxc'])
            if monto_credito>0:
                tipopago = TipoPago.objects.get(codigo='N')
                notacredito=NotaCredito(
                    numeronotacredito  = correlativo.NumeroNotaCredito,
                    tipopago =  tipopago,
                    propietario = propietario,
                    observacion  = '',
                    fecha=str(date.today()),
                    monto=   monto_credito, 
                    saldo=    monto_credito,
                    pagoestadocuenta=Cabacera
                )
                notacredito.save()
                correlativo.NumeroNotaCredito=correlativo.NumeroNotaCredito+1
                correlativo.save()
        
        for detalle in items:
            tipopago =    None if detalle['tipopago']==   None else TipoPago.objects.get(codigo=detalle['tipopago'])
            bancocuenta = None if detalle['bancocuenta']==None else BancoCuenta.objects.get(id=detalle['bancocuenta'])
            Detalle=PagoEstadoCuentaDetalle(
                pagoestadocuenta=Cabacera,
                tipopago = tipopago,
                bancocuenta=bancocuenta,
                monto  = float(detalle['monto']),
                #fechapago =  str(date.today()),#detalle['fechapago'],
                fechapago =  detalle['fechapago'],
                nro_referencia = detalle['nro_referencia'],
                nro_aprobacion = detalle['nro_aprobacion'],
                nro_lote = detalle['nro_lote']
            )
            if detalle['tipopago']=='N':
                notacredito=NotaCredito.objects.get(propietario = propietario,numeronotacredito=detalle['nro_referencia'])
                notacredito.saldo=float(notacredito.saldo)-float(detalle['monto'])
                notacredito.save()
                ##print('nota de credito',float(notacredito.saldo),float(detalle['monto']),float(notacredito.saldo)-float(detalle['monto']))
            Detalle.save()
        #actualiza el correlativo de numero de pagos
        #correlativo.NumeroPago=correlativo.NumeroPago+1  
        # solo aplica cuando la peticion viene de catastro y es una de esas 3 opciones
        print('liquidacion',liquidacion)
        if liquidacion:
            if liquidacion.tipoflujo.carandai:
                #solo aplica cuanbdo es inscripcion, el inmueble se debe crear nuevo
                if liquidacion.tipoflujo.crea_expediente:
                    #crear inmuebles
                    estatusinmueble=EstatusInmueble.objects.get(codigo='99')
                    ##print(estatusinmueble)

                    InmuebleNew=Inmueble(numero_expediente=correlativo.ExpedienteCatastro,
                                        #fecha_inscripcion=date.today(),
                                        fecha_creacion=date.today(),
                                        status=estatusinmueble)
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
                    InmuebleValoracionTerreno2024New=InmuebleValoracionTerreno2024(inmueble=InmuebleNew)
                    InmuebleValoracionTerreno2024New.save()
                    InmuebleUbicacionNew=InmuebleUbicacion(inmueble=InmuebleNew)
                    InmuebleUbicacionNew.save()
                    InmuebleFaltanteNew=InmuebleFaltante(inmueble=InmuebleNew)
                    InmuebleFaltanteNew.save()
                    #actualiza en correlativo del expediente 
                    correlativo.ExpedienteCatastro=correlativo.ExpedienteCatastro+1
                    correlativo.save()
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
                correlativo.save() 
            #actualiza corrrelativo de pago
            #correlativo.save()
            #marca la liquidacion como procesada
            print('entre a liq')
            liquidacion.habilitado=False
            liquidacion.save()

            queryset = LiquidacionDetalle.objects.filter(liquidacion=liquidacion.id)
            # Convierte el QuerySet a una lista de diccionarios
            lista_de_diccionarios = list(queryset.values())

            # Convierte la lista de diccionarios a una cadena JSON
            json_resultado = json.dumps(lista_de_diccionarios, cls=DjangoJSONEncoder)          
        else:
            json_resultado = {}

        ##print(json_resultado)
        result = {
        "documento": Cabacera.numero,
        "idpago": Cabacera.id ,
        "liquidacionDetalleData":json_resultado,}
        return Response(result, status=status.HTTP_200_OK)
    else:
        result = {
        "documento": 'Insert Pago NOT Ok'
        }
        return Response(result, status=status.HTTP_400_BAD_REQUEST)

def Crear_Inmueble_Propietario(request):
    if (request):
        inmueble = Inmueble.objects.get(id=request['inmueble'])
        propietario = Propietario.objects.get(id=request['propietario'])
        inmubelepropietario=InmueblePropietarios(
            inmueble=inmueble,
            propietario=propietario,
            #fecha_compra=request['fecha_compra']

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
        data_IC_MIU = []
        data_IC_MMU = []
        data_IC_MIM = []
        data_IC_MMM = []
        total_IC_MIU = 0
        total_IC_MMU = 0
        total_IC_MIM = 0
        total_IC_MMM = 0
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
            ##print('fecha_inscripcion:',fecha_inscripcion,'today:',today,'diferencia:',diferenciai.days,'bInscripcion:',bInscripcion)

            ##print('fecha_compra:',fecha_compra,'today:',today,'diferencia:',diferenciac.days,'bModifica:',bModifica)

            if (bModifica or bInscripcion): # Artículo 20
                baseCalculo = TasaBCV.objects.get(habilitado=True)
                baseCalculoBs= float(baseCalculo.monto)
                if bInscripcion:
                    #fechaVencidaI=fecha_inscripcion+ datetime.timedelta(days=90) # Sumar los 90 dias de plazo a la fecha vencida para determinar el periodo vencido
                    fechaVencidaI=fecha_inscripcion+ timedelta(days=90) # Sumar los 90 dias de plazo a la fecha vencida para determinar el periodo vencido

                    mesesVencidosI = meses_transcurridos(fechaVencidaI, today)
                    ##print("Meses Vencidos Inscripcion:", mesesVencidosI)
                    #Artículo 99
                    MultaMinInscripcionUni=0 * baseCalculoBs  #Si no maneja una multa mínima, coloque 0 !!!!! No implementado!!!
                    alicuotaMultaInscripcionUni=0.011111111
                    alicuotaMoraInscripcionUni=0.05 # por año de mora hasta 10 años

                    MultaMinInscripcionMULTI=0 * baseCalculoBs #Si no maneja una multa mínima, coloque 0 !!!!! No implementado!!!
                    alicuotaMultaInscripcionMULTI=0.02
                    alicuotaMoraInscripcionMULTI=0.033333333  # por año de mora hasta 10 años


                if bModifica:
                    fechaVencidaM=fecha_compra+ timedelta(days=90) # Sumar los 90 dias de plazo a la fecha vencida para determinar el periodo vencido
                    mesesVencidosM= meses_transcurridos(fechaVencidaM, today)
                    ##print("Meses Vencidos Modificacion:", mesesVencidosM)
                    #Artículo 101
                    MultaMinModificaUni=0 * baseCalculoBs #Si no maneja una multa mínima, coloque 0 !!!!! No implementado!!!
                    alicuotaMultaModificaUni=0.033
                    alicuotaMoraModificaUni=0.025 # por año de mora hasta 10 años
                    
                    MultaMinModificaMULTI=0 * baseCalculoBs #Si no maneja una multa mínima, coloque 0 !!!!! No implementado!!!
                    alicuotaMultaModificaMULTI=0.033
                    alicuotaMoraModificaMULTI=0.05 # por año de mora hasta 10 años (ojo por m2)
                
                terreno=InmuebleValoracionTerreno.objects.get(inmueble=request['inmueble'])
                ocupacion=InmuebleValoracionConstruccion.objects.filter(inmueblevaloracionterreno=terreno.id)
                ##print(terreno)
                ###print(ocupacion)
                for dato in ocupacion:
                    # Validar la multa por los m2 del inmueble si esa multa es menor al mínimo, la multa final sera el mínimo
                    metrosCuadrados=float(dato.area)
                    if (dato.tipo.tipo=='U'): #Unifamiliar
                        if bInscripcion:
                            multa=metrosCuadrados*alicuotaMultaInscripcionUni
                            if MultaMinInscripcionUni: # Aca valida si es diferente de 0 osea que tendrá un mínimo, de lo contrario la multa es la calculada segun los m2
                                multa=multa if multa>MultaMinInscripcionUni else MultaMinInscripcionUni
                            moraFraccionada=alicuotaMoraInscripcionUni/12  # determinar la fraccion, Ya que la multa se calcula por mes en mora y este el multipica por la multa/12
                            mora=moraFraccionada*mesesVencidosI#*metrosCuadrados
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
                                'TOTA Bs a PAGAR:':(mora+multa)*baseCalculoBs,
                            }
                            total_IC_MIU=total_IC_MIU+((mora+multa)*baseCalculoBs)
                            data_IC_MIU.append(item)
                        if bModifica:
                            multa=metrosCuadrados*alicuotaMultaModificaUni
                            if MultaMinModificaUni: # Aca valida si es diferente de 0 osea que tendrá un mínimo, de lo contrario la multa es la calculada segun los m2
                                multa=multa if multa>MultaMinModificaUni else MultaMinModificaUni
                            moraFraccionada=alicuotaMoraModificaUni/12  # determinar la fraccion, Ya que la multa se calcula por mes en mora y este el multipica por la multa/12
                            mora=moraFraccionada*mesesVencidosM#*metrosCuadrados
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
                                'TOTA Bs a PAGAR:':(mora+multa)*baseCalculoBs,
                            }
                            total_IC_MMU=total_IC_MMU+((mora+multa)*baseCalculoBs)
                            data_IC_MMU.append(item)

                    else: #MULTIfamiliar
                        if bInscripcion:
                            multa=metrosCuadrados*alicuotaMultaInscripcionMULTI
                            if MultaMinInscripcionMULTI: # Aca valida si es diferente de 0 osea que tendrá un mínimo, de lo contrario la multa es la calculada segun los m2
                                multa=multa if multa>MultaMinInscripcionMULTI else MultaMinInscripcionMULTI
                            moraFraccionada=alicuotaMoraInscripcionMULTI/12  # determinar la fraccion, Ya que la multa se calcula por mes en mora y este el multipica por la multa/12
                            mora=moraFraccionada*mesesVencidosI#*metrosCuadrados
                            item = {
                                'codigo':'IC_MIM',
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
                                'TOTA Bs a PAGAR:':(mora+multa)*baseCalculoBs,
                            }
                            total_IC_MIM=total_IC_MIM+((mora+multa)*baseCalculoBs)
                            data_IC_MIM.append(item)
                        if bModifica:
                            multa=metrosCuadrados*alicuotaMultaModificaMULTI
                            if MultaMinModificaMULTI: # Aca valida si es diferente de 0 osea que tendrá un mínimo, de lo contrario la multa es la calculada segun los m2
                                multa=multa if multa>MultaMinModificaMULTI else MultaMinModificaMULTI
                            moraFraccionada=alicuotaMoraModificaMULTI/12  # determinar la fraccion, Ya que la multa se calcula por mes en mora y este el multipica por la multa/12
                            mora=moraFraccionada*mesesVencidosM#*metrosCuadrados
                            item = {
                                'codigo':'IC_MMM',
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
                                'TOTA Bs a PAGAR:':(mora+multa)*baseCalculoBs,
                            }
                            total_IC_MMM=total_IC_MMM+((mora+multa)*baseCalculoBs)
                            data_IC_MMM.append(item)

                datos={
                    'basefiscalmulta':baseCalculoBs,
                    'cabecera_IC_MIU':total_IC_MIU,
                    'cabecera_IC_MMU':total_IC_MMU,
                    'cabecera_IC_MIM':total_IC_MIM,
                    'cabecera_IC_MMM':total_IC_MMM,
                    'data_IC_MIU':data_IC_MIU,
                    'data_IC_MMU':data_IC_MMU,
                    'data_IC_MIM':data_IC_MIM,
                    'data_IC_MMM':data_IC_MMM,
                }
                data.append(datos)
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
def Impuesto_Inmueble2023(request):
    if (request):
        anioini=0
        mesini=0
        data = []
        aDetalle = []
        aDescuento = []
        aInteres = []
        if (request['inmueble']):
            not_process=False
            try:
                oInmueble = Inmueble.objects.get(id=request['inmueble'], status__inmueble_activo=True)
            except Inmueble.DoesNotExist:
                 not_process=True
            if not_process:
                return Response('Inmueble con estatus por procesar en catastro', status=status.HTTP_400_BAD_REQUEST)
            else:
                ## esto contruye la tabla de periodos por inmueble para mantener el historico
                # esto permite saber si esta pendientes por cancelar
                ############## inicio
                today = date.today()
                #Zona = Urbanizacion.objects.get(id=oInmueble.urbanizacion.id)
                Zona = oInmueble
                oPeriodo = IC_Periodo.objects.filter(aplica='C')
                ano_fin= 2023 #request['anio']  #today.year
                ##print('oInmueble.anio:',oInmueble.anio)
                if oInmueble.anio is None: # si al momento de importar de excel  no tiene pagos, le coloco el año de la fecha de inscripcion
                    oInmueble.anio=oInmueble.fecha_inscripcion.year
                    oInmueble.periodo=IC_Periodo.objects.get(aplica='C',periodo=1)
                    oInmueble.save()
                    dAnio=oInmueble.anio
                    dPeriodo=oInmueble.periodo.periodo 
                    ##print('creadooo')
                dAnio=oInmueble.anio        # Año qe iica la deuda
                dPeriodo=oInmueble.periodo.periodo  # Periodo que inicia la deuda
                anioini=dAnio
                if anioini<((today.year+1)-7):
                    anioini=((today.year+1)-7)
                    dAnio=anioini
                mesini=dPeriodo
                primero=True
                ##print('kkkkkkkkkkkkkkkkkkkkkk',dPeriodo) 

                IC_ImpuestoPeriodo.objects.filter(inmueble=oInmueble).delete()  # elimina el historial de periodos pendientes
                                                        #por que este dato lo puede cambiar hacienda con acceso.borrar=true
                while dAnio<=ano_fin: # crea la cxc de periodos pendientes
                    if primero:
                        oPeriodo = IC_Periodo.objects.filter(aplica='C',periodo__gte=dPeriodo)
                        primero=False
                    else:
                        oPeriodo = IC_Periodo.objects.filter(aplica='C')
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
                    # se maneja ahora un metepo por año por rso se quita eso aca
                    #oBaseCalculo = UnidadTributaria.objects.get(habilitado=True)
                    #baseCalculoBs= float(oBaseCalculo.monto)

                    #Crear lista con los años presentes en la cxc
                    oAnio = IC_ImpuestoPeriodo.objects.filter(inmueble=request['inmueble']).values('anio').distinct().order_by('anio')
                    maximo_ano = oAnio.aggregate(Max('anio'))['anio__max']
                    minimo_ano = oAnio.aggregate(Min('anio'))['anio__min']
                    
                    # Contar la cantidad de periodos configurados para C atastro
                    tPeriodo= IC_Periodo.objects.filter(aplica='C')
                    CountPeriodo= tPeriodo.count()
                    terreno =      InmuebleValoracionTerreno.objects.get(inmueble=request['inmueble'])
                    construccion = InmuebleValoracionConstruccion.objects.filter(inmueblevaloracionterreno=terreno)
                    if terreno:
                        total_area_terreno = terreno.area 
                    else:
                        total_area_terreno = 0

                    if construccion:
                        total_area_construccion = construccion.aggregate(Sum('area'))['area__sum']
                    else:
                        total_area_construccion = 0

                    if (total_area_construccion > total_area_terreno) or (total_area_terreno==0 and total_area_construccion>0):
                        ocupacion=construccion
                    elif total_area_terreno>0 and total_area_construccion==0:
                        ocupacion =  InmuebleValoracionTerreno.objects.filter(inmueble=request['inmueble'])
                        ocupacion = list(ocupacion) 
                    else:
                        ocupacion=construccion
                        if terreno: # hay inmuebles que NO TIENEN TERRENO, PARA ESE CASO NO ENTRA, SOLO TOMA LA CONTRUCCION
                            if total_area_construccion < total_area_terreno:
                                # Crear una nueva instancia de InmuebleValoracionConstruccion sin guardar en la base de datos
                                
                                nuevo_objeto_construccion = InmuebleValoracionConstruccion(
                                    tipologia=terreno.tipologia,
                                    tipo=terreno.tipo,
                                    area=terreno.area-total_area_construccion,
                                    aplica=terreno.aplica,
                                    inmueblevaloracionterreno=terreno  # Asignar la relación con el objeto terreno
                                )
                                # Agregar el nuevo objeto a la variable "ocupacion"
                                ocupacion = list(ocupacion)  # Convertir "ocupacion" en una lista
                                ocupacion.append(nuevo_objeto_construccion)  # Agregar el nuevo objeto a la lista
                            # En este punto, "ocupacion" contiene todos los objetos, incluido el nuevo objeto si se cumple la condición
                    ##print('ocupacion',ocupacion)
                    ZonaInmueble=Zona.zona
                    oTipologia=Tipologia.objects.filter(zona=ZonaInmueble)

                    #Ubicar la fecha de compra
                    ##oPropietario = InmueblePropietarios.objects.get(propietario=request['propietario'],inmueble=request['inmueble'])
                    ##fechaCompra=oPropietario.fecha_compra
                    ##diferencia=today-fechaCompra
                    ####print(fechaCompra,today,diferencia.days)
                    # valida si aplica descuentos por pronto pago.
                    oDescuento=0 # Bandera que valida si aplica descuento o no
                    try:
                        oDescuento=IC_ImpuestoDescuento.objects.filter(habilitado=True,aplica='C')
                    except:
                        oDescuento=0
                    bMulta=True
                    oCargos=IC_ImpuestoCargos.objects.filter(habilitado=True,aplica='C')
                    fMulta=float(oCargos.get(codigo='multa').porcentaje)
                    fRecargo=float(oCargos.get(codigo='recargo').porcentaje)
                    tBaseMultaRecargoInteres=0
                    tTotalInteresMoratorio=0
                    tMulta=0
                    tRecargo=0
                    tInteres=0
                    tTotal=0
                    tTotalMora=0
                    tDescuento=0
                    while minimo_ano<=maximo_ano:
                        oBaseCalculo = UnidadTributaria.objects.get(habilitado=True,fecha__year=minimo_ano)
                        baseCalculoBs= float(oBaseCalculo.monto)
                        #para los años menores al actual, toma los periodos pendientes segun el historico
                        PeriodosCxc=oImpuestoPeriodo.filter(anio=minimo_ano).order_by('periodo')
                        if minimo_ano==today.year:
                            # para el año en curso, solo procesa hasta el periodo que el contribuyente decide cancelar
                            PeriodosCxc=oImpuestoPeriodo.filter(anio=minimo_ano,periodo__lte=4).order_by('periodo')

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
                                today <= fDiasGracia.fechadesde+timedelta(days=fDiasGracia.dias_gracia) :
                                    # La fecha actual está entre las fechas del modelo
                                    ##print("La fecha actual está entre fecha_desde y fecha_hasta.",fDiasGracia)
                                    bMulta=False
                                else:
                                    if today<= fDiasGracia.fechadesde and  \
                                        today <= fDiasGracia.fechadesde+timedelta(days=fDiasGracia.dias_gracia) :
                                        # La fecha actual es menor a las fechas del modelo (periodos proximos)
                                        ##print("La fecha actual es menor a las fechas del modelo (periodos proximos).",fDiasGracia)
                                        bMulta=False

                                    # La fecha actual NO está entre las fechas del modelo
                                    ##print("La fecha actual NO está entre fecha_desde y fecha_hasta.")
                            for dato in ocupacion:
                                #Zona 1: Terrenos sin edificar mayores de 2.000 m2 en
                                #posesión por 5 años o más por el mismo propietario
                                Alicuota=float(oTipologia.get(id=dato.tipologia.id).tarifa)
                                Monto=float(dato.area)*(Alicuota*iAlicuota)*baseCalculoBs
                                mDescuento=0
                                ppDescuento=0
                                if oDescuento: # and minimo_ano==today.year:
                                    # Valida que aplique descuento solamente con el año actual  !! inactivo. aplica descuento segun la tabla
                                    # Aplica descuentos generales
                                    aPeriodoMesDesde=aPeriodo.periodo.fechadesde.month
                                    aPeriodoMesHasta=aPeriodo.periodo.fechahasta.month
                                    aPeriodoDiaDesde=aPeriodo.periodo.fechadesde.day
                                    aPeriodoDiaHasta=aPeriodo.periodo.fechahasta.day
                                    try:
                                        pDescuento=oDescuento.filter(Q(tipologia__isnull=True) | Q(tipologia=dato.tipologia.id,) | Q(inmueble__isnull=True) | Q(inmueble=oInmueble.id,),prontopago=False)
                                        ##print('descuento',pDescuento)
                                        ##print('registros',aPeriodo.periodo.fechadesde,aPeriodo.periodo.fechahasta) 
                                        registros_validos = pDescuento.filter(
                                            fechadesde__year__lte=minimo_ano,
                                            fechahasta__year__gte=minimo_ano,
                                            fechadesde__month__lte=aPeriodoMesDesde,
                                            fechahasta__month__gte=aPeriodoMesHasta,
                                            fechadesde__day__lte=aPeriodoDiaDesde,
                                            fechahasta__day__gte=aPeriodoDiaHasta) 
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
                                            'IC_impuestoperiodo':aPeriodo.periodo.id,
                                            'uso_id':dato.tipologia.id,
                                            'uso_descripcion':dato.tipologia.descripcion,
                                            'apica':dato.aplica,
                                            'anio': minimo_ano,
                                            'periodo': aPeriodo.periodo.periodo,
                                        }
                                        aDescuento.append(ImpuestoDetalleDescuentos)

                                    # Aplica descuentos prontopago
                                    try:
                                        pDescuento=oDescuento.filter(Q(tipologia__isnull=True) | Q(tipologia=dato.tipologia.id,)  | Q(inmueble__isnull=True) | Q(inmueble=oInmueble.id,),prontopago=True)
                                        ##print('descuento Pronto Pago',pDescuento)
                                        ##print('fecha actual',today.year,today.month,today.day) 
                                        ##print('fecha periodo',minimo_ano,aPeriodoMesDesde,aPeriodoDiaDesde,minimo_ano,aPeriodoMesHasta,aPeriodoDiaHasta) 
                                        registros_validos = pDescuento.filter(
                                            #fechadesde__year__lte=today.year,   # < =
                                            #fechahasta__year__gte=today.year,   # > =
                                            fechadesde__year=minimo_ano,
                                            fechadesde__month__lte=today.month, # < =
                                            fechahasta__month__gte=today.month, # > =
                                            fechadesde__day__lte=today.day,     # < =
                                            fechahasta__day__gte=today.day)     # > =
                                        ##print('registros_validos pronto pago 1',registros_validos)
                                        registros_validos2 = registros_validos.filter(
                                            fechadesde__year__lte=minimo_ano,       # < =
                                            fechahasta__year__gte=minimo_ano,       # > =
                                            fechadesde__month__lte=aPeriodoMesDesde,# < =
                                            fechahasta__month__gte=aPeriodoMesDesde,# > =
                                            fechadesde__day__lte=aPeriodoDiaDesde,  # < =
                                            fechahasta__day__gte=aPeriodoDiaDesde)  # > =
                                        ##print('registros_validos pronto pago 2',registros_validos2)
                                        ppDescuento=float(registros_validos.aggregate(Sum('porcentaje'))['porcentaje__sum'])
                                    except:
                                        ppDescuento=0
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
                                            'IC_impuestoperiodo':aPeriodo.periodo.id,
                                            'uso_id':dato.tipologia.id,
                                            'uso_descripcion':dato.tipologia.descripcion,
                                            'apica':dato.aplica,
                                            'anio': minimo_ano,
                                            'periodo': aPeriodo.periodo.periodo,
                                        }
                                        aDescuento.append(ImpuestoDetalleDescuentos)


                                Total=float(Monto-(Monto*((mDescuento+ppDescuento)/100)))

                                ImpuestoDetalle = {
                                    'IC_impuestoperiodo':aPeriodo.periodo.id,
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
                                    'mdescuento':mDescuento+ppDescuento,
                                    'total':Total,
                                }
                                tTotalInteresMoratorio=tTotalInteresMoratorio+Total
                                tDescuento=tDescuento+mDescuento+ppDescuento
                                aDetalle.append(ImpuestoDetalle)
                                tTotal=tTotal+Total
                                if bMulta:
                                    tTotalMora=tTotalMora+Total
                                    tBaseMultaRecargoInteres=tBaseMultaRecargoInteres+Total
                                    tMulta=tMulta+(Total*(fMulta/100))
                                    tRecargo=tRecargo+(Total*(fRecargo/100))
                        if tTotalMora:
                            #oTasaInteres=TasaInteres.objects.filter(anio=minimo_ano).order_by('mes')
                            #tTotalMora=(tTotalMora/12)
                            #for aTasa in oTasaInteres:
                                #if (aTasa.mes<=today.month and minimo_ano==today.year) or minimo_ano!=today.year:
                                    #cantidad_dias = obtener_cantidad_dias(aTasa.anio, aTasa.mes)
                                    #tasa_porcentaje=float(aTasa.tasa/100)
                                    #monto=((tTotalMora*tasa_porcentaje)/360)*cantidad_dias
                                    #ImpuestoInteresMoratorio={
                                    #        'anio':aTasa.anio,
                                    #        'mes':aTasa.mes,
                                    #        'tasa':tasa_porcentaje*100,
                                    #        'dias':cantidad_dias,
                                    #        'moramensual':tTotalMora,
                                    #        'interesmensual':monto,
                                    #    }
                                    #aInteres.append(ImpuestoInteresMoratorio)
                                    #tInteres=tInteres+monto
                                #end If
                            # end For oTasaInteres                    
                            oTasaInteres=TasaInteres.objects.filter(anio=minimo_ano).order_by('mes')
                            if minimo_ano==today.year:
                                tTotalInteresMoratorio=tTotalInteresMoratorio/request['periodo']
                                tTotalInteresMoratorio=tTotalInteresMoratorio*4
                            tTotalMora4=(tTotalInteresMoratorio/1)
                            tTotalMora3=(tTotalInteresMoratorio/4)*3
                            tTotalMora2=(tTotalInteresMoratorio/2)
                            tTotalMora1=(tTotalInteresMoratorio/4)
                            incremento=1.200000000
                            incremento_decimal = Decimal(str(incremento))
                            for aTasa in oTasaInteres:
                                if (aTasa.mes<=today.month and minimo_ano==today.year) or minimo_ano!=today.year:
                                    if (aTasa.mes==today.month and minimo_ano==today.year):
                                        cantidad_dias = today.day
                                    else:
                                        cantidad_dias = obtener_cantidad_dias(aTasa.anio, aTasa.mes) 
                                    tasa_porcentaje=float((aTasa.tasa*incremento_decimal)/100)
                                    if  aTasa.mes==1: 
                                        monto=0
                                        por_mes=0
                                    if  aTasa.mes==2:
                                        monto=0
                                        por_mes=0
                                    if  aTasa.mes==3:
                                        monto=0
                                        por_mes=0
                                    if  aTasa.mes==4:
                                        monto=((tTotalMora1*tasa_porcentaje)/360)*cantidad_dias 
                                        por_mes=tTotalMora1
                                    if  aTasa.mes==5:
                                        monto=((tTotalMora2*tasa_porcentaje)/360)*cantidad_dias
                                        por_mes=tTotalMora2
                                    if  aTasa.mes==6:
                                        monto=((tTotalMora2*tasa_porcentaje)/360)*cantidad_dias
                                        por_mes=tTotalMora2
                                    if  aTasa.mes==7:
                                        monto=((tTotalMora2*tasa_porcentaje)/360)*cantidad_dias
                                        por_mes=tTotalMora2
                                    if  aTasa.mes==8:
                                        monto=((tTotalMora3*tasa_porcentaje)/360)*cantidad_dias
                                        por_mes=tTotalMora3
                                    if  aTasa.mes==9:
                                        monto=((tTotalMora3*tasa_porcentaje)/360)*cantidad_dias
                                        por_mes=tTotalMora3
                                    if  aTasa.mes==10:
                                        monto=((tTotalMora3*tasa_porcentaje)/360)*cantidad_dias
                                        por_mes=tTotalMora3
                                    if  aTasa.mes==11:
                                        monto=((tTotalMora4*tasa_porcentaje)/360)*cantidad_dias
                                        por_mes=tTotalMora4
                                    if  aTasa.mes==12:
                                        monto=((tTotalMora4*tasa_porcentaje)/360)*cantidad_dias
                                        por_mes=tTotalMora4
                                    ImpuestoInteresMoratorio={
                                            'anio':aTasa.anio,
                                            'mes':aTasa.mes,
                                            'tasa':tasa_porcentaje*100,
                                            'dias':cantidad_dias,
                                            'moramensual':por_mes,
                                            'interesmensual':monto,
                                        }
                                    aInteres.append(ImpuestoInteresMoratorio)
                                    tInteres=tInteres+monto
                                #end If
                            # end For oTasaInteres 

                            tTotalMora=0


                        tTotalInteresMoratorio=0
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
                        'descuento':tDescuento,
                        'total':tTotal+tMulta+tRecargo+tInteres,
                        'BaseMultaRecargoInteres':tBaseMultaRecargoInteres,
                        'flujo':Flujo.objects.filter(inmueble=oInmueble,estado='1').count() ,
                        'anioini':anioini,
                        'mesini':mesini,
                        'aniofin':request['anio'],
                        'mesfin':request['periodo'],
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

def Impuesto_Inmueble2023_Public(request):
    if (request):
        anioini=0
        mesini=0
        data = []
        aDetalle = []
        aDescuento = []
        aInteres = []
        if (request['inmueble']):
            not_process=False
            try:
                oInmueble = Inmueble.objects.get(numero_expediente=request['inmueble'], status__inmueble_activo=True)
            except Inmueble.DoesNotExist:
                 not_process=True
            if not_process:
                return Response('Inmueble con estatus por procesar en catastro', status=status.HTTP_400_BAD_REQUEST)
            else:
                ## esto contruye la tabla de periodos por inmueble para mantener el historico
                # esto permite saber si esta pendientes por cancelar
                ############## inicio
                today = date.today()
                #Zona = Urbanizacion.objects.get(id=oInmueble.urbanizacion.id)
                Zona = oInmueble
                oPeriodo = IC_Periodo.objects.filter(aplica='C')
                ano_fin= 2023 #request['anio']  #today.year
                ##print('oInmueble.anio:',oInmueble.anio)
                if oInmueble.anio is None: # si al momento de importar de excel  no tiene pagos, le coloco el año de la fecha de inscripcion
                    oInmueble.anio=oInmueble.fecha_inscripcion.year
                    oInmueble.periodo=IC_Periodo.objects.get(aplica='C',periodo=1)
                    oInmueble.save()
                    dAnio=oInmueble.anio
                    dPeriodo=oInmueble.periodo.periodo 
                    ##print('creadooo')
                dAnio=oInmueble.anio        # Año que incia la deuda
                dPeriodo=oInmueble.periodo.periodo  # Periodo que inicia la deuda
                anioini=dAnio
                ##print('AÑO INICIO DEUDAAAAAA1111111111',anioini)
                if anioini<((today.year+1)-7):
                    anioini=((today.year+1)-7)
                    dAnio=anioini
                ##print('AÑO INICIO DEUDAAAAAA2222222222',anioini)  
                mesini=dPeriodo
                primero=True
                ##print('kkkkkkkkkkkkkkkkkkkkkk',dPeriodo) 

                IC_ImpuestoPeriodo.objects.filter(inmueble=oInmueble).delete()  # elimina el historial de periodos pendientes
                                                        #por que este dato lo puede cambiar hacienda con acceso.borrar=true
                while dAnio<=ano_fin: # crea la cxc de periodos pendientes
                    if primero:
                        oPeriodo = IC_Periodo.objects.filter(aplica='C',periodo__gte=dPeriodo)
                        primero=False
                    else:
                        oPeriodo = IC_Periodo.objects.filter(aplica='C')
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
                oImpuestoPeriodo = IC_ImpuestoPeriodo.objects.filter(inmueble__numero_expediente=request['inmueble']).order_by('anio', 'periodo')
                if oImpuestoPeriodo:
                    # se maneja ahora un metepo por año por rso se quita eso aca
                    #oBaseCalculo = UnidadTributaria.objects.get(habilitado=True)
                    #baseCalculoBs= float(oBaseCalculo.monto)

                    #Crear lista con los años presentes en la cxc
                    oAnio = IC_ImpuestoPeriodo.objects.filter(inmueble__numero_expediente=request['inmueble']).values('anio').distinct().order_by('anio')
                    maximo_ano = oAnio.aggregate(Max('anio'))['anio__max']
                    minimo_ano = oAnio.aggregate(Min('anio'))['anio__min']
                    
                    # Contar la cantidad de periodos configurados para C atastro
                    tPeriodo= IC_Periodo.objects.filter(aplica='C')
                    CountPeriodo= tPeriodo.count()
                    terreno =      InmuebleValoracionTerreno.objects.get(inmueble__numero_expediente=request['inmueble'])
                    construccion = InmuebleValoracionConstruccion.objects.filter(inmueblevaloracionterreno=terreno)
                    if terreno:
                        total_area_terreno = terreno.area 
                    else:
                        total_area_terreno = 0

                    if construccion:
                        total_area_construccion = construccion.aggregate(Sum('area'))['area__sum']
                    else:
                        total_area_construccion = 0

                    if (total_area_construccion > total_area_terreno) or (total_area_terreno==0 and total_area_construccion>0):
                        ocupacion=construccion
                    elif total_area_terreno>0 and total_area_construccion==0:
                        ocupacion =  InmuebleValoracionTerreno.objects.filter(inmueble__numero_expediente=request['inmueble'])
                        ocupacion = list(ocupacion) 
                    else:
                        ocupacion=construccion
                        if terreno: # hay inmuebles que NO TIENEN TERRENO, PARA ESE CASO NO ENTRA, SOLO TOMA LA CONTRUCCION
                            if total_area_construccion < total_area_terreno:
                                # Crear una nueva instancia de InmuebleValoracionConstruccion sin guardar en la base de datos
                                
                                nuevo_objeto_construccion = InmuebleValoracionConstruccion(
                                    tipologia=terreno.tipologia,
                                    tipo=terreno.tipo,
                                    area=terreno.area-total_area_construccion,
                                    aplica=terreno.aplica,
                                    inmueblevaloracionterreno=terreno  # Asignar la relación con el objeto terreno
                                )
                                # Agregar el nuevo objeto a la variable "ocupacion"
                                ocupacion = list(ocupacion)  # Convertir "ocupacion" en una lista
                                ocupacion.append(nuevo_objeto_construccion)  # Agregar el nuevo objeto a la lista
                            # En este punto, "ocupacion" contiene todos los objetos, incluido el nuevo objeto si se cumple la condición
                    ##print('ocupacion',ocupacion)
                    ZonaInmueble=Zona.zona
                    oTipologia=Tipologia.objects.filter(zona=ZonaInmueble)

                    #Ubicar la fecha de compra
                    ##oPropietario = InmueblePropietarios.objects.get(propietario=request['propietario'],inmueble__numero_expediente=request['inmueble'])
                    ##fechaCompra=oPropietario.fecha_compra
                    ##diferencia=today-fechaCompra
                    ####print(fechaCompra,today,diferencia.days)
                    # valida si aplica descuentos por pronto pago.
                    oDescuento=0 # Bandera que valida si aplica descuento o no
                    try:
                        oDescuento=IC_ImpuestoDescuento.objects.filter(habilitado=True,aplica='C')
                    except:
                        oDescuento=0
                    bMulta=True
                    oCargos=IC_ImpuestoCargos.objects.filter(habilitado=True,aplica='C')
                    fMulta=float(oCargos.get(codigo='multa').porcentaje)
                    fRecargo=float(oCargos.get(codigo='recargo').porcentaje)
                    tBaseMultaRecargoInteres=0
                    tTotalInteresMoratorio=0
                    tMulta=0
                    tRecargo=0
                    tInteres=0
                    tTotal=0
                    tTotalMora=0
                    tDescuento=0
                    while minimo_ano<=maximo_ano:
                        oBaseCalculo = UnidadTributaria.objects.get(habilitado=True,fecha__year=minimo_ano)
                        baseCalculoBs= float(oBaseCalculo.monto)
                        #para los años menores al actual, toma los periodos pendientes segun el historico
                        PeriodosCxc=oImpuestoPeriodo.filter(anio=minimo_ano).order_by('periodo')
                        if minimo_ano==today.year:
                            # para el año en curso, solo procesa hasta el periodo que el contribuyente decide cancelar
                            PeriodosCxc=oImpuestoPeriodo.filter(anio=minimo_ano,periodo__lte=4).order_by('periodo')

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
                                today <= fDiasGracia.fechadesde+timedelta(days=fDiasGracia.dias_gracia) :
                                    # La fecha actual está entre las fechas del modelo
                                    ##print("La fecha actual está entre fecha_desde y fecha_hasta.",fDiasGracia)
                                    bMulta=False
                                else:
                                    if today<= fDiasGracia.fechadesde and  \
                                        today <= fDiasGracia.fechadesde+timedelta(days=fDiasGracia.dias_gracia) :
                                        # La fecha actual es menor a las fechas del modelo (periodos proximos)
                                        ##print("La fecha actual es menor a las fechas del modelo (periodos proximos).",fDiasGracia)
                                        bMulta=False

                                    # La fecha actual NO está entre las fechas del modelo
                                    ##print("La fecha actual NO está entre fecha_desde y fecha_hasta.")
                            for dato in ocupacion:
                                #Zona 1: Terrenos sin edificar mayores de 2.000 m2 en
                                #posesión por 5 años o más por el mismo propietario 
                                Alicuota=float(oTipologia.get(id=dato.tipologia.id).tarifa)
                                Monto=float(dato.area)*(Alicuota*iAlicuota)*baseCalculoBs
                                mDescuento=0
                                ppDescuento=0
                                if oDescuento: # and minimo_ano==today.year:
                                    # Valida que aplique descuento solamente con el año actual  !! inactivo. aplica descuento segun la tabla
                                    # Aplica descuentos generales
                                    aPeriodoMesDesde=aPeriodo.periodo.fechadesde.month
                                    aPeriodoMesHasta=aPeriodo.periodo.fechahasta.month
                                    aPeriodoDiaDesde=aPeriodo.periodo.fechadesde.day
                                    aPeriodoDiaHasta=aPeriodo.periodo.fechahasta.day
                                    try:
                                        pDescuento=oDescuento.filter(Q(tipologia__isnull=True) | Q(tipologia=dato.tipologia.id,) | Q(inmueble__isnull=True) | Q(inmueble=oInmueble.id,),prontopago=False)
                                        ##print('descuento',pDescuento)
                                        ##print('registros',aPeriodo.periodo.fechadesde,aPeriodo.periodo.fechahasta) 
                                        registros_validos = pDescuento.filter(
                                            fechadesde__year__lte=minimo_ano,
                                            fechahasta__year__gte=minimo_ano,
                                            fechadesde__month__lte=aPeriodoMesDesde,
                                            fechahasta__month__gte=aPeriodoMesHasta,
                                            fechadesde__day__lte=aPeriodoDiaDesde,
                                            fechahasta__day__gte=aPeriodoDiaHasta) 
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
                                            'IC_impuestoperiodo':aPeriodo.periodo.id,
                                            'uso_id':dato.tipologia.id,
                                            'uso_descripcion':dato.tipologia.descripcion,
                                            'apica':dato.aplica,
                                            'anio': minimo_ano,
                                            'periodo': aPeriodo.periodo.periodo,
                                        }
                                        aDescuento.append(ImpuestoDetalleDescuentos)

                                    # Aplica descuentos prontopago
                                    try:
                                        pDescuento=oDescuento.filter(Q(tipologia__isnull=True) | Q(tipologia=dato.tipologia.id,) | Q(inmueble__isnull=True) | Q(inmueble=oInmueble.id,),prontopago=True)
                                        ##print('descuento Pronto Pago',pDescuento)
                                        ##print('fecha actual',today.year,today.month,today.day) 
                                        ##print('fecha periodo',minimo_ano,aPeriodoMesDesde,aPeriodoDiaDesde,minimo_ano,aPeriodoMesHasta,aPeriodoDiaHasta) 
                                        registros_validos = pDescuento.filter(
                                            #fechadesde__year__lte=today.year,   # < =
                                            #fechahasta__year__gte=today.year,   # > =
                                            fechadesde__year=minimo_ano,
                                            fechadesde__month__lte=today.month, # < =
                                            fechahasta__month__gte=today.month, # > =
                                            fechadesde__day__lte=today.day,     # < =
                                            fechahasta__day__gte=today.day)     # > =
                                        ##print('registros_validos pronto pago 1',registros_validos)
                                        registros_validos2 = registros_validos.filter(
                                            fechadesde__year__lte=minimo_ano,       # < =
                                            fechahasta__year__gte=minimo_ano,       # > =
                                            fechadesde__month__lte=aPeriodoMesDesde,# < =
                                            fechahasta__month__gte=aPeriodoMesDesde,# > =
                                            fechadesde__day__lte=aPeriodoDiaDesde,  # < =
                                            fechahasta__day__gte=aPeriodoDiaDesde)  # > =
                                        ##print('registros_validos pronto pago 2',registros_validos2)
                                        ppDescuento=float(registros_validos.aggregate(Sum('porcentaje'))['porcentaje__sum'])
                                    except:
                                        ppDescuento=0
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
                                            'IC_impuestoperiodo':aPeriodo.periodo.id,
                                            'uso_id':dato.tipologia.id,
                                            'uso_descripcion':dato.tipologia.descripcion,
                                            'apica':dato.aplica,
                                            'anio': minimo_ano,
                                            'periodo': aPeriodo.periodo.periodo,
                                        }
                                        aDescuento.append(ImpuestoDetalleDescuentos)
                                Total=float(Monto-(Monto*((mDescuento+ppDescuento)/100)))
                                ImpuestoDetalle = {
                                    'IC_impuestoperiodo':aPeriodo.periodo.id,
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
                                    'mdescuento':mDescuento+ppDescuento,
                                    'total':Total,
                                }
                                tTotalInteresMoratorio=tTotalInteresMoratorio+Total
                                tDescuento=tDescuento+mDescuento+ppDescuento
                                aDetalle.append(ImpuestoDetalle)
                                tTotal=tTotal+Total
                                if bMulta:
                                    tTotalMora=tTotalMora+Total
                                    tBaseMultaRecargoInteres=tBaseMultaRecargoInteres+Total
                                    tMulta=tMulta+(Total*(fMulta/100))
                                    tRecargo=tRecargo+(Total*(fRecargo/100))
                        if tTotalMora:                   
                            oTasaInteres=TasaInteres.objects.filter(anio=minimo_ano).order_by('mes')
                            if minimo_ano==today.year:
                                tTotalInteresMoratorio=tTotalInteresMoratorio/request['periodo']
                                tTotalInteresMoratorio=tTotalInteresMoratorio*4
                            tTotalMora4=(tTotalInteresMoratorio/1)
                            tTotalMora3=(tTotalInteresMoratorio/4)*3
                            tTotalMora2=(tTotalInteresMoratorio/2)
                            tTotalMora1=(tTotalInteresMoratorio/4)
                            incremento=1.200000000
                            incremento_decimal = Decimal(str(incremento))
                            for aTasa in oTasaInteres:
                                if (aTasa.mes<=today.month and minimo_ano==today.year) or minimo_ano!=today.year:
                                    if (aTasa.mes==today.month and minimo_ano==today.year):
                                        cantidad_dias = today.day
                                    else:
                                        cantidad_dias = obtener_cantidad_dias(aTasa.anio, aTasa.mes) 
                                    tasa_porcentaje=float((aTasa.tasa*incremento_decimal)/100)
                                    if  aTasa.mes==1: 
                                        monto=0
                                        por_mes=0
                                    if  aTasa.mes==2:
                                        monto=0
                                        por_mes=0
                                    if  aTasa.mes==3:
                                        monto=0
                                        por_mes=0
                                    if  aTasa.mes==4:
                                        monto=((tTotalMora1*tasa_porcentaje)/360)*cantidad_dias 
                                        por_mes=tTotalMora1
                                    if  aTasa.mes==5:
                                        monto=((tTotalMora2*tasa_porcentaje)/360)*cantidad_dias
                                        por_mes=tTotalMora2
                                    if  aTasa.mes==6:
                                        monto=((tTotalMora2*tasa_porcentaje)/360)*cantidad_dias
                                        por_mes=tTotalMora2
                                    if  aTasa.mes==7:
                                        monto=((tTotalMora2*tasa_porcentaje)/360)*cantidad_dias
                                        por_mes=tTotalMora2
                                    if  aTasa.mes==8:
                                        monto=((tTotalMora3*tasa_porcentaje)/360)*cantidad_dias
                                        por_mes=tTotalMora3
                                    if  aTasa.mes==9:
                                        monto=((tTotalMora3*tasa_porcentaje)/360)*cantidad_dias
                                        por_mes=tTotalMora3
                                    if  aTasa.mes==10:
                                        monto=((tTotalMora3*tasa_porcentaje)/360)*cantidad_dias
                                        por_mes=tTotalMora3
                                    if  aTasa.mes==11:
                                        monto=((tTotalMora4*tasa_porcentaje)/360)*cantidad_dias
                                        por_mes=tTotalMora4
                                    if  aTasa.mes==12:
                                        monto=((tTotalMora4*tasa_porcentaje)/360)*cantidad_dias
                                        por_mes=tTotalMora4
                                    ImpuestoInteresMoratorio={
                                            'anio':aTasa.anio,
                                            'mes':aTasa.mes,
                                            'tasa':tasa_porcentaje*100,
                                            'dias':cantidad_dias,
                                            'moramensual':por_mes,
                                            'interesmensual':monto,
                                        }
                                    aInteres.append(ImpuestoInteresMoratorio)
                                    tInteres=tInteres+monto
                                #end If
                            # end For oTasaInteres 
                            tTotalMora=0
                        tTotalInteresMoratorio=0
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
                        'descuento':tDescuento,
                        'total':tTotal+tMulta+tRecargo+tInteres,
                        'BaseMultaRecargoInteres':tBaseMultaRecargoInteres,
                        'flujo':Flujo.objects.filter(inmueble=oInmueble,estado='1').count() ,
                        'anioini':anioini,
                        'mesini':mesini,
                        'aniofin':request['anio'],
                        'mesfin':request['periodo'],
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

def Datos_Inmuebles_Public(request):
    # esta Api publica permite ver la salud de un expediente para calculo de impuestos y retorna los siguientes errorres:
    # Response({'error':1,'mensaje':'Error: Falta Período de último pago'}, status=status.HTTP_200_OK)
    # Response({'error':2,'mensaje':'Error: No tiene Valoración Económica'}, status=status.HTTP_200_OK)
    # Response({'error':3,'mensaje':'Error: Falta Periodo de último pago y no tiene Valoración Económica'}, status=status.HTTP_200_OK)
    # Response({'error':4,'mensaje':'Inmueble con estatus por procesar en catastro o No existe'}, status=status.HTTP_200_OK)
    # Response({'error':5,'mensaje':'Error: Sin CATEGORIZACION. Revisar en Catastro'}, status=status.HTTP_200_OK)
    # Response({'error':5,'mensaje':'Error: Sin ZONA. Revisar en Catastro'}, status=status.HTTP_200_OK)
    # Response({'error':6,'mensaje':'Error: La ZONA de la ficha no es la misma que tiene el uso de TERRENO.'}, status=status.HTTP_200_OK)
    # Response({'error':6,'mensaje':'Error: La CATEGORIZACION de la ficha no es la misma que tiene el uso de TERRENO.'}, status=status.HTTP_200_OK)
    # Response({'error':7,'mensaje':'Error: La ZONA de la ficha no es la misma que tiene el uso de CONSTRUCION.'}, status=status.HTTP_200_OK)
    # Response({'error':7,'mensaje':'Error: La CATEGORIZACION de la ficha no es la misma que tiene el uso de CONSTRUCION.'}, status=status.HTTP_200_OK) 
    # Response({'error':9,'mensaje':'Sin datos'}, status=status.HTTP_200_OK)
    # Response({'error':8,'mensaje':'Error: El area de Valoración Económica de TERRENO NO conincide en ZONA y en CATEGORIZACION.'}, status=status.HTTP_200_OK)     
    # Response({'error':8,'mensaje':'Error: El area de Valoración Económica de CONSTRUCCION NO conincide en ZONA y en CATEGORIZACION.'}, status=status.HTTP_200_OK)     


    if (request):
        data = []
        aPropietario = []
        if (request['inmueble']):
            not_process=False
            try:
                oInmueble = Inmueble.objects.get(numero_expediente=request['inmueble'], status__inmueble_activo=True)
                if oInmueble.categorizacion:
                    categoria=oInmueble.categorizacion.codigo
                else:
                    categoria='SIN CATEGORIZACION!!!'
                    return Response({'error':5,'mensaje':'Error: Sin CATEGORIZACION. Revisar en Catastro'}, status=status.HTTP_200_OK)
                if oInmueble.zona:
                    zona=oInmueble.zona.codigo
                else:
                    zona='SIN ZONA!!!'
                    return Response({'error':5,'mensaje':'Error: Sin ZONA. Revisar en Catastro'}, status=status.HTTP_200_OK)
                total_area_terreno=0
                total_area_construccion = 0
                total_area_terreno2024=0
                total_area_construccion2024 = 0
                dAnio=oInmueble.anio        # Año que inicia la deuda
                if oInmueble.periodo is None:
                    return Response({'error':1,'mensaje':'Error: Falta Périodo de último pago'}, status=status.HTTP_200_OK)

                if dAnio>=2024:
                    terreno=False
                    construccion=False
                    terreno2024 =      InmuebleValoracionTerreno2024.objects.get(inmueble__numero_expediente=request['inmueble'])
                    construccion2024 = InmuebleValoracionConstruccion2024.objects.filter(inmueblevaloracionterreno=terreno2024) 
                else:
                    terreno =          InmuebleValoracionTerreno.objects.get(inmueble__numero_expediente=request['inmueble'])
                    construccion =     InmuebleValoracionConstruccion.objects.filter(inmueblevaloracionterreno=terreno)
                    terreno2024 =      InmuebleValoracionTerreno2024.objects.get(inmueble__numero_expediente=request['inmueble'])
                    construccion2024 = InmuebleValoracionConstruccion2024.objects.filter(inmueblevaloracionterreno=terreno2024)
                # Aca se valida si la zona/categoria del terreno o costruccion es igual a la zona de la ficha solo si tiene algo de area
                # Si se cumple entonces envia error, esto para avisar que no podra calcular impuesto con esta inconsitencia
                if terreno:    
                    total_area_terreno = terreno.area 
                    if (total_area_terreno>0 and terreno.tipologia.zona.codigo!=zona): 
                        return Response({'error':6,'mensaje':'Error: La ZONA de la ficha no es la misma que tiene el uso de TERRENO.'}, status=status.HTTP_200_OK)
                if construccion:
                    total_area_construccion = construccion.aggregate(Sum('area'))['area__sum']
                    zona_errada = construccion.exclude(tipologia__zona__codigo=zona).count() 
                    if (total_area_construccion>0 and zona_errada>0): 
                        return Response({'error':7,'mensaje':'Error: La ZONA de la ficha no es la misma que tiene el uso de CONSTRUCION.'}, status=status.HTTP_200_OK)
                if terreno2024:
                    total_area_terreno2024 = terreno2024.area 
                    if (total_area_terreno2024>0 and terreno2024.tipologia_categorizacion.categorizacion.codigo!=categoria):
                        return Response({'error':6,'mensaje':'Error: La CATEGORIZACION de la ficha no es la misma que tiene el uso de TERRENO.'}, status=status.HTTP_200_OK)
                if construccion2024:
                    total_area_construccion2024 = construccion2024.aggregate(Sum('area'))['area__sum']
                    categoria_errada = construccion2024.exclude(tipologia_categorizacion__categorizacion__codigo=categoria).count() 
                    if (total_area_construccion2024>0 and categoria_errada>0): 
                        return Response({'error':7,'mensaje':'Error: La CATEGORIZACION de la ficha  no es la misma que tiene el uso de CONSTRUCION.'}, status=status.HTTP_200_OK)     
                # Aca se valida si las area de terreno ZONA es diferente terreno CATEGORIA. Igual en construccion.
                if dAnio<2024:
                    if total_area_terreno!=total_area_terreno2024:
                        return Response({'error':8,'mensaje':'Error: El area de Valoración Económica de TERRENO NO conincide en ZONA y en CATEGORIZACION.'}, status=status.HTTP_200_OK)     
                    if total_area_construccion!=total_area_construccion2024:
                        return Response({'error':8,'mensaje':'Error: El área de Valoración Económica de CONSTRUCCION NO conincide en ZONA y en CATEGORIZACION.'}, status=status.HTTP_200_OK)     
                if oInmueble.periodo is None and total_area_terreno+total_area_construccion==0:
                    return Response({'error':3,'mensaje':'Error: Falta Período de último pago y no tiene Valoración Económica'}, status=status.HTTP_200_OK)
                
                if (total_area_terreno+total_area_construccion==0 and dAnio<2024) and total_area_terreno2024+total_area_construccion2024==0:
                    return Response({'error':2,'mensaje':'Error: No tiene Valoración Económica ZONA tampoco Valoración Económica CATEGORIZACION'}, status=status.HTTP_200_OK)
                if total_area_terreno+total_area_construccion==0 and dAnio<2024:
                    return Response({'error':2,'mensaje':'Error: No tiene Valoración Económica ZONA'}, status=status.HTTP_200_OK)
                if total_area_terreno2024+total_area_construccion2024==0:
                    return Response({'error':2,'mensaje':'Error: No tiene Valoración Económica CATEGORIZACION'}, status=status.HTTP_200_OK)
                dPeriodo=oInmueble.periodo.periodo  # Periodo que inicia la deuda
                oPropietario = InmueblePropietarios.objects.filter(inmueble__numero_expediente=request['inmueble'])
            except Inmueble.DoesNotExist:
                 not_process=True
            if not_process:
                return Response({'error':4,'mensaje':'Inmueble con estatus por procesar en catastro o No existe'}, status=status.HTTP_200_OK)
            else:
                if oPropietario:
                    for propietario in oPropietario:
                        inmueblepropietarios={
                            'Documento':propietario.propietario.numero_documento,
                            'Nombre':propietario.propietario.nombre,
                            'Telefono':propietario.propietario.telefono_principal,
                            'email':propietario.propietario.email_principal,
                            'direccion':propietario.propietario.direccion,
                            'direccionI':oInmueble.direccion,
                        }
                        aPropietario.append(inmueblepropietarios)
                Impuesto={
                    'expediente':oInmueble.numero_expediente,
                    'zona':oInmueble.zona.codigo,
                    'categoria':categoria,
                    'Anio':dAnio,
                    'Periodo':dPeriodo,
                    'AreaTerreno':total_area_terreno,
                    'AreaConstruccion':total_area_construccion,
                    'AreaTerreno2024':total_area_terreno2024,
                    'AreaConstruccion2024':total_area_construccion2024,
                }
                datos={
                    'cabacera':Impuesto,
                    'propietarios':aPropietario,
                    'error':0,
                    'mensaje':'Carga exitosa'
                }
                data.append(datos)
            return Response(data, status=status.HTTP_200_OK)
        return Response({'error':9,'mensaje':'Sin datos'}, status=status.HTTP_200_OK)
    else:
        return Response({'error':9,'mensaje':'Sin datos'}, status=status.HTTP_200_OK)


def Impuesto_Inmueble_Pago(request):
    if (request):
        if (request['inmueble']):
            if not math.isnan(request['inmueble']):
                numero_expediente = int((request['inmueble']))
            else:
                numero_expediente = 0
            anio = int((request['anio']))
            periodoId = int((request['periodo']))
            if periodoId==4:
                periodoId=1
                anio=anio+1
            else:
                periodoId=periodoId+1
            try:
                periodo=IC_Periodo.objects.get(periodo=periodoId,aplica='C')
                inmueble=Inmueble.objects.get(numero_expediente=numero_expediente)
                ##print('anio',anio,'periodo',periodo)
                inmueble.anio=anio
                inmueble.periodo=periodo
                inmueble.save()
                #response_data = {
                #    'id': numero_expediente
                #}

                ## Devolver la respuesta como JSON
                #return JsonResponse(response_data)
            except Inmueble.DoesNotExist:
                return Response('Insert NOT Ok, No existe el numero de expediente', status=status.HTTP_400_BAD_REQUEST)
            except IC_Periodo.DoesNotExist:
                return Response('Insert NOT Ok, No existe el Periodo', status=status.HTTP_400_BAD_REQUEST)
            except IntegrityError as e:
                return Response('Insert NOT Ok,Error de integridad', status=status.HTTP_400_BAD_REQUEST)
        return Response('Insert OK', status=status.HTTP_200_OK)



def Certifica_Ficha(ficha):
    if ficha:
        try:
            correlativo = Correlativo.objects.get()
            logo_path1 = correlativo.Logo1.url  # URL de la primera imagen

            inmueble = Inmueble.objects.get(numero_expediente=ficha) 
            dataDocumentoPropiedad = InmueblePropiedad.objects.get(inmueble=inmueble) 
            propietarios = InmueblePropietarios.objects.filter(inmueble=inmueble) 
            dataFinesFiscales = InmuebleFaltante.objects.get(inmueble=inmueble) 
            ##print('logo_path1',logo_path1)

            numero_expediente = inmueble.numero_expediente
            sector = inmueble.sector
            urbanizacion = inmueble.urbanizacion
            tipo = inmueble.tipo

            html_content = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Certificación de Cédula Catastral</title>
                    <style>
                        .container {{
                            border: 1px solid #000;
                            padding: 10px;
                            width: 800px; /* Ajusta el ancho según tus necesidades */
                            margin: 0 auto; /* Centra el contenido */
                        }}
                        .column {{
                            float: left;
                            width: 50%;
                        }}
                        .clear {{
                            clear: both;
                        }}
                        table {{
                            width: 100%;
                            border-collapse: collapse;
                        }}
                        th, td {{
                            border: 1px solid #000;
                            padding: 8px;
                            text-align: center;
                        }}
                        .certification-image {{
                            max-width: 100%; /* Ajusta el tamaño máximo de la imagen al 100% del contenedor */
                            height: auto; /* Ajusta la altura automáticamente para mantener la proporción */
                            display: block; /* Evita el espacio adicional debajo de la imagen */
                            margin: 10px auto; /* Centra la imagen horizontalmente */
                        }}
                    </style> 
                </head>
                    <body style="font-size: 14px; font-family: Arial, sans-serif;">
                    <div class="container">

                        <div style="display: flex; align-items: center; justify-content: space-between;">
                            <img src="{logo_path1}" alt="Logo 1" style="max-width: 30%;">
                            <h2 style="text-align: center;">Certificación de {dataDocumentoPropiedad.tipo_documento.descripcion}</h2>
                            <div>
                             <p style="max-width: 30%;"><b>Expediente Nro.:</b> <h1>{numero_expediente} </h1></p>
                             </div>
                        </div>
            """

            if propietarios:
                html_content += """
                <div class="column">
                    <p><b>Propietario(s) :</b></p>
                    </div>
                    <table>
                        <tr>
                            <th>Número de Documento</th>
                            <th>Nombre</th>
                        </tr>
                """
                for propietario in propietarios:
                    html_content += f"""
                        <tr>
                            <td>{propietario.propietario.numero_documento}</td>
                            <td>{propietario.propietario.nombre}</td>
                        </tr>
                    """
                html_content += "</table>"
            else:
                html_content += "<p>No se encontraron propietarios para este inmueble.</p>"

            html_content += f"""
                        <p><b>Sector       :</b> {sector.codigo if sector else "Sin información de sector"}</p>
                        <p><b>Urbanización :</b> {urbanizacion.nombre if urbanizacion else "Sin información de urbanización"}</p>
                        <p><b>Tipo Inmueble:</b> {tipo.descripcion if tipo else "Sin información de Tipo Inmueble"}</p>
                """
            

            if dataDocumentoPropiedad.numero_documento and dataDocumentoPropiedad.numero_documento != 'null':
                html_content += """
                    <p><b>1.- Datos del documento.</b></p>
                    <table>
                        <tr>
                            <th>Fecha.Doc.</th>
                            <th>Nro. Doc.</th>
                            <th>Nro. Matrícula</th>
                            <th>Año libro real</th>
                            <th>M2 Terreno</th>
                            <th>Valor Terreno</th>
                            <th>M2 Construcción</th>
                            <th>Valor Construcción</th>
                        </tr>
                        """
                html_content += f"""
                        <tr>
                            <td> {dataDocumentoPropiedad.fecha_documento if dataDocumentoPropiedad.fecha_documento else '&nbsp;'}</td>
                            <td> {dataDocumentoPropiedad.numero_documento if dataDocumentoPropiedad.numero_documento else '&nbsp;'}</td>
                            <td> {dataDocumentoPropiedad.matricula_documento if dataDocumentoPropiedad.matricula_documento else '&nbsp;'}</td>
                            <td> {dataDocumentoPropiedad.anio_folio_documento if dataDocumentoPropiedad.anio_folio_documento else '&nbsp;'}</td>
                            <td> {'{:.2f}'.format(dataDocumentoPropiedad.area_terreno) if dataDocumentoPropiedad.area_terreno else '&nbsp;'}</td>
                            <td> {dataDocumentoPropiedad.valor_terreno if dataDocumentoPropiedad.valor_terreno else '&nbsp;'}</td>
                            <td> {'{:.2f}'.format(dataDocumentoPropiedad.area_construccion) if dataDocumentoPropiedad.area_construccion else '&nbsp;'}</td>
                            <td> {dataDocumentoPropiedad.valor_construccion   if dataDocumentoPropiedad.valor_construccion else '&nbsp;'}</td>
                        </tr>
                """
                html_content += "</table>"
            if dataDocumentoPropiedad.numero_terreno and dataDocumentoPropiedad.numero_terreno != 'null':
                html_content += """
                    <p><b>1.1.- Datos de Terreno según documento.</b></p>
                    <table>
                        <tr>
                            <th>Fecha</th>
                            <th>Nro. Doc.</th>
                            <th>Folios</th>
                            <th>Prot.</th>
                            <th>Tomo</th>
                            <th>Sup. M2</th>
                            <th>Valor Bs. Total</th>
                        </tr>
                        """
                html_content += f"""
                        <tr>
                            <td> {dataDocumentoPropiedad.fecha_terreno if dataDocumentoPropiedad.fecha_terreno else '&nbsp;'}</td>
                            <td> {dataDocumentoPropiedad.numero_terreno if dataDocumentoPropiedad.numero_terreno else '&nbsp;'}</td>
                            <td> {dataDocumentoPropiedad.folio_terreno if dataDocumentoPropiedad.folio_terreno else '&nbsp;'}</td>
                            <td> {dataDocumentoPropiedad.protocolo_terreno if dataDocumentoPropiedad.protocolo_terreno else '&nbsp;'}</td>
                            <td> {dataDocumentoPropiedad.tomo_terreno if dataDocumentoPropiedad.tomo_terreno else '&nbsp;'}</td>
                            <td> {'{:.2f}'.format(dataDocumentoPropiedad.area_terreno) if dataDocumentoPropiedad.area_terreno else '&nbsp;'}</td>
                            <td> {dataDocumentoPropiedad.valor_terreno   if dataDocumentoPropiedad.valor_terreno else '&nbsp;'}</td>
                        </tr>
                """
                html_content += "</table>"
            if dataDocumentoPropiedad.numero_construccion and dataDocumentoPropiedad.numero_construccion != 'null':
                html_content += """
                    <p><b>1.2.- Datos de Contrucción según documento.</b></p>
                    <table>
                        <tr>
                            <th>Fecha</th>
                            <th>Nro. Doc.</th>
                            <th>Folios</th>
                            <th>Prot.</th>
                            <th>Tomo</th>
                            <th>Sup. M2</th>
                            <th>Valor Bs. Total</th>
                        </tr>
                        """
                html_content += f"""
                        <tr>
                            <td> {dataDocumentoPropiedad.fecha_construccion if dataDocumentoPropiedad.fecha_construccion else '&nbsp;'}</td>
                            <td> {dataDocumentoPropiedad.numero_construccion if dataDocumentoPropiedad.numero_construccion else '&nbsp;'}</td>
                            <td> {dataDocumentoPropiedad.folio_construccion if dataDocumentoPropiedad.folio_construccion else '&nbsp;'}</td>
                            <td> {dataDocumentoPropiedad.protocolo_construccion if dataDocumentoPropiedad.protocolo_construccion else '&nbsp;'}</td>
                            <td> {dataDocumentoPropiedad.tomo_construccion if dataDocumentoPropiedad.tomo_construccion else '&nbsp;'}</td>
                            <td> {'{:.2f}'.format(dataDocumentoPropiedad.area_construccion) if dataDocumentoPropiedad.area_construccion else '&nbsp;'}</td>
                            <td> {dataDocumentoPropiedad.valor_construccion   if dataDocumentoPropiedad.valor_construccion else '&nbsp;'}</td>
                        </tr>
                """
                html_content += "</table>"



            html_content += """
                    <p><b>2. Metrajes según Inspección.</b></p>
                    <table>
                        <tr>
                            <th>2.1 Superficie de construcción M2</th>
                            <th>2.1 Superficie de terreno M2</th>
                        </tr>
                        """
            html_content += f"""
                        <tr>
                            <td> {dataFinesFiscales.cedula if dataFinesFiscales.cedula else '&nbsp;'}</td>
                            <td> {dataFinesFiscales.documentopropiedad  if dataFinesFiscales.documentopropiedad  else '&nbsp;'}</td>
                        </tr>
                """
            html_content += "</table>"
            html_content += f"""
                        <p><b>Dirección  :</b> {inmueble.direccion if inmueble.direccion  else "Sin información de Dirección"}</p> 
                        <p><b>Referencia :</b> {inmueble.referencia if inmueble.referencia  else "Sin información de Referencia"}</p>
                        <p><b>Observación:</b> {inmueble.observaciones if inmueble.observaciones else "Sin información de Observación"}</p>
                """

            html_content += f"""
                    </div>
                </body>
                </html>
                """

            return HttpResponse(html_content, content_type="text/html; charset=utf-8")

        except Inmueble.DoesNotExist:
            return Response('Insert NOT Ok, No existe el numero de expediente', status=status.HTTP_400_BAD_REQUEST)
        except IntegrityError as e:
            return Response('Insert NOT Ok,Error de integridad', status=status.HTTP_400_BAD_REQUEST)

    return Response('Insert OK', status=status.HTTP_200_OK)



#****************************************************************************************************
#ORDENANZA 2024
#**************************************************************************************************** 
def Impuesto_Inmueble(request):
    if (request):
        anioini=0
        mesini=0
        data = []
        aDetalle = []
        aDescuento = []
        aInteres = []
        if (request['inmueble']):
            not_process=False
            try:
                oInmueble = Inmueble.objects.get(id=request['inmueble'], status__inmueble_activo=True)
            except Inmueble.DoesNotExist:
                 not_process=True
            if not_process:
                return Response('Inmueble no esta en USO', status=status.HTTP_400_BAD_REQUEST)
            else:
                ## esto contruye la tabla de periodos por inmueble para mantener el historico
                # esto permite saber si esta pendientes por cancelar
                ############## inicio
                today = date.today()
                #Zona = Urbanizacion.objects.get(id=oInmueble.urbanizacion.id)
                Categorizacion = oInmueble
                oPeriodo = IC_Periodo.objects.filter(aplica='C')
                ano_fin=request['anio']  #today.year
                ##print('oInmueble.anio:',oInmueble.anio)
                if oInmueble.anio is None: # si al momento de importar de excel  no tiene pagos, le coloco el año de la fecha de inscripcion
                    oInmueble.anio=oInmueble.fecha_inscripcion.year
                    oInmueble.periodo=IC_Periodo.objects.get(aplica='C',periodo=1)
                    oInmueble.save()
                    dAnio=oInmueble.anio
                    dPeriodo=oInmueble.periodo.periodo 
                    ##print('creadooo')
                dAnio=oInmueble.anio        # Año qe inicio la deuda
                dPeriodo=oInmueble.periodo.periodo  # Periodo que inicia la deuda
                if dAnio<2024:
                    dAnio=2024
                    dPeriodo=1 

                anioini=dAnio
                mesini=dPeriodo
                primero=True
                ##print('kkkkkkkkkkkkkkkkkkkkkk',dPeriodo) 

                IC_ImpuestoPeriodo.objects.filter(inmueble=oInmueble).delete()  # elimina el historial de periodos pendientes
                                                        #por que este dato lo puede cambiar hacienda con acceso.borrar=true
                while dAnio<=ano_fin: # crea la cxc de periodos pendientes
                    if primero:
                        oPeriodo = IC_Periodo.objects.filter(aplica='C',periodo__gte=dPeriodo)
                        primero=False
                    else:
                        oPeriodo = IC_Periodo.objects.filter(aplica='C')
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
                    oBaseCalculo = TasaBCV.objects.get(habilitado=True)
                    baseCalculoBs= float(oBaseCalculo.monto)
                    #Crear lista con los años presentes en la cxc
                    oAnio = IC_ImpuestoPeriodo.objects.filter(inmueble=request['inmueble']).values('anio').distinct().order_by('anio')
                    maximo_ano = oAnio.aggregate(Max('anio'))['anio__max']
                    minimo_ano = oAnio.aggregate(Min('anio'))['anio__min']
                    
                    # Contar la cantidad de periodos configurados para C atastro
                    tPeriodo= IC_Periodo.objects.filter(aplica='C')
                    CountPeriodo= tPeriodo.count()
                    terreno =      InmuebleValoracionTerreno2024.objects.get(inmueble=request['inmueble'])
                    construccion = InmuebleValoracionConstruccion2024.objects.filter(inmueblevaloracionterreno=terreno)
                    if terreno:
                        total_area_terreno = terreno.area 
                    else:
                        total_area_terreno = 0

                    if construccion:
                        total_area_construccion = construccion.aggregate(Sum('area'))['area__sum']
                    else:
                        total_area_construccion = 0

                    if (total_area_construccion > total_area_terreno) or (total_area_terreno==0 and total_area_construccion>0):
                        ocupacion=construccion
                    elif total_area_terreno>0 and total_area_construccion==0:
                        ocupacion =  InmuebleValoracionTerreno2024.objects.filter(inmueble=request['inmueble'])
                        ocupacion = list(ocupacion) 
                    else:
                        ocupacion=construccion
                        if terreno: # hay inmuebles que NO TIENEN TERRENO, PARA ESE CASO NO ENTRA, SOLO TOMA LA CONTRUCCION
                            if total_area_construccion < total_area_terreno:
                                # Crear una nueva instancia de InmuebleValoracionConstruccion sin guardar en la base de datos
                                
                                nuevo_objeto_construccion = InmuebleValoracionConstruccion2024(
                                    tipologia_categorizacion=terreno.tipologia_categorizacion,
                                    tipo=terreno.tipo,
                                    area=terreno.area-total_area_construccion,
                                    aplica=terreno.aplica,
                                    inmueblevaloracionterreno=terreno  # Asignar la relación con el objeto terreno
                                )
                                # Agregar el nuevo objeto a la variable "ocupacion"
                                ocupacion = list(ocupacion)  # Convertir "ocupacion" en una lista
                                ocupacion.append(nuevo_objeto_construccion)  # Agregar el nuevo objeto a la lista
                            # En este punto, "ocupacion" contiene todos los objetos, incluido el nuevo objeto si se cumple la condición
                    ##print('ocupacion',ocupacion)
                    CategorizacionInmueble=Categorizacion.categorizacion
                    oTipologia=Tipologia_Categorizacion.objects.filter(categorizacion=CategorizacionInmueble)

                    #Ubicar la fecha de compra
                    #oPropietario = InmueblePropietarios.objects.get(propietario=request['propietario'],inmueble=request['inmueble'])
                    #fechaCompra=oPropietario.fecha_compra
                    #diferencia=today-fechaCompra 
                    ###print(fechaCompra,today,diferencia.days)
                    # valida si aplica descuentos por pronto pago.
                    oDescuento=0 # Bandera que valida si aplica descuento o no
                    try:
                        oDescuento=IC_ImpuestoDescuento.objects.filter(habilitado=True,aplica='C')
                    except:
                        oDescuento=0
                    bMulta=True
                    oCargos=IC_ImpuestoCargos.objects.filter(habilitado=True,aplica='C')
                    fMulta=float(oCargos.get(codigo='multa').porcentaje)
                    fRecargo=float(oCargos.get(codigo='recargo').porcentaje)
                    tBaseMultaRecargoInteres=0
                    tTotalInteresMoratorio=0
                    tMulta=0
                    tRecargo=0
                    tInteres=0
                    tTotal=0
                    tTotalMora=0
                    tDescuento=0
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
                                today <= fDiasGracia.fechadesde+timedelta(days=fDiasGracia.dias_gracia) :
                                    # La fecha actual está entre las fechas del modelo
                                    ##print("La fecha actual está entre fecha_desde y fecha_hasta.",fDiasGracia)
                                    bMulta=False
                                else:
                                    if today<= fDiasGracia.fechadesde and  \
                                        today <= fDiasGracia.fechadesde+timedelta(days=fDiasGracia.dias_gracia) :
                                        # La fecha actual es menor a las fechas del modelo (periodos proximos)
                                        ##print("La fecha actual es menor a las fechas del modelo (periodos proximos).",fDiasGracia)
                                        bMulta=False

                                    # La fecha actual NO está entre las fechas del modelo
                                    ##print("La fecha actual NO está entre fecha_desde y fecha_hasta.")
                            for dato in ocupacion:

                                Alicuota=float(oTipologia.get(id=dato.tipologia_categorizacion.id).tarifa)
                                Monto=float(dato.area)*(Alicuota*iAlicuota)*baseCalculoBs
                                mDescuento=0
                                ppDescuento=0
                                if oDescuento: # and minimo_ano==today.year:
                                    # Valida que aplique descuento solamente con el año actual  !! inactivo. aplica descuento segun la tabla
                                    # Aplica descuentos generales
                                    aPeriodoMesDesde=aPeriodo.periodo.fechadesde.month
                                    aPeriodoMesHasta=aPeriodo.periodo.fechahasta.month
                                    aPeriodoDiaDesde=aPeriodo.periodo.fechadesde.day
                                    aPeriodoDiaHasta=aPeriodo.periodo.fechahasta.day
                                    try:
                                        pDescuento=oDescuento.filter(Q(tipologia_categorizacion__isnull=True) | Q(tipologia_categorizacion=dato.tipologia_categorizacion.id,) | Q(inmueble__isnull=True) | Q(inmueble=oInmueble.id,),prontopago=False)
                                        ##print('descuento',pDescuento)
                                        ##print('registros',aPeriodo.periodo.fechadesde,aPeriodo.periodo.fechahasta) 
                                        registros_validos = pDescuento.filter(
                                            fechadesde__year__lte=minimo_ano,
                                            fechahasta__year__gte=minimo_ano,
                                            fechadesde__month__lte=aPeriodoMesDesde,
                                            fechahasta__month__gte=aPeriodoMesHasta,
                                            fechadesde__day__lte=aPeriodoDiaDesde,
                                            fechahasta__day__gte=aPeriodoDiaHasta) 
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
                                            'IC_impuestoperiodo':aPeriodo.periodo.id,
                                            'uso_id':dato.tipologia_categorizacion.id,
                                            'uso_descripcion':dato.tipologia_categorizacion.descripcion,
                                            'apica':dato.aplica,
                                            'anio': minimo_ano,
                                            'periodo': aPeriodo.periodo.periodo,
                                        }
                                        aDescuento.append(ImpuestoDetalleDescuentos)

                                    # Aplica descuentos prontopago
                                    try:
                                        pDescuento=oDescuento.filter(Q(tipologia_categorizacion__isnull=True) | Q(tipologia_categorizacion=dato.tipologia_categorizacion.id,) | Q(inmueble__isnull=True) | Q(inmueble=oInmueble.id,),prontopago=True)
                                        ##print('descuento Pronto Pago',pDescuento)
                                        ##print('fecha actual',today.year,today.month,today.day) 
                                        ##print('fecha periodo',minimo_ano,aPeriodoMesDesde,aPeriodoDiaDesde,minimo_ano,aPeriodoMesHasta,aPeriodoDiaHasta) 
                                        registros_validos = pDescuento.filter(
                                            #fechadesde__year__lte=today.year,   # < =
                                            #fechahasta__year__gte=today.year,   # > =
                                            fechadesde__year=minimo_ano,
                                            fechadesde__month__lte=today.month, # < =
                                            fechahasta__month__gte=today.month, # > =
                                            fechadesde__day__lte=today.day,     # < =
                                            fechahasta__day__gte=today.day)     # > =
                                        ##print('registros_validos pronto pago 1',registros_validos)
                                        registros_validos2 = registros_validos.filter(
                                            fechadesde__year__lte=minimo_ano,       # < =
                                            fechahasta__year__gte=minimo_ano,       # > =
                                            fechadesde__month__lte=aPeriodoMesDesde,# < =
                                            fechahasta__month__gte=aPeriodoMesDesde,# > =
                                            fechadesde__day__lte=aPeriodoDiaDesde,  # < =
                                            fechahasta__day__gte=aPeriodoDiaDesde)  # > =
                                        ##print('registros_validos pronto pago 2',registros_validos2)
                                        ppDescuento=float(registros_validos.aggregate(Sum('porcentaje'))['porcentaje__sum'])
                                    except:
                                        ppDescuento=0
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
                                            'IC_impuestoperiodo':aPeriodo.periodo.id,
                                            'uso_id':dato.tipologia_categorizacion.id,
                                            'uso_descripcion':dato.tipologia_categorizacion.descripcion,
                                            'apica':dato.aplica,
                                            'anio': minimo_ano,
                                            'periodo': aPeriodo.periodo.periodo,
                                        }
                                        aDescuento.append(ImpuestoDetalleDescuentos)


                                Total=float(Monto-(Monto*((mDescuento+ppDescuento)/100)))

                                ImpuestoDetalle = {
                                    'IC_impuestoperiodo':aPeriodo.periodo.id,
                                    'anio': minimo_ano,
                                    'periodo': aPeriodo.periodo.periodo,
                                    'multa':bMulta,
                                    'uso_id':dato.tipologia_categorizacion.id,
                                    'uso_descripcion':dato.tipologia_categorizacion.descripcion,
                                    'apica':dato.aplica,
                                    'tipo':dato.tipo.id,
                                    'tipo_descripcion':dato.tipo.descripcion,
                                    'area_m2':dato.area,
                                    'factor':iAlicuota,
                                    'alicuota_full':Alicuota,
                                    'alicuota':Alicuota*iAlicuota,
                                    'basecalculobs':baseCalculoBs, 
                                    'sub_total':Monto,
                                    'mdescuento':mDescuento+ppDescuento,
                                    'total':Total,
                                }
                                tTotalInteresMoratorio=tTotalInteresMoratorio+Total
                                tDescuento=tDescuento+mDescuento+ppDescuento
                                aDetalle.append(ImpuestoDetalle)
                                tTotal=tTotal+Total
                                if bMulta:
                                    tTotalMora=tTotalMora+Total
                                    tBaseMultaRecargoInteres=tBaseMultaRecargoInteres+Total
                                    tMulta=tMulta+(Total*(fMulta/100))
                                    tRecargo=tRecargo+(Total*(fRecargo/100))
                        if tTotalMora:                   
                            oTasaInteres=TasaInteres.objects.filter(anio=minimo_ano).order_by('mes')
                            # se cambia tTotalMora por ttotal--Arturo 2-4-2024
                            if minimo_ano==today.year:
                                tTotalInteresMoratorio=tTotalInteresMoratorio/request['periodo']
                                tTotalInteresMoratorio=tTotalInteresMoratorio*4
                            tTotalMora4=(tTotalInteresMoratorio/1)
                            tTotalMora3=(tTotalInteresMoratorio/4)*3
                            tTotalMora2=(tTotalInteresMoratorio/2)
                            tTotalMora1=(tTotalInteresMoratorio/4)
                            incremento=1.200000000
                            incremento_decimal = Decimal(str(incremento))
                            for aTasa in oTasaInteres:
                                if (aTasa.mes<=today.month and minimo_ano==today.year) or minimo_ano!=today.year:
                                    if (aTasa.mes==today.month and minimo_ano==today.year):
                                        cantidad_dias = today.day
                                    else:
                                        cantidad_dias = obtener_cantidad_dias(aTasa.anio, aTasa.mes) 
                                    tasa_porcentaje=float((aTasa.tasa*incremento_decimal)/100)
                                    if  aTasa.mes==1: 
                                        monto=0
                                        por_mes=0
                                    if  aTasa.mes==2:
                                        monto=0
                                        por_mes=0
                                    if  aTasa.mes==3:
                                        monto=0
                                        por_mes=0
                                    if  aTasa.mes==4:
                                        monto=((tTotalMora1*tasa_porcentaje)/360)*cantidad_dias 
                                        por_mes=tTotalMora1
                                    if  aTasa.mes==5:
                                        monto=((tTotalMora2*tasa_porcentaje)/360)*cantidad_dias
                                        por_mes=tTotalMora2
                                    if  aTasa.mes==6:
                                        monto=((tTotalMora2*tasa_porcentaje)/360)*cantidad_dias
                                        por_mes=tTotalMora2
                                    if  aTasa.mes==7:
                                        monto=((tTotalMora2*tasa_porcentaje)/360)*cantidad_dias
                                        por_mes=tTotalMora2
                                    if  aTasa.mes==8:
                                        monto=((tTotalMora3*tasa_porcentaje)/360)*cantidad_dias
                                        por_mes=tTotalMora3
                                    if  aTasa.mes==9:
                                        monto=((tTotalMora3*tasa_porcentaje)/360)*cantidad_dias
                                        por_mes=tTotalMora3
                                    if  aTasa.mes==10:
                                        monto=((tTotalMora3*tasa_porcentaje)/360)*cantidad_dias
                                        por_mes=tTotalMora3
                                    if  aTasa.mes==11:
                                        monto=((tTotalMora4*tasa_porcentaje)/360)*cantidad_dias
                                        por_mes=tTotalMora4
                                    if  aTasa.mes==12:
                                        monto=((tTotalMora4*tasa_porcentaje)/360)*cantidad_dias
                                        por_mes=tTotalMora4
                                    ImpuestoInteresMoratorio={
                                            'anio':aTasa.anio,
                                            'mes':aTasa.mes,
                                            'tasa':tasa_porcentaje*100,
                                            'dias':cantidad_dias,
                                            'moramensual':por_mes,
                                            'interesmensual':monto,
                                        }
                                    aInteres.append(ImpuestoInteresMoratorio)
                                    tInteres=tInteres+monto
                                #end If
                            # end For oTasaInteres 
                            tTotalMora=0
                        tTotalInteresMoratorio=0
                        minimo_ano=minimo_ano+1
                    #EndWhile
                    correlativo=Correlativo.objects.get(id=1)
                    numero=correlativo.NumeroIC_Impuesto

                    Impuesto={
                        'numero':numero,
                        'zona':CategorizacionInmueble.codigo,
                        'basecalculobs':baseCalculoBs,
                        'inmueble':oInmueble.id,
                        'subtotal':tTotal,
                        'multa':tMulta,
                        'recargo':tRecargo,
                        'interes':tInteres,
                        'fmulta':fMulta,
                        'frecargo':fRecargo,
                        'descuento':tDescuento,
                        'total':tTotal+tMulta+tRecargo+tInteres,
                        'BaseMultaRecargoInteres':tBaseMultaRecargoInteres,
                        'flujo':Flujo.objects.filter(inmueble=oInmueble,estado='1').count() ,
                        'anioini':anioini,
                        'mesini':mesini,
                        'aniofin':request['anio'],
                        'mesfin':request['periodo'],
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

def Impuesto_Inmueble_Public(request):
    if (request):
        anioini=0
        mesini=0
        data = []
        aDetalle = []
        aDescuento = []
        aInteres = []
        if (request['inmueble']):
            not_process=False
            try:
                oInmueble = Inmueble.objects.get(numero_expediente=request['inmueble'], status__inmueble_activo=True)
            except Inmueble.DoesNotExist:
                 not_process=True
            if not_process:
                return Response('Inmueble no esta en USO', status=status.HTTP_400_BAD_REQUEST)
            else:
                ## esto contruye la tabla de periodos por inmueble para mantener el historico
                # esto permite saber si esta pendientes por cancelar
                ############## inicio
                today = date.today()
                #Zona = Urbanizacion.objects.get(id=oInmueble.urbanizacion.id)
                Categorizacion = oInmueble
                oPeriodo = IC_Periodo.objects.filter(aplica='C')
                ano_fin=request['anio']  #today.year
                ##print('oInmueble.anio:',oInmueble.anio)
                if oInmueble.anio is None: # si al momento de importar de excel  no tiene pagos, le coloco el año de la fecha de inscripcion
                    oInmueble.anio=oInmueble.fecha_inscripcion.year
                    oInmueble.periodo=IC_Periodo.objects.get(aplica='C',periodo=1)
                    oInmueble.save()
                    dAnio=oInmueble.anio
                    dPeriodo=oInmueble.periodo.periodo 
                    ##print('creadooo')
                dAnio=oInmueble.anio        # Año qe inicio la deuda
                dPeriodo=oInmueble.periodo.periodo  # Periodo que inicia la deuda
                if dAnio<2024:
                    dAnio=2024
                    dPeriodo=1 

                anioini=dAnio
                mesini=dPeriodo
                primero=True
                ##print('kkkkkkkkkkkkkkkkkkkkkk',dPeriodo) 

                IC_ImpuestoPeriodo.objects.filter(inmueble=oInmueble).delete()  # elimina el historial de periodos pendientes
                                                        #por que este dato lo puede cambiar hacienda con acceso.borrar=true
                while dAnio<=ano_fin: # crea la cxc de periodos pendientes
                    if primero:
                        oPeriodo = IC_Periodo.objects.filter(aplica='C',periodo__gte=dPeriodo)
                        primero=False
                    else:
                        oPeriodo = IC_Periodo.objects.filter(aplica='C')
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
                oImpuestoPeriodo = IC_ImpuestoPeriodo.objects.filter(inmueble__numero_expediente=request['inmueble']).order_by('anio', 'periodo')
                if oImpuestoPeriodo:
                    oBaseCalculo = TasaBCV.objects.get(habilitado=True)
                    baseCalculoBs= float(oBaseCalculo.monto)
                    #Crear lista con los años presentes en la cxc
                    oAnio = IC_ImpuestoPeriodo.objects.filter(inmueble__numero_expediente=request['inmueble']).values('anio').distinct().order_by('anio')
                    maximo_ano = oAnio.aggregate(Max('anio'))['anio__max']
                    minimo_ano = oAnio.aggregate(Min('anio'))['anio__min']
                    
                    # Contar la cantidad de periodos configurados para C atastro
                    tPeriodo= IC_Periodo.objects.filter(aplica='C')
                    CountPeriodo= tPeriodo.count()
                    terreno =      InmuebleValoracionTerreno2024.objects.get(inmueble__numero_expediente=request['inmueble'])
                    construccion = InmuebleValoracionConstruccion2024.objects.filter(inmueblevaloracionterreno=terreno)
                    if terreno:
                        total_area_terreno = terreno.area 
                    else:
                        total_area_terreno = 0

                    if construccion:
                        total_area_construccion = construccion.aggregate(Sum('area'))['area__sum']
                    else:
                        total_area_construccion = 0

                    if (total_area_construccion > total_area_terreno) or (total_area_terreno==0 and total_area_construccion>0):
                        ocupacion=construccion
                    elif total_area_terreno>0 and total_area_construccion==0:
                        ocupacion =  InmuebleValoracionTerreno2024.objects.filter(inmueble__numero_expediente=request['inmueble'])
                        ocupacion = list(ocupacion) 
                    else:
                        ocupacion=construccion
                        if terreno: # hay inmuebles que NO TIENEN TERRENO, PARA ESE CASO NO ENTRA, SOLO TOMA LA CONTRUCCION
                            if total_area_construccion < total_area_terreno:
                                # Crear una nueva instancia de InmuebleValoracionConstruccion sin guardar en la base de datos
                                
                                nuevo_objeto_construccion = InmuebleValoracionConstruccion2024(
                                    tipologia_categorizacion=terreno.tipologia_categorizacion,
                                    tipo=terreno.tipo,
                                    area=terreno.area-total_area_construccion,
                                    aplica=terreno.aplica,
                                    inmueblevaloracionterreno=terreno  # Asignar la relación con el objeto terreno
                                )
                                # Agregar el nuevo objeto a la variable "ocupacion"
                                ocupacion = list(ocupacion)  # Convertir "ocupacion" en una lista
                                ocupacion.append(nuevo_objeto_construccion)  # Agregar el nuevo objeto a la lista
                            # En este punto, "ocupacion" contiene todos los objetos, incluido el nuevo objeto si se cumple la condición
                    ##print('ocupacion',ocupacion)
                    CategorizacionInmueble=Categorizacion.categorizacion
                    oTipologia=Tipologia_Categorizacion.objects.filter(categorizacion=CategorizacionInmueble)

                    #Ubicar la fecha de compra
                    #oPropietario = InmueblePropietarios.objects.get(propietario=request['propietario'],inmueble=request['inmueble'])
                    #fechaCompra=oPropietario.fecha_compra
                    #diferencia=today-fechaCompra 
                    ###print(fechaCompra,today,diferencia.days)
                    # valida si aplica descuentos por pronto pago.
                    oDescuento=0 # Bandera que valida si aplica descuento o no
                    try:
                        oDescuento=IC_ImpuestoDescuento.objects.filter(habilitado=True,aplica='C')
                    except:
                        oDescuento=0
                    bMulta=True
                    oCargos=IC_ImpuestoCargos.objects.filter(habilitado=True,aplica='C')
                    fMulta=float(oCargos.get(codigo='multa').porcentaje)
                    fRecargo=float(oCargos.get(codigo='recargo').porcentaje)
                    tBaseMultaRecargoInteres=0
                    tTotalInteresMoratorio=0
                    tMulta=0
                    tRecargo=0
                    tInteres=0
                    tTotal=0
                    tTotalMora=0
                    tDescuento=0
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
                                today <= fDiasGracia.fechadesde+timedelta(days=fDiasGracia.dias_gracia) :
                                    # La fecha actual está entre las fechas del modelo
                                    ##print("La fecha actual está entre fecha_desde y fecha_hasta.",fDiasGracia)
                                    bMulta=False
                                else:
                                    if today<= fDiasGracia.fechadesde and  \
                                        today <= fDiasGracia.fechadesde+timedelta(days=fDiasGracia.dias_gracia) :
                                        # La fecha actual es menor a las fechas del modelo (periodos proximos)
                                        ##print("La fecha actual es menor a las fechas del modelo (periodos proximos).",fDiasGracia)
                                        bMulta=False

                                    # La fecha actual NO está entre las fechas del modelo
                                    ##print("La fecha actual NO está entre fecha_desde y fecha_hasta.")
                            for dato in ocupacion:

                                Alicuota=float(oTipologia.get(id=dato.tipologia_categorizacion.id).tarifa)
                                Monto=float(dato.area)*(Alicuota*iAlicuota)*baseCalculoBs
                                mDescuento=0
                                ppDescuento=0
                                if oDescuento: # and minimo_ano==today.year:
                                    # Valida que aplique descuento solamente con el año actual  !! inactivo. aplica descuento segun la tabla
                                    # Aplica descuentos generales
                                    aPeriodoMesDesde=aPeriodo.periodo.fechadesde.month
                                    aPeriodoMesHasta=aPeriodo.periodo.fechahasta.month
                                    aPeriodoDiaDesde=aPeriodo.periodo.fechadesde.day
                                    aPeriodoDiaHasta=aPeriodo.periodo.fechahasta.day
                                    try:
                                        pDescuento=oDescuento.filter(Q(tipologia_categorizacion__isnull=True) | Q(tipologia_categorizacion=dato.tipologia_categorizacion.id,) | Q(inmueble__isnull=True) | Q(inmueble=oInmueble.id,),prontopago=False)
                                        ##print('descuento',pDescuento)
                                        ##print('registros',aPeriodo.periodo.fechadesde,aPeriodo.periodo.fechahasta) 
                                        registros_validos = pDescuento.filter(
                                            fechadesde__year__lte=minimo_ano,
                                            fechahasta__year__gte=minimo_ano,
                                            fechadesde__month__lte=aPeriodoMesDesde,
                                            fechahasta__month__gte=aPeriodoMesHasta,
                                            fechadesde__day__lte=aPeriodoDiaDesde,
                                            fechahasta__day__gte=aPeriodoDiaHasta) 
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
                                            'IC_impuestoperiodo':aPeriodo.periodo.id,
                                            'uso_id':dato.tipologia_categorizacion.id,
                                            'uso_descripcion':dato.tipologia_categorizacion.descripcion,
                                            'apica':dato.aplica,
                                            'anio': minimo_ano,
                                            'periodo': aPeriodo.periodo.periodo,
                                        }
                                        aDescuento.append(ImpuestoDetalleDescuentos)

                                    # Aplica descuentos prontopago
                                    try:
                                        pDescuento=oDescuento.filter(Q(tipologia_categorizacion__isnull=True) | Q(tipologia_categorizacion=dato.tipologia_categorizacion.id,) | Q(inmueble__isnull=True) | Q(inmueble=oInmueble.id,),prontopago=True)
                                        ##print('descuento Pronto Pago',pDescuento)
                                        ##print('fecha actual',today.year,today.month,today.day) 
                                        ##print('fecha periodo',minimo_ano,aPeriodoMesDesde,aPeriodoDiaDesde,minimo_ano,aPeriodoMesHasta,aPeriodoDiaHasta) 
                                        registros_validos = pDescuento.filter(
                                            #fechadesde__year__lte=today.year,   # < =
                                            #fechahasta__year__gte=today.year,   # > =
                                            fechadesde__year=minimo_ano,
                                            fechadesde__month__lte=today.month, # < =
                                            fechahasta__month__gte=today.month, # > =
                                            fechadesde__day__lte=today.day,     # < =
                                            fechahasta__day__gte=today.day)     # > =
                                        ##print('registros_validos pronto pago 1',registros_validos)
                                        registros_validos2 = registros_validos.filter(
                                            fechadesde__year__lte=minimo_ano,       # < =
                                            fechahasta__year__gte=minimo_ano,       # > =
                                            fechadesde__month__lte=aPeriodoMesDesde,# < =
                                            fechahasta__month__gte=aPeriodoMesDesde,# > =
                                            fechadesde__day__lte=aPeriodoDiaDesde,  # < =
                                            fechahasta__day__gte=aPeriodoDiaDesde)  # > =
                                        ##print('registros_validos pronto pago 2',registros_validos2)
                                        ppDescuento=float(registros_validos.aggregate(Sum('porcentaje'))['porcentaje__sum'])
                                    except:
                                        ppDescuento=0
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
                                            'IC_impuestoperiodo':aPeriodo.periodo.id,
                                            'uso_id':dato.tipologia_categorizacion.id,
                                            'uso_descripcion':dato.tipologia_categorizacion.descripcion,
                                            'apica':dato.aplica,
                                            'anio': minimo_ano,
                                            'periodo': aPeriodo.periodo.periodo,
                                        }
                                        aDescuento.append(ImpuestoDetalleDescuentos)


                                Total=float(Monto-(Monto*((mDescuento+ppDescuento)/100)))

                                ImpuestoDetalle = {
                                    'IC_impuestoperiodo':aPeriodo.periodo.id,
                                    'anio': minimo_ano,
                                    'periodo': aPeriodo.periodo.periodo,
                                    'multa':bMulta,
                                    'uso_id':dato.tipologia_categorizacion.id,
                                    'uso_descripcion':dato.tipologia_categorizacion.descripcion,
                                    'apica':dato.aplica,
                                    'tipo':dato.tipo.id,
                                    'tipo_descripcion':dato.tipo.descripcion,
                                    'area_m2':dato.area,
                                    'factor':iAlicuota,
                                    'alicuota_full':Alicuota,
                                    'alicuota':Alicuota*iAlicuota,
                                    'basecalculobs':baseCalculoBs, 
                                    'sub_total':Monto,
                                    'mdescuento':mDescuento+ppDescuento,
                                    'total':Total,
                                }
                                tTotalInteresMoratorio=tTotalInteresMoratorio+Total
                                tDescuento=tDescuento+mDescuento+ppDescuento
                                aDetalle.append(ImpuestoDetalle)
                                tTotal=tTotal+Total
                                if bMulta:
                                    tTotalMora=tTotalMora+Total
                                    tBaseMultaRecargoInteres=tBaseMultaRecargoInteres+Total
                                    tMulta=tMulta+(Total*(fMulta/100))
                                    tRecargo=tRecargo+(Total*(fRecargo/100))
                        if tTotalMora:                   
                            oTasaInteres=TasaInteres.objects.filter(anio=minimo_ano).order_by('mes') 
                            if minimo_ano==today.year:
                                tTotalInteresMoratorio=tTotalInteresMoratorio/request['periodo']
                                tTotalInteresMoratorio=tTotalInteresMoratorio*4
                            tTotalMora4=(tTotalInteresMoratorio/1)
                            tTotalMora3=(tTotalInteresMoratorio/4)*3
                            tTotalMora2=(tTotalInteresMoratorio/2)
                            tTotalMora1=(tTotalInteresMoratorio/4)
                            incremento=1.200000000
                            incremento_decimal = Decimal(str(incremento))
                            for aTasa in oTasaInteres:
                                if (aTasa.mes<=today.month and minimo_ano==today.year) or minimo_ano!=today.year:
                                    if (aTasa.mes==today.month and minimo_ano==today.year):
                                        cantidad_dias = today.day
                                    else:
                                        cantidad_dias = obtener_cantidad_dias(aTasa.anio, aTasa.mes) 
                                    tasa_porcentaje=float((aTasa.tasa*incremento_decimal)/100)
                                    if  aTasa.mes==1: 
                                        monto=0
                                        por_mes=0
                                    if  aTasa.mes==2:
                                        monto=0
                                        por_mes=0
                                    if  aTasa.mes==3:
                                        monto=0
                                        por_mes=0
                                    if  aTasa.mes==4:
                                        monto=((tTotalMora1*tasa_porcentaje)/360)*cantidad_dias 
                                        por_mes=tTotalMora1
                                    if  aTasa.mes==5:
                                        monto=((tTotalMora2*tasa_porcentaje)/360)*cantidad_dias
                                        por_mes=tTotalMora2
                                    if  aTasa.mes==6:
                                        monto=((tTotalMora2*tasa_porcentaje)/360)*cantidad_dias
                                        por_mes=tTotalMora2
                                    if  aTasa.mes==7:
                                        monto=((tTotalMora2*tasa_porcentaje)/360)*cantidad_dias
                                        por_mes=tTotalMora2
                                    if  aTasa.mes==8:
                                        monto=((tTotalMora3*tasa_porcentaje)/360)*cantidad_dias
                                        por_mes=tTotalMora3
                                    if  aTasa.mes==9:
                                        monto=((tTotalMora3*tasa_porcentaje)/360)*cantidad_dias
                                        por_mes=tTotalMora3
                                    if  aTasa.mes==10:
                                        monto=((tTotalMora3*tasa_porcentaje)/360)*cantidad_dias
                                        por_mes=tTotalMora3
                                    if  aTasa.mes==11:
                                        monto=((tTotalMora4*tasa_porcentaje)/360)*cantidad_dias
                                        por_mes=tTotalMora4
                                    if  aTasa.mes==12:
                                        monto=((tTotalMora4*tasa_porcentaje)/360)*cantidad_dias
                                        por_mes=tTotalMora4
                                    ImpuestoInteresMoratorio={
                                            'anio':aTasa.anio,
                                            'mes':aTasa.mes,
                                            'tasa':tasa_porcentaje*100,
                                            'dias':cantidad_dias,
                                            'moramensual':por_mes,
                                            'interesmensual':monto,
                                        }
                                    aInteres.append(ImpuestoInteresMoratorio)
                                    tInteres=tInteres+monto
                                #end If
                            # end For oTasaInteres 
                            tTotalMora=0
                        tTotalInteresMoratorio=0
                        minimo_ano=minimo_ano+1
                    #EndWhile
                    correlativo=Correlativo.objects.get(id=1)
                    numero=correlativo.NumeroIC_Impuesto

                    Impuesto={
                        'numero':numero,
                        'zona':CategorizacionInmueble.codigo,
                        'basecalculobs':baseCalculoBs,
                        'inmueble':oInmueble.id,
                        'subtotal':tTotal,
                        'multa':tMulta,
                        'recargo':tRecargo,
                        'interes':tInteres,
                        'fmulta':fMulta,
                        'frecargo':fRecargo,
                        'descuento':tDescuento,
                        'total':tTotal+tMulta+tRecargo+tInteres,
                        'BaseMultaRecargoInteres':tBaseMultaRecargoInteres,
                        'flujo':Flujo.objects.filter(inmueble=oInmueble,estado='1').count() ,
                        'anioini':anioini,
                        'mesini':mesini,
                        'aniofin':request['anio'],
                        'mesfin':request['periodo'],
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



def Impuesto_Inmueble_Public_old(request):
    if (request):
        anioini=0
        mesini=0
        data = []
        aDetalle = []
        aDescuento = []
        aInteres = []
        if (request['inmueble']):
            not_process=False
            try:
                oInmueble = Inmueble.objects.get(numero_expediente=request['inmueble'], status__inmueble_activo=True)
            except Inmueble.DoesNotExist:
                 not_process=True
            if not_process:
                return Response('Exoediente de Inmueble No existe o tiene estatus de inactivo', status=status.HTTP_400_BAD_REQUEST)
            else:
                ## esto contruye la tabla de periodos por inmueble para mantener el historico
                # esto permite saber si esta pendientes por cancelar
                ############## inicio
                today = date.today()
                #Zona = Urbanizacion.objects.get(id=oInmueble.urbanizacion.id)
                Zona = oInmueble
                oPeriodo = IC_Periodo.objects.filter(aplica='C')
                ano_fin=request['anio']  #today.year
                ##print('oInmueble.anio:',oInmueble.anio)
                if oInmueble.anio is None: # si al momento de importar de excel  no tiene pagos, le coloco el año de la fecha de inscripcion
                    oInmueble.anio=oInmueble.fecha_inscripcion.year
                    oInmueble.periodo=IC_Periodo.objects.get(aplica='C',periodo=1)
                    oInmueble.save()
                    dAnio=oInmueble.anio
                    dPeriodo=oInmueble.periodo.periodo 
                    ##print('creadooo')
                dAnio=oInmueble.anio        # Año qe iica la deuda
                dPeriodo=oInmueble.periodo.periodo  # Periodo que inicia la deuda
                anioini=dAnio
                mesini=dPeriodo
                primero=True
                ##print('kkkkkkkkkkkkkkkkkkkkkk',dPeriodo) 

                IC_ImpuestoPeriodo.objects.filter(inmueble=oInmueble).delete()  # elimina el historial de periodos pendientes
                                                        #por que este dato lo puede cambiar hacienda con acceso.borrar=true
                while dAnio<=ano_fin: # crea la cxc de periodos pendientes
                    if primero:
                        oPeriodo = IC_Periodo.objects.filter(aplica='C',periodo__gte=dPeriodo)
                        primero=False
                    else:
                        oPeriodo = IC_Periodo.objects.filter(aplica='C')
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
                oImpuestoPeriodo = IC_ImpuestoPeriodo.objects.filter(inmueble__numero_expediente=request['inmueble']).order_by('anio', 'periodo')
                if oImpuestoPeriodo:
                    oBaseCalculo = TasaBCV.objects.get(habilitado=True)
                    baseCalculoBs= float(oBaseCalculo.monto)
                    #Crear lista con los años presentes en la cxc
                    oAnio = IC_ImpuestoPeriodo.objects.filter(inmueble__numero_expediente=request['inmueble']).values('anio').distinct().order_by('anio')
                    maximo_ano = oAnio.aggregate(Max('anio'))['anio__max']
                    minimo_ano = oAnio.aggregate(Min('anio'))['anio__min']
                    
                    # Contar la cantidad de periodos configurados para C atastro
                    tPeriodo= IC_Periodo.objects.filter(aplica='C')
                    CountPeriodo= tPeriodo.count()
                    terreno =      InmuebleValoracionTerreno.objects.get(inmueble__numero_expediente=request['inmueble'])
                    construccion = InmuebleValoracionConstruccion.objects.filter(inmueblevaloracionterreno=terreno)
                    if terreno:
                        total_area_terreno = terreno.area 
                    else:
                        total_area_terreno = 0

                    if construccion:
                        total_area_construccion = construccion.aggregate(Sum('area'))['area__sum']
                    else:
                        total_area_construccion = 0

                    if (total_area_construccion > total_area_terreno) or (total_area_terreno==0 and total_area_construccion>0):
                        ocupacion=construccion
                    elif total_area_terreno>0 and total_area_construccion==0:
                        ocupacion =  InmuebleValoracionTerreno.objects.filter(inmueble__numero_expediente=request['inmueble'])
                        ocupacion = list(ocupacion) 
                    else:
                        ocupacion=construccion
                        if terreno: # hay inmuebles que NO TIENEN TERRENO, PARA ESE CASO NO ENTRA, SOLO TOMA LA CONTRUCCION
                            if total_area_construccion < total_area_terreno:
                                # Crear una nueva instancia de InmuebleValoracionConstruccion sin guardar en la base de datos
                                
                                nuevo_objeto_construccion = InmuebleValoracionConstruccion(
                                    tipologia=terreno.tipologia,
                                    tipo=terreno.tipo,
                                    area=terreno.area-total_area_construccion,
                                    aplica=terreno.aplica,
                                    inmueblevaloracionterreno=terreno  # Asignar la relación con el objeto terreno
                                )
                                # Agregar el nuevo objeto a la variable "ocupacion"
                                ocupacion = list(ocupacion)  # Convertir "ocupacion" en una lista
                                ocupacion.append(nuevo_objeto_construccion)  # Agregar el nuevo objeto a la lista
                            # En este punto, "ocupacion" contiene todos los objetos, incluido el nuevo objeto si se cumple la condición
                    ##print('ocupacion',ocupacion)
                    ZonaInmueble=Zona.zona
                    oTipologia=Tipologia.objects.filter(zona=ZonaInmueble)

                    #Ubicar la fecha de compra
                    oPropietario = InmueblePropietarios.objects.get(propietario__numero_documento=request['propietario'],inmueble__numero_expediente=request['inmueble'])
                    fechaCompra=oPropietario.fecha_compra
                    diferencia=today-fechaCompra
                    ##print(fechaCompra,today,diferencia.days)
                    # valida si aplica descuentos por pronto pago.
                    oDescuento=0 # Bandera que valida si aplica descuento o no
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
                    tDescuento=0
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
                                today <= fDiasGracia.fechadesde+timedelta(days=fDiasGracia.dias_gracia) :
                                    # La fecha actual está entre las fechas del modelo
                                    ##print("La fecha actual está entre fecha_desde y fecha_hasta.",fDiasGracia)
                                    bMulta=False
                                else:
                                    if today<= fDiasGracia.fechadesde and  \
                                        today <= fDiasGracia.fechadesde+timedelta(days=fDiasGracia.dias_gracia) :
                                        # La fecha actual es menor a las fechas del modelo (periodos proximos)
                                        ##print("La fecha actual es menor a las fechas del modelo (periodos proximos).",fDiasGracia)
                                        bMulta=False

                                    # La fecha actual NO está entre las fechas del modelo
                                    ##print("La fecha actual NO está entre fecha_desde y fecha_hasta.")
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
                                ppDescuento=0
                                if oDescuento: # and minimo_ano==today.year:
                                    # Valida que aplique descuento solamente con el año actual  !! inactivo. aplica descuento segun la tabla
                                    # Aplica descuentos generales
                                    aPeriodoMesDesde=aPeriodo.periodo.fechadesde.month
                                    aPeriodoMesHasta=aPeriodo.periodo.fechahasta.month
                                    aPeriodoDiaDesde=aPeriodo.periodo.fechadesde.day
                                    aPeriodoDiaHasta=aPeriodo.periodo.fechahasta.day
                                    try:
                                        pDescuento=oDescuento.filter(Q(tipologia__isnull=True) | Q(tipologia=dato.tipologia.id,),prontopago=False)
                                        ##print('descuento',pDescuento)
                                        ##print('registros',aPeriodo.periodo.fechadesde,aPeriodo.periodo.fechahasta) 
                                        registros_validos = pDescuento.filter(
                                            fechadesde__year__lte=minimo_ano,
                                            fechahasta__year__gte=minimo_ano,
                                            fechadesde__month__lte=aPeriodoMesDesde,
                                            fechahasta__month__gte=aPeriodoMesHasta,
                                            fechadesde__day__lte=aPeriodoDiaDesde,
                                            fechahasta__day__gte=aPeriodoDiaHasta) 
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
                                            'IC_impuestoperiodo':aPeriodo.periodo.id,
                                            'uso_id':dato.tipologia.id,
                                            'uso_descripcion':dato.tipologia.descripcion,
                                            'apica':dato.aplica,
                                            'anio': minimo_ano,
                                            'periodo': aPeriodo.periodo.periodo,
                                        }
                                        aDescuento.append(ImpuestoDetalleDescuentos)

                                    # Aplica descuentos prontopago
                                    try:
                                        pDescuento=oDescuento.filter(Q(tipologia__isnull=True) | Q(tipologia=dato.tipologia.id,),prontopago=True)
                                        ##print('descuento Pronto Pago',pDescuento)
                                        ##print('fecha actual',today.year,today.month,today.day) 
                                        ##print('fecha periodo',minimo_ano,aPeriodoMesDesde,aPeriodoDiaDesde,minimo_ano,aPeriodoMesHasta,aPeriodoDiaHasta) 
                                        registros_validos = pDescuento.filter(
                                            #fechadesde__year__lte=today.year,   # < =
                                            #fechahasta__year__gte=today.year,   # > =
                                            fechadesde__year=minimo_ano,
                                            fechadesde__month__lte=today.month, # < =
                                            fechahasta__month__gte=today.month, # > =
                                            fechadesde__day__lte=today.day,     # < =
                                            fechahasta__day__gte=today.day)     # > =
                                        ##print('registros_validos pronto pago 1',registros_validos)
                                        registros_validos2 = registros_validos.filter(
                                            fechadesde__year__lte=minimo_ano,       # < =
                                            fechahasta__year__gte=minimo_ano,       # > =
                                            fechadesde__month__lte=aPeriodoMesDesde,# < =
                                            fechahasta__month__gte=aPeriodoMesDesde,# > =
                                            fechadesde__day__lte=aPeriodoDiaDesde,  # < =
                                            fechahasta__day__gte=aPeriodoDiaDesde)  # > =
                                        ##print('registros_validos pronto pago 2',registros_validos2)
                                        ppDescuento=float(registros_validos.aggregate(Sum('porcentaje'))['porcentaje__sum'])
                                    except:
                                        ppDescuento=0
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
                                            'IC_impuestoperiodo':aPeriodo.periodo.id,
                                            'uso_id':dato.tipologia.id,
                                            'uso_descripcion':dato.tipologia.descripcion,
                                            'apica':dato.aplica,
                                            'anio': minimo_ano,
                                            'periodo': aPeriodo.periodo.periodo,
                                        }
                                        aDescuento.append(ImpuestoDetalleDescuentos)


                                Total=float(Monto-(Monto*((mDescuento+ppDescuento)/100)))
                                ImpuestoDetalle = {
                                    'IC_impuestoperiodo':aPeriodo.periodo.id,
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
                                    'mdescuento':mDescuento+ppDescuento,
                                    'total':Total,
                                }
                                tDescuento=tDescuento+mDescuento+ppDescuento
                                aDetalle.append(ImpuestoDetalle)
                                tTotal=tTotal+Total
                                if bMulta:
                                    tTotalMora=tTotalMora+Total
                                    tBaseMultaRecargoInteres=tBaseMultaRecargoInteres+Total
                                    tMulta=tMulta+(Total*(fMulta/100))
                                    tRecargo=tRecargo+(Total*(fRecargo/100))
                        if tTotalMora:
                            oTasaInteres=TasaInteres.objects.filter(anio=minimo_ano).order_by('mes')
                            tTotalMora=(tTotalMora/12)
                            for aTasa in oTasaInteres:
                                if (aTasa.mes<=today.month and minimo_ano==today.year) or minimo_ano!=today.year:
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
                        'descuento':tDescuento,
                        'total':tTotal+tMulta+tRecargo+tInteres,
                        'BaseMultaRecargoInteres':tBaseMultaRecargoInteres,
                        'flujo':Flujo.objects.filter(inmueble=oInmueble,estado='1').count() ,
                        'anioini':anioini,
                        'mesini':mesini,
                        'aniofin':request['anio'],
                        'mesfin':request['periodo'],
                        'propietario_numero_documento':oPropietario.propietario.numero_documento,
                        'propietario_direccion':oPropietario.propietario.direccion,
                        'propietario_nombre':oPropietario.propietario.nombre,
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

def Validar_Transferencia(request):
    oTransfencia=CorridasBancarias.objects.get(id=request['id'])
    try:
        oPagoEstadoCuentaDetalle=PagoEstadoCuentaDetalle.objects.get(bancocuenta=oTransfencia.bancocuenta, 
                                                fechapago=oTransfencia.fecha,
                                                nro_referencia=oTransfencia.referencia,
                                                monto=oTransfencia.monto)
    except PagoEstadoCuentaDetalle.DoesNotExist:
        oPagoEstadoCuentaDetalle=[]
    return Response(oPagoEstadoCuentaDetalle, status=status.HTTP_200_OK)



def Impuesto_Inmueble_Detalle(request):
    oCabacera=request['cabecera']
    oDetalle=request['detalle']
    oDescuento=request['descuento']
    oInteres=request['interes']
    oCorrelativo=Correlativo.objects.get(id=1)
    oEstadoCuenta=EstadoCuenta.objects.get(id=request['estadocuenta'])
    oZona=Zona.objects.get(id=oCabacera['zona'])
    cabecera=IC_Impuesto(
            numero = oCorrelativo.NumeroIC_Impuesto,
            estadocuenta =oEstadoCuenta,
            zona = oZona,
            basecalculobs = oCabacera['basecalculobs'],
            subtotal = oCabacera['subtotal'],
            multa =  oCabacera['multa'],
            recargo =  oCabacera['recargo'],
            interes =  oCabacera['interes'],
            total = oCabacera['total'],
            descuento  =  oCabacera['descuento'],
            aniopagoini=oCabacera['anioini'],
            periodopagoini=oCabacera['mesini'],
            aniopagofin=oCabacera['aniofin'],
            periodopagofin=oCabacera['mesfin'] 
    )
    cabecera.save()

    for cDetalle in oDetalle:
        oTipologia=Tipologia.objects.get(id=cDetalle['uso_id'])
        oPeriodo=IC_Periodo.objects.get(id=cDetalle['IC_impuestoperiodo'])
        oTipo=TipoInmueble.objects.get(id=cDetalle['tipo'])
        detalle=IC_ImpuestoDetalle(
                IC_impuesto  = cabecera,
                periodo  = oPeriodo,
                anio=cDetalle['anio'],
                tipologia = oTipologia,
                area = cDetalle['area_m2'] ,
                alicuota_articulo41=cDetalle['alicuota'],
                base=cDetalle['sub_total'],
                descuento=cDetalle['mdescuento'],
                total=cDetalle['total'],
                multa=cDetalle['multa'],
                tipo=oTipo 
        )
        detalle.save() 

    for cDetalle in oDescuento:
        oTipologia=Tipologia.objects.get(id=cDetalle['uso_id'])
        oPeriodo=IC_Periodo.objects.get(id=cDetalle['IC_impuestoperiodo'])
        oImpuestoDescuento=IC_ImpuestoDescuento.objects.get(id=cDetalle['IC_impuestodescuento'])
        detalleDescuento=IC_ImpuestoDetalleDescuentos(
                IC_impuesto  = cabecera,
                IC_impuestodescuento=oImpuestoDescuento,
                periodo  = oPeriodo,
                anio=cDetalle['anio'],
                tipologia = oTipologia,
                base=cDetalle['base'],
                porcentaje=cDetalle['descuento'],
                total=cDetalle['total']
        )
        detalleDescuento.save() 

    for cDetalle in oInteres:
        detalleMora=IC_ImpuestoDetalleMora(
                IC_impuesto  = cabecera,
                anio=cDetalle['anio'],
                mes = cDetalle['mes'],
                tasa=cDetalle['tasa'],
                dias=cDetalle['dias'],
                moramensual=cDetalle['moramensual'],
                interesmensual=cDetalle['interesmensual']
        )
        detalleMora.save() 
    oCorrelativo.NumeroIC_Impuesto=oCorrelativo.NumeroIC_Impuesto+1
    oCorrelativo.save() 

    return Response('Insert OK', status=status.HTTP_200_OK)    


def Crear_Estado_Cuenta1(request):
    if (request):
        items=request['detalle']
        correlativo=Correlativo.objects.get(id=1)
        valor_petro=TasaBCV.objects.get(habilitado=True).monto
        valor_tasabcv=TasaBCV.objects.get(habilitado=True).monto
        ##print('numero',correlativo.NumeroEstadoCuenta)
        ##print('tipoflujo',request['flujo'])
        ##print('fecha',str(datetime.now()))
        ##print('propietario',request['propietario'])
        ##print('observaciones',request['observacion'])
        ##print('valor_petro',valor_petro)
        ##print('valor_tasa_bs',valor_tasabcv)
        ##print('monto_total',request['monto_total'])
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
            ###print('estadocuenta')
            ##print('tasamulta',detalle['tasa_multa_id'])

            #monto_unidad_tributaria=TasaMulta.objects.get(id=detalle['tasa_multa_id']).unidad_tributaria
            ###print('monto_unidad_tributaria',monto_unidad_tributaria)
            ###print('monto_tasa',monto_unidad_tributaria*detalle['cantidad']*valor_petro*valor_tasabcv)
            ####print('monto_tasa',detalle['monto_unidad_tributaria']*detalle['cantidad']*valor_petro*valor_tasabcv)

            ##print('monto_unidad_tributaria',detalle['monto_unidad_tributaria'])
            ##print('monto_tasa',detalle['calculo'])
            ##print('cantidad',detalle['cantidad'])
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
    
def importar_datos_desde_excel(archivo,pestana):
    print('Backend procesando: ',pestana)
    importar=pestana
   # ExcelDocumentLOG.objects.filter(codigo=importar).delete()
    excel_document=ExcelDocument.objects.get(title=archivo)

    if importar=='CategorizacionUrbana':
        ruta_archivo_excel = excel_document.excel_file.path
        datos_excel = pd.read_excel(ruta_archivo_excel, sheet_name='CategorizacionUrbana')
        for index, row in datos_excel.iterrows():
            if not math.isnan(row['id_inmueble']):
                numero_expediente = int((row['id_inmueble']))
            else:
                numero_expediente = 0
            nComunidad = (row['comunidad']) #nombre de la comunidad
            try:
                oComunidad=Comunidad.objects.get(comunidad=nComunidad)                  #Ubicamos la comunidad segun el excel
                oCategoria=Categorizacion.objects.get(codigo=oComunidad.categoria)      #Ubicamos en codigo de la categorizacion segun el excel
                oIinmueble=Inmueble.objects.get(numero_expediente=numero_expediente)    #Ubicamos el inmuevle segun el excel
                oIinmueble.comunidad=oComunidad
                oIinmueble.categorizacion=oCategoria
                print("INMUEBLE EXCEL :",numero_expediente)
                print("comunidadexcel :",row['comunidad'],oComunidad)
                print("Categoria excel:",oCategoria)
                if oComunidad.categoria!='X': # solo ENTRA A PROCESAR cuando la comunidad es difeente de X "SIN COMUNIDAD" PERO SI ACTUALIZO LA FICHA OARA QUE MUESTRE LA ALERTA, QUE FALTA COLOCAR LA COMUNIDAD CORRECTA.

                    #------------------------------- actualizar la valoracion economica
                    TerrenoValido=True
                    try:
                        terreno=InmuebleValoracionTerreno2024.objects.get(inmueble=oIinmueble)
                        if terreno.tipologia_categorizacion==None:
                            TerrenoValido=False
                    except InmuebleValoracionTerreno2024.DoesNotExist:
                        TerrenoValido=False
                    print('terreno.tipologia_categorizacion',terreno.tipologia_categorizacion)
                    if TerrenoValido: 
                        print('Actual Codigo Cateforizacion terreno:',terreno.tipologia_categorizacion.codigo)
                        print('Actual Nombre Cateforizacion terreno:',terreno.tipologia_categorizacion.descripcion)
                        print('Actual codigo Tipologia      terreno:',terreno.tipologia_categorizacion.categorizacion.codigo)
                        NewdUso=Tipologia_Categorizacion.objects.get(categorizacion=oCategoria,descripcion=terreno.tipologia_categorizacion.descripcion)
                        terreno.tipologia_categorizacion=NewdUso   
                        print('NewdUso terreno',NewdUso.codigo,NewdUso.descripcion)
                        terreno.save()
                    else:
                        print('Inmueble sin terreno!!!!!!!!!!!!!!!!!!!')
                    
                    construccion = InmuebleValoracionConstruccion2024.objects.filter(inmueblevaloracionterreno=terreno)
                    for detalle in construccion:
                        print('Actual Codigo Cateforizacion construccion:',detalle.tipologia_categorizacion.codigo)
                        print('Actual Nombre Cateforizacion construccion:',detalle.tipologia_categorizacion.descripcion)
                        print('Actual codigo Tipologia      construccion:',detalle.tipologia_categorizacion.categorizacion.codigo)
                        NewdUso=Tipologia_Categorizacion.objects.get(categorizacion=oCategoria,descripcion=detalle.tipologia_categorizacion.descripcion)
                        detalle.tipologia_categorizacion=NewdUso  
                        detalle.save() 
                        print('NewdUso construccion',NewdUso.codigo,NewdUso.descripcion)                 
                        #input()
                oIinmueble.save() 
            except Inmueble.DoesNotExist:
                print(f"No existe el numero de expediente {numero_expediente}")
                ExcelDocumentLOG.objects.create(pestana=importar, codigo=numero_expediente, error='No existe expediente')
            except IntegrityError as e:
                # Maneja cualquier error de integridad si es necesario
                print(f"Error de integridad al crear el registro: {e}")
                ExcelDocumentLOG.objects.create(pestana=importar, codigo=numero_expediente, error=e)
        print("Ultimo pagos actualizados exitosamente.")  
    if importar=='comunidad':
        #Comunidad.objects.all().delete()
        ruta_archivo_excel = excel_document.excel_file.path
        datos_excel = pd.read_excel(ruta_archivo_excel, sheet_name='comunidad')
        for index, row in datos_excel.iterrows():
            print('comunidad',row['comunidad'],'categoria',row['categoria'])
            try:
                # Intenta obtener un registro existente o crear uno nuevo si no existe
                creado = Comunidad.objects.get_or_create(
                    comunidad = row['comunidad'],
                    categoria = row['categoria'], 
                )
                if not creado:
                    print(f"El registro ya existe y no se creó uno nuevo.")
                    
            except IntegrityError as e:
                print(f"Error de integridad al crear el registro: {e}")
                ExcelDocumentLOG.objects.create(pestana=importar, codigo=mes, error=e)
        print("Datos importados exitosamente.")
    if importar=='inmueblecategorizacion':
        # aca se crear un modelo igual a Inmueble. luego se importa un excel generado nueva,mente dela BD de sicadi
        # solo para trabajar lo categorizacion 
        InmuebleCategorizacion.objects.all().delete()
        ruta_archivo_excel = excel_document.excel_file.path
        datos_excel = pd.read_excel(ruta_archivo_excel, sheet_name='inmueblecategorizacion')
        for index, row in datos_excel.iterrows():
            print('id_inmueble',row['id_inmueble'])
            try:
                # Intenta obtener un registro existente o crear uno nuevo si no existe
                creado = InmuebleCategorizacion.objects.get_or_create(
                    id_inmueble = row['id_inmueble'],
                    tipo_inmueble = row['tipo_inmueble'],
                    id_ambito = row['id_ambito'],
                    sector = row['sector'],
                    id_manzana = row['id_manzana'],
                    id_parcela = row['id_parcela'],
                    id_sub_parcela = row['id_sub_parcela'],
                    urb_barrio = row['urb_barrio'],
                    con_residencial = row['con_residencial'],
                    edificio = row['edificio'],
                    avenida = row['avenida'],
                    via = row['via'],
                    referencia = row['referencia'],
                    telefono = row['telefono'],
                    observaciones = row['observaciones'],
                    direccion = row['direccion'],
                    total_construccion = row['total_construccion'],
                    total_terreno = row['total_terreno'],
                )
                if not creado:
                    print(f"El registro ya existe y no se creó uno nuevo.")
                    
            except IntegrityError as e:
                print(f"Error de integridad al crear el registro: {e}")
                ExcelDocumentLOG.objects.create(pestana=importar, codigo=mes, error=e)
        print("Datos importados exitosamente.")
    if importar=='inicio':
        # asignar al control de correlativos el ultimo numero de expediemte importado
        max_numero_expediente = Inmueble.objects.exclude(numero_expediente__isnull=True).exclude(numero_expediente='').filter(numero_expediente__regex=r'^\d+$').aggregate(max_numero_expediente=Max('numero_expediente'))['max_numero_expediente']

        print(max_numero_expediente)
        correlativo=Correlativo.objects.get(id=1)
        correlativo.ExpedienteCatastro=int(max_numero_expediente)+1
        correlativo.save()           
    if importar=='vaciar':
        NotaCredito.objects.all().delete()
        print('NotaCredito')
        AE_Patente_ActividadEconomica.objects.all().delete()
        print('AE_Patente_ActividadEconomica')
        AE_Patente.objects.all().delete()
        print('AE_Patente')
        FlujoDetalle.objects.all().delete()
        print('FlujoDetalle')
        Flujo.objects.all().delete()
        print('Flujo')
        IC_ImpuestoDetalleDescuentos.objects.all().delete()
        print('IC_ImpuestoDetalleDescuentos')

        IC_ImpuestoDetalleMora.objects.all().delete()
        print('IC_ImpuestoDetalleMora')

        IC_ImpuestoDetalle.objects.all().delete()
        print('IC_ImpuestoDetalle')
        IC_Impuesto.objects.all().delete()
        print('IC_Impuesto')

        PagoEstadoCuentaDetalle.objects.all().delete()
        print('PagoEstadoCuentaDetalle')
        PagoEstadoCuenta.objects.all().delete()
        print('PagoEstadoCuenta')
        LiquidacionDetalle.objects.all().delete()
        print('LiquidacionDetalle')
        Liquidacion.objects.all().delete()
        print('Liquidacion')
        EstadoCuentaDetalle.objects.all().delete()
        print('EstadoCuentaDetalle')
        EstadoCuenta.objects.all().delete()
        print('EstadoCuenta')
        InmueblePropietarios.objects.all().delete()
        print('InmueblePropietarios')
        Propietario.objects.all().delete()
        print('Propietario')
        ################ eliminar inmueble inicio
        IC_ImpuestoPeriodo.objects.all().delete()
        print('IC_ImpuestoPeriodo')
        InmueblePropiedad.objects.all().delete()
        print('InmueblePropiedad')
        InmuebleConstruccion.objects.all().delete()
        print('InmuebleConstruccion')
        InmuebleFaltante.objects.all().delete()
        print('InmuebleFaltante')
        InmuebleTerrenoUso.objects.all().delete()
        print('InmuebleTerrenoUso')
        InmuebleTerreno.objects.all().delete()
        print('InmuebleTerreno')
        InmuebleUbicacion.objects.all().delete()
        print('InmuebleUbicacion')
        InmuebleValoracionConstruccion.objects.all().delete()
        print('InmuebleValoracionConstruccion')
        InmuebleValoracionTerreno.objects.all().delete()

        print('InmuebleUbicacion2024')
        InmuebleValoracionConstruccion2024.objects.all().delete()
        print('InmuebleValoracionConstruccion2024')
        InmuebleValoracionTerreno2024.objects.all().delete()

        print('InmuebleValoracionTerreno')
        Inmueble.objects.all().delete()
        print('Inmueble')       
        ################# fin
        #SubParcela.objects.all().delete()
        #Parcela.objects.all().delete() 
        #Manzana.objects.all().delete() 
        #Calle.objects.all().delete()
        #Avenida.objects.all().delete()
        #Torre.objects.all().delete()
        #Edificio.objects.all().delete()
        #ConjuntoResidencial.objects.all().delete()
        #Urbanizacion.objects.all().delete()
        #Sector.objects.all().delete() 
        #Ambito.objects.all().delete()
        #ExcelDocumentLOG.objects.all().delete()
    if importar=='tasas':
        TasaInteres.objects.all().delete()
        # esto se cambia porque hay problemas al acesar al archivo en fisico, se cambia para que se cargue en un modelo.
        # tambien sa debe colocar en elmismo excel pero otra pestaña.
        #ruta_archivo_excel = os.path.join('media', 'archivos_excel/tasa.xlsx')
        #datos_excel = pd.read_excel(ruta_archivo_excel)
        ruta_archivo_excel = excel_document.excel_file.path
        datos_excel = pd.read_excel(ruta_archivo_excel, sheet_name='tasa_interes')
        for index, row in datos_excel.iterrows():
            print('anio',row['anio'],'mes',row['anio'],'mes',row['tasa'])
            anio = row['anio']
            mes = row['mes']
            tasa = row['tasa']
            try:
                # Intenta obtener un registro existente o crear uno nuevo si no existe
                creado = TasaInteres.objects.get_or_create(
                    anio = anio,
                    mes  = mes,
                    tasa = tasa,
                )
                if not creado:
                    print(f"El registro con anio {anio} y mes {mes} ya existe y no se creó uno nuevo.")
                    
            except IntegrityError as e:
                # Maneja cualquier error de integridad si es necesario
                print(f"Error de integridad al crear el registro: {e}")
                ExcelDocumentLOG.objects.create(pestana=importar, codigo=mes, error=e)
            # Crea un nuevo objeto TasaInteres y guárdalo en la base de datos
            #TasaInteres.objects.create(anio=anio, mes=mes, tasa=tasa)
        print("Datos importados exitosamente.")
    if importar=='ambito':
        # metodo anterior que se leia desde un directorio, se cambia por metodo de lectura desde la carga en un modelo ya,
        # que falla cuando se puclica en nube, lovcal si funciona
        #ruta_archivo_excel = os.path.join('media', 'archivos_excel/maestros_dir_estructurada.xlsx')
        #datos_excel = pd.read_excel(ruta_archivo_excel, sheet_name='ambito')
        ruta_archivo_excel = excel_document.excel_file.path
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
                ExcelDocumentLOG.objects.create(pestana=importar, codigo=codigo, error=e)
        print("Ambito importados exitosamente.")
    if importar=='sector':
        #ruta_archivo_excel = os.path.join('media', 'archivos_excel/maestros_dir_estructurada.xlsx')
        ruta_archivo_excel = excel_document.excel_file.path
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
                ExcelDocumentLOG.objects.create(pestana=importar, codigo=codigo, error=e)
        print("Sector importados exitosamente.")  
    if importar=='manzana':
        #ruta_archivo_excel = os.path.join('media', 'archivos_excel/maestros_dir_estructurada.xlsx')
        ruta_archivo_excel = excel_document.excel_file.path
        datos_excel = pd.read_excel(ruta_archivo_excel, sheet_name='manzana')
        for index, row in datos_excel.iterrows():
            ambito=Ambito.objects.get(codigo=row['id_ambito']) # integridad con ambito
            sector=Sector.objects.get(codigo=row['id_sector'],ambito=ambito) # integridad con ambito
            codigo = row['id_manzana']
            area = row['area'] if not math.isnan(row['area']) else Decimal('0')
            perimetro = row['perimetro'] if not math.isnan(row['perimetro']) else Decimal('0')
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
                ExcelDocumentLOG.objects.create(pestana=importar, codigo=codigo, error=e)
        print("manzana importados exitosamente.")
    if importar=='parcela':
        #ruta_archivo_excel = os.path.join('media', 'archivos_excel/maestros_dir_estructurada.xlsx')
        ruta_archivo_excel = excel_document.excel_file.path
        datos_excel = pd.read_excel(ruta_archivo_excel, sheet_name='parcela')
        for index, row in datos_excel.iterrows():
            ambito=Ambito.objects.get(codigo=row['id_ambito']) # integridad con ambito
            sector=Sector.objects.get(codigo=row['id_sector'],ambito=ambito) # integridad con sector
            manzana=Manzana.objects.get(codigo=row['id_manzana'],sector=sector) # integridad con manzana
            codigo = row['id_parcela']
            area = row['area'] if not math.isnan(row['area']) else Decimal('0')
            perimetro = row['perimetro'] if not math.isnan(row['perimetro']) else Decimal('0')
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
                ExcelDocumentLOG.objects.create(pestana=importar, codigo=codigo, error=e)
        print("parcela importados exitosamente.")  
    if importar=='sub-parcela':
        #ruta_archivo_excel = os.path.join('media', 'archivos_excel/maestros_dir_estructurada.xlsx')
        ruta_archivo_excel = excel_document.excel_file.path
        datos_excel = pd.read_excel(ruta_archivo_excel, sheet_name='sub_parcela')
        for index, row in datos_excel.iterrows():
            ambito=Ambito.objects.get(codigo=row['id_ambito']) # integridad con ambito
            sector=Sector.objects.get(codigo=row['id_sector'],ambito=ambito) # integridad con sector
            manzana=Manzana.objects.get(codigo=row['id_manzana'],sector=sector) # integridad con manzana
            parcela=Parcela.objects.get(codigo=row['id_parcela'],manzana=manzana) # integridad con parcela
            codigo = row['id_sub_parcela']
            area = row['area'] if not math.isnan(row['area']) else Decimal('0')
            perimetro = row['perimetro'] if not math.isnan(row['perimetro']) else Decimal('0')
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
                ExcelDocumentLOG.objects.create(pestana=importar, codigo=codigo, error=e)
        print("SubParcela importados exitosamente.")  
    if importar=='barrios': #Urbanizacion
        #ruta_archivo_excel = os.path.join('media', 'archivos_excel/maestros_dir_estructurada.xlsx')
        ruta_archivo_excel = excel_document.excel_file.path
        datos_excel = pd.read_excel(ruta_archivo_excel, sheet_name='barrioss')
        for index, row in datos_excel.iterrows():
            ambito=Ambito.objects.get(codigo=row['id_ambito']) # integridad con ambito
            sector=Sector.objects.get(codigo=row['id_sector'],ambito=ambito) # integridad con ambito
            codigo = row['id_urb_barrio']
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
                ExcelDocumentLOG.objects.create(pestana=importar, codigo=codigo, error=e)
        print("barrios importados exitosamente.")
    if importar=='contribuyente':
        #ruta_archivo_excel = os.path.join('media', 'archivos_excel/maestros_dir_estructurada.xlsx')
        ruta_archivo_excel = excel_document.excel_file.path
        datos_excel = pd.read_excel(ruta_archivo_excel, sheet_name='persona')
        for index, row in datos_excel.iterrows():
            numero_documento = row['id_persona']
            nombre = row['nombre']
            telefono_principal = row['telefono']
            direccion = row['direccion']
            #telefono_secundario = row['fax']
            email_principal = row['correo']
            #emaill_secundario = row['correo2']
            try:
                # Intenta obtener un registro existente o crear uno nuevo si no existe
                creado = Propietario.objects.get_or_create(
                    numero_documento=numero_documento,
                    defaults={
                        'nombre': nombre,
                        'telefono_principal':telefono_principal,
                        'direccion':direccion,
                        #'telefono_secundario':telefono_secundario,
                        'email_principal':email_principal,
                        #'emaill_secundario':emaill_secundario,
                    }
                )
                if not creado:
                    print(f"El registro con código {numero_documento} ya existe y no se creó uno nuevo.")
            except IntegrityError as e:
                # Maneja cualquier error de integridad si es necesario
                print(f"Error de integridad al crear el registro: {e}")
                ExcelDocumentLOG.objects.create(pestana=importar, codigo=codigo, error=e)
        print("Persona/contribuyente importados exitosamente.")
    if importar=='conj_resinden':
        #ruta_archivo_excel = os.path.join('media', 'archivos_excel/maestros_dir_estructurada.xlsx')
        ruta_archivo_excel = excel_document.excel_file.path
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
                ExcelDocumentLOG.objects.create(pestana=importar, codigo=numero_documento, error=e)
        print("conj_resinden importados exitosamente.")
    if importar=='edificio':
        #ruta_archivo_excel = os.path.join('media', 'archivos_excel/maestros_dir_estructurada.xlsx')
        ruta_archivo_excel = excel_document.excel_file.path
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
                    ExcelDocumentLOG.objects.create(pestana=importar, codigo=codigo, error=e)
            except ConjuntoResidencial.DoesNotExist:
                print("Conjunto residencial  no existe.")
        print("edificio importados exitosamente.")
    if importar=='torre':
        #ruta_archivo_excel = os.path.join('media', 'archivos_excel/maestros_dir_estructurada.xlsx')
        ruta_archivo_excel = excel_document.excel_file.path
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
                    ExcelDocumentLOG.objects.create(pestana=importar, codigo=codigo, error=e)
            except ConjuntoResidencial.DoesNotExist:
                print("Conjunto residencial  no existe.")
        print("Torre importados exitosamente.")
    if importar=='avenida':
        #ruta_archivo_excel = os.path.join('media', 'archivos_excel/maestros_dir_estructurada.xlsx')
        ruta_archivo_excel = excel_document.excel_file.path
        datos_excel = pd.read_excel(ruta_archivo_excel, sheet_name='avenida')
        for index,row in datos_excel.iterrows():
            codigo = row['id_avenida']
            nombre = row['nombre']
            tipo = int(row['id_tipo_avenida'])
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
                ExcelDocumentLOG.objects.create(pestana=importar, codigo=codigo, error=e)
        print("avenida importados exitosamente.")
    if importar=='calle':
        #ruta_archivo_excel = os.path.join('media', 'archivos_excel/maestros_dir_estructurada.xlsx')
        ruta_archivo_excel = excel_document.excel_file.path
        datos_excel = pd.read_excel(ruta_archivo_excel, sheet_name='via')
        for index,row in datos_excel.iterrows():
            codigo = row['id_via']
            nombre = row['nombre']
            tipo = int(row['id_tipo_via'])
            try:
                # Intenta obtener un registro existente o crear uno nuevo si no existe
                creado = Calle.objects.get_or_create(
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
                ExcelDocumentLOG.objects.create(pestana=importar, codigo=codigo, error=e)
        print("calle importados exitosamente.")
    if importar=='inmueble':
        #ruta_archivo_excel = os.path.join('media', 'archivos_excel/maestros_dir_estructurada.xlsx')
        ruta_archivo_excel = excel_document.excel_file.path
        datos_excel = pd.read_excel(ruta_archivo_excel, sheet_name='inmueble')
        for index, row in datos_excel.iterrows():
            strZona= row['id_zona2004']
            if not math.isnan(strZona):
                parte_entera = int(strZona)
            else:
                parte_entera = 99

            if  len(str(row['id_inmueble']))<6 and row['id_inmueble'] !=0: 
                #print(int(row['id_urb_barrio']) if not math.isnan(row['id_urb_barrio']) else '',int(row['id_conj_residencial']) if not math.isnan(row['id_conj_residencial']) else '')

                try:
                    zona=Zona.objects.get(codigo=parte_entera) # integridad con zona
                    try:
                        ambito=Ambito.objects.get(codigo=row['id_ambito']) # integridad con ambito
                    except Ambito.DoesNotExist:
                        ambito=None
                    try:
                        sector=Sector.objects.get(codigo=int(row['id_sector']) if not math.isnan(row['id_sector']) else '',ambito=ambito) # integridad con sector 
                    except Sector.DoesNotExist:
                        sector=None
                    try:
                        manzana=Manzana.objects.get(codigo=int(row['id_manzana']) if not math.isnan(row['id_manzana']) else '',sector=sector) # integridad con manzana
                    except Manzana.DoesNotExist:
                        manzana=None
                    try:
                        parcela=Parcela.objects.get(codigo=int(row['id_parcela']) if not math.isnan(row['id_parcela']) else '' ,manzana=manzana) # integridad con parcela
                    except Parcela.DoesNotExist:
                        parcela=None
                    try:
                        subparcela=SubParcela.objects.get(codigo=int(row['id_sub_parcela']) if not math.isnan(row['id_sub_parcela']) else '' ,parcela=parcela) # integridad con sector
                    except SubParcela.DoesNotExist:
                        subparcela=None
                    try:
                        id_urb_barrio = row['id_urb_barrio']

                        # Comprobar si id_urb_barrio es numérico y no es NaN
                        if isinstance(id_urb_barrio, (int, float)) and not math.isnan(id_urb_barrio):
                            id_urb_barrio = int(id_urb_barrio)
                        else:
                            id_urb_barrio = None  # O puedes asignar otro valor predeterminado si es apropiado


                        urbanizacion=Urbanizacion.objects.get(codigo= id_urb_barrio,sector=sector) # integridad con sector
                    except Urbanizacion.DoesNotExist:
                        urbanizacion=None
                    try:
                        conjunto_residencial=ConjuntoResidencial.objects.get(codigo=int(row['id_conj_residencial']) if not math.isnan(row['id_conj_residencial']) else '' ) # integridad con conjunto_residencial
                    except ConjuntoResidencial.DoesNotExist:
                        conjunto_residencial=None
                    ## ojo le quito el fltro de urbanizacion porque no esab bien el dato en la hoja de inmuebles

                    try:
                        edificio=Edificio.objects.get(codigo=int(row['id_edificio']) if not math.isnan(row['id_edificio']) else ' ' ,conjuntoresidencial=conjunto_residencial) # integridad con sector
                    except Edificio.DoesNotExist:
                        edificio=None
                    try:
                        torre=Torre.objects.get(codigo=int(row['id_torre']) if not math.isnan(row['id_torre']) else ' ' , conjuntoresidencial=conjunto_residencial) # integridad con sector
                    except Torre.DoesNotExist:
                        torre=None
                    try:
                        avenida=Avenida.objects.get(codigo= int(row['id_avenida']) if not math.isnan(row['id_avenida']) else '') # integridad con sector
                    except Avenida.DoesNotExist:
                        avenida=None
                    numero_expediente = row['id_inmueble']
                    fecha_inscripcion = row['fecha_inscripcion']

                    if isinstance(fecha_inscripcion, str) and len(fecha_inscripcion) > 0:
                    # Cadena de fecha y hora en el formato original
                        cadena_fecha_hora = row['fecha_inscripcion']

                        # Extrae la parte de la cadena que contiene la fecha
                        partes = cadena_fecha_hora.split(' ')
                        fecha_original = partes[0]
                    else:
                        fecha_original=None

                    try:
                        # Intenta obtener un registro existente o crear uno nuevo si no existe
                        inmueble, creado = Inmueble.objects.get_or_create(
                            numero_expediente=numero_expediente,
                            ambito=ambito, 
                            sector=sector,
                            manzana=manzana,
                            parcela=parcela,
                            subparcela=subparcela,
                            urbanizacion=urbanizacion,
                            conjunto_residencial=conjunto_residencial,
                            edificio=edificio,
                            torre=torre,
                            avenida=avenida,
                            defaults={
                                'fecha_inscripcion':fecha_original,
                                'zona': zona,
                                'numero_piso':row['piso'],
                                'numero_civico':row['nro_civico'],
                                'referencia':row['referencia'],
                                'observaciones':row['observaciones'],
                                'direccion':row['direccion'],
                                'telefono':row['telefono'],
                            }
                        )
                        InmueblePropiedad(inmueble=inmueble).save()
                        InmuebleTerreno(inmueble=inmueble).save()
                        InmuebleConstruccion(inmueble=inmueble).save()
                        InmuebleValoracionTerreno(inmueble=inmueble).save()
                        InmuebleUbicacion(inmueble=inmueble).save()
                        InmuebleFaltante(inmueble=inmueble).save()
                        if not creado:
                            print(f"El registro con código {numero_expediente} ya existe y no se creó uno nuevo.")
                            ExcelDocumentLOG.objects.create(pestana=importar, codigo=numero_expediente, error='Expediente ya existe.')
                        #else:
                            #print(f"El registro con código {numero_expediente} SE CREO.")
                            #response_data = {
                            #    'id': numero_expediente
                            #}

                            ## Devolver la respuesta como JSON
                            ##return JsonResponse(response_data)
                            

                    except IntegrityError as e:
                        # Maneja cualquier error de integridad si es necesario
                        print(f"Error de integridad al crear el registro: {e}")
                        ExcelDocumentLOG.objects.create(pestana=importar, codigo=numero_expediente, error=e)
                except Zona.DoesNotExist:
                    print("Zona no existe.")
                    ExcelDocumentLOG.objects.create(pestana=importar, codigo=numero_expediente, error="Zona no existe.")
                except Ambito.DoesNotExist:
                    print("Ambito no existe.")
                except Sector.DoesNotExist:
                    print("Sector no existe.")
                except Manzana.DoesNotExist:
                    print("Manzana no existe.")
                except Parcela.DoesNotExist:
                    print("Parcela no existe.")
                except SubParcela.DoesNotExist:
                    print("SubParcela no existe.")                   
                except Urbanizacion.DoesNotExist:
                    print("Urbanizacion no existe.")
                except ConjuntoResidencial.DoesNotExist:
                    print("ConjuntoResidencial no existe.")
                except Edificio.DoesNotExist:
                    print("Edificio no existe.")
                except Torre.DoesNotExist:
                    print("Torre no existe.")
                except Avenida.DoesNotExist:
                    print("Avenida no existe.")
        # asignar al control de correlativos el ultimo numero de expediemte importado
        #max_numero_expediente = Inmueble.objects.all().aggregate(max_numero_expediente=Max('numero_expediente'))['max_numero_expediente']
        #correlativo=Correlativo.objects.get(id=1)
        #correlativo.ExpedienteCatastro=int(max_numero_expediente)+1
        #correlativo.save()

        print("inmueble importados exitosamente.")
    if importar=='propietario':
        #ruta_archivo_excel = os.path.join('media', 'archivos_excel/maestros_dir_estructurada.xlsx')
        ruta_archivo_excel = excel_document.excel_file.path
        datos_excel = pd.read_excel(ruta_archivo_excel, sheet_name='propietario')
        for index, row in datos_excel.iterrows():
            if  len(str(row['id_inmueble']))<6: 
                try:
                    inmueble=Inmueble.objects.get(numero_expediente=row['id_inmueble']) # integridad con inmueble
                    propietario=Propietario.objects.get(numero_documento=row['id_persona']) # integridad con propietario
                    try:
                        # Intenta obtener un registro existente o crear uno nuevo si no existe
                        creado = InmueblePropietarios.objects.get_or_create(
                            inmueble=inmueble,
                            propietario=propietario,
                            defaults={
                                'fecha_compra': inmueble.fecha_inscripcion,
                            }
                        )
                        if not creado:
                            print(f"El registro con código {inmueble} ya existe y no se creó uno nuevo.")
                        else:
                            print(f"El registro con código {inmueble} SE CREO.")

                    except IntegrityError as e:
                        # Maneja cualquier error de integridad si es necesario
                        print(f"Error de integridad al crear el registro: {e}")
                        ExcelDocumentLOG.objects.create(pestana=importar, codigo=inmueble, error=e)
                except Inmueble.DoesNotExist:
                    print("Inmueble no existe.")
                    ExcelDocumentLOG.objects.create(pestana=importar, codigo=row['id_inmueble'], error="Inmueble no existe.")
                except Propietario.DoesNotExist:
                    print("Propietario no existe.")
                    ExcelDocumentLOG.objects.create(pestana=importar, codigo=row['id_persona'], error="Propietario no existe.")

        print("propietario importados exitosamente.")
    if importar=='ult_pago':
        periodoId=0
        ruta_archivo_excel = excel_document.excel_file.path
        datos_excel = pd.read_excel(ruta_archivo_excel, sheet_name='ult_pago')
        for index, row in datos_excel.iterrows():
            today = date.today()
            if not math.isnan(row['expediente']):
                numero_expediente = int((row['expediente']))
            else:
                numero_expediente = 0
            anio = int((row['age']))
            periodoId = int((row['mes']))
            if periodoId==4:
                periodoId=1
                anio=anio+1
            else:
                periodoId=periodoId+1
            try:
                periodo=IC_Periodo.objects.get(periodo=periodoId,aplica='C')
                inmueble=Inmueble.objects.get(numero_expediente=numero_expediente)
                print('anio',anio,'periodo',periodo)
                inmueble.anio=anio
                inmueble.periodo=periodo
                inmueble.save()
                #response_data = {
                #    'id': numero_expediente
                #}

                ## Devolver la respuesta como JSON
                #return JsonResponse(response_data)

            except Inmueble.DoesNotExist:
                print(f"No existe el numero de expediente {numero_expediente}")
                ExcelDocumentLOG.objects.create(pestana=importar, codigo=numero_expediente, error='No existe expediente')
            except IntegrityError as e:
                # Maneja cualquier error de integridad si es necesario
                print(f"Error de integridad al crear el registro: {e}")
                ExcelDocumentLOG.objects.create(pestana=importar, codigo=numero_expediente, error=e)
        print("Ultimo pagos actualizados exitosamente.")  
    if importar=='tipologia':
        ruta_archivo_excel = excel_document.excel_file.path
        datos_excel = pd.read_excel(ruta_archivo_excel, sheet_name='tipologia')
        for index, row in datos_excel.iterrows():
            strZona= row['zona']
            if not math.isnan(strZona):
                parte_entera = int(strZona)
            else:
                parte_entera = 99 

            zona=Zona.objects.get(codigo=parte_entera) 
            codigo = row['codigo']
            descripcion = row['descripcion']
            tarifa = row['tarifa']
            try:
                # Intenta obtener un registro existente o crear uno nuevo si no existe
                tipologia, creado = Tipologia.objects.get_or_create(
                    codigo=codigo,
                    defaults={
                        'descripcion': descripcion,
                        'zona': zona,
                        'tarifa': tarifa,
                    }
                )
                if not creado:
                    print(f"El registro con código {codigo} ya existe y no se creó uno nuevo.")
            except IntegrityError as e:
                # Maneja cualquier error de integridad si es necesario
                print(f"Error de integridad al crear el registro: {e}")
                ExcelDocumentLOG.objects.create(pestana=importar, codigo=codigo, error=e)
        print("Ambito importados exitosamente.")
    if importar=='val_terreno':
        ruta_archivo_excel = excel_document.excel_file.path
        datos_excel = pd.read_excel(ruta_archivo_excel, sheet_name='val_terreno')
        for index, row in datos_excel.iterrows():
            if not math.isnan(row['id_inmueble']):
                numero_expediente = int((row['id_inmueble']))
            else:
                numero_expediente = 0
            if not math.isnan(row['tipologia']):
                tipologiaId = int(row['tipologia'])
            else:
                tipologiaId = 0
            tipologia = Tipologia.objects.get(codigo=tipologiaId)
            if tipologia.descripcion=='RESIDENCIAL' :
                tipoinmuebleId=1
            if tipologia.descripcion=='COMERCIAL' :
                tipoinmuebleId=2
            if tipologia.descripcion=='INDUSTRIAL' : 
                tipoinmuebleId=3
            tipoinmueble=TipoInmueble.objects.get(codigo=tipoinmuebleId)      
            area = row['area']
            try:
                print('numero_expediente',numero_expediente,'tipologia',tipologia)
                inmueble=Inmueble.objects.get(numero_expediente=numero_expediente)
                inmueblevaloracionterreno=InmuebleValoracionTerreno.objects.get(inmueble=inmueble.id)
                print('inmueblevaloracionterreno',inmueblevaloracionterreno)
                inmueblevaloracionterreno.tipologia=tipologia
                inmueblevaloracionterreno.area=area
                inmueblevaloracionterreno.tipo=tipoinmueble
                inmueblevaloracionterreno.save()

            except InmuebleValoracionTerreno.DoesNotExist:
                print(f"No existe el numero de expediente {numero_expediente}")
                ExcelDocumentLOG.objects.create(pestana=importar, codigo=numero_expediente, error='No existe InmuebleValoracionTerreno')
            except Inmueble.DoesNotExist:
                print(f"No existe el INMUEBLE numero de expediente {numero_expediente}")
                ExcelDocumentLOG.objects.create(pestana=importar, codigo=numero_expediente, error='No existe INMUEBLE')
            except IntegrityError as e:
                # Maneja cualquier error de integridad si es necesario
                print(f"Error de integridad al crear el registro: {e}")
                ExcelDocumentLOG.objects.create(pestana=importar, codigo=numero_expediente, error=e)
        print("val_terreno actualizados exitosamente.")  
    if importar=='val_construccion':
        InmuebleValoracionConstruccion.objects.all().delete()
        ruta_archivo_excel = excel_document.excel_file.path
        datos_excel = pd.read_excel(ruta_archivo_excel, sheet_name='val_construccion')
        for index, row in datos_excel.iterrows():
            if not math.isnan(row['id_inmueble']):
                numero_expediente = int((row['id_inmueble']))
            else:
                numero_expediente = 0
            if not math.isnan(row['tipologia']):
                tipologiaId = int(row['tipologia'])
            else:
                tipologiaId = 0
            tipologia = Tipologia.objects.get(codigo=tipologiaId)
            if tipologia.descripcion=='RESIDENCIAL' :
                tipoinmuebleId=1
            if tipologia.descripcion=='COMERCIAL' :
                tipoinmuebleId=2
            if tipologia.descripcion=='INDUSTRIAL' :
                tipoinmuebleId=3
            tipoinmueble=TipoInmueble.objects.get(codigo=tipoinmuebleId)

            area = row['area']

            try:
                #print('numero_expediente',numero_expediente)
                inmueble=Inmueble.objects.get(numero_expediente=numero_expediente)
                inmueblevaloracionterreno=InmuebleValoracionTerreno.objects.get(inmueble=inmueble.id)
                try:
                    # Intenta obtener un registro existente o crear uno nuevo si no existe
                    creado = InmuebleValoracionConstruccion.objects.get_or_create(
                        inmueblevaloracionterreno=inmueblevaloracionterreno,
                        tipologia=tipologia,
                        area= area,
                        tipo=tipoinmueble,
                    )
                    if not creado:
                        print(f"El registro con código {numero_expediente} YA EXISTE y no se creó uno nuevo.")
                        ExcelDocumentLOG.objects.create(pestana=importar, codigo=numero_expediente, error=e)
                except IntegrityError as e:
                    # Maneja cualquier error de integridad si es necesario
                    print(f"Error de integridad al crear el registro: {e}")
                    ExcelDocumentLOG.objects.create(pestana=importar, codigo=numero_expediente, error=e)
            except InmuebleValoracionTerreno.DoesNotExist:
                print(f"No existe el numero de expediente {numero_expediente}")
                ExcelDocumentLOG.objects.create(pestana=importar, codigo=numero_expediente, error='No existe InmuebleValoracionTerreno')
            except Inmueble.DoesNotExist:
                print(f"No existe el INMUEBLE numero de expediente {numero_expediente}")
                ExcelDocumentLOG.objects.create(pestana=importar, codigo=numero_expediente, error='No existe INMUEBLE')
            except IntegrityError as e:
                # Maneja cualquier error de integridad si es necesario
                print(f"Error de integridad al crear el registro: {e}")
                ExcelDocumentLOG.objects.create(pestana=importar, codigo=numero_expediente, error=e)
        print("val_terreno actualizados exitosamente.")

    if importar=='val_terreno2024': 
        InmuebleValoracionTerreno2024.objects.all().delete()
        terreno = InmuebleValoracionTerreno.objects.all() #filter(tipologia__isnull=False)
        for detalle in terreno:
            try:
                numero_expediente=detalle.inmueble
                try:
                    print('detalle.tipologia',detalle.tipologia)
                    vId=detalle.tipologia.id if detalle.tipologia else 0
                    oTipologia=Tipologia.objects.get(id=vId)
                    vUso=oTipologia.descripcion
                    print('vUso',vUso)
                    vZona=oTipologia.zona.codigo
                    print('vZona',vZona)
                    print('numero_expediente',numero_expediente.numero_expediente,numero_expediente.id)
                    tipoinmuebleId=0
                    if vUso=='RESIDENCIAL' :
                        tipoinmuebleId=1
                    if vUso=='COMERCIAL' :
                        tipoinmuebleId=2
                    if vUso=='INDUSTRIAL' : 
                        tipoinmuebleId=3
                    if tipoinmuebleId!=0:
                        tipoinmueble=TipoInmueble.objects.get(codigo=tipoinmuebleId)
                    else:
                        tipoinmueble=None
                    if vZona=='1':
                        vCategoria='B'
                    if vZona=='2':
                        vCategoria='C'
                    if vZona=='3':
                        vCategoria='D'
                    if vZona=='4':
                        vCategoria='E'

                    oCategoria=Categorizacion.objects.get(codigo=vCategoria).id
                    
                    if vUso=='RESIDENCIAL' and vZona=='1':
                        vCodigo='B5'
                    if vUso=='COMERCIAL' and vZona=='1':
                        vCodigo='B6'
                    if vUso=='INDUSTRIAL' and vZona=='1':
                        vCodigo='B6'
                    if vUso=='OTROS' and vZona=='1':
                        vCodigo='B6'
                    if vUso=='ESPECIAL' and vZona=='1':
                        vCodigo='B6'

                    if vUso=='RESIDENCIAL' and vZona=='2':
                        vCodigo='C5'
                    if vUso=='COMERCIAL' and vZona=='2':
                        vCodigo='C6'
                    if vUso=='INDUSTRIAL' and vZona=='2':
                        vCodigo='C6'
                    if vUso=='OTROS' and vZona=='2':
                        vCodigo='C6'
                    if vUso=='ESPECIAL' and vZona=='2':
                        vCodigo='C6'

                    if vUso=='RESIDENCIAL' and vZona=='3':
                        vCodigo='D5'
                    if vUso=='COMERCIAL' and vZona=='3':
                        vCodigo='D6'
                    if vUso=='INDUSTRIAL' and vZona=='3':
                        vCodigo='D6'
                    if vUso=='OTROS' and vZona=='3':
                        vCodigo='D6'
                    if vUso=='ESPECIAL' and vZona=='3':
                        vCodigo='D6'

                    if vUso=='RESIDENCIAL' and vZona=='4':
                        vCodigo='E5'
                    if vUso=='COMERCIAL' and vZona=='4':
                        vCodigo='E6'
                    if vUso=='INDUSTRIAL' and vZona=='4':
                        vCodigo='E6'
                    if vUso=='OTROS' and vZona=='4':
                        vCodigo='E6'
                    if vUso=='ESPECIAL' and vZona=='4':
                        vCodigo='E6'
                    tipologia =  Tipologia_Categorizacion.objects.get(codigo=vCodigo,categorizacion=oCategoria)
                    Detalle=InmuebleValoracionTerreno2024(
                        inmueble=detalle.inmueble,
                        area = detalle.area,
                        tipologia_categorizacion = tipologia,
                        tipo=tipoinmueble,
                        aplica='T'
                    )
                    Detalle.save()
                except Tipologia.DoesNotExist:
                    InmuebleValoracionTerreno2024(inmueble=detalle.inmueble).save()
                    print(f"No existe el la tipologia , pero se creo un expediente:{numero_expediente} InmuebleValoracionTerreno2024 en blanco ")
                    ExcelDocumentLOG.objects.create(pestana=importar, codigo=numero_expediente, error='No existe Tipologia') 
            except Tipologia.DoesNotExist:
                print(f"No existe el la tipologia {vUso}")
                ExcelDocumentLOG.objects.create(pestana=importar, codigo=numero_expediente, error='No existe Tipologia') 
            except Categorizacion.DoesNotExist:
                print(f"No existe el la Categorizacion {vUso}")
                ExcelDocumentLOG.objects.create(pestana=importar, codigo=numero_expediente, error='No existe Tipologia') 
            except Tipologia_Categorizacion.DoesNotExist:
                print(f"No existe el la Tipologia_Categorizacion {vUso}")
                ExcelDocumentLOG.objects.create(pestana=importar, codigo=numero_expediente, error='No existe Tipologia_Categorizacion')           
            except IntegrityError as e:
                # Maneja cualquier error de integridad si es necesario
                print(f"Error de integridad al crear el registro: {e}")
                ExcelDocumentLOG.objects.create(pestana=importar, codigo=numero_expediente, error=e)
        print("val_terreno actualizados exitosamente.")  

    if importar=='val_construccion2024':
        InmuebleValoracionConstruccion2024.objects.all().delete()
        terreno=InmuebleValoracionConstruccion.objects.all()
        for detalle in terreno:
            try:
                numero_expediente=detalle.inmueblevaloracionterreno.inmueble
                try:
                    print('detalle.tipologia',detalle.tipologia)
                    vId=detalle.tipologia.id if detalle.tipologia else 0
                    oTipologia=Tipologia.objects.get(id=vId)
                    vUso=oTipologia.descripcion
                    print('vUso',vUso)

                    vZona=oTipologia.zona.codigo
                    print('vZona',vZona)

                    print('numero_expediente',numero_expediente.numero_expediente,numero_expediente.id)
                    tipoinmuebleId=0
                    if vUso=='RESIDENCIAL' :
                        tipoinmuebleId=1
                    if vUso=='COMERCIAL' :
                        tipoinmuebleId=2
                    if vUso=='INDUSTRIAL' : 
                        tipoinmuebleId=3
                    if tipoinmuebleId!=0:
                        tipoinmueble=TipoInmueble.objects.get(codigo=tipoinmuebleId)
                    else:
                        tipoinmueble=None

                    if vZona=='1':
                        vCategoria='B'
                    if vZona=='2':
                        vCategoria='C'
                    if vZona=='3':
                        vCategoria='D'
                    if vZona=='4':
                        vCategoria='E'
                    oCategoria=Categorizacion.objects.get(codigo=vCategoria).id
                    

                    if vUso=='RESIDENCIAL' and vZona=='1':
                        vCodigo='B1'
                    if vUso=='COMERCIAL' and vZona=='1':
                        vCodigo='B2'
                    if vUso=='INDUSTRIAL' and vZona=='1':
                        vCodigo='B3'
                    if vUso=='OTROS' and vZona=='1':
                        vCodigo='B4'
                    if vUso=='ESPECIAL' and vZona=='1':
                        vCodigo='B4'

                    if vUso=='RESIDENCIAL' and vZona=='2':
                        vCodigo='C1'
                    if vUso=='COMERCIAL' and vZona=='2':
                        vCodigo='C2'
                    if vUso=='INDUSTRIAL' and vZona=='2':
                        vCodigo='C3'
                    if vUso=='OTROS' and vZona=='2':
                        vCodigo='C4'
                    if vUso=='ESPECIAL' and vZona=='2':
                        vCodigo='C4'

                    if vUso=='RESIDENCIAL' and vZona=='3':
                        vCodigo='D1'
                    if vUso=='COMERCIAL' and vZona=='3':
                        vCodigo='D2'
                    if vUso=='INDUSTRIAL' and vZona=='3':
                        vCodigo='D3'
                    if vUso=='OTROS' and vZona=='3':
                        vCodigo='D4'
                    if vUso=='ESPECIAL' and vZona=='3':
                        vCodigo='D4'

                    if vUso=='RESIDENCIAL' and vZona=='4':
                        vCodigo='E1'
                    if vUso=='COMERCIAL' and vZona=='4':
                        vCodigo='E2'
                    if vUso=='INDUSTRIAL' and vZona=='4':
                        vCodigo='E3'
                    if vUso=='OTROS' and vZona=='4':
                        vCodigo='E4'
                    if vUso=='ESPECIAL' and vZona=='4':
                        vCodigo='E4'
                    tipologia =  Tipologia_Categorizacion.objects.get(codigo=vCodigo,categorizacion=oCategoria)
                    inmueble=Inmueble.objects.get(numero_expediente=numero_expediente.numero_expediente)
                    try:
                        inmueblevaloracionterreno=InmuebleValoracionTerreno2024.objects.get(inmueble=inmueble.id)
                        Detalle=InmuebleValoracionConstruccion2024(
                            inmueblevaloracionterreno=inmueblevaloracionterreno,
                            area = detalle.area,
                            tipologia_categorizacion = tipologia,
                            tipo=tipoinmueble,
                            aplica='C'
                        )
                        Detalle.save() 
                    except InmuebleValoracionTerreno2024.DoesNotExist:
                        print(f"No existe InmuebleValoracionTerreno2024 {numero_expediente}")
                        ExcelDocumentLOG.objects.create(pestana=importar, codigo=numero_expediente, error='No existe InmuebleValoracionTerreno2024')                       
                except Tipologia.DoesNotExist:
                    print(f"No existe el la tipologia {vUso}")
                    ExcelDocumentLOG.objects.create(pestana=importar, codigo=numero_expediente, error='No existe Tipologia') 
            except Tipologia.DoesNotExist:
                print(f"No existe el la tipologia {vUso}")
                ExcelDocumentLOG.objects.create(pestana=importar, codigo=numero_expediente, error='No existe Tipologia') 
            except Categorizacion.DoesNotExist:
                print(f"No existe el la Categorizacion {vUso}")
                ExcelDocumentLOG.objects.create(pestana=importar, codigo=numero_expediente, error='No existe Tipologia') 
            except Tipologia_Categorizacion.DoesNotExist:
                print(f"No existe el la Tipologia_Categorizacion {vUso}")
                ExcelDocumentLOG.objects.create(pestana=importar, codigo=numero_expediente, error='No existe Tipologia_Categorizacion')           
            except IntegrityError as e:
                # Maneja cualquier error de integridad si es necesario
                print(f"Error de integridad al crear el registro: {e}")
                ExcelDocumentLOG.objects.create(pestana=importar, codigo=numero_expediente, error=e)
        print("val_construccion actualizados exitosamente.")
    if importar=='tipologiaNew':

        with transaction.atomic():  # Para garantizar la atomicidad de las operaciones
            oZona=Zona.objects.get(codigo='1')
            categoria = Categorizacion.objects.get(codigo='B') 
            inmuebles_zona = Inmueble.objects.filter(zona=oZona)
            for inmueble in inmuebles_zona:
                print('expediente',inmueble.numero_expediente,inmueble.zona.codigo)
                inmueble.categorizacion = categoria
                inmueble.save()
        with transaction.atomic():  # Para garantizar la atomicidad de las operaciones
            oZona=Zona.objects.get(codigo='2')
            categoria = Categorizacion.objects.get(codigo='C') 
            inmuebles_zona = Inmueble.objects.filter(zona=oZona)
            for inmueble in inmuebles_zona:
                print('expediente',inmueble.numero_expediente,inmueble.zona.codigo)
                inmueble.categorizacion = categoria
                inmueble.save()
        with transaction.atomic():  # Para garantizar la atomicidad de las operaciones
            oZona=Zona.objects.get(codigo='3')
            categoria = Categorizacion.objects.get(codigo='D') 
            inmuebles_zona = Inmueble.objects.filter(zona=oZona)
            for inmueble in inmuebles_zona:
                print('expediente',inmueble.numero_expediente,inmueble.zona.codigo)
                inmueble.categorizacion = categoria
                inmueble.save()
        with transaction.atomic():  # Para garantizar la atomicidad de las operaciones
            oZona=Zona.objects.get(codigo='4')
            categoria = Categorizacion.objects.get(codigo='E') 
            inmuebles_zona = Inmueble.objects.filter(zona=oZona)
            for inmueble in inmuebles_zona:
                print('expediente',inmueble.numero_expediente,inmueble.zona.codigo)
                inmueble.categorizacion = categoria
                inmueble.save()
        with transaction.atomic():  # Para garantizar la atomicidad de las operaciones
            oZona=Zona.objects.get(codigo='5')
            categoria = Categorizacion.objects.get(codigo='X') 
            inmuebles_zona = Inmueble.objects.filter(zona=oZona)
            for inmueble in inmuebles_zona:
                print('expediente',inmueble.numero_expediente,inmueble.zona.codigo)
                inmueble.categorizacion = categoria
                inmueble.save()
        with transaction.atomic():  # Para garantizar la atomicidad de las operaciones
            oZona=Zona.objects.get(codigo='99')
            categoria = Categorizacion.objects.get(codigo='X') 
            inmuebles_zona = Inmueble.objects.filter(zona=oZona)
            for inmueble in inmuebles_zona:
                print('expediente',inmueble.numero_expediente,inmueble.zona.codigo)
                inmueble.categorizacion = categoria
                inmueble.save()              
        print("tipologiaNew actualizados exitosamente.")
   
#***************************************************************************************** CorridaBancaria.xlsx
    if importar=='cien':
        ruta_archivo_excel = excel_document.excel_file.path
        datos_excel = pd.read_excel(ruta_archivo_excel, sheet_name='cien')
        for index, row in datos_excel.iterrows():
            bancocuenta = BancoCuenta.objects.get(codigocuenta='12')
            fecha = row['Fecha']
            referencia = row['Referencia']
            descripcion = row['Descripción']           
            monto = row['Monto']
            try:
                if isinstance(monto, str):
                    monto = float(monto.replace(',', ''))  # Intenta convertir la cadena a float
            except (ValueError, TypeError):
                monto = 0.0  # Si la conversión falla, asigna 0.0

            if math.isnan(monto):
                monto = 0.0

            if row['Tipo']=='T':
                situado = 'T'
            else:
                situado = 'D'
            situado = 'T' 
            if row['Situado']=='R':
                situado = 'R'
            if row['Situado']=='N':
                situado = 'N'
            try:
                # Intenta obtener un registro existente o crear uno nuevo si no existe
                corridabancaria, creado = CorridasBancarias.objects.get_or_create(
                    bancocuenta=bancocuenta,
                    fecha=fecha,
                    referencia=referencia,
                    descripcion=descripcion,
                    monto=monto, 
                    defaults={
                        'situado': situado,
                    }
                )
                if not creado:
                    print(f"El registro con anio {referencia} y mes {monto} ya existe y no se creó uno nuevo.")
                    
            except IntegrityError as e:
                # Maneja cualquier error de integridad si es necesario
                print(f"Error de integridad al crear el registro: {e}")
                ExcelDocumentLOG.objects.create(pestana=importar, codigo=referencia, error=e)
            # Crea un nuevo objeto TasaInteres y guárdalo en la base de datos
            #TasaInteres.objects.create(anio=anio, mes=mes, tasa=tasa)
        print("Datos importados exitosamente.")   
    if importar=='bancaribe':
        # este banco NO tiene nombre de columnas y se lee  apartir de la linea 2
        ruta_archivo_excel = excel_document.excel_file.path
        datos_excel = pd.read_excel(ruta_archivo_excel, sheet_name='bancaribe')
        for index, row in datos_excel.iterrows():
            bancocuenta = BancoCuenta.objects.get(codigocuenta='17')
            fecha = row['Fecha']
            referencia = row['Referencia']
            descripcion = row['Descripción']           
            monto = row['Monto']
            try:
                if isinstance(monto, str):
                    monto = float(monto.replace(',', ''))  # Intenta convertir la cadena a float
            except (ValueError, TypeError):
                monto = 0.0  # Si la conversión falla, asigna 0.0

            if math.isnan(monto):
                monto = 0.0
            if row['Tipo']=='T':
                situado = 'T'
            else:
                situado = 'D'
            situado = 'T' 
            if row['Situado']=='R':
                situado = 'R'
            if row['Situado']=='N':
                situado = 'N'
            try:
                # Intenta obtener un registro existente o crear uno nuevo si no existe
                corridabancaria,creado = CorridasBancarias.objects.get_or_create(
                    bancocuenta=bancocuenta,
                    fecha=fecha,
                    referencia=referencia,
                    descripcion=descripcion,
                    monto=monto, 
                    defaults={
                        'situado': situado,
                    }
                )
                if not creado:
                    print(f"El registro con referencia {referencia} y monto {monto} ya existe y no se creó uno nuevo.")
                    
            except IntegrityError as e:
                # Maneja cualquier error de integridad si es necesario
                print(f"Error de integridad al crear el registro: {e}")
                ExcelDocumentLOG.objects.create(pestana=importar, codigo=referencia, error=e)
        print("Datos importados exitosamente.")
    if importar=='banesco':
        ruta_archivo_excel = excel_document.excel_file.path
        datos_excel = pd.read_excel(ruta_archivo_excel, sheet_name='banesco')
        filas_filtradas = datos_excel[datos_excel['Descripción'].str.contains("TRF")] # solo carga las transferencias

        for index, row in filas_filtradas.iterrows():
            bancocuenta = BancoCuenta.objects.get(codigocuenta='16')
            fecha = row['Fecha']
            referencia = row['Referencia']
            descripcion = row['Descripción']           
            monto = row['Monto']
            try:
                if isinstance(monto, str):
                    monto = float(monto.replace(',', ''))  # Intenta convertir la cadena a float
            except (ValueError, TypeError):
                monto = 0.0  # Si la conversión falla, asigna 0.0

            if math.isnan(monto):
                monto = 0.0
            if row['Tipo']=='T':
                situado = 'T'
            else:
                situado = 'D'
            situado = 'T' 
            if row['Situado']=='R':
                situado = 'R'
            if row['Situado']=='N':
                situado = 'N'
            try:
                # Intenta obtener un registro existente o crear uno nuevo si no existe
                corridabancaria, creado = CorridasBancarias.objects.get_or_create(
                    bancocuenta=bancocuenta,
                    fecha=fecha,
                    referencia=referencia,
                    descripcion=descripcion,
                    monto=monto, 
                    defaults={
                        'situado': situado,
                    }
                )
                if not creado:
                    print(f"El registro con referencia {referencia} y monto {monto} ya existe y no se creó uno nuevo.")
                    
            except IntegrityError as e:
                # Maneja cualquier error de integridad si es necesario
                print(f"Error de integridad al crear el registro: {e}")
                ExcelDocumentLOG.objects.create(pestana=importar, codigo=referencia, error=e)
            # Crea un nuevo objeto TasaInteres y guárdalo en la base de datos
            #TasaInteres.objects.create(anio=anio, mes=mes, tasa=tasa)
        print("Datos importados exitosamente.")
    if importar=='bfc':
        ruta_archivo_excel = excel_document.excel_file.path
        datos_excel = pd.read_excel(ruta_archivo_excel, sheet_name='bfc')
        filas_filtradas = datos_excel[~datos_excel['Descripción'].str.contains("AB.LOTE")] # esos son puntos de venta, se excluyen
        for index, row in filas_filtradas.iterrows():
            bancocuenta = BancoCuenta.objects.get(codigocuenta='3')
            fecha = row['Fecha']
            fecha_obj = datetime.strptime(fecha, "%d/%m/%Y")  # Convierte al formato "YYYY-MM-DD"
            fecha_formateada = fecha_obj.strftime("%Y-%m-%d")  # Formatea como "YYYY-MM-DD"
            referencia = row['Referencia']
            descripcion = row['Descripción']           
            monto = row['Monto']
            try:
                if isinstance(monto, str):
                    monto = float(monto.replace('.', '').replace(',', '.'))  # Intenta convertir la cadena a float
            except (ValueError, TypeError):
                monto = 0.0  # Si la conversión falla, asigna 0.0

            if math.isnan(monto):
                monto = 0.0
            if row['Tipo']=='T':
                situado = 'T'
            else:
                situado = 'D'
            situado = 'T' 
            if row['Situado']=='R':
                situado = 'R'
            if row['Situado']=='N':
                situado = 'N'
            try:
                # Intenta obtener un registro existente o crear uno nuevo si no existe
                corridabancaria, creado = CorridasBancarias.objects.get_or_create(
                    bancocuenta=bancocuenta,
                    fecha=fecha_formateada,
                    referencia=referencia,
                    descripcion=descripcion,
                    monto=monto, 
                    defaults={
                        'situado': situado,
                    }
                )
                if not creado:
                    print(f"El registro con referencia {referencia} y monto {monto} ya existe y no se creó uno nuevo.")
                    
            except IntegrityError as e:
                # Maneja cualquier error de integridad si es necesario
                print(f"Error de integridad al crear el registro: {e}")
                ExcelDocumentLOG.objects.create(pestana=importar, codigo=referencia, error=e)
            # Crea un nuevo objeto TasaInteres y guárdalo en la base de datos
            #TasaInteres.objects.create(anio=anio, mes=mes, tasa=tasa)
        print("Datos importados exitosamente.")
    if importar=='bnc':
        ruta_archivo_excel = excel_document.excel_file.path
        datos_excel = pd.read_excel(ruta_archivo_excel, sheet_name='bnc')
        for index, row in datos_excel.iterrows():
            bancocuenta = BancoCuenta.objects.get(codigocuenta='51')
            fecha = row['Fecha']
            fecha_obj = datetime.strptime(fecha, "%d/%m/%Y")  # Convierte al formato "YYYY-MM-DD"
            fecha_formateada = fecha_obj.strftime("%Y-%m-%d")  # Formatea como "YYYY-MM-DD"
            referencia = row['Referencia']
            descripcion = row['Descripción']           
            monto = row['Monto']
            try:
                if isinstance(monto, str):
                    monto = float(monto.replace('.', '').replace(',', '.'))  # Intenta convertir la cadena a float
            except (ValueError, TypeError):
                monto = 0.0  # Si la conversión falla, asigna 0.0

            if math.isnan(monto):
                monto = 0.0
            if row['Tipo']=='T':
                situado = 'T'
            else:
                situado = 'D'
            situado = 'T' 
            if row['Situado']=='R':
                situado = 'R'
            if row['Situado']=='N':
                situado = 'N'
            try:
                # Intenta obtener un registro existente o crear uno nuevo si no existe
                corridabancaria, creado = CorridasBancarias.objects.get_or_create(
                    bancocuenta=bancocuenta,
                    fecha=fecha_formateada,
                    referencia=referencia,
                    descripcion=descripcion,
                    monto=monto, 
                    defaults={
                        'situado': situado,
                    }
                )
                if not creado:
                    print(f"El registro con referencia {referencia} y monto {monto} ya existe y no se creó uno nuevo.")
                    
            except IntegrityError as e:
                # Maneja cualquier error de integridad si es necesario
                print(f"Error de integridad al crear el registro: {e}")
                ExcelDocumentLOG.objects.create(pestana=importar, codigo=referencia, error=e)
            # Crea un nuevo objeto TasaInteres y guárdalo en la base de datos
            #TasaInteres.objects.create(anio=anio, mes=mes, tasa=tasa)
        print("Datos importados exitosamente.")
    if importar=='venezuela':
        ruta_archivo_excel = excel_document.excel_file.path
        datos_excel = pd.read_excel(ruta_archivo_excel, sheet_name='venezuela')
        for index, row in datos_excel.iterrows():
            bancocuenta = BancoCuenta.objects.get(codigocuenta='50')
            fecha = row['Fecha']
            fecha_obj = datetime.strptime(fecha, "%d/%m/%Y")  # Convierte al formato "YYYY-MM-DD"
            fecha_formateada = fecha_obj.strftime("%Y-%m-%d")  # Formatea como "YYYY-MM-DD"
            referencia = row['Referencia']
            if 'Descripción' in datos_excel.columns:
                descripcion = row['Descripción'] 
            if 'concepto' in datos_excel.columns:
                descripcion = row['concepto'] 
            if 'Monto' in datos_excel.columns:     
                monto = row['Monto']
            if 'importe' in datos_excel.columns:     
                monto = row['importe']

            try:
                if isinstance(monto, str):
                    monto = float(monto.replace('.', '').replace(',', '.'))  # Intenta convertir la cadena a float
            except (ValueError, TypeError):
                monto = 0.0  # Si la conversión falla, asigna 0.0

            if math.isnan(monto):
                monto = 0.0
            if row['Tipo']=='T':
                situado = 'T'
            else:
                situado = 'D'
            situado = 'T' 
            if row['Situado']=='R':
                situado = 'R'
            if row['Situado']=='N':
                situado = 'N'
            try:
                # Intenta obtener un registro existente o crear uno nuevo si no existe
                corridabancaria, creado = CorridasBancarias.objects.get_or_create(
                    bancocuenta=bancocuenta,
                    fecha=fecha_formateada,
                    referencia=referencia,
                    descripcion=descripcion,
                    monto=monto, 
                    defaults={
                        'situado': situado,
                    }
                )
                if not creado:
                    print(f"El registro con referencia {referencia} y monto {monto} ya existe y no se creó uno nuevo.")
                    
            except IntegrityError as e:
                # Maneja cualquier error de integridad si es necesario
                print(f"Error de integridad al crear el registro: {e}")
                ExcelDocumentLOG.objects.create(pestana=importar, codigo=referencia, error=e)
            # Crea un nuevo objeto TasaInteres y guárdalo en la base de datos
            #TasaInteres.objects.create(anio=anio, mes=mes, tasa=tasa)
        print("Datos importados exitosamente.")
    return Response('Datos importados exitosamente.',status=status.HTTP_200_OK) 

def importar_datos_desde_excel_old(archivo,pestana):
    print('Backend procesando: ',pestana)
    importar=pestana
    ExcelDocumentLOG.objects.filter(codigo=importar).delete()
    excel_document=ExcelDocument.objects.get(title=archivo)
    if importar=='inicio':
        # asignar al control de correlativos el ultimo numero de expediemte importado
        max_numero_expediente = Inmueble.objects.exclude(numero_expediente__isnull=True).exclude(numero_expediente='').filter(numero_expediente__regex=r'^\d+$').aggregate(max_numero_expediente=Max('numero_expediente'))['max_numero_expediente']

        print(max_numero_expediente)
        correlativo=Correlativo.objects.get(id=1)
        correlativo.ExpedienteCatastro=int(max_numero_expediente)+1
        correlativo.save()           
    if importar=='vaciar':
        NotaCredito.objects.all().delete()
        print('NotaCredito')
        AE_Patente.objects.all().delete()
        print('AE_Patente') 
        FlujoDetalle.objects.all().delete()
        print('FlujoDetalle')
        Flujo.objects.all().delete()
        print('Flujo')
        PagoEstadoCuentaDetalle.objects.all().delete()
        print('PagoEstadoCuentaDetalle')
        PagoEstadoCuenta.objects.all().delete()
        print('PagoEstadoCuenta')
        LiquidacionDetalle.objects.all().delete()
        print('LiquidacionDetalle')
        Liquidacion.objects.all().delete()
        print('Liquidacion')
        EstadoCuentaDetalle.objects.all().delete()
        print('EstadoCuentaDetalle')
        EstadoCuenta.objects.all().delete()
        print('EstadoCuenta')
        InmueblePropietarios.objects.all().delete()
        print('InmueblePropietarios')
        Propietario.objects.all().delete()
        print('Propietario')
        ################ eliminar inmueble inicio
        IC_ImpuestoPeriodo.objects.all().delete()
        print('IC_ImpuestoPeriodo')
        InmueblePropiedad.objects.all().delete()
        print('InmueblePropiedad')
        InmuebleConstruccion.objects.all().delete()
        print('InmuebleConstruccion')
        InmuebleFaltante.objects.all().delete()
        print('InmuebleFaltante')
        InmuebleTerrenoUso.objects.all().delete()
        print('InmuebleTerrenoUso')
        InmuebleTerreno.objects.all().delete()
        print('InmuebleTerreno')
        InmuebleUbicacion.objects.all().delete()
        print('InmuebleUbicacion')
        InmuebleValoracionConstruccion.objects.all().delete()
        print('InmuebleValoracionConstruccion')
        InmuebleValoracionTerreno.objects.all().delete()
        print('InmuebleValoracionTerreno')
        Inmueble.objects.all().delete()
        print('Inmueble')       
        ################# fin
        #SubParcela.objects.all().delete()
        #Parcela.objects.all().delete() 
        #Manzana.objects.all().delete() 
        #Calle.objects.all().delete()
        #Avenida.objects.all().delete()
        #Torre.objects.all().delete()
        #Edificio.objects.all().delete()
        #ConjuntoResidencial.objects.all().delete()
        #Urbanizacion.objects.all().delete()
        #Sector.objects.all().delete() 
        #Ambito.objects.all().delete()
        #ExcelDocumentLOG.objects.all().delete()
    if importar=='tasas':
        # esto se cambia porque hay problemas al acesar al archivo en fisico, se cambia para que se cargue en un modelo.
        # tambien sa debe colocar en elmismo excel pero otra pestaña.
        #ruta_archivo_excel = os.path.join('media', 'archivos_excel/tasa.xlsx')
        #datos_excel = pd.read_excel(ruta_archivo_excel)
        ruta_archivo_excel = excel_document.excel_file.path
        datos_excel = pd.read_excel(ruta_archivo_excel, sheet_name='tasa_interes')
        for index, row in datos_excel.iterrows():
            anio = row['anio']
            mes = row['mes']
            tasa = row['tasa']
            try:
                # Intenta obtener un registro existente o crear uno nuevo si no existe
                creado = TasaInteres.objects.get_or_create(
                    defaults={
                        'anio' : anio,
                        'mes'  : mes,
                        'tasa' : tasa,
                    }
                )
                if not creado:
                    print(f"El registro con anio {anio} y mes {mes} ya existe y no se creó uno nuevo.")
                    
            except IntegrityError as e:
                # Maneja cualquier error de integridad si es necesario
                print(f"Error de integridad al crear el registro: {e}")
                ExcelDocumentLOG.objects.create(pestana=importar, codigo=mes, error=e)
            # Crea un nuevo objeto TasaInteres y guárdalo en la base de datos
            #TasaInteres.objects.create(anio=anio, mes=mes, tasa=tasa)
        print("Datos importados exitosamente.")
    if importar=='ambito':
        # metodo anterior que se leia desde un directorio, se cambia por metodo de lectura desde la carga en un modelo ya,
        # que falla cuando se puclica en nube, lovcal si funciona
        #ruta_archivo_excel = os.path.join('media', 'archivos_excel/maestros_dir_estructurada.xlsx')
        #datos_excel = pd.read_excel(ruta_archivo_excel, sheet_name='ambito')
        ruta_archivo_excel = excel_document.excel_file.path
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
                ExcelDocumentLOG.objects.create(pestana=importar, codigo=codigo, error=e)
        print("Ambito importados exitosamente.")
    if importar=='sector':
        #ruta_archivo_excel = os.path.join('media', 'archivos_excel/maestros_dir_estructurada.xlsx')
        ruta_archivo_excel = excel_document.excel_file.path
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
                ExcelDocumentLOG.objects.create(pestana=importar, codigo=codigo, error=e)
        print("Sector importados exitosamente.")  
    if importar=='manzana':
        #ruta_archivo_excel = os.path.join('media', 'archivos_excel/maestros_dir_estructurada.xlsx')
        ruta_archivo_excel = excel_document.excel_file.path
        datos_excel = pd.read_excel(ruta_archivo_excel, sheet_name='manzana')
        for index, row in datos_excel.iterrows():
            ambito=Ambito.objects.get(codigo=row['id_ambito']) # integridad con ambito
            sector=Sector.objects.get(codigo=row['id_sector'],ambito=ambito) # integridad con ambito
            codigo = row['id_manzana']
            area = row['area'] if not math.isnan(row['area']) else Decimal('0')
            perimetro = row['perimetro'] if not math.isnan(row['perimetro']) else Decimal('0')
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
                ExcelDocumentLOG.objects.create(pestana=importar, codigo=codigo, error=e)
        print("manzana importados exitosamente.")
    if importar=='parcela':
        #ruta_archivo_excel = os.path.join('media', 'archivos_excel/maestros_dir_estructurada.xlsx')
        ruta_archivo_excel = excel_document.excel_file.path
        datos_excel = pd.read_excel(ruta_archivo_excel, sheet_name='parcela')
        for index, row in datos_excel.iterrows():
            ambito=Ambito.objects.get(codigo=row['id_ambito']) # integridad con ambito
            sector=Sector.objects.get(codigo=row['id_sector'],ambito=ambito) # integridad con sector
            manzana=Manzana.objects.get(codigo=row['id_manzana'],sector=sector) # integridad con manzana
            codigo = row['id_parcela']
            area = row['area'] if not math.isnan(row['area']) else Decimal('0')
            perimetro = row['perimetro'] if not math.isnan(row['perimetro']) else Decimal('0')
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
                ExcelDocumentLOG.objects.create(pestana=importar, codigo=codigo, error=e)
        print("parcela importados exitosamente.")  
    if importar=='sub-parcela':
        #ruta_archivo_excel = os.path.join('media', 'archivos_excel/maestros_dir_estructurada.xlsx')
        ruta_archivo_excel = excel_document.excel_file.path
        datos_excel = pd.read_excel(ruta_archivo_excel, sheet_name='sub_parcela')
        for index, row in datos_excel.iterrows():
            ambito=Ambito.objects.get(codigo=row['id_ambito']) # integridad con ambito
            sector=Sector.objects.get(codigo=row['id_sector'],ambito=ambito) # integridad con sector
            manzana=Manzana.objects.get(codigo=row['id_manzana'],sector=sector) # integridad con manzana
            parcela=Parcela.objects.get(codigo=row['id_parcela'],manzana=manzana) # integridad con parcela
            codigo = row['id_sub_parcela']
            area = row['area'] if not math.isnan(row['area']) else Decimal('0')
            perimetro = row['perimetro'] if not math.isnan(row['perimetro']) else Decimal('0')
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
                ExcelDocumentLOG.objects.create(pestana=importar, codigo=codigo, error=e)
        print("SubParcela importados exitosamente.")  
    if importar=='barrios': #Urbanizacion
        #ruta_archivo_excel = os.path.join('media', 'archivos_excel/maestros_dir_estructurada.xlsx')
        ruta_archivo_excel = excel_document.excel_file.path
        datos_excel = pd.read_excel(ruta_archivo_excel, sheet_name='barrioss')
        for index, row in datos_excel.iterrows():
            ambito=Ambito.objects.get(codigo=row['id_ambito']) # integridad con ambito
            sector=Sector.objects.get(codigo=row['id_sector'],ambito=ambito) # integridad con ambito
            codigo = row['id_urb_barrio']
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
                ExcelDocumentLOG.objects.create(pestana=importar, codigo=codigo, error=e)
        print("barrios importados exitosamente.")
    if importar=='contribuyente':
        #ruta_archivo_excel = os.path.join('media', 'archivos_excel/maestros_dir_estructurada.xlsx')
        ruta_archivo_excel = excel_document.excel_file.path
        datos_excel = pd.read_excel(ruta_archivo_excel, sheet_name='persona')
        for index, row in datos_excel.iterrows():
            numero_documento = row['id_persona']
            nombre = row['nombre']
            telefono_principal = row['telefono']
            direccion = row['direccion']
            #telefono_secundario = row['fax']
            email_principal = row['correo']
            #emaill_secundario = row['correo2']
            try:
                # Intenta obtener un registro existente o crear uno nuevo si no existe
                creado = Propietario.objects.get_or_create(
                    numero_documento=numero_documento,
                    defaults={
                        'nombre': nombre,
                        'telefono_principal':telefono_principal,
                        'direccion':direccion,
                        #'telefono_secundario':telefono_secundario,
                        'email_principal':email_principal,
                        #'emaill_secundario':emaill_secundario,
                    }
                )
                if not creado:
                    print(f"El registro con código {numero_documento} ya existe y no se creó uno nuevo.")
            except IntegrityError as e:
                # Maneja cualquier error de integridad si es necesario
                print(f"Error de integridad al crear el registro: {e}")
                ExcelDocumentLOG.objects.create(pestana=importar, codigo=codigo, error=e)
        print("Persona/contribuyente importados exitosamente.")
    if importar=='conj_resinden':
        #ruta_archivo_excel = os.path.join('media', 'archivos_excel/maestros_dir_estructurada.xlsx')
        ruta_archivo_excel = excel_document.excel_file.path
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
                ExcelDocumentLOG.objects.create(pestana=importar, codigo=numero_documento, error=e)
        print("conj_resinden importados exitosamente.")
    if importar=='edificio':
        #ruta_archivo_excel = os.path.join('media', 'archivos_excel/maestros_dir_estructurada.xlsx')
        ruta_archivo_excel = excel_document.excel_file.path
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
                    ExcelDocumentLOG.objects.create(pestana=importar, codigo=codigo, error=e)
            except ConjuntoResidencial.DoesNotExist:
                print("Conjunto residencial  no existe.")
        print("edificio importados exitosamente.")
    if importar=='torre':
        #ruta_archivo_excel = os.path.join('media', 'archivos_excel/maestros_dir_estructurada.xlsx')
        ruta_archivo_excel = excel_document.excel_file.path
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
                    ExcelDocumentLOG.objects.create(pestana=importar, codigo=codigo, error=e)
            except ConjuntoResidencial.DoesNotExist:
                print("Conjunto residencial  no existe.")
        print("Torre importados exitosamente.")
    if importar=='avenida':
        #ruta_archivo_excel = os.path.join('media', 'archivos_excel/maestros_dir_estructurada.xlsx')
        ruta_archivo_excel = excel_document.excel_file.path
        datos_excel = pd.read_excel(ruta_archivo_excel, sheet_name='avenida')
        for index,row in datos_excel.iterrows():
            codigo = row['id_avenida']
            nombre = row['nombre']
            tipo = int(row['id_tipo_avenida'])
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
                ExcelDocumentLOG.objects.create(pestana=importar, codigo=codigo, error=e)
        print("avenida importados exitosamente.")
    if importar=='calle':
        #ruta_archivo_excel = os.path.join('media', 'archivos_excel/maestros_dir_estructurada.xlsx')
        ruta_archivo_excel = excel_document.excel_file.path
        datos_excel = pd.read_excel(ruta_archivo_excel, sheet_name='via')
        for index,row in datos_excel.iterrows():
            codigo = row['id_via']
            nombre = row['nombre']
            tipo = int(row['id_tipo_via'])
            try:
                # Intenta obtener un registro existente o crear uno nuevo si no existe
                creado = Calle.objects.get_or_create(
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
                ExcelDocumentLOG.objects.create(pestana=importar, codigo=codigo, error=e)
        print("calle importados exitosamente.")
    if importar=='inmueble':
        #ruta_archivo_excel = os.path.join('media', 'archivos_excel/maestros_dir_estructurada.xlsx')
        ruta_archivo_excel = excel_document.excel_file.path
        datos_excel = pd.read_excel(ruta_archivo_excel, sheet_name='inmueble')
        for index, row in datos_excel.iterrows():
            strZona= row['id_zona2004']
            if not math.isnan(strZona):
                parte_entera = int(strZona)
            else:
                parte_entera = 99

            if  len(str(row['id_inmueble']))<6 and row['id_inmueble'] !=0: 
                #print(int(row['id_urb_barrio']) if not math.isnan(row['id_urb_barrio']) else '',int(row['id_conj_residencial']) if not math.isnan(row['id_conj_residencial']) else '')

                try:
                    zona=Zona.objects.get(codigo=parte_entera) # integridad con zona
                    try:
                        ambito=Ambito.objects.get(codigo=row['id_ambito']) # integridad con ambito
                    except Ambito.DoesNotExist:
                        ambito=None
                    try:
                        sector=Sector.objects.get(codigo=int(row['id_sector']) if not math.isnan(row['id_sector']) else '',ambito=ambito) # integridad con sector 
                    except Sector.DoesNotExist:
                        sector=None
                    try:
                        manzana=Manzana.objects.get(codigo=int(row['id_manzana']) if not math.isnan(row['id_manzana']) else '',sector=sector) # integridad con manzana
                    except Manzana.DoesNotExist:
                        manzana=None
                    try:
                        parcela=Parcela.objects.get(codigo=int(row['id_parcela']) if not math.isnan(row['id_parcela']) else '' ,manzana=manzana) # integridad con parcela
                    except Parcela.DoesNotExist:
                        parcela=None
                    try:
                        subparcela=SubParcela.objects.get(codigo=int(row['id_sub_parcela']) if not math.isnan(row['id_sub_parcela']) else '' ,parcela=parcela) # integridad con sector
                    except SubParcela.DoesNotExist:
                        subparcela=None
                    try:
                        id_urb_barrio = row['id_urb_barrio']

                        # Comprobar si id_urb_barrio es numérico y no es NaN
                        if isinstance(id_urb_barrio, (int, float)) and not math.isnan(id_urb_barrio):
                            id_urb_barrio = int(id_urb_barrio)
                        else:
                            id_urb_barrio = None  # O puedes asignar otro valor predeterminado si es apropiado


                        urbanizacion=Urbanizacion.objects.get(codigo= id_urb_barrio,sector=sector) # integridad con sector
                    except Urbanizacion.DoesNotExist:
                        urbanizacion=None
                    try:
                        conjunto_residencial=ConjuntoResidencial.objects.get(codigo=int(row['id_conj_residencial']) if not math.isnan(row['id_conj_residencial']) else '' ) # integridad con conjunto_residencial
                    except ConjuntoResidencial.DoesNotExist:
                        conjunto_residencial=None
                    ## ojo le quito el fltro de urbanizacion porque no esab bien el dato en la hoja de inmuebles

                    try:
                        edificio=Edificio.objects.get(codigo=int(row['id_edificio']) if not math.isnan(row['id_edificio']) else ' ' ,conjuntoresidencial=conjunto_residencial) # integridad con sector
                    except Edificio.DoesNotExist:
                        edificio=None
                    try:
                        torre=Torre.objects.get(codigo=int(row['id_torre']) if not math.isnan(row['id_torre']) else ' ' , conjuntoresidencial=conjunto_residencial) # integridad con sector
                    except Torre.DoesNotExist:
                        torre=None
                    try:
                        avenida=Avenida.objects.get(codigo= int(row['id_avenida']) if not math.isnan(row['id_avenida']) else '') # integridad con sector
                    except Avenida.DoesNotExist:
                        avenida=None
                    numero_expediente = row['id_inmueble']
                    fecha_inscripcion = row['fecha_inscripcion']

                    if isinstance(fecha_inscripcion, str) and len(fecha_inscripcion) > 0:
                    # Cadena de fecha y hora en el formato original
                        cadena_fecha_hora = row['fecha_inscripcion']

                        # Extrae la parte de la cadena que contiene la fecha
                        partes = cadena_fecha_hora.split(' ')
                        fecha_original = partes[0]
                    else:
                        fecha_original=None

                    try:
                        # Intenta obtener un registro existente o crear uno nuevo si no existe
                        inmueble, creado = Inmueble.objects.get_or_create(
                            numero_expediente=numero_expediente,
                            ambito=ambito, 
                            sector=sector,
                            manzana=manzana,
                            parcela=parcela,
                            subparcela=subparcela,
                            urbanizacion=urbanizacion,
                            conjunto_residencial=conjunto_residencial,
                            edificio=edificio,
                            torre=torre,
                            avenida=avenida,
                            defaults={
                                'fecha_inscripcion':fecha_original,
                                'zona': zona,
                                'numero_piso':row['piso'],
                                'numero_civico':row['nro_civico'],
                                'referencia':row['referencia'],
                                'observaciones':row['observaciones'],
                                'direccion':row['direccion'],
                                'telefono':row['telefono'],
                            }
                        )
                        InmueblePropiedad(inmueble=inmueble).save()
                        InmuebleTerreno(inmueble=inmueble).save()
                        InmuebleConstruccion(inmueble=inmueble).save()
                        InmuebleValoracionTerreno(inmueble=inmueble).save()
                        InmuebleUbicacion(inmueble=inmueble).save()
                        InmuebleFaltante(inmueble=inmueble).save()
                        if not creado:
                            print(f"El registro con código {numero_expediente} ya existe y no se creó uno nuevo.")
                            ExcelDocumentLOG.objects.create(pestana=importar, codigo=numero_expediente, error='Expediente ya existe.')
                        #else:
                            #print(f"El registro con código {numero_expediente} SE CREO.")
                            #response_data = {
                            #    'id': numero_expediente
                            #}

                            ## Devolver la respuesta como JSON
                            ##return JsonResponse(response_data)
                            

                    except IntegrityError as e:
                        # Maneja cualquier error de integridad si es necesario
                        print(f"Error de integridad al crear el registro: {e}")
                        ExcelDocumentLOG.objects.create(pestana=importar, codigo=numero_expediente, error=e)
                except Zona.DoesNotExist:
                    print("Zona no existe.")
                    ExcelDocumentLOG.objects.create(pestana=importar, codigo=numero_expediente, error="Zona no existe.")
                except Ambito.DoesNotExist:
                    print("Ambito no existe.")
                except Sector.DoesNotExist:
                    print("Sector no existe.")
                except Manzana.DoesNotExist:
                    print("Manzana no existe.")
                except Parcela.DoesNotExist:
                    print("Parcela no existe.")
                except SubParcela.DoesNotExist:
                    print("SubParcela no existe.")                   
                except Urbanizacion.DoesNotExist:
                    print("Urbanizacion no existe.")
                except ConjuntoResidencial.DoesNotExist:
                    print("ConjuntoResidencial no existe.")
                except Edificio.DoesNotExist:
                    print("Edificio no existe.")
                except Torre.DoesNotExist:
                    print("Torre no existe.")
                except Avenida.DoesNotExist:
                    print("Avenida no existe.")
        # asignar al control de correlativos el ultimo numero de expediemte importado
        #max_numero_expediente = Inmueble.objects.all().aggregate(max_numero_expediente=Max('numero_expediente'))['max_numero_expediente']
        #correlativo=Correlativo.objects.get(id=1)
        #correlativo.ExpedienteCatastro=int(max_numero_expediente)+1
        #correlativo.save()
        print("inmueble importados exitosamente.")
    if importar=='propietario':
        #ruta_archivo_excel = os.path.join('media', 'archivos_excel/maestros_dir_estructurada.xlsx')
        ruta_archivo_excel = excel_document.excel_file.path
        datos_excel = pd.read_excel(ruta_archivo_excel, sheet_name='propietario')
        for index, row in datos_excel.iterrows():
            if  len(str(row['id_inmueble']))<6: 
                try:
                    inmueble=Inmueble.objects.get(numero_expediente=row['id_inmueble']) # integridad con inmueble
                    propietario=Propietario.objects.get(numero_documento=row['id_persona']) # integridad con propietario
                    try:
                        # Intenta obtener un registro existente o crear uno nuevo si no existe
                        creado = InmueblePropietarios.objects.get_or_create(
                            inmueble=inmueble,
                            propietario=propietario,
                            defaults={
                                'fecha_compra': inmueble.fecha_inscripcion,
                            }
                        )
                        if not creado:
                            print(f"El registro con código {inmueble} ya existe y no se creó uno nuevo.")
                        else:
                            print(f"El registro con código {inmueble} SE CREO.")

                    except IntegrityError as e:
                        # Maneja cualquier error de integridad si es necesario
                        print(f"Error de integridad al crear el registro: {e}")
                        ExcelDocumentLOG.objects.create(pestana=importar, codigo=inmueble, error=e)
                except Inmueble.DoesNotExist:
                    print("Inmueble no existe.")
                    ExcelDocumentLOG.objects.create(pestana=importar, codigo=row['id_inmueble'], error="Inmueble no existe.")
                except Propietario.DoesNotExist:
                    print("Propietario no existe.")
                    ExcelDocumentLOG.objects.create(pestana=importar, codigo=row['id_persona'], error="Propietario no existe.")

        print("propietario importados exitosamente.")
    if importar=='ult_pago':
        periodoId=0
        ruta_archivo_excel = excel_document.excel_file.path
        datos_excel = pd.read_excel(ruta_archivo_excel, sheet_name='ult_pago')
        for index, row in datos_excel.iterrows():
            today = date.today()
            if not math.isnan(row['expediente']):
                numero_expediente = int((row['expediente']))
            else:
                numero_expediente = 0
            anio = int((row['age']))
            periodoId = int((row['mes']))
            if periodoId==4:
                periodoId=1
                anio=anio+1
            else:
                periodoId=periodoId+1
            try:
                periodo=IC_Periodo.objects.get(periodo=periodoId,aplica='C')
                inmueble=Inmueble.objects.get(numero_expediente=numero_expediente)
                print('anio',anio,'periodo',periodo)
                inmueble.anio=anio
                inmueble.periodo=periodo
                inmueble.save()
                #response_data = {
                #    'id': numero_expediente
                #}

                ## Devolver la respuesta como JSON
                #return JsonResponse(response_data)

            except Inmueble.DoesNotExist:
                print(f"No existe el numero de expediente {numero_expediente}")
                ExcelDocumentLOG.objects.create(pestana=importar, codigo=numero_expediente, error='No existe expediente')
            except IntegrityError as e:
                # Maneja cualquier error de integridad si es necesario
                print(f"Error de integridad al crear el registro: {e}")
                ExcelDocumentLOG.objects.create(pestana=importar, codigo=numero_expediente, error=e)
        print("Ultimo pagos actualizados exitosamente.")  
    if importar=='tipologia':
        ruta_archivo_excel = excel_document.excel_file.path
        datos_excel = pd.read_excel(ruta_archivo_excel, sheet_name='tipologia')
        for index, row in datos_excel.iterrows():
            strZona= row['zona']
            if not math.isnan(strZona):
                parte_entera = int(strZona)
            else:
                parte_entera = 99 

            zona=Zona.objects.get(codigo=parte_entera) 
            codigo = row['codigo']
            descripcion = row['descripcion']
            tarifa = row['tarifa']
            try:
                # Intenta obtener un registro existente o crear uno nuevo si no existe
                tipologia, creado = Tipologia.objects.get_or_create(
                    codigo=codigo,
                    defaults={
                        'descripcion': descripcion,
                        'zona': zona,
                        'tarifa': tarifa,
                    }
                )
                if not creado:
                    print(f"El registro con código {codigo} ya existe y no se creó uno nuevo.")
            except IntegrityError as e:
                # Maneja cualquier error de integridad si es necesario
                print(f"Error de integridad al crear el registro: {e}")
                ExcelDocumentLOG.objects.create(pestana=importar, codigo=codigo, error=e)
        print("Ambito importados exitosamente.")
    if importar=='val_terreno':
        ruta_archivo_excel = excel_document.excel_file.path
        datos_excel = pd.read_excel(ruta_archivo_excel, sheet_name='val_terreno')
        for index, row in datos_excel.iterrows():
            if not math.isnan(row['id_inmueble']):
                numero_expediente = int((row['id_inmueble']))
            else:
                numero_expediente = 0
            if not math.isnan(row['tipologia']):
                tipologiaId = int(row['tipologia'])
            else:
                tipologiaId = 0

            tipologia = Tipologia.objects.get(codigo=tipologiaId)
            if tipologia.descripcion=='RESIDENCIAL' :
                tipoinmuebleId=1
            if tipologia.descripcion=='COMERCIAL' :
                tipoinmuebleId=2
            if tipologia.descripcion=='INDUSTRIAL' : 
                tipoinmuebleId=3
            tipoinmueble=TipoInmueble.objects.get(codigo=tipoinmuebleId)      
            area = row['area']
            try:
                print('numero_expediente',numero_expediente)
                inmueble=Inmueble.objects.get(numero_expediente=numero_expediente)
                inmueblevaloracionterreno=InmuebleValoracionTerreno.objects.get(inmueble=inmueble.id)
                inmueblevaloracionterreno.tipologia=tipologia
                inmueblevaloracionterreno.area=area
                inmueblevaloracionterreno.tipo=tipoinmueble
                inmueblevaloracionterreno.save()

            except InmuebleValoracionTerreno.DoesNotExist:
                print(f"No existe el numero de expediente {numero_expediente}")
                ExcelDocumentLOG.objects.create(pestana=importar, codigo=numero_expediente, error='No existe InmuebleValoracionTerreno')
            except Inmueble.DoesNotExist:
                print(f"No existe el INMUEBLE numero de expediente {numero_expediente}")
                ExcelDocumentLOG.objects.create(pestana=importar, codigo=numero_expediente, error='No existe INMUEBLE')
            except IntegrityError as e:
                # Maneja cualquier error de integridad si es necesario
                print(f"Error de integridad al crear el registro: {e}")
                ExcelDocumentLOG.objects.create(pestana=importar, codigo=numero_expediente, error=e)
        print("val_terreno actualizados exitosamente.")  
    if importar=='val_construccion':
        ruta_archivo_excel = excel_document.excel_file.path
        datos_excel = pd.read_excel(ruta_archivo_excel, sheet_name='val_construccion')
        for index, row in datos_excel.iterrows():
            if not math.isnan(row['id_inmueble']):
                numero_expediente = int((row['id_inmueble']))
            else:
                numero_expediente = 0
            if not math.isnan(row['tipologia']):
                tipologiaId = int(row['tipologia'])
            else:
                tipologiaId = 0
            tipologia = Tipologia.objects.get(codigo=tipologiaId)
            if tipologia.descripcion=='RESIDENCIAL' :
                tipoinmuebleId=1
            if tipologia.descripcion=='COMERCIAL' :
                tipoinmuebleId=2
            if tipologia.descripcion=='INDUSTRIAL' :
                tipoinmuebleId=3
            tipoinmueble=TipoInmueble.objects.get(codigo=tipoinmuebleId)

            area = row['area']

            try:
                print('numero_expediente',numero_expediente)
                inmueble=Inmueble.objects.get(numero_expediente=numero_expediente)
                inmueblevaloracionterreno=InmuebleValoracionTerreno.objects.get(inmueble=inmueble.id)
                try:
                    # Intenta obtener un registro existente o crear uno nuevo si no existe
                    creado = InmuebleValoracionConstruccion.objects.get_or_create(
                        inmueblevaloracionterreno=inmueblevaloracionterreno,
                        defaults={
                            'tipologia': tipologia,
                            'area': area,
                            'tipo':tipoinmueble,
                        }
                    )
                    if not creado:
                        print(f"El registro con código {numero_expediente} ya existe y no se creó uno nuevo.")
                except IntegrityError as e:
                    # Maneja cualquier error de integridad si es necesario
                    print(f"Error de integridad al crear el registro: {e}")
                    ExcelDocumentLOG.objects.create(pestana=importar, codigo=numero_expediente, error=e)
            except InmuebleValoracionTerreno.DoesNotExist:
                print(f"No existe el numero de expediente {numero_expediente}")
                ExcelDocumentLOG.objects.create(pestana=importar, codigo=numero_expediente, error='No existe InmuebleValoracionTerreno')
            except Inmueble.DoesNotExist:
                print(f"No existe el INMUEBLE numero de expediente {numero_expediente}")
                ExcelDocumentLOG.objects.create(pestana=importar, codigo=numero_expediente, error='No existe INMUEBLE')
            except IntegrityError as e:
                # Maneja cualquier error de integridad si es necesario
                print(f"Error de integridad al crear el registro: {e}")
                ExcelDocumentLOG.objects.create(pestana=importar, codigo=numero_expediente, error=e)
        print("val_terreno actualizados exitosamente.")
#***************************************************************************************** CorridaBancaria.xlsx
    if importar=='cien':
        ruta_archivo_excel = excel_document.excel_file.path
        datos_excel = pd.read_excel(ruta_archivo_excel, sheet_name='cien')
        for index, row in datos_excel.iterrows():
            bancocuenta = BancoCuenta.objects.get(codigocuenta='12')
            fecha = row['Fecha Efec.']
            referencia = row['Descripción Movimiento']
            descripcion = row['Descripción Movimiento']
           
            monto = row['Abono']
            try:
                if isinstance(monto, str):
                    monto = float(monto.replace(',', ''))  # Intenta convertir la cadena a float
            except (ValueError, TypeError):
                monto = 0.0  # Si la conversión falla, asigna 0.0

            if math.isnan(monto):
                monto = 0.0
            situado = 'T' 
            if row['Situado Regional']==14:
                situado = 'R'
            try:
                # Intenta obtener un registro existente o crear uno nuevo si no existe
                corridabancaria, creado = CorridasBancarias.objects.get_or_create(
                    bancocuenta=bancocuenta,
                    fecha=fecha,
                    referencia=referencia,
                    descripcion=descripcion,
                    monto=monto, 
                    defaults={
                        'situado': situado,
                    }
                )
                if not creado:
                    print(f"El registro con anio {referencia} y mes {monto} ya existe y no se creó uno nuevo.")
                    
            except IntegrityError as e:
                # Maneja cualquier error de integridad si es necesario
                print(f"Error de integridad al crear el registro: {e}")
                ExcelDocumentLOG.objects.create(pestana=importar, codigo=referencia, error=e)
            # Crea un nuevo objeto TasaInteres y guárdalo en la base de datos
            #TasaInteres.objects.create(anio=anio, mes=mes, tasa=tasa)
        print("Datos importados exitosamente.")
    
    if importar=='bancaribe':
        # este banco NO tiene nombre de columnas y se lee  apartir de la linea 2
        ruta_archivo_excel = excel_document.excel_file.path
        datos_excel = pd.read_excel(ruta_archivo_excel, header=None, skiprows=1,sheet_name='bancaribe')
        for index, row in datos_excel.iterrows():
            bancocuenta = BancoCuenta.objects.get(codigocuenta='17')
            fecha = row[0]
            referencia = row[1]
            descripcion = row[2]           
            monto = row[4] 
            print(fecha)
            print(referencia)
            print(descripcion)
            print(monto)
            try:
                if isinstance(monto, str):
                    monto = float(monto.replace(',', ''))  # Intenta convertir la cadena a float
            except (ValueError, TypeError):
                monto = 0.0  # Si la conversión falla, asigna 0.0

            if math.isnan(monto):
                monto = 0.0
            situado = 'T' # este banco NO maneja situados, todas son transferencias
            try:
                # Intenta obtener un registro existente o crear uno nuevo si no existe
                corridabancaria,creado = CorridasBancarias.objects.get_or_create(
                    bancocuenta=bancocuenta,
                    fecha=fecha,
                    referencia=referencia,
                    descripcion=descripcion,
                    monto=monto, 
                    defaults={
                        'situado': situado,
                    }
                )
                if not creado:
                    print(f"El registro con referencia {referencia} y monto {monto} ya existe y no se creó uno nuevo.")
                    
            except IntegrityError as e:
                # Maneja cualquier error de integridad si es necesario
                print(f"Error de integridad al crear el registro: {e}")
                ExcelDocumentLOG.objects.create(pestana=importar, codigo=referencia, error=e)
        print("Datos importados exitosamente.")
    if importar=='banesco':
        ruta_archivo_excel = excel_document.excel_file.path
        datos_excel = pd.read_excel(ruta_archivo_excel, sheet_name='banesco')
        filas_filtradas = datos_excel[datos_excel['Descripción'].str.contains("TRF")] # solo carga las transferencias

        for index, row in filas_filtradas.iterrows():
            bancocuenta = BancoCuenta.objects.get(codigocuenta='16')
            fecha = row['Fecha']
            referencia = row['Referencia']
            descripcion = row['Descripción']
            monto = row['Monto']
            try:
                if isinstance(monto, str):
                    monto = float(monto.replace(',', ''))  # Intenta convertir la cadena a float
            except (ValueError, TypeError):
                monto = 0.0  # Si la conversión falla, asigna 0.0

            if math.isnan(monto):
                monto = 0.0
            situado = 'T' 
            # este banco NO maneja situados
            try:
                # Intenta obtener un registro existente o crear uno nuevo si no existe
                corridabancaria, creado = CorridasBancarias.objects.get_or_create(
                    bancocuenta=bancocuenta,
                    fecha=fecha,
                    referencia=referencia,
                    descripcion=descripcion,
                    monto=monto, 
                    defaults={
                        'situado': situado,
                    }
                )
                if not creado:
                    print(f"El registro con referencia {referencia} y monto {monto} ya existe y no se creó uno nuevo.")
                    
            except IntegrityError as e:
                # Maneja cualquier error de integridad si es necesario
                print(f"Error de integridad al crear el registro: {e}")
                ExcelDocumentLOG.objects.create(pestana=importar, codigo=referencia, error=e)
            # Crea un nuevo objeto TasaInteres y guárdalo en la base de datos
            #TasaInteres.objects.create(anio=anio, mes=mes, tasa=tasa)
        print("Datos importados exitosamente.")
    if importar=='bfc':
        ruta_archivo_excel = excel_document.excel_file.path
        datos_excel = pd.read_excel(ruta_archivo_excel, sheet_name='bfc')
        filas_filtradas = datos_excel[~datos_excel['Descripción'].str.contains("AB.LOTE")] # esos son puntos de venta, se excluyen
        for index, row in filas_filtradas.iterrows():
            bancocuenta = BancoCuenta.objects.get(codigocuenta='3')
            fecha = row['Fecha Efectiva']
            fecha_obj = datetime.strptime(fecha, "%d/%m/%Y")  # Convierte al formato "YYYY-MM-DD"
            fecha_formateada = fecha_obj.strftime("%Y-%m-%d")  # Formatea como "YYYY-MM-DD"
            referencia = row['Referencia']
            descripcion = row['Descripción']
            monto = row['Monto']
            try:
                if isinstance(monto, str):
                    monto = float(monto.replace('.', '').replace(',', '.'))  # Intenta convertir la cadena a float
            except (ValueError, TypeError):
                monto = 0.0  # Si la conversión falla, asigna 0.0

            if math.isnan(monto):
                monto = 0.0
            situado = 'T'
            if row['Situado Nacional']==14:
                situado = 'N'
            try:
                # Intenta obtener un registro existente o crear uno nuevo si no existe
                corridabancaria, creado = CorridasBancarias.objects.get_or_create(
                    bancocuenta=bancocuenta,
                    fecha=fecha_formateada,
                    referencia=referencia,
                    descripcion=descripcion,
                    monto=monto, 
                    defaults={
                        'situado': situado,
                    }
                )
                if not creado:
                    print(f"El registro con referencia {referencia} y monto {monto} ya existe y no se creó uno nuevo.")
                    
            except IntegrityError as e:
                # Maneja cualquier error de integridad si es necesario
                print(f"Error de integridad al crear el registro: {e}")
                ExcelDocumentLOG.objects.create(pestana=importar, codigo=referencia, error=e)
            # Crea un nuevo objeto TasaInteres y guárdalo en la base de datos
            #TasaInteres.objects.create(anio=anio, mes=mes, tasa=tasa)
        print("Datos importados exitosamente.")
    if importar=='bnc':
        ruta_archivo_excel = excel_document.excel_file.path
        datos_excel = pd.read_excel(ruta_archivo_excel, sheet_name='bnc')
        for index, row in datos_excel.iterrows():
            bancocuenta = BancoCuenta.objects.get(codigocuenta='51')
            fecha = row['Fecha']
            fecha_obj = datetime.strptime(fecha, "%d/%m/%Y")  # Convierte al formato "YYYY-MM-DD"
            fecha_formateada = fecha_obj.strftime("%Y-%m-%d")  # Formatea como "YYYY-MM-DD"
            referencia = row['Referencia']
            descripcion = row['Referencia']
            monto = row['Haber']
            try:
                if isinstance(monto, str):
                    monto = float(monto.replace('.', '').replace(',', '.'))  # Intenta convertir la cadena a float
            except (ValueError, TypeError):
                monto = 0.0  # Si la conversión falla, asigna 0.0

            if math.isnan(monto):
                monto = 0.0
            situado = 'T' # este banco NO maneja situado
            #if row['Situado Nacional']==14:
            #    situado = 'N'
            try:
                # Intenta obtener un registro existente o crear uno nuevo si no existe
                corridabancaria, creado = CorridasBancarias.objects.get_or_create(
                    bancocuenta=bancocuenta,
                    fecha=fecha_formateada,
                    referencia=referencia,
                    descripcion=descripcion,
                    monto=monto, 
                    defaults={
                        'situado': situado,
                    }
                )
                if not creado:
                    print(f"El registro con referencia {referencia} y monto {monto} ya existe y no se creó uno nuevo.")
                    
            except IntegrityError as e:
                # Maneja cualquier error de integridad si es necesario
                print(f"Error de integridad al crear el registro: {e}")
                ExcelDocumentLOG.objects.create(pestana=importar, codigo=referencia, error=e)
            # Crea un nuevo objeto TasaInteres y guárdalo en la base de datos
            #TasaInteres.objects.create(anio=anio, mes=mes, tasa=tasa)
        print("Datos importados exitosamente.")
    if importar=='venezuela':
        ruta_archivo_excel = excel_document.excel_file.path
        datos_excel = pd.read_excel(ruta_archivo_excel, sheet_name='venezuela')
        for index, row in datos_excel.iterrows():
            bancocuenta = BancoCuenta.objects.get(codigocuenta='50')
            fecha = row['fecha']
            fecha_obj = datetime.strptime(fecha, "%d/%m/%Y")  # Convierte al formato "YYYY-MM-DD"
            fecha_formateada = fecha_obj.strftime("%Y-%m-%d")  # Formatea como "YYYY-MM-DD"
            referencia = row['referencia']
            descripcion = row['concepto']
            monto = row['monto']
            try:
                if isinstance(monto, str):
                    monto = float(monto.replace('.', '').replace(',', '.'))  # Intenta convertir la cadena a float
            except (ValueError, TypeError):
                monto = 0.0  # Si la conversión falla, asigna 0.0

            if math.isnan(monto):
                monto = 0.0
            situado = 'T' # este banco NO maneja situado
            #if row['Situado Nacional']==14:
            #    situado = 'N'
            try:
                # Intenta obtener un registro existente o crear uno nuevo si no existe
                corridabancaria, creado = CorridasBancarias.objects.get_or_create(
                    bancocuenta=bancocuenta,
                    fecha=fecha_formateada,
                    referencia=referencia,
                    descripcion=descripcion,
                    monto=monto, 
                    defaults={
                        'situado': situado,
                    }
                )
                if not creado:
                    print(f"El registro con referencia {referencia} y monto {monto} ya existe y no se creó uno nuevo.")
                    
            except IntegrityError as e:
                # Maneja cualquier error de integridad si es necesario
                print(f"Error de integridad al crear el registro: {e}")
                ExcelDocumentLOG.objects.create(pestana=importar, codigo=referencia, error=e)
            # Crea un nuevo objeto TasaInteres y guárdalo en la base de datos
            #TasaInteres.objects.create(anio=anio, mes=mes, tasa=tasa)
        print("Datos importados exitosamente.")
    return Response('Datos importados exitosamente.',status=status.HTTP_200_OK) 

#***************************************************************************************** CorridaBancaria.xlsx
def importar_corrida_bancaria(archivo,pestana,ruta):
    print('Backend procesando: ',pestana)
    importar=pestana
    ExcelDocumentLOG.objects.filter(codigo=importar).delete()
    excel_document=ExcelDocument.objects.get(title=archivo)
    ruta_archivo_excel = ruta
    if importar=='BNC':
        print('ruta_archivo_excel',ruta)
        #ruta_archivo_excel = ruta

        datos_excel = pd.read_excel(ruta_archivo_excel, skiprows=15)
        print(datos_excel)
        filas_filtradas = datos_excel[~datos_excel['Fecha'].str.contains("Totales")& (datos_excel['Haber'] > 0)] # se excluyen
        for index, row in filas_filtradas.iterrows():
            bancocuenta = BancoCuenta.objects.get(codigocuenta='51')
            fecha = row['Fecha']
            fecha_obj = datetime.strptime(fecha, "%d/%m/%Y")  # Convierte al formato "YYYY-MM-DD"
            fecha_formateada = fecha_obj.strftime("%Y-%m-%d")  # Formatea como "YYYY-MM-DD"
            referencia = row['Referencia']
            descripcion = row['Descripción']
            monto = row['Haber']
            try:
                if isinstance(monto, str):
                    monto = float(monto.replace('.', '').replace(',', '.'))  # Intenta convertir la cadena a float
            except (ValueError, TypeError):
                monto = 0.0  # Si la conversión falla, asigna 0.0

            if math.isnan(monto):
                monto = 0.0
            situado = 'T' # este banco NO maneja situado
            #if row['Situado Nacional']==14:
            #    situado = 'N'
            if monto > 0:
                try:
                    corridabancaria, creado = CorridasBancarias.objects.get_or_create(
                        bancocuenta=bancocuenta,
                        fecha=fecha_formateada,
                        referencia=referencia,
                        descripcion=descripcion,
                        monto=monto, 
                        defaults={
                            'situado': situado,
                        }
                    )
                    if not creado:
                        print(f"El registro con referencia {referencia} y monto {monto} ya existe y no se creó uno nuevo.")
                except IntegrityError as e:
                    print(f"Error de integridad al crear el registro: {e}")
                    ExcelDocumentLOG.objects.create(pestana=importar, codigo=referencia, error=e)
        print("Datos importados exitosamente.")
   
    if importar=='BanCaribe':
        # este banco NO tiene nombre de columnas y se lee  apartir de la linea 2
        #ruta_archivo_excel = excel_document.excel_file.path
        datos_excel = pd.read_excel(ruta_archivo_excel, header=None, skiprows=1)
        filas_filtradas = datos_excel[~datos_excel[3].str.contains("D")] # se excluyen
        for index, row in datos_excel.iterrows():
            bancocuenta = BancoCuenta.objects.get(codigocuenta='17')
            fecha = row[0]
            referencia = row[1]
            descripcion = row[2]           
            monto = row[4] 
            print(fecha)
            print(referencia)
            print(descripcion)
            print(monto)
            try:
                if isinstance(monto, str):
                    monto = float(monto.replace(',', ''))  # Intenta convertir la cadena a float
            except (ValueError, TypeError):
                monto = 0.0  # Si la conversión falla, asigna 0.0
            if math.isnan(monto):
                monto = 0.0
            situado = 'T' # este banco NO maneja situados, todas son transferencias
            if monto > 0:
                try:
                    # Intenta obtener un registro existente o crear uno nuevo si no existe
                    corridabancaria,creado = CorridasBancarias.objects.get_or_create(
                        bancocuenta=bancocuenta,
                        fecha=fecha,
                        referencia=referencia,
                        descripcion=descripcion,
                        monto=monto, 
                        defaults={
                            'situado': situado,
                        }
                    )
                    if not creado:
                        print(f"El registro con referencia {referencia} y monto {monto} ya existe y no se creó uno nuevo.")
                except IntegrityError as e:
                    # Maneja cualquier error de integridad si es necesario
                    print(f"Error de integridad al crear el registro: {e}")
                    ExcelDocumentLOG.objects.create(pestana=importar, codigo=referencia, error=e)
        print("Datos importados exitosamente.")
    
    if importar=='100Banco':
        #ruta_archivo_excel = excel_document.excel_file.path
        datos_excel = pd.read_excel(ruta_archivo_excel, skiprows=1)
        filas_filtradas = datos_excel[datos_excel['Cargo'].isna()] # cargo este vacio
        for index, row in filas_filtradas.iterrows():
            bancocuenta = BancoCuenta.objects.get(codigocuenta='12')
            fecha = row['Fecha Efec.']
            referencia = row['Referencia']
            descripcion = row['Descripción Movimiento']
            monto = row['Abono']
            try:
                if isinstance(monto, str):
                    monto = float(monto.replace(',', ''))  # Intenta convertir la cadena a float
            except (ValueError, TypeError):
                monto = 0.0  # Si la conversión falla, asigna 0.0

            if math.isnan(monto):
                monto = 0.0
            situado = 'T' 
            if monto > 0:
            #if row['Situado Regional']==14:
            #    situado = 'R'
                try:
                    # Intenta obtener un registro existente o crear uno nuevo si no existe
                    corridabancaria, creado = CorridasBancarias.objects.get_or_create(
                        bancocuenta=bancocuenta,
                        fecha=fecha,
                        referencia=referencia,
                        descripcion=descripcion,
                        monto=monto, 
                        defaults={
                            'situado': situado,
                        }
                    )
                    if not creado:
                        print(f"El registro con referencia {referencia} y monto {monto} ya existe y no se creó uno nuevo.")
                except IntegrityError as e:
                    print(f"Error de integridad al crear el registro: {e}")
                    ExcelDocumentLOG.objects.create(pestana=importar, codigo=referencia, error=e)
        print("Datos importados exitosamente.")
    
    if importar=='BANESCO':
        #ruta_archivo_excel = excel_document.excel_file.path
        datos_excel = pd.read_excel(ruta_archivo_excel)
        filas_filtradas = datos_excel[datos_excel['Descripción'].str.contains("TRF")] # solo carga las transferencias

        for index, row in filas_filtradas.iterrows():
            bancocuenta = BancoCuenta.objects.get(codigocuenta='16')
            fecha = row['Fecha']
            referencia = row['Referencia']
            descripcion = row['Descripción']
            monto = row['Monto']
            try:
                if isinstance(monto, str):
                    monto = float(monto.replace(',', ''))  # Intenta convertir la cadena a float
            except (ValueError, TypeError):
                monto = 0.0  # Si la conversión falla, asigna 0.0

            if math.isnan(monto):
                monto = 0.0
            situado = 'T' 
            # este banco NO maneja situados
            if monto > 0:
                try:
                    # Intenta obtener un registro existente o crear uno nuevo si no existe
                    corridabancaria, creado = CorridasBancarias.objects.get_or_create(
                        bancocuenta=bancocuenta,
                        fecha=fecha,
                        referencia=referencia,
                        descripcion=descripcion,
                        monto=monto, 
                        defaults={
                            'situado': situado,
                        }
                    )
                    if not creado:
                        print(f"El registro con referencia {referencia} y monto {monto} ya existe y no se creó uno nuevo.")
                except IntegrityError as e:
                    print(f"Error de integridad al crear el registro: {e}")
                    ExcelDocumentLOG.objects.create(pestana=importar, codigo=referencia, error=e)
        print("Datos importados exitosamente.")
    if importar=='BFC':
        #ruta_archivo_excel = excel_document.excel_file.path
        datos_excel = pd.read_excel(ruta_archivo_excel)
        filas_filtradas = datos_excel[~datos_excel['Descripción'].str.contains("AB.LOTE")] # esos son puntos de venta, se excluyen
        for index, row in filas_filtradas.iterrows():
            bancocuenta = BancoCuenta.objects.get(codigocuenta='3')
            fecha = row['Fecha Efectiva']
            fecha_obj = datetime.strptime(fecha, "%d/%m/%Y")  # Convierte al formato "YYYY-MM-DD"
            fecha_formateada = fecha_obj.strftime("%Y-%m-%d")  # Formatea como "YYYY-MM-DD"
            referencia = row['Referencia']
            descripcion = row['Descripción']
            monto = row['Monto']
            try:
                if isinstance(monto, str):
                    monto = float(monto.replace('.', '').replace(',', '.'))  # Intenta convertir la cadena a float
            except (ValueError, TypeError):
                monto = 0.0  # Si la conversión falla, asigna 0.0

            if math.isnan(monto):
                monto = 0.0
            situado = 'T'
            #if row['Situado Nacional']==14:
            #    situado = 'N'
            if monto > 0:
                try:
                    # Intenta obtener un registro existente o crear uno nuevo si no existe
                    corridabancaria, creado = CorridasBancarias.objects.get_or_create(
                        bancocuenta=bancocuenta,
                        fecha=fecha_formateada,
                        referencia=referencia,
                        descripcion=descripcion,
                        monto=monto, 
                        defaults={
                            'situado': situado,
                        }
                    )
                    if not creado:
                        print(f"El registro con referencia {referencia} y monto {monto} ya existe y no se creó uno nuevo.")
                except IntegrityError as e:
                    print(f"Error de integridad al crear el registro: {e}")
                    ExcelDocumentLOG.objects.create(pestana=importar, codigo=referencia, error=e)
        print("Datos importados exitosamente.")
    if importar=='BDV':
        datos_excel = pd.read_excel(ruta_archivo_excel)
        #datos_excel['tipoMovimiento'] = datos_excel['tipoMovimiento'].str.upper()
        #filas_filtradas = datos_excel[~datos_excel['tipoMovimiento'].str.contains("Saldo Inicial")]

        for index, row in datos_excel.iterrows():
            bancocuenta = BancoCuenta.objects.get(codigocuenta='50')
            fecha = row['fecha']
            referencia = row['referencia']
            if 'descripcion' in datos_excel.columns:
                descripcion = row['descripcion'] 
            if 'concepto' in datos_excel.columns:
                descripcion = row['concepto'] 
            if 'monto' in datos_excel.columns:     
                monto = row['monto']
            if 'importe' in datos_excel.columns:     
                monto = row['importe']
                fecha_obj = datetime.strptime(fecha, '%d-%m-%Y %H:%M')  # Convierte al formato "YYYY-MM-DD"
            else:
                fecha_obj = datetime.strptime(fecha, "%d/%m/%Y")  # Convierte al formato "YYYY-MM-DD"
            fecha_formateada = fecha_obj.strftime("%Y-%m-%d")  # Formatea como "YYYY-MM-DD"   
            try:
                if isinstance(monto, str):
                    monto = float(monto.replace('.', '').replace(',', '.'))  # Intenta convertir la cadena a float
            except (ValueError, TypeError):
                monto = 0.0  # Si la conversión falla, asigna 0.0

            if math.isnan(monto):
                monto = 0.0
            situado = 'T' # este banco NO maneja situado
            #if row['Situado Nacional']==14:
            #    situado = 'N'
            if monto > 0:
                try:
                    # Intenta obtener un registro existente o crear uno nuevo si no existe
                    corridabancaria, creado = CorridasBancarias.objects.get_or_create(
                        bancocuenta=bancocuenta,
                        fecha=fecha_formateada,
                        referencia=referencia,
                        descripcion=descripcion,
                        monto=monto, 
                        defaults={
                            'situado': situado,
                        }
                    )
                    if not creado:
                        print(f"El registro con referencia {referencia} y monto {monto} ya existe y no se creó uno nuevo.")
                        
                except IntegrityError as e:
                    print(f"Error de integridad al crear el registro: {e}")
                    ExcelDocumentLOG.objects.create(pestana=importar, codigo=referencia, error=e)

        print("Datos importados exitosamente.")
    return Response('Datos importados exitosamente.',status=status.HTTP_200_OK) 


def Crear_Perfil(request):
    #Para crear nuevos usuarios para el sistema de la alcaldia desde uno ya existente
    # primero: se crea el usuario desde el admin de django
    # segundo: se crear el perfil desde el admin de django
    # tercero: se ejecuta esta API pasando el usuario origen y el usuario destino
    if (request): 
        UsuarioOrigen=User.objects.get(username=request['origen'])
        UsuarioDestino=User.objects.get(username=request['destino'])
        PerfilOrigen=Perfil.objects.get(usuario=UsuarioOrigen)
        PerfilDestino=Perfil.objects.get(usuario=UsuarioDestino)
        PermisoOrigen=Permiso.objects.filter(perfil=PerfilOrigen)
        for item in PermisoOrigen:
            try:
                 # Intenta obtener un registro existente o crear uno nuevo si no existe
                creado = Permiso.objects.get_or_create(
                    perfil=PerfilDestino,
                    modulo=item.modulo,
                    defaults={
                    'leer': item.leer,
                    'escribir': item.escribir,
                    'borrar': item.borrar,
                    'actualizar': item.actualizar,
                    }
                )
                if not creado:
                    print(f"El registro con código {PerfilDestino} ya existe y no se creó uno nuevo.")
                else:
                    print(f"El registro con código {PerfilDestino} SE CREO.")

            except IntegrityError as e:
                # Maneja cualquier error de integridad si es necesario
                print(f"Error de integridad al crear el registro: {e}")
        return Response('Insert PERFIL OK', status=status.HTTP_200_OK)
    else:
        return Response('Insert PERFIL NOT Ok', status=status.HTTP_400_BAD_REQUEST)

def Crear_Patente(request):
    if (request):
        items=request['detalle']
        correlativo=Correlativo.objects.get(id=1)
        nNumero=correlativo.NumeroEstadoCuenta
        correlativo.NumeroEstadoCuenta=correlativo.NumeroEstadoCuenta+1
        correlativo.save()
        valor_petro=TasaBCV.objects.get(habilitado=True).monto
        valor_tasabcv=TasaBCV.objects.get(habilitado=True).monto
        tipoflujo = None if request['flujo']==None else TipoFlujo.objects.get(codigo=request['flujo'])
        inmueble = None if request['inmueble']==None else Inmueble.objects.get(id=request['inmueble'])
        propietario = Propietario.objects.get(id=request['propietario'])
        Cabacera=EstadoCuenta(
            numero=nNumero,
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

        result = {
        "documento": Cabacera.numero,
        "id": Cabacera.id

        }
        return Response(result, status=status.HTTP_200_OK)
    else:
        result = {
        "documento": 'Insert EstadoCuenta NOT Ok'
 
        }
        return Response(result, status=status.HTTP_400_BAD_REQUEST)
 


def Estadistica_Flujo(request):
    queryset=()
    if (request):
        queryset = Flujo.objects.values(
            'fecha__year', 
            'fecha__month', 
            'estado', 
            'pagoestadocuenta__liquidacion__tipoflujo__descripcion'
        ).annotate(
            estado_descripcion=Count('estado'),
            cantidad=Count('*')
        ).order_by('fecha__year', 'fecha__month', 'estado')

        queryset = (
            Flujo.objects.annotate(
                año=ExtractYear('fecha'),
                mes=ExtractMonth('fecha'),
                #descripcion='pagoestadocuenta__liquidacion__tipoflujo__descripcion',
                estado_descripcion=Case(
                    When(estado='1', then=Value('en proceso')),
                    When(estado='2', then=Value('Cerrado')),
                    default=Value('Estado no reconocido'),
                    output_field=CharField(),
                ),
            )
            .values('año', 'mes', 'estado', 'estado_descripcion', 'pagoestadocuenta__liquidacion__tipoflujo__descripcion')
            .annotate(total=Count('*'))
            .order_by('año', 'mes', 'estado')
        )


        return Response(queryset, status=status.HTTP_200_OK)
    else:
        return Response(queryset, status=status.HTTP_400_BAD_REQUEST)