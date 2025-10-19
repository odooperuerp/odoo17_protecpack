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

class PleInventariosBalancesDetalleSaldoCuenta10Line(models.Model):
	_name='ple.inventarios.balances.3.2.line'

	ple_inventarios_balances_3_2_id=fields.Many2one("ple.inventarios.balances.3.2",string="id PLE",
		ondelete="cascade",readonly=True)
	
	periodo=fields.Char(string="Periodo PLE",readonly=True)
	account_id=fields.Many2one("account.account",string="Cuenta",readonly=True)
	codigo_cuenta_desagregado=fields.Char(string="Código Cuenta Desagregado",readonly=True,
		compute="compute_campo_codigo_cuenta_desagregado", store=True)
	denominacion_cuenta=fields.Char(string="Denominación Cuenta",readonly=True,
		compute="compute_campo_denominacion_cuenta", store=True)

	codigo_entidad_financiera = fields.Char(string="Código Entidad Financiera",readonly=True,
		compute="compute_campo_codigo_entidad_financiera", store=True)
	numero_cuenta_entidad = fields.Char(string="Número de Cuenta en Entidad Financiera",readonly=True,
		compute="compute_campo_numero_cuenta_entidad", store=True)

	currency_id = fields.Many2one('res.currency',string="Moneda",
		compute="compute_campo_currency_id", store=True)
	tipo_moneda_de_cuenta = fields.Char(string="Tipo de Moneda de Cuenta",
		compute="compute_campo_tipo_moneda_de_cuenta", store=True)
	saldo_deudor_cuenta = fields.Float(string="Saldo Deudor Cuenta",readonly=True,
		compute="compute_campo_saldo_deudor_cuenta", store=True)
	saldo_acreedor_cuenta = fields.Float(string="Saldo Acreedor Cuenta",readonly=True,
		compute="compute_campo_saldo_acreedor_cuenta", store=True)

	indicador_estado_operacion=fields.Char(string="Estado Operación",readonly=True,
		compute="compute_campo_estado_operacion", store=True)


	@api.depends('account_id')
	def compute_campo_codigo_cuenta_desagregado(self):
		for rec in self:
			if rec.account_id:
				rec.codigo_cuenta_desagregado = rec.account_id.code or ''


	@api.depends('account_id')
	def compute_campo_denominacion_cuenta(self):
		for rec in self:
			if rec.account_id:
				rec.denominacion_cuenta = rec.account_id.name or ''


	@api.depends('account_id')
	def compute_campo_codigo_entidad_financiera(self):
		for rec in self:
			if rec.account_id:
				journal_id = self.env['account.journal'].search([('default_account_id','=',rec.account_id.id)],limit=1)
				if journal_id:
					rec.codigo_entidad_financiera = journal_id.bank_id.code_sunat or ''


	@api.depends('account_id')
	def compute_campo_numero_cuenta_entidad(self):
		for rec in self:
			if rec.account_id:
				journal_id = self.env['account.journal'].search([('default_account_id','=',rec.account_id.id)],limit=1)
				if journal_id:
					rec.numero_cuenta_entidad = journal_id.bank_account_id.acc_number or ''


	@api.depends('account_id')
	def compute_campo_currency_id(self):
		for rec in self:
			if rec.account_id:
				rec.currency_id = rec.account_id.currency_id or rec.ple_inventarios_balances_3_2_id.company_id.currency_id


	@api.depends('account_id','currency_id')
	def compute_campo_tipo_moneda_de_cuenta(self):
		for rec in self:
			if rec.account_id and rec.currency_id:
				rec.tipo_moneda_de_cuenta = rec.currency_id.name or ''


	@api.depends('account_id')
	def compute_campo_indicador_estado_operacion(self):
		for rec in self:
			rec.indicador_estado_operacion ='1'