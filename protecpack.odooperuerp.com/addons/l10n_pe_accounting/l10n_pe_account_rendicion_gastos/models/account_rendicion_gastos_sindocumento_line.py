# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError , ValidationError
import logging
from itertools import *
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)


class  AccountRendicionGastosSinDocumentoLine(models.Model):

	_name = 'account.rendicion.gastos.sindocumento.line'
	_description = "Registro de Rendición de Gastos sin Documento"


	rendicion_gastos_id = fields.Many2one('account.rendicion.gastos',string="Gastos sin Documento a Rendir",readonly=False,ondelete="cascade")

	gasto_account_id=fields.Many2one('account.account',string="Cuenta de Gasto",required=True)
	descripcion_gasto=fields.Char(string="Descripción Gasto")
	date_emision= fields.Date(string="Fecha Gasto",required=True)
	partner_id=fields.Many2one('res.partner',string="Proveedor")
	
	currency_id=fields.Many2one('res.currency',string="Moneda del Gasto",
		default=lambda self: self.env['res.company']._company_default_get('account.invoice').currency_id)

	company_currency_id=fields.Many2one('res.currency',string="Moneda de Compañia",
		compute="compute_campo_company_currency_id",store=True)
	
	amount_total = fields.Monetary(string="Monto Gasto", currency_field="currency_id",required=True)
	
	amount_total_company_currency= fields.Monetary(string="Monto Gasto en MN", 
		currency_field="company_currency_id",
		compute="compute_campo_amount_total_company_currency",store=True)

	
	balance_sign = fields.Integer(string="Debe/Haber",compute="compute_campo_balance_sign",store=True)

	###################################################################################################
	analytic_distribution = fields.Json('Distribución Analítica',
		compute="_compute_analytic_distribution", store=True, copy=True, readonly=False,
		precompute=True)

	analytic_distribution_search = fields.Json(store=False,search="_search_analytic_distribution")

	analytic_precision = fields.Integer(store=False,
		default=lambda self: self.env['decimal.precision'].precision_get("Percentage Analytic"))


	def _compute_analytic_distribution(self):
		pass


	def _search_analytic_distribution(self, operator, value):
		if operator not in ['=', '!=', 'ilike', 'not ilike'] or not isinstance(value, (str, bool)):
			raise UserError(_('Operation not supported'))

		operator_name_search = '=' if operator in ('=', '!=') else 'ilike'
		account_ids = list(self.env['account.analytic.account']._name_search(name=value, operator=operator_name_search))

		query = f"""
			SELECT id
			FROM {self._table}
			WHERE analytic_distribution ?| array[%s]
			"""
		operator_inselect = 'inselect' if operator in ('=', 'ilike') else 'not inselect'
		return [('id', operator_inselect, (query, [[str(account_id) for account_id in account_ids]]))]

	###################################################################################################

	@api.depends('rendicion_gastos_id','rendicion_gastos_id.company_id')
	def compute_campo_company_currency_id(self):
		for rec in self:
			if rec.rendicion_gastos_id and rec.rendicion_gastos_id.company_id:
				rec.company_currency_id = rec.rendicion_gastos_id.company_id.currency_id or False
			else:
				rec.company_currency_id = False



	@api.depends('currency_id',
		'date_emision',
		'rendicion_gastos_id.rendicion_date',
		'company_currency_id',
		'amount_total')
	def compute_campo_amount_total_company_currency(self):
		for rec in self:
			if rec.rendicion_gastos_id.rendicion_date and rec.currency_id and (rec.currency_id != rec.company_currency_id):
				rec.amount_total_company_currency =abs(rec.currency_id._convert(rec.amount_total,rec.company_currency_id,
					self.env['res.company']._company_default_get('account.invoice'),rec.rendicion_gastos_id.rendicion_date))

			else:
				rec.amount_total_company_currency = abs(rec.amount_total)


	@api.depends('amount_total')
	def compute_campo_balance_sign(self):
		for rec in self:
			rec.balance_sign = +1 if rec.amount_total>=0 else -1