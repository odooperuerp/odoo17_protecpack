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
class PleDiaryCashBoxAndBanksLine(models.Model):
	_name='ple.diary.cash.box.and.banks.line'

	#####################################
	ple_diary_cash_box_and_banks_bank_id=fields.Many2one("ple.diary.cash.box.and.banks",string="id PLE",ondelete="cascade")
	ple_diary_cash_box_and_banks_cash_id=fields.Many2one("ple.diary.cash.box.and.banks",string="id PLE",ondelete="cascade")

	company_id = fields.Many2one('res.company',
		string="Compañia", 
		default=lambda self: self.env['res.company']._company_default_get('account.invoice'),
		domain = lambda self: [('id', 'in',[i.id for i in self.env['res.users'].browse(self.env.user.id).company_ids] )])
	
	move_id=fields.Many2one("account.move", string="Asiento contable" , readonly=True )
	move_line_id=fields.Many2one("account.move.line" , string="Apuntes Contables" , readonly=True )

	periodo=fields.Char(string="Periodo PLE",size=8)
	
	diario= fields.Many2one('account.journal',readonly=True, string="Diario")
	periodo_apunte=fields.Char(string="Periodo del apunte contable",compute='_compute_campo_periodo_apunte',
		store=True,readonly=True)
	
	asiento_contable=fields.Char(string="Nombre del asiento contable",compute='_compute_campo_asiento_contable',
		store=True , readonly=True)

	m_correlativo_asiento_contable=fields.Char(string="M-correlativo asiento contable",store=True,readonly=True)

	codigo_cuenta_desagregado_id=fields.Many2one("account.account",string="Código cuenta contable desagregado",
		compute='_compute_campo_codigo_cuenta_desagregado_id',store=True,readonly=True)

	codigo_cuenta_desagregado=fields.Char(string="Código cuenta contable desagregado",
		compute='_compute_campo_codigo_cuenta_desagregado',store=True,readonly=True)

	codigo_unidad_operacion=fields.Char(string="Código unidad operación",default="")

	codigo_centro_costos=fields.Char(string="Código centro de costos",default="")

	tipo_moneda_origen= fields.Char(string="Tipo de Moneda de origen",
		compute='_compute_campo_tipo_moneda_origen',store=True,readonly=True)

	tipo_doc_iden_emisor = fields.Char(string="Tipo Documento Identidad Emisor",
		compute='_compute_campo_tipo_doc_iden_emisor',store=True,readonly=True)

	num_doc_iden_emisor= fields.Char(string="Número Documento Identidad Emisor",
		compute='_compute_campo_num_doc_iden_emisor',store=True,readonly=True)

	tipo_comprobante_pago= fields.Char(string="Tipo de Comprobante Pago",
		compute='_compute_campo_tipo_comprobante_pago',store = True,readonly = True)

	num_serie_comprobante_pago= fields.Char(string="Número serie Comprobante Pago",
		compute='_compute_campo_num_serie_comprobante_pago',store = True,readonly=False)

	num_comprobante_pago= fields.Char(string="Número Comprobante de Pago",compute='_compute_campo_num_comprobante_pago',
		store = True,readonly=False)

	fecha_contable= fields.Date(string="Fecha Contable",compute='_compute_campo_fecha_contable',store=True,readonly=True)

	fecha_vencimiento = fields.Date(string="Fecha de vencimiento",compute='_compute_campo_fecha_vencimiento',
		store=True,readonly=True)

	fecha_operacion = fields.Date(string="Fecha de la operación o emisión",compute='_compute_campo_fecha_operacion',
		store=True,readonly=True)

	glosa = fields.Char(string="Glosa o descripción naturaleza de operación",compute='_compute_campo_glosa',
		store=True,readonly=False,)

	glosa_referencial = fields.Char(string="Glosa referencial" , default="")

	movimientos_debe = fields.Float(string="Movimientos del Debe",compute='_compute_campo_movimientos_debe',
		store=True,readonly=True)

	movimientos_haber =  fields.Float(string="Movimientos del Haber",compute='_compute_campo_movimientos_haber',
		store=True,readonly=True)

	balance = fields.Float(string="Balance",compute='_compute_campo_balance',
		store=True,readonly=True)

	currency_movimientos_debe = fields.Float(string="Movimientos del Debe ME",compute='_compute_campo_currency_movimientos_debe',
		store=True,readonly=True)

	currency_movimientos_haber =  fields.Float(string="Movimientos del Haber ME",compute='_compute_campo_currency_movimientos_haber',
		store=True,readonly=True)

	amount_currency = fields.Float(string="Movimientos ME",compute='_compute_campo_amount_currency',
		store=True,readonly=True)

	dato_estructurado= fields.Char(string="Dato estructurado",compute='_compute_campo_dato_estructurado',
		store=True,readonly=True)

	indicador_estado_operacion= fields.Char(string="Dato estado operación",compute='_compute_campo_indicador_estado_operacion',
		store=True,readonly=True)

	conjunto=fields.Char(string="Libro al que pertenece")
	###############################################################################################################

	codigo_entidad_financiera=fields.Char(string="Código Entidad Financiera de Cuenta Bancaria",
		compute='_compute_campo_codigo_entidad_financiera',store=True,readonly=True)

	codigo_cuenta_bancaria_contribuyente=fields.Char(string="Código Cuenta Bancaria Contribuyente",
		compute='_compute_campo_codigo_cuenta_bancaria_contribuyente',store=True,readonly=True)

	medio_pago_utilizado=fields.Char(string="Medio de pago utilizado en op.bancaria",
		compute='_compute_campo_medio_pago_utilizado',store=True,readonly=True)

	descripcion_operacion_bancaria=fields.Char(string="Descripción operación bancaria",
		compute='_compute_campo_descripcion_operacion_bancaria',store=True,readonly=True)

	apellidos_nombre_o_razon_social_girador_o_beneficiario=fields.Char(string="Nombre o razón social gorador o beneficiario",
		compute='_compute_campo_apellidos_nombre_o_razon_social_girador_o_beneficiario',store=True,readonly=True)

	numero_transaccion_bancaria=fields.Char(string="Número transacción bancaria o doc.sustentatorio",
		compute='_compute_campo_numero_transaccion_bancaria',store=True,readonly=True)

	#######################################################################################################

	@api.depends('move_id')
	def _compute_campo_periodo_apunte(self):
		for rec in self:
			rec.periodo_apunte = False
			if rec.move_id:
				mes = (rec.move_id.date and rec.move_id.date.strftime("%m")) or ''
				if rec.move_id.date:
					rec.periodo_apunte = "%s%s00" % (rec.move_id.date and rec.move_id.date.strftime("%Y") or 'YYYY', mes or 'MM')
				else:
					rec.periodo_apunte = "YYYYMM00"


	@api.depends('move_line_id','diario')
	def _compute_campo_codigo_entidad_financiera(self):
		for rec in self:
			rec.codigo_entidad_financiera = False
			if rec.move_line_id.payment_id:
				rec.codigo_entidad_financiera = rec.move_line_id.payment_id.journal_id.bank_id.bic or ''
			elif rec.diario:
				rec.codigo_entidad_financiera = rec.diario.bank_id.bic or ''
			else:
				rec.codigo_entidad_financiera = ''


	@api.depends('move_line_id','diario')
	def _compute_campo_codigo_cuenta_bancaria_contribuyente(self):
		for rec in self:
			rec.codigo_cuenta_bancaria_contribuyente = False
			if rec.move_line_id.payment_id:
				rec.codigo_cuenta_bancaria_contribuyente=rec.move_line_id.payment_id.journal_id.bank_account_id.acc_number or ''
			elif rec.diario:
				rec.codigo_cuenta_bancaria_contribuyente=rec.diario.bank_account_id.acc_number or ''
			else:
				rec.codigo_cuenta_bancaria_contribuyente= ''


	@api.depends('move_line_id')
	def _compute_campo_medio_pago_utilizado(self):
		for rec in self:
			rec.medio_pago_utilizado = False

			if rec.move_line_id and rec.move_line_id.payment_id and rec.move_line_id.payment_id.sunat_table_01_id:
				rec.medio_pago_utilizado = rec.move_line_id.payment_id.sunat_table_01_id.code or "999"

			else:
				rec.medio_pago_utilizado = "999"				



	@api.depends('move_line_id')
	def _compute_campo_descripcion_operacion_bancaria(self):
		for rec in self:
			rec.descripcion_operacion_bancaria= (rec.move_line_id.payment_id and \
				rec.move_line_id.payment_id.ref) or rec.move_line_id.ref or ''



	@api.depends('move_line_id')
	def _compute_campo_apellidos_nombre_o_razon_social_girador_o_beneficiario(self):
		for rec in self:
			rec.apellidos_nombre_o_razon_social_girador_o_beneficiario = rec.move_line_id.partner_id.name or 'varios'


	@api.depends('move_line_id')
	def _compute_campo_numero_transaccion_bancaria(self):
		for rec in self:
			rec.numero_transaccion_bancaria = False
			if rec.move_line_id:
				rec.numero_transaccion_bancaria=(rec.move_line_id.payment_id and rec.move_line_id.payment_id.operation_number) or \
					rec.move_line_id.operation_number or '-'


	@api.depends('move_id')
	def _compute_campo_asiento_contable(self):
		for rec in self:
			rec.asiento_contable =rec.move_id.name or '-'



	"""@api.depends('move_line_id','move_id')
	def _compute_campo_m_correlativo_asiento_contable(self):
		for rec in self:
			rec.m_correlativo_asiento_contable= False
			if rec.move_id.line_ids:
				indice= sorted([(line.account_id.code,line.id) for line in rec.move_id.line_ids]).index((rec.move_line_id.account_id.code,rec.move_line_id.id))
				rec.m_correlativo_asiento_contable='M' + str(indice+1)"""


	@api.depends('move_line_id')
	def _compute_campo_codigo_cuenta_desagregado_id(self):
		for rec in self:
			rec.codigo_cuenta_desagregado_id = rec.move_line_id.account_id or ''


	@api.depends('codigo_cuenta_desagregado_id')
	def _compute_campo_codigo_cuenta_desagregado(self):
		for rec in self:
			rec.codigo_cuenta_desagregado = rec.codigo_cuenta_desagregado_id.code or ''


	@api.depends('move_id')
	def _compute_campo_tipo_moneda_origen(self):
		for rec in self:
			rec.tipo_moneda_origen = rec.move_id.currency_id.name or ''


	@api.depends('move_id','move_line_id')
	def _compute_campo_tipo_doc_iden_emisor(self):
		for rec in self:
			rec.tipo_doc_iden_emisor = rec.move_line_id.partner_id.l10n_latam_identification_type_id.l10n_pe_vat_code or \
				rec.move_id.partner_id.l10n_latam_identification_type_id.l10n_pe_vat_code or '-'


	@api.depends('move_id','move_line_id')
	def _compute_campo_num_doc_iden_emisor(self):
		for rec in self:
			rec.num_doc_iden_emisor =rec.move_line_id.partner_id.vat or rec.move_id.partner_id.vat or '-'



	@api.depends('move_line_id','conjunto')
	def _compute_campo_tipo_comprobante_pago(self):
		for rec in self:
			rec.tipo_comprobante_pago = False
			if rec.conjunto=='010100':

				if rec.move_line_id:

					rec.tipo_comprobante_pago = (rec.move_line_id.l10n_latam_document_type_id and rec.move_line_id.l10n_latam_document_type_id.code) or '00'
				else:
					rec.tipo_comprobante_pago = '00'

			else:
				rec.tipo_comprobante_pago = ''


	@api.depends('move_line_id','conjunto')
	def _compute_campo_num_serie_comprobante_pago(self):
		for rec in self:
			rec.num_serie_comprobante_pago = False
			
			if rec.conjunto=='010100':
				if rec.move_line_id:
					rec.num_serie_comprobante_pago = (rec.move_line_id and rec.move_line_id.l10n_pe_prefix_code) or \
						(rec.move_line_id.l10n_pe_prefix_code or '')

			else:
				rec.num_serie_comprobante_pago = ''


	@api.depends('move_line_id','conjunto')
	def _compute_campo_num_comprobante_pago(self):
		for rec in self:
			rec.num_comprobante_pago = False

			if rec.conjunto=='010100':
				if rec.move_line_id:
					rec.num_comprobante_pago = (rec.move_line_id and rec.move_line_id.l10n_pe_invoice_number) or \
						(rec.move_line_id.l10n_pe_invoice_number or '-')
			
			else:
				rec.num_comprobante_pago = '-'



	@api.depends('move_line_id')
	def _compute_campo_fecha_contable(self):
		for rec in self:
			rec.fecha_contable = rec.move_line_id.date or ''


	@api.depends('move_line_id')
	def _compute_campo_fecha_vencimiento(self):
		for rec in self:
			rec.fecha_vencimiento = rec.move_line_id.date_maturity or ''


	@api.depends('move_line_id')
	def _compute_campo_fecha_operacion(self):
		for rec in self:
			rec.fecha_operacion = rec.move_line_id.date or ''


	@api.depends('move_line_id')
	def _compute_campo_glosa(self):
		for rec in self:
			rec.glosa= rec.move_line_id.ref or '-'


	@api.depends('move_line_id','diario')
	def _compute_campo_currency_movimientos_debe(self):
		for rec in self:
			rec.currency_movimientos_debe = 0.00
			if rec.conjunto =="010100":
				if rec.diario and rec.diario.currency_id and rec.company_id.currency_id != rec.diario.currency_id:
					amount_currency=rec.move_line_id.amount_currency
					rec.currency_movimientos_debe = round(abs(amount_currency) if amount_currency>=0 else 0.00,2)

			elif rec.conjunto=="010200":
				if rec.diario and rec.diario.currency_id and rec.company_id.currency_id != rec.diario.currency_id:
					amount_currency=rec.move_line_id.amount_currency
					rec.currency_movimientos_debe = round(abs(amount_currency) if amount_currency>=0 else 0.00,2)


	@api.depends('move_line_id','diario')
	def _compute_campo_currency_movimientos_haber(self):
		for rec in self:
			rec.currency_movimientos_haber = 0.00
			if rec.conjunto =="010100":
				if rec.diario and rec.diario.currency_id and rec.company_id.currency_id != rec.diario.currency_id:
					amount_currency=rec.move_line_id.amount_currency
					rec.currency_movimientos_haber = round(abs(amount_currency) if amount_currency<0 else 0.00,2)

			elif rec.conjunto=="010200":
				if rec.diario and rec.diario.currency_id and rec.company_id.currency_id != rec.diario.currency_id:
					amount_currency=rec.move_line_id.amount_currency
					rec.currency_movimientos_haber = round(abs(amount_currency) if amount_currency<0 else 0.00,2)


	@api.depends('currency_movimientos_debe','currency_movimientos_haber')
	def _compute_campo_amount_currency(self):
		for rec in self:
			rec.amount_currency = rec.currency_movimientos_debe - rec.currency_movimientos_haber



	@api.depends('move_line_id')
	def _compute_campo_movimientos_haber(self):
		for rec in self:
			rec.movimientos_haber = round(rec.move_line_id.credit,2)


	@api.depends('move_line_id')
	def _compute_campo_movimientos_debe(self):
		for rec in self:
			rec.movimientos_debe = round(rec.move_line_id.debit,2)


	@api.depends('move_line_id','movimientos_debe','movimientos_haber')
	def _compute_campo_balance(self):
		for rec in self:
			rec.balance = round(rec.move_line_id.debit - rec.move_line_id.credit,2)


	@api.depends('move_line_id','conjunto')
	def _compute_campo_dato_estructurado(self):
		for rec in self:
			rec.dato_estructurado = False
			"""if rec.conjunto in ['010100']:
				dato=''
				valor_campo_3=''
				line= rec.move_line_id.move_id or False
				if line:
					if line.move_type in ['out_invoice' , 'out_refund' ] :
						dato += '140100'
						if tools.getDateYYYYMM(line.date) == tools.getDateYYYYMM(line.invoice_date or line.date):
							if line.state=='cancel':
								valor_campo_3='M2'
							else:
								valor_campo_3='M1'
						elif tools.getDateYYYYMM(line.date) > tools.getDateYYYYMM(line.invoice_date or line.date):
							valor_campo_3='M8'					
					
					elif str(line.partner_id.l10n_latam_identification_type_id.l10n_pe_vat_code)=='0':
						dato += '080200'
						if(tools.getDateYYYYMM(line.date) > tools.getDateYYYYMM(line.invoice_date or line.date)):
							valor_campo_3 ='M9'
						else:
							valor_campo_3 ='M0'

					else:
						dato += '080100'
						
						if(tools.getDateYYYYMM(line.date) > tools.getDateYYYYMM(line.invoice_date or line.date)):
							if(line.amount_tax==0):
								valor_campo_3='M7'
							elif(line.amount_tax>0):
								valor_campo_3='M6'
						elif(tools.getDateYYYYMMDD(line.date ) >= tools.getDateYYYYMMDD(line.invoice_date or line.date)):
							if(line.amount_tax==0):
								valor_campo_3='M0'
							elif(line.amount_tax>0):
								valor_campo_3='M1'

					dato += "&" + str(tools.getDateYYYYMM(line.date)) + "00&" +  str(line.name) + "&" + valor_campo_3
				rec.dato_estructurado=dato"""
			rec.dato_estructurado = ''



	@api.depends('fecha_contable','fecha_operacion','periodo')
	def _compute_campo_indicador_estado_operacion(self):
		for rec in self:
			rec.indicador_estado_operacion = False
			if(rec.fecha_contable):

				#if tools.getDateYYYYMMDD(rec.fecha_contable) >= (rec.periodo or '') :
				if rec.fecha_contable.strftime("%Y%m%d") >= (rec.periodo or ''):
					rec.indicador_estado_operacion='1'
				elif rec.fecha_contable.strftime("%Y%m%d") < (rec.periodo or '') :
					rec.indicador_estado_operacion='8'

			else:
				rec.indicador_estado_operacion='1'


	def _convert_object_date(self, date):
		if date:
			return date.strftime('%d/%m/%Y')
		else:
			return ''