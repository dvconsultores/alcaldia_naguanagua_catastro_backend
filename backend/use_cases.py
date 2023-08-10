from .models import *
from .serializers import *
from django.contrib.auth import authenticate
from knox.models import AuthToken
from rest_framework.response import Response
from rest_framework import viewsets, status, generics
import re
from datetime import datetime,timedelta,date
from pyDolarVenezuela import price
import datetime
from django.db.models import Max,Min,Sum,Q

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
        tipoflujo = None if request['flujo']==None else TipoFlujo.objects.get(id=request['flujo'])
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
                fechapago =  str(date.today()),#detalle['fechapago'],
                nro_referencia = detalle['referencia']
            )
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
            
            diferencia=today-fecha_compra

            print('fecha_compra:',fecha_compra,'today:',today,diferencia.days,'bInscripcion:',bInscripcion,'bModifica:',bModifica)

            if (bModifica or bInscripcion): # Artículo 20
                baseCalculo = UnidadTributaria.objects.get(habilitado=True)
                baseCalculoBs= float(baseCalculo.monto)
                if bInscripcion:
                    fechaVencidaI=fecha_inscripcion+ datetime.timedelta(days=90) # Sumar los 90 dias de plazo a la fecha vencida para determinar el periodo vencido
                    mesesVencidosI = meses_transcurridos(fechaVencidaI, today)
                    print("Meses Vencidos:", mesesVencidosI)
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
                    print("Meses mesesVencidos:", mesesVencidosM)
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
                                'aplica':'Multa Inscripcion Uni  Art.99',
                                #'tipologia':dato.tipologia.id,
                                #'sub_utilizado':dato.sub_utilizado,
                                #'tipo':dato.tipo.id,
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
                                'aplica':'Multa Modifica Uni Art.101',
                                #'tipologia':dato.tipologia.id,
                                #'sub_utilizado':dato.sub_utilizado,
                                #'tipo':dato.tipo.id,
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
                                'aplica':'Multa Inscripcion MULTI  Art.99',
                                #'tipologia':dato.tipologia.id,
                                #'sub_utilizado':dato.sub_utilizado,
                                #'tipo':dato.tipo.id,
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
                                'aplica':'Multa Modifica MULTI  Art.101',
                                #'tipologia':dato.tipologia.id,
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
                cabecera = {
                    'aplica':'Multa Modifica MULTI  Art.101',
                    #'tipologia':dato.tipologia.id,
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
        if (request['inmueble']):
            oInmueble = Inmueble.objects.get(id=request['inmueble'])
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
                ZonaInmueble=oInmueble.zona
                oTipologia=Tipologia.objects.filter(zona=ZonaInmueble)

                #Ubicar la fecha de compra
                oPropietario = InmueblePropietarios.objects.get(propietario=request['propietario'],inmueble=request['inmueble'])
                fechaCompra=oPropietario.fecha_compra
                today = date.today()
                diferencia=today-fechaCompra
                print(fechaCompra,today,diferencia.days)
                # valida si aplica descuentos por pronto pago.
                oDescuento=0 # Bandera que valida si aplica descuento o no
                if (diferencia.days<=90):
                #if (diferencia.days<=90 and minimo_ano==today.year):
                    try:
                        oDescuento=IC_ImpuestoDescuento.objects.filter(habilitado=True,aplica='C')
                    except:
                        oDescuento=0
                bMulta=True
                oCargos=IC_ImpuestoCargos.objects.filter(habilitado=True,aplica='C')
                fMulta=float(oCargos.get(codigo='multa').porcentaje)
                fRecargo=float(oCargos.get(codigo='recargo').porcentaje)
                fInteres=float(oCargos.get(codigo='interes').porcentaje)
                tMulta=0
                tRecargo=0
                tInteres=0
                tTotal=0
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

                            if dato.tipologia.codigo=='17' and oInmueble.zona.codigo=='1':
                                mesesTrascurridos = meses_transcurridos(fechaCompra, today)
                                if mesesTrascurridos>=60: # tiene 5 años de antiguedad
                                    Alicuota=float(oTipologia.get(id=dato.tipologia.id).tarifa)
                                else:
                                    # si no se comple aplico Otros Usos=5
                                    Alicuota=float(oTipologia.get(codigo='15').tarifa)
                            else:
                                Alicuota=float(oTipologia.get(id=dato.tipologia.id).tarifa)
                            Monto=float(dato.area)*(Alicuota*iAlicuota)*baseCalculoBs
                            mDescuento=0
                            if oDescuento and minimo_ano==today.year:
                                # Valida que aplique descuento solamente con el año actual
                                try:
                                    pDescuento=oDescuento.filter(Q(tipologia__isnull=True) | Q(tipologia=dato.tipologia.id,))
                                    registros_validos = pDescuento.filter(fechadesde__month__lte=today.month,
                                            fechahasta__month__gte=today.month,
                                            fechadesde__day__lte=today.day,
                                            fechahasta__day__gte=today.day)
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
                                tMulta=tMulta+(Total*(fMulta/100))
                                tRecargo=tRecargo+(Total*(fRecargo/100))
                                tInteres=tInteres+(Total*(fInteres/100))
                    minimo_ano=minimo_ano+1
                print('tMulta',tMulta)
                correlativo=Correlativo.objects.get(id=1)
                numero=correlativo.NumeroIC_Impuesto
                Impuesto={
                    'numero':numero,
                    'zona':oInmueble.zona.id,
                    'basecalculobs':baseCalculoBs,
                    'inmueble':oInmueble.id,
                    'subtotal':tTotal,
                    'multa':tMulta,
                    'recargo':tRecargo,
                    'interes':tInteres,
                    'fmulta':fMulta,
                    'frecargo':fRecargo,
                    'finteres':fInteres,
                    'total':tTotal+tMulta+tRecargo+tInteres,
                }
                datos={
                    'cabacera':Impuesto,
                    'detalle':aDetalle,
                    'descuento':aDescuento,
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

