# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError , ValidationError
import logging
from itertools import *
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)


class  AccountRendicionCajaChicaLine(models.Model):
	_name = 'account.rendicion.caja.chica.line'
	_description = "Registro de Rendición de Caja Chica"

	company_id = fields.Many2one('res.company',
		string="Compañia",
		default=lambda self: self.env['res.company']._company_default_get('account.invoice'),
		domain=lambda self: [('id', 'in', [i.id for i in self.env['res.users'].browse(self.env.user.id).company_ids])],
		compute="compute_campo_company_id",store=True)


	rendicion_caja_chica_id = fields.Many2one('account.rendicion.caja.chica',string="Documento a Rendir",
		readonly=False,ondelete="cascade")

	invoice_id= fields.Many2one('account.move',string="Factura a Rendir",
		domain="[('move_type', 'in',['in_invoice','in_refund']),('state','in',['posted']),('payment_state','in',['not_paid','partial'])]")

	tipo_doc_id=fields.Many2one('l10n_latam.document.type',string="Tipo de Documento",
		compute="compute_campo_tipo_doc_id",store=True)

	l10n_pe_prefix_code= fields.Char(string="Número de serie",compute="compute_campo_invoice_details",store=True)
	l10n_pe_invoice_number= fields.Char(string="Número de Documento",compute="compute_campo_invoice_details",store=True)
	date_emision= fields.Date(string="Fecha Emisión Documento",compute="compute_campo_invoice_details",store=True)
	partner_id=fields.Many2one('res.partner',string="Proveedor",compute="compute_campo_invoice_details",store=True)
	invoice_currency_id=fields.Many2one('res.currency',string="Moneda del Documento",
		compute="compute_campo_invoice_details",store=True)

	company_currency_id=fields.Many2one('res.currency',string="Moneda de Compañia",
		compute="compute_campo_company_currency_id",store=True)
	
	amount_total = fields.Monetary(string="Monto Total", currency_field="invoice_currency_id",
		compute="compute_campo_amounts",store=True)

	amount_residual_currency= fields.Monetary(string="Saldo en ME", currency_field="invoice_currency_id",
		compute="compute_campo_amounts",store=True)

	amount_residual_company_currency= fields.Monetary(string="Saldo en MN", currency_field="company_currency_id",
		compute="compute_campo_amounts",store=True)


	amount_total_rendir_currency = fields.Monetary(string="Monto a Rendir", currency_field="invoice_currency_id", default=0.00)
	amount_total_rendir_company_currency = fields.Monetary(string="Monto a Rendir en MN", currency_field="company_currency_id", 
		compute="compute_campo_amount_total_rendir_company_currency",store=True)

	balance_sign = fields.Integer(string="Debe/Haber",compute="compute_campo_amounts",store=True)
	############################################################################################
	invoice_aml_id = fields.Many2one('account.move.line',string="Apunte Contable Factura Gasto",
		compute="compute_campo_invoice_aml_id",store=True)



	@api.depends('invoice_id','invoice_id.journal_id')
	def compute_campo_tipo_doc_id(self):
		for rec in self:
			if rec.invoice_id and rec.invoice_id.l10n_latam_document_type_id:
				rec.tipo_doc_id = rec.invoice_id.l10n_latam_document_type_id or False
			else:
				rec.tipo_doc_id = False


	@api.depends('invoice_id','invoice_id.l10n_pe_prefix_code','invoice_id.l10n_pe_invoice_number','invoice_id.invoice_date',
		'invoice_id.partner_id','invoice_id.currency_id')
	def compute_campo_invoice_details(self):
		for rec in self:
			if rec.invoice_id:
				rec.l10n_pe_prefix_code = rec.invoice_id.l10n_pe_prefix_code or False
				rec.l10n_pe_invoice_number = rec.invoice_id.l10n_pe_invoice_number or False
				rec.date_emision = rec.invoice_id.invoice_date or False
				rec.partner_id = rec.invoice_id.partner_id or False
				rec.invoice_currency_id = rec.invoice_id.currency_id or False



	@api.depends('company_id')
	def compute_campo_company_id(self):
		for rec in self:
			rec.company_id = self.env['res.company']._company_default_get('account.invoice')


	@api.depends('company_id')
	def compute_campo_company_currency_id(self):
		for rec in self:
			if rec.company_id:
				rec.company_currency_id = rec.company_id.currency_id or False
			else:
				rec.company_currency_id = False



	@api.depends(
		'invoice_id',
		'invoice_currency_id',
		'rendicion_caja_chica_id',
		'rendicion_caja_chica_id.company_id',
		'rendicion_caja_chica_id.company_id.currency_id',
		'rendicion_caja_chica_id.rendicion_date',
		'company_currency_id')
	def compute_campo_amounts(self):
		for rec in self:
			if rec.invoice_id:

				aml_id = rec.invoice_id.line_ids.filtered(lambda r: r.account_id.account_type == 'liability_payable')[0]
				residual_signed=aml_id.amount_residual_currency
				residual_company_signed=aml_id.amount_residual
				amount_currency=aml_id.amount_currency or 0.00
				rec.balance_sign = +1 if aml_id.balance>=0.00 else -1

				if rec.invoice_currency_id and (rec.invoice_currency_id != rec.company_currency_id):
					rec.amount_residual_company_currency = abs(rec.invoice_currency_id._convert(residual_signed,rec.company_currency_id,
						self.env['res.company']._company_default_get('account.invoice'), rec.invoice_id.invoice_date))
					rec.amount_residual_currency = abs(residual_signed)
					rec.amount_total = abs(amount_currency)
				else:
					rec.amount_residual_company_currency = abs(residual_company_signed)
					rec.amount_residual_currency = 0.00
					#abs(residual_company_signed)
					rec.amount_total = abs(aml_id.balance)




	@api.depends('invoice_id')
	def compute_campo_invoice_aml_id(self):
		for rec in self:
			if rec.invoice_id:
				aml_id = rec.invoice_id.line_ids.filtered(lambda r: r.account_id.account_type == 'liability_payable')[0]
				rec.invoice_aml_id=aml_id

	############################################################################################################

	@api.onchange(
		'invoice_id',
		'amount_residual_currency',
		'amount_residual_company_currency',
		'invoice_currency_id',
		'company_currency_id')
	def onchange_amount_total_rendir_currency(self):
		for rec in self:
			if rec.invoice_id:
				if rec.invoice_currency_id and rec.invoice_currency_id != rec.company_currency_id:
					rec.amount_total_rendir_currency = rec.amount_residual_currency
				else:
					rec.amount_total_rendir_currency = rec.amount_residual_company_currency



	@api.depends('invoice_id',
		'amount_total_rendir_currency',
		'invoice_currency_id',
		'company_currency_id',
		'rendicion_caja_chica_id.rendicion_date')
	def compute_campo_amount_total_rendir_company_currency(self):
		for rec in self:
			if rec.rendicion_caja_chica_id.rendicion_date and rec.invoice_id:
				if rec.invoice_currency_id and rec.invoice_currency_id != rec.company_currency_id:

					rec.amount_total_rendir_company_currency = rec.invoice_currency_id._convert(rec.amount_total_rendir_currency,rec.company_currency_id,
						self.env['res.company']._company_default_get('account.invoice'),rec.rendicion_caja_chica_id.rendicion_date)
				else:
					rec.amount_total_rendir_company_currency = rec.amount_total_rendir_currency
	############################################################################################################