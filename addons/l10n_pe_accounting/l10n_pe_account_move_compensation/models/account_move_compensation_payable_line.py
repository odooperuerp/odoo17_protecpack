# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError , ValidationError
import logging
from itertools import *
from datetime import datetime, timedelta


_logger = logging.getLogger(__name__)


class AccountMoveCompensationPayableLine(models.Model):
	_name = 'account.move.compensation.payable.line'
	_description = "Documentos por Pagar a Compensar"

	account_move_compensation_payable_id = fields.Many2one('account.move.compensation',
		string="Cuentas por Pagar a Compensar",
		readonly=False,ondelete="cascade")


	invoice_aml_id= fields.Many2one('account.move.line',string="Documento")

	partner_id = fields.Many2one('res.partner',string="Proveedor",
		compute="compute_campo_invoice_details",store=True)

	tipo_doc_id = fields.Many2one('l10n_latam.document.type',string="Tipo de Documento",
		compute="compute_campo_tipo_doc_id",store=True)

	prefix_code= fields.Char(string="Número de serie",compute="compute_campo_invoice_details",store=True)
	invoice_number= fields.Char(string="Número de Documento",compute="compute_campo_invoice_details",store=True)
	date_emision= fields.Date(string="Fecha Emisión Documento",compute="compute_campo_invoice_details",store=True)
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
	amount_compensation = fields.Monetary(string="Monto a Compensar en Moneda Documento",currency_field="invoice_currency_id")
	amount_compensation_company_currency = fields.Monetary(string="Monto a Compensar en MN",currency_field="company_currency_id",
		compute="compute_campo_amount_compensation_company_currency",store=True)
	#####################
				

	
	@api.depends('invoice_aml_id','invoice_aml_id.l10n_latam_document_type_id')
	def compute_campo_tipo_doc_id(self):
		for rec in self:
			if rec.invoice_aml_id and rec.invoice_aml_id.l10n_latam_document_type_id:
				rec.tipo_doc_id = rec.invoice_aml_id.l10n_latam_document_type_id or False
			else:
				rec.tipo_doc_id = False


	
	@api.depends('invoice_aml_id','invoice_aml_id.l10n_pe_prefix_code','invoice_aml_id.l10n_pe_invoice_number','invoice_aml_id.move_id.invoice_date',
		'invoice_aml_id.partner_id','invoice_aml_id.currency_id')
	def compute_campo_invoice_details(self):
		for rec in self:
			if rec.invoice_aml_id:
				rec.partner_id = rec.invoice_aml_id.partner_id or False
				rec.prefix_code = rec.invoice_aml_id.l10n_pe_prefix_code or False
				rec.invoice_number = rec.invoice_aml_id.l10n_pe_invoice_number or False
				rec.date_emision = rec.invoice_aml_id.move_id.invoice_date or False
				rec.invoice_currency_id = rec.invoice_aml_id.currency_id or False


	
	@api.depends('account_move_compensation_payable_id','account_move_compensation_payable_id.company_id')
	def compute_campo_company_currency_id(self):
		for rec in self:
			if rec.account_move_compensation_payable_id and rec.account_move_compensation_payable_id.company_id:
				rec.company_currency_id = rec.account_move_compensation_payable_id.company_id.currency_id or False
			else:
				rec.company_currency_id = False



	
	@api.depends('invoice_aml_id','invoice_aml_id.move_id','invoice_currency_id','company_currency_id')
	def compute_campo_amounts(self):
		for rec in self:
			if rec.invoice_aml_id and rec.invoice_aml_id.move_id:

				if rec.invoice_currency_id and (rec.invoice_currency_id != rec.company_currency_id):

					rec.amount_residual_company_currency = abs(rec.invoice_aml_id.amount_residual)
					rec.amount_residual_currency = abs(rec.invoice_aml_id.amount_residual_currency)
					rec.amount_total = abs(rec.invoice_aml_id.amount_currency)
				else:
					rec.amount_residual_company_currency = abs(rec.invoice_aml_id.amount_residual)
					rec.amount_residual_currency = 0.00
					rec.amount_total = abs(rec.invoice_aml_id.balance)

	###################################################################################################

	
	@api.depends('account_move_compensation_payable_id','account_move_compensation_payable_id.compensation_date',
		'invoice_aml_id','invoice_currency_id','company_currency_id','amount_compensation')
	def compute_campo_amount_compensation_company_currency(self):
		for rec in self:
			if rec.invoice_currency_id and (rec.invoice_currency_id != rec.company_currency_id) and rec.account_move_compensation_payable_id.compensation_date:

				rec.amount_compensation_company_currency = abs(rec.invoice_currency_id._convert(rec.amount_compensation or 0.00,rec.company_currency_id,
					self.env['res.company']._company_default_get('account.invoice'), rec.account_move_compensation_payable_id.compensation_date))
			else:
				rec.amount_compensation_company_currency = abs(rec.amount_compensation or 0.00)


	#########################################################################
	@api.onchange('invoice_aml_id')
	def onchange_invoice_aml_id(self):
		for rec in self:
			rec.amount_compensation = 0.00
			if rec.invoice_aml_id:
				if rec.invoice_currency_id and (rec.invoice_currency_id != rec.company_currency_id):
					rec.amount_compensation = abs(rec.invoice_aml_id.amount_residual_currency)
				else:
					rec.amount_compensation = abs(rec.invoice_aml_id.amount_residual)
	##########################################################################
