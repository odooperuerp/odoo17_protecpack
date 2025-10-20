
import pytz
import calendar
import base64
from io import BytesIO, StringIO
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta
from odoo.addons import ple_base as tools

import logging
_logger=logging.getLogger(__name__)

class PleFixedAssetLine(models.Model):
	_name='ple.fixed.asset.line'


	ple_fixed_asset_id=fields.Many2one('ple.fixed.asset',string="id PLE FIXED ASSET",
		ondelete="cascade",readonly=True)

	move_id=fields.Many2one('account.move',string="Asiento Contable",readonly=True)
	account_id=fields.Many2one('account.account',string="Cuenta",readonly=True)
	account_asset_id=fields.Many2one('account.asset',string="Activo Fijo",readonly=True)
	periodo=fields.Char(string="Periodo PLE")


	periodo_apunte=fields.Char(string="Periodo del apunte contable",compute='_compute_campo_periodo_apunte',
		store=True,readonly=True)
	asiento_contable = fields.Char(string="Nombre del asiento contable",compute='_compute_campo_asiento_contable',
		store=True,readonly=True)
	m_correlativo_asiento_contable=fields.Char(string="M-correlativo asiento contable",
		compute='_compute_campo_m_correlativo_asiento_contable',store=True,readonly=True)
	codigo_catalogo_existencias_utilizado=fields.Char(string="Código catálogo de existencias Sunat",
		compute='_compute_campo_codigo_catalogo_existencias_utilizado',store=True,readonly=True)
	codigo_propio_activo=fields.Char(string="Código propio Activo Fijo",
		compute='_compute_campo_codigo_propio_activo',store=True,readonly=True)
	codigo_existencias_OSCE=fields.Char(string="Código de existencia de acuerdo a OSCE",
		default='',readonly=True)
	codigo_tipo_activo_fijo=fields.Char(string="Código tipo Activo Fijo",
		compute='_compute_campo_codigo_tipo_activo_fijo',store=True,readonly=True)
	codigo_cuenta_desagregado=fields.Char(string="Código cuenta contable desagregado",
		compute='_compute_campo_codigo_cuenta_desagregado',store=True,readonly=True)
	estado_activo_fijo=fields.Char(string="Estado Activo Fijo",compute='_compute_campo_estado_activo_fijo',
		store=True,readonly=True)
	descripcion_activo_fijo=fields.Char(string="Descripción Activo Fijo",
		compute='_compute_campo_descripcion_activo_fijo',store=True,readonly=True)
	marca_activo_fijo=fields.Char(string="Marca Activo Fijo",compute='_compute_campo_marca_activo_fijo',
		store=True , readonly=True)
	modelo_activo_fijo=fields.Char(string="Modelo Activo Fijo",compute='_compute_campo_modelo_activo_fijo',
		store=True , readonly=True)
	numero_serie_placa_activo=fields.Char(string="Número de serie/Placa Activo Fijo",
		compute='_compute_campo_numero_serie_placa_activo',store=True,readonly=True)
	importe_saldo_inicial_activo_fijo=fields.Float(string="Importe Saldo Inicial",
		compute='_compute_campo_importe_saldo_inicial_activo_fijo',store=True,readonly=True)
	importe_adquisiciones_adiciones=fields.Float(string="Importe Adquisiciones o Adiciones",
		compute='_compute_campo_importe_adquisiciones_adiciones',store=True,readonly=True)
	importe_mejoras=fields.Float(string="Importe Mejoras",compute='_compute_campo_importe_mejoras',
		store=True,readonly=True)
	importe_retiros_bajas=fields.Float(string="Importe Retiros y/o Bajas",
		compute='_compute_campo_importe_retiros_bajas',store=True,readonly=True)
	importe_otros_ajustes=fields.Float(string="Importe Otros Ajustes" , compute='_compute_campo_importe_otros_ajustes',store=True , readonly=True)
	valor_revaluacion_voluntaria_efectuada=fields.Float(string="Valor de Revaluación Voluntaria efectuada",
		compute='_compute_campo_valor_revaluacion_voluntaria_efectuada',store=True,readonly=True)
	valor_revaluacion_efectuada_reorganizacion_sociedades=fields.Float(
		string="Valor de Revaluación Voluntaria efectuada",
		compute='_compute_campo_valor_revaluacion_efectuada_reorganizacion_sociedades',store=True,readonly=True)
	valor_otras_revaluaciones_efectuadas=fields.Float(string="Valor de Revaluacion Voluntaria efectuada",
		compute='_compute_campo_valor_otras_revaluaciones_efectuadas',store=True,readonly=True)
	importe_valor_ajuste_por_inflacion=fields.Float(string="Importe Valor del Ajuste por Inflacion",
		compute='_compute_campo_importe_valor_ajuste_por_inflacion',store=True,readonly=True)
	fecha_adquisicion_activo=fields.Date(string="Fecha Adquisicion Activo Fijo",
		compute='_compute_campo_fecha_adquisicion_activo',store=True,readonly=True)
	fecha_inicio_uso_activo_fijo=fields.Date(string="Fecha Inicio de Uso del Activo Fijo",
		compute='_compute_campo_fecha_inicio_uso_activo_fijo',store=True,readonly=True)
	codigo_metodo_aplicado_calculo_depreciacion=fields.Char(
		string="Codigo del Método aplicado en Cálculo Depreciacion",
		compute='_compute_campo_codigo_metodo_aplicado_calculo_depreciacion',store=True,readonly=True)
	numero_documento_cambio_metodo_depreciacion=fields.Char(
		string="Nº Documento de autorizacion para cambiar Método Depreciacion",
		compute='_compute_campo_numero_documento_cambio_metodo_depreciacion',store=True,readonly=True)
	porcentaje_depreciacion=fields.Float(string="Porcentaje de Depreciacion",
		compute='_compute_campo_porcentaje_depreciacion',store=True,readonly=True)
	depreciacion_acumulada_cierre_ejercicio_anterior=fields.Float(
		string="Depreciacion Acumulada al cierre Ejercicio Anterior",
		compute='_compute_campo_depreciacion_acumulada_cierre_ejercicio_anterior',store=True,readonly=True)
	valor_depreciacion_ejercicio_sin_considerar_revaluacion=fields.Float(
		string="Valor Depreciacion ejercicio sin considerar revaluacion",
		compute='_compute_campo_valor_depreciacion_ejercicio_sin_considerar_revaluacion',store=True,readonly=True)
	valor_depreciacion_ejercicio_relacionada_con_retiros_bajas=fields.Float(
		string="Valor Depreciacion Ejercicio Relacionada con retiros y/o bajas",
		compute='_compute_campo_valor_depreciacion_ejercicio_relacionada_con_retiros_bajas',store=True,readonly=True)
	valor_depreciacion_relacionada_con_otros_ajustes=fields.Float(
		string="Valor Depreciacion Relacionada con Otros Ajustes",
		compute='_compute_campo_valor_depreciacion_relacionada_con_otros_ajustes',store=True,readonly=True)
	valor_depreci_de_revaluaci_efectuada_reorgani_soci=fields.Float(
		string="Valor Depreciacion de Revaluacion efectuada por Reorganizacion de Sociedades",
		compute='_compute_campo_valor_depreci_de_revaluaci_efectuada_reorgani_soci',store=True,readonly=True)
	valor_depreciacion_otras_revaluaciones_efectuadas=fields.Float(
		string="Valor Depreciacion de otras Revaluaciones Efectuadas",
		compute='_compute_campo_valor_depreciacion_otras_revaluaciones_efectuadas',store=True,readonly=True)
	valor_ajuste_por_inflacion_de_depreciacion=fields.Float(string="Valor Ajuste por inflacion de Depreciacion",
		compute='_compute_campo_Valor_ajuste_por_inflacion_de_depreciacion',store=True,readonly=True)
	estado_operacion=fields.Char(string="Estado de la operacion",compute='_compute_campo_estado_operacion',
		store=True,readonly=True)



	@api.depends('move_id')
	def _compute_campo_periodo_apunte(self):
		for rec in self:
			if rec.move_id:
				mes=(rec.move_id.date and rec.move_id.date.month or '')
				rec.periodo_apunte = "%s%s00" % (
					rec.move_id.date.year or 'YYYY',
					('0' + str(mes) if mes<10 else str(mes)) or 'MM')


	
	@api.depends('move_id')
	def _compute_campo_asiento_contable(self):
		for rec in self:
			if rec.move_id:
				rec.asiento_contable =rec.move_id.name or ''

	
	@api.depends('move_id')
	def _compute_campo_m_correlativo_asiento_contable(self):
		for rec in self:
			if rec.move_id:
				rec.m_correlativo_asiento_contable = "M1"

	
	@api.depends('account_asset_id')
	def _compute_campo_codigo_catalogo_existencias_utilizado(self):
		for rec in self:
			rec.codigo_catalogo_existencias_utilizado = rec.account_asset_id.asset_encoding_type_sunat or ''


	
	@api.depends('account_asset_id')
	def _compute_campo_codigo_propio_activo(self):
		for rec in self:
			rec.codigo_propio_activo = rec.account_asset_id.asset_code or ''


	
	@api.depends('account_asset_id')
	def _compute_campo_codigo_existencias_OSCE(self):
		for rec in self:
			rec.codigo_existencias_OSCE = rec.account_asset_id.fixed_asset_type_sunat or ''


	
	@api.depends('account_asset_id')
	def _compute_campo_codigo_tipo_activo_fijo(self):
		for rec in self:
			rec.codigo_tipo_activo_fijo=''


	@api.depends('account_asset_id')
	def _compute_campo_codigo_cuenta_desagregado(self):
		for rec in self:
			rec.codigo_cuenta_desagregado=rec.account_id.code or ''


	# 1 ACTIVOS EN DESUSO
	# 2 ACTIVOS OBSOLETOS
	# 9 RESTO DE ACTIVOS

	
	@api.depends('account_asset_id')
	def _compute_campo_estado_activo_fijo(self):
		for rec in self:
			rec.estado_activo_fijo=\
				'9' if rec.account_asset_id.state=='open' else '2' if rec.account_asset_id.state=='close' else '1'


	
	@api.depends('account_asset_id')
	def _compute_campo_descripcion_activo_fijo(self):
		for rec in self:
			rec.descripcion_activo_fijo=rec.account_asset_id.name or ''


	
	@api.depends('account_asset_id')
	def _compute_campo_marca_activo_fijo(self):
		for rec in self:
			rec.marca_activo_fijo=rec.account_asset_id.brand_id and rec.account_asset_id.brand_id.name or ''


	
	@api.depends('account_asset_id')
	def _compute_campo_modelo_activo_fijo(self):
		for rec in self:
			rec.modelo_activo_fijo=rec.account_asset_id.model_id and rec.account_asset_id.model_id.name or ''


	
	@api.depends('account_asset_id')
	def _compute_campo_numero_serie_placa_activo(self):
		for rec in self:
			rec.numero_serie_placa_activo=rec.account_asset_id.serial_number_plate or ''


	##########################################################################################
	@api.depends('account_asset_id')
	def _compute_campo_importe_saldo_inicial_activo_fijo(self):
		for rec in self:
			if rec.account_asset_id:
				saldo_inicial_activo_fijo = rec.account_asset_id.original_value - rec.account_asset_id.salvage_value
				
				if rec.account_asset_id.currency_id and rec.account_asset_id.currency_id != rec.account_asset_id.company_id.currency_id:

					saldo_inicial_activo_fijo = rec.account_asset_id.currency_id._convert(saldo_inicial_activo_fijo,
						rec.account_asset_id.company_id.currency_id,rec.account_asset_id.company_id,
						rec.account_asset_id.date or rec.account_asset_id.first_depreciation_manual_date or fields.Date.today())

				rec.importe_saldo_inicial_activo_fijo = saldo_inicial_activo_fijo
	##########################################################################################
	
	@api.depends('account_asset_id')
	def _compute_campo_importe_adquisiciones_adiciones(self):
		for rec in self:
			rec.importe_adquisiciones_adiciones=0.0

	
	@api.depends('account_asset_id')
	def _compute_campo_importe_mejoras(self):
		for rec in self:
			rec.importe_mejoras=0.0

	
	@api.depends('account_asset_id')
	def _compute_campo_importe_retiros_bajas(self):
		for rec in self:
			rec.importe_retiros_bajas=0.0

	
	@api.depends('account_asset_id')
	def _compute_campo_importe_otros_ajustes(self):
		for rec in self:
			rec.importe_otros_ajustes=0.0

	
	@api.depends('account_asset_id')
	def _compute_campo_valor_revaluacion_voluntaria_efectuada(self):
		for rec in self:
			rec.valor_revaluacion_voluntaria_efectuada=0.0

	
	@api.depends('account_asset_id')
	def _compute_campo_valor_revaluación_efectuada_reorganizacion_sociedades(self):
		for rec in self:
			rec.valor_revaluación_efectuada_reorganizacion_sociedades=0.0

	
	@api.depends('account_asset_id')
	def _compute_campo_valor_otras_revaluaciones_efectuadas(self):
		for rec in self:
			rec.valor_otras_revaluaciones_efectuadas=0.0

	
	@api.depends('account_asset_id')
	def _compute_campo_importe_valor_ajuste_por_inflacion(self):
		for rec in self:
			rec.importe_valor_ajuste_por_inflacion=0.0


	@api.depends('account_asset_id')
	def _compute_campo_fecha_adquisicion_activo(self):
		for rec in self:
			rec.fecha_adquisicion_activo=rec.account_asset_id.acquisition_date or False

	
	@api.depends('account_asset_id')
	def _compute_campo_fecha_inicio_uso_activo_fijo(self):
		for rec in self:
			rec.fecha_inicio_uso_activo_fijo = rec.account_asset_id.prorata_date or False			


	@api.depends('account_asset_id')
	def _compute_campo_codigo_metodo_aplicado_calculo_depreciacion(self):
		for rec in self:
			metodo=rec.account_asset_id.method
			if metodo=='linear':
				rec.codigo_metodo_aplicado_calculo_depreciacion= '1'
			else:
				rec.codigo_metodo_aplicado_calculo_depreciacion= '9'


	
	@api.depends('account_asset_id')
	def _compute_campo_numero_documento_cambio_metodo_depreciacion(self):
		for rec in self:
			rec.numero_documento_cambio_metodo_depreciacion =\
				rec.account_asset_id.document_number_for_depreciation_method_change or ''


	###############################################################
	
	@api.depends('account_asset_id')
	def _compute_campo_porcentaje_depreciacion(self):
		for rec in self:
		
			frec_anual = 0

			if int(rec.account_asset_id.method_period) == 1:
				frec_anual = 12.00
			elif int(rec.account_asset_id.method_period) == 12:
				frec_anual = 1.00

			porcentaje_anual = round(frec_anual/rec.account_asset_id.method_number*100.00)

			rec.porcentaje_depreciacion = porcentaje_anual or 0

	#################################################################

	
	@api.depends('account_asset_id','periodo')
	def _compute_campo_depreciacion_acumulada_cierre_ejercicio_anterior(self):
		for rec in self:

			if rec.account_asset_id and rec.account_asset_id.depreciation_move_ids and rec.periodo:

				anio_cierre = rec.periodo[:4]
				string_cierre = "%s0101"%(anio_cierre)
				
				acum = sum(rec.account_asset_id.depreciation_move_ids.\
					filtered(lambda r:r.date.strftime("%Y%m%d") < string_cierre).mapped('depreciation_value'))
				rec.depreciacion_acumulada_cierre_ejercicio_anterior = acum
			else:
				rec.depreciacion_acumulada_cierre_ejercicio_anterior = 0.00
	##################################################################

	
	@api.depends('account_asset_id','periodo','ple_fixed_asset_id')
	def _compute_campo_valor_depreciacion_ejercicio_sin_considerar_revaluacion(self):
		for rec in self:
			if rec.account_asset_id and rec.account_asset_id.depreciation_move_ids and rec.periodo and rec.ple_fixed_asset_id.date_to:
				infimo = "%s0101"%(rec.periodo[:4])
				supremo = rec.ple_fixed_asset_id.date_to.strftime("%Y%m%d")

				cum = sum([line.depreciation_value for line in rec.account_asset_id.depreciation_move_ids if tools.getDateYYYYMMDD(line.date)>=infimo and tools.getDateYYYYMMDD(line.date)<=supremo])
				rec.valor_depreciacion_ejercicio_sin_considerar_revaluacion = cum
			else:
				rec.valor_depreciacion_ejercicio_sin_considerar_revaluacion = 0.00
	###################################################################

	
	@api.depends('account_asset_id')
	def _compute_campo_valor_depreciacion_ejercicio_relacionada_con_retiros_bajas(self):
		for rec in self:
			rec.valor_depreciacion_ejercicio_relacionada_con_retiros_bajas=0.00


	
	@api.depends('account_asset_id')
	def _compute_campo_valor_depreciacion_relacionada_con_otros_ajustes(self):
		for rec in self:
			rec.valor_depreciacion_relacionada_con_otros_ajustes=0.0


	
	@api.depends('account_asset_id')
	def _compute_campo_valor_depreci_de_revaluaci_efectuada_reorgani_soci(self):
		for rec in self:
			rec.valor_depreci_de_revaluaci_efectuada_reorgani_soci=0.0


	
	@api.depends('account_asset_id')
	def _compute_campo_valor_depreciacion_otras_revaluaciones_efectuadas(self):
		for rec in self:
			rec.valor_depreciacion_otras_revaluaciones_efectuadas=0.0


	
	@api.depends('account_asset_id')
	def _compute_campo_valor_ajuste_por_inflacion_de_depreciacion(self):
		for rec in self:
			rec.valor_ajuste_por_inflacion_de_depreciacion=0.0


	
	@api.depends('account_asset_id')
	def _compute_campo_estado_operacion(self):
		for rec in self:
			rec.estado_operacion='1'