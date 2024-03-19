# Generated by Django 4.2 on 2024-03-18 01:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0211_flujo_backend_flu_numero_77c665_idx_and_more'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='acabadopared',
            index=models.Index(fields=['codigo'], name='backend_aca_codigo_8d297b_idx'),
        ),
        migrations.AddIndex(
            model_name='acceso',
            index=models.Index(fields=['codigo'], name='backend_acc_codigo_a6f360_idx'),
        ),
        migrations.AddIndex(
            model_name='ambito',
            index=models.Index(fields=['codigo'], name='backend_amb_codigo_596b43_idx'),
        ),
        migrations.AddIndex(
            model_name='avenida',
            index=models.Index(fields=['nombre'], name='backend_ave_nombre_dcf709_idx'),
        ),
        migrations.AddIndex(
            model_name='banco',
            index=models.Index(fields=['descripcion'], name='backend_ban_descrip_6a2f14_idx'),
        ),
        migrations.AddIndex(
            model_name='calle',
            index=models.Index(fields=['nombre'], name='backend_cal_nombre_783aba_idx'),
        ),
        migrations.AddIndex(
            model_name='categorizacion',
            index=models.Index(fields=['codigo'], name='backend_cat_codigo_51a226_idx'),
        ),
        migrations.AddIndex(
            model_name='comunidad',
            index=models.Index(fields=['comunidad'], name='backend_com_comunid_ff3709_idx'),
        ),
        migrations.AddIndex(
            model_name='conjuntoresidencial',
            index=models.Index(fields=['nombre'], name='backend_con_nombre_8a3495_idx'),
        ),
        migrations.AddIndex(
            model_name='conservacion',
            index=models.Index(fields=['codigo'], name='backend_con_codigo_ae7f97_idx'),
        ),
        migrations.AddIndex(
            model_name='cubierta',
            index=models.Index(fields=['codigo'], name='backend_cub_codigo_52be10_idx'),
        ),
        migrations.AddIndex(
            model_name='edificio',
            index=models.Index(fields=['nombre'], name='backend_edi_nombre_ee3679_idx'),
        ),
        migrations.AddIndex(
            model_name='estadocuenta',
            index=models.Index(fields=['numero'], name='backend_est_numero_12b84f_idx'),
        ),
        migrations.AddIndex(
            model_name='estadocuentadetalle',
            index=models.Index(fields=['estadocuenta'], name='backend_est_estadoc_ddb447_idx'),
        ),
        migrations.AddIndex(
            model_name='estatusinmueble',
            index=models.Index(fields=['codigo'], name='backend_est_codigo_b8b854_idx'),
        ),
        migrations.AddIndex(
            model_name='finesfiscales',
            index=models.Index(fields=['codigo'], name='backend_fin_codigo_a83134_idx'),
        ),
        migrations.AddIndex(
            model_name='forma',
            index=models.Index(fields=['codigo'], name='backend_for_codigo_9feb4a_idx'),
        ),
        migrations.AddIndex(
            model_name='ic_periodo',
            index=models.Index(fields=['periodo'], name='backend_ic__periodo_7b9cfc_idx'),
        ),
        migrations.AddIndex(
            model_name='inmueble',
            index=models.Index(fields=['numero_expediente'], name='backend_inm_numero__2fa500_idx'),
        ),
        migrations.AddIndex(
            model_name='inmuebleconstruccion',
            index=models.Index(fields=['inmueble'], name='backend_inm_inmuebl_e6e8bc_idx'),
        ),
        migrations.AddIndex(
            model_name='inmuebleconstruccioncubierta',
            index=models.Index(fields=['inmueble_construccion'], name='backend_inm_inmuebl_906635_idx'),
        ),
        migrations.AddIndex(
            model_name='inmuebleconstruccionsoporte',
            index=models.Index(fields=['inmueble_construccion'], name='backend_inm_inmuebl_99055f_idx'),
        ),
        migrations.AddIndex(
            model_name='inmuebleconstrucciontecho',
            index=models.Index(fields=['inmueble_construccion'], name='backend_inm_inmuebl_6d7b94_idx'),
        ),
        migrations.AddIndex(
            model_name='inmueblefaltante',
            index=models.Index(fields=['inmueble'], name='backend_inm_inmuebl_c65217_idx'),
        ),
        migrations.AddIndex(
            model_name='inmueblepropiedad',
            index=models.Index(fields=['inmueble'], name='backend_inm_inmuebl_95057c_idx'),
        ),
        migrations.AddIndex(
            model_name='inmueblepropietarios',
            index=models.Index(fields=['inmueble'], name='backend_inm_inmuebl_e37894_idx'),
        ),
        migrations.AddIndex(
            model_name='inmuebleterreno',
            index=models.Index(fields=['inmueble'], name='backend_inm_inmuebl_ccf426_idx'),
        ),
        migrations.AddIndex(
            model_name='inmuebleterrenoacceso',
            index=models.Index(fields=['inmueble_terreno'], name='backend_inm_inmuebl_ca8e0d_idx'),
        ),
        migrations.AddIndex(
            model_name='inmuebleterrenoservicio',
            index=models.Index(fields=['inmueble_terreno'], name='backend_inm_inmuebl_fd199a_idx'),
        ),
        migrations.AddIndex(
            model_name='inmuebleterrenotopografia',
            index=models.Index(fields=['inmueble_terreno'], name='backend_inm_inmuebl_b01a0a_idx'),
        ),
        migrations.AddIndex(
            model_name='inmuebleterrenouso',
            index=models.Index(fields=['inmueble_terreno'], name='backend_inm_inmuebl_873735_idx'),
        ),
        migrations.AddIndex(
            model_name='inmuebleubicacion',
            index=models.Index(fields=['inmueble'], name='backend_inm_inmuebl_ce98eb_idx'),
        ),
        migrations.AddIndex(
            model_name='inmueblevaloracionconstruccion',
            index=models.Index(fields=['inmueblevaloracionterreno'], name='backend_inm_inmuebl_9c938e_idx'),
        ),
        migrations.AddIndex(
            model_name='inmueblevaloracionconstruccion2024',
            index=models.Index(fields=['inmueblevaloracionterreno'], name='backend_inm_inmuebl_eb5f7e_idx'),
        ),
        migrations.AddIndex(
            model_name='inmueblevaloracionterreno',
            index=models.Index(fields=['inmueble'], name='backend_inm_inmuebl_91cc1b_idx'),
        ),
        migrations.AddIndex(
            model_name='inmueblevaloracionterreno2024',
            index=models.Index(fields=['inmueble'], name='backend_inm_inmuebl_deb142_idx'),
        ),
        migrations.AddIndex(
            model_name='liquidacion',
            index=models.Index(fields=['numero'], name='backend_liq_numero_fd5a26_idx'),
        ),
        migrations.AddIndex(
            model_name='liquidaciondetalle',
            index=models.Index(fields=['liquidacion'], name='backend_liq_liquida_8d2ab0_idx'),
        ),
        migrations.AddIndex(
            model_name='manzana',
            index=models.Index(fields=['codigo'], name='backend_man_codigo_a5ce70_idx'),
        ),
        migrations.AddIndex(
            model_name='nivelinmueble',
            index=models.Index(fields=['codigo'], name='backend_niv_codigo_115dd1_idx'),
        ),
        migrations.AddIndex(
            model_name='pagoestadocuenta',
            index=models.Index(fields=['numero'], name='backend_pag_numero_0d6f7f_idx'),
        ),
        migrations.AddIndex(
            model_name='pagoestadocuentadetalle',
            index=models.Index(fields=['pagoestadocuenta'], name='backend_pag_pagoest_b6b82d_idx'),
        ),
        migrations.AddIndex(
            model_name='parcela',
            index=models.Index(fields=['codigo'], name='backend_par_codigo_f7a864_idx'),
        ),
        migrations.AddIndex(
            model_name='propietario',
            index=models.Index(fields=['numero_documento'], name='backend_pro_numero__df01e6_idx'),
        ),
        migrations.AddIndex(
            model_name='regimen',
            index=models.Index(fields=['codigo'], name='backend_reg_codigo_9bbf72_idx'),
        ),
        migrations.AddIndex(
            model_name='sector',
            index=models.Index(fields=['codigo'], name='backend_sec_codigo_0c8685_idx'),
        ),
        migrations.AddIndex(
            model_name='servicios',
            index=models.Index(fields=['codigo'], name='backend_ser_codigo_956a76_idx'),
        ),
        migrations.AddIndex(
            model_name='soporte',
            index=models.Index(fields=['codigo'], name='backend_sop_codigo_42a3db_idx'),
        ),
        migrations.AddIndex(
            model_name='subparcela',
            index=models.Index(fields=['codigo'], name='backend_sub_codigo_7766c8_idx'),
        ),
        migrations.AddIndex(
            model_name='tasamulta',
            index=models.Index(fields=['codigo'], name='backend_tas_codigo_ac1afb_idx'),
        ),
        migrations.AddIndex(
            model_name='techo',
            index=models.Index(fields=['codigo'], name='backend_tec_codigo_f11b6b_idx'),
        ),
        migrations.AddIndex(
            model_name='tipodesincorporacion',
            index=models.Index(fields=['codigo'], name='backend_tip_codigo_c45e84_idx'),
        ),
        migrations.AddIndex(
            model_name='tipodocumento',
            index=models.Index(fields=['codigo'], name='backend_tip_codigo_d44640_idx'),
        ),
        migrations.AddIndex(
            model_name='tipoespecial',
            index=models.Index(fields=['codigo'], name='backend_tip_codigo_47ff50_idx'),
        ),
        migrations.AddIndex(
            model_name='tipoflujo',
            index=models.Index(fields=['codigo'], name='backend_tip_codigo_e3a228_idx'),
        ),
        migrations.AddIndex(
            model_name='tipoflujodetalle',
            index=models.Index(fields=['tipoflujo'], name='backend_tip_tipoflu_084060_idx'),
        ),
        migrations.AddIndex(
            model_name='tipoinmueble',
            index=models.Index(fields=['codigo'], name='backend_tip_codigo_c3bf67_idx'),
        ),
        migrations.AddIndex(
            model_name='tipologia',
            index=models.Index(fields=['codigo'], name='backend_tip_codigo_2b5b9c_idx'),
        ),
        migrations.AddIndex(
            model_name='tipologia_categorizacion',
            index=models.Index(fields=['codigo'], name='backend_tip_codigo_147a76_idx'),
        ),
        migrations.AddIndex(
            model_name='tipopago',
            index=models.Index(fields=['descripcion'], name='backend_tip_descrip_4666d0_idx'),
        ),
        migrations.AddIndex(
            model_name='tipopared',
            index=models.Index(fields=['codigo'], name='backend_tip_codigo_420757_idx'),
        ),
        migrations.AddIndex(
            model_name='tipotenencia',
            index=models.Index(fields=['codigo'], name='backend_tip_codigo_168d3c_idx'),
        ),
        migrations.AddIndex(
            model_name='tipotransaccion',
            index=models.Index(fields=['codigo'], name='backend_tip_codigo_1bc757_idx'),
        ),
        migrations.AddIndex(
            model_name='topografia',
            index=models.Index(fields=['codigo'], name='backend_top_codigo_87cda5_idx'),
        ),
        migrations.AddIndex(
            model_name='torre',
            index=models.Index(fields=['nombre'], name='backend_tor_nombre_a754b8_idx'),
        ),
        migrations.AddIndex(
            model_name='ubicacion',
            index=models.Index(fields=['codigo'], name='backend_ubi_codigo_694fcf_idx'),
        ),
        migrations.AddIndex(
            model_name='unidadinmueble',
            index=models.Index(fields=['codigo'], name='backend_uni_codigo_106740_idx'),
        ),
        migrations.AddIndex(
            model_name='urbanizacion',
            index=models.Index(fields=['nombre'], name='backend_urb_nombre_8ad17f_idx'),
        ),
        migrations.AddIndex(
            model_name='uso',
            index=models.Index(fields=['codigo'], name='backend_uso_codigo_c20857_idx'),
        ),
        migrations.AddIndex(
            model_name='usoconstruccion',
            index=models.Index(fields=['codigo'], name='backend_uso_codigo_321f66_idx'),
        ),
        migrations.AddIndex(
            model_name='zona',
            index=models.Index(fields=['codigo'], name='backend_zon_codigo_283747_idx'),
        ),
    ]
