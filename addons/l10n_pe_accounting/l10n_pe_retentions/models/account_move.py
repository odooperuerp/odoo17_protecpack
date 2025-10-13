# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError
from odoo.tools import float_is_zero, float_compare
from datetime import datetime, timedelta

import logging
_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
	_inherit = 'account.move'

	retention_company_currency_id=fields.Many2one('res.currency',string="Moneda de la Compañia",
		default=lambda self: self.env['res.company']._company_default_get('account.invoice').currency_id)

	account_invoice_retention_ids = fields.Many2many('account.invoice.retention', 
		string="Registros de Retención de la Factura",readonly=True)

	is_retention=fields.Boolean(string="Documento sujeto a Retención",compute="_compute_retention",default=False)
	
	retention_percentaje=fields.Float(default=lambda self: float(self.env['ir.config_parameter'].sudo().get_param('retention_percentaje')),
		copy=False,string="% Retención ")
	
	amount_min_retention = fields.Monetary(default=lambda self: float(self.env['ir.config_parameter'].sudo().get_param('amount_min_retention')),
		copy=False,string="Monto Mínimo Retención")
 
	retention_amount = fields.Monetary(string="Monto de Retención", compute="_compute_retention_amount", store=True)


	@api.depends('amount_total', 'retention_percentaje','invoice_line_ids', 'invoice_line_ids.quantity','invoice_line_ids.price_unit', 'invoice_line_ids.tax_ids','is_retention')
	def _compute_retention_amount(self):
		for rec in self:
			if rec.is_retention:
				rec.retention_amount = rec.amount_total * (rec.retention_percentaje / 100)
			else:
				rec.retention_amount = 0.00
    
 

	@api.depends(
		'company_id',
		'company_id.is_retention_agent',
		'company_id.currency_id',
		'company_id.is_perception_agent',
		'company_id.is_good_taxpayer',
		'amount_total',
		'retention_percentaje',
		'amount_min_retention',
		'partner_id.is_retention_agent',
		'total_sale_igv',
		'invoice_date',
		'currency_id')
	def _compute_retention(self):
		for rec in self:
			rec.is_retention = False
			if rec.total_sale_igv:
				if rec.partner_id.is_retention_agent:
					if not(rec.company_id.is_retention_agent or rec.company_id.is_perception_agent or rec.company_id.is_good_taxpayer):
						
						aux_amount_in_company_currency = 0.00

						if rec.currency_id and rec.currency_id != rec.company_id.currency_id:
							aux_amount_in_company_currency = rec.currency_id._convert(rec.amount_total,
								rec.company_id.currency_id,rec.company_id,rec.invoice_date or fields.Date.context_today(rec))

						elif rec.currency_id:
							aux_amount_in_company_currency = rec.amount_total

						if aux_amount_in_company_currency > rec.amount_min_retention:
							rec.is_retention=True
	###########################################################################################################

	def action_open_account_invoice_retention_ids(self):
		#self.ensure_one()
		#view = self.env.ref('l10n_pe_retentions.account_invoice_retention_view_tree')
		if self.account_invoice_retention_ids:

			return {
				'name': 'Registros de Retención',
				'view_mode': 'tree,form',
				'res_model': 'account.invoice.retention',
				'view_id': False,
				#'views': [(view.id, 'tree')],
				'type': 'ir.actions.act_window',
				"domain":[('id','in',
					list(self.account_invoice_retention_ids.mapped('id')) or [])],
				'context': {'company_id': self.company_id.id}}



class AccountMoveLine(models.Model):
	_inherit = "account.move.line"

	is_retention = fields.Char(string="Es Retencion", copy=False)
	invoice_retention_id = fields.Many2one('account.invoice.retention',string="Registro Retención",copy=False)

	@api.model
	def _compute_amount_fields(self, amount, src_currency, company_currency):

		amount_currency = False
		currency_id = False
		date = self.env.context.get('date') or fields.Date.today()
		company = self.env.context.get('company_id')
		company = self.env['res.company'].browse(company) if company else self.env.user.company_id
		
		if src_currency and src_currency != company_currency:
			amount_currency = amount
			amount = src_currency._convert(amount, company_currency, company, date)
			currency_id = src_currency
		else:
			amount_currency = amount
			currency_id = company_currency

		debit = amount > 0 and amount or 0.0
		credit = amount < 0 and -amount or 0.0
		return debit, credit, amount_currency, currency_id