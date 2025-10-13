import base64
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

import logging
_logger=logging.getLogger(__name__)

class DiaryLedgerMultiCurrencyLine(models.TransientModel):
	_name='diary.ledger.multi.currency.line'

	diary_ledger_multi_currency_id=fields.Many2one("diary.ledger.multi.currency",string="Libro Diario-Mayor", ondelete="cascade")

	company_id = fields.Many2one('res.company',
		string="Compañia", 
		default=lambda self: self.env['res.company']._company_default_get('account.invoice'),
		domain = lambda self:[('id','in',[i.id for i in self.env['res.users'].browse(self.env.user.id).company_ids])],
		readonly=True)

	##############################################################
	account_move_line_id = fields.Many2one('account.move.line',string="Apunte Contable",readonly=True)
	move_id = fields.Many2one('account.move',string="Asiento Contable",readonly=True)
	journal_id = fields.Many2one('account.journal',string="Diario",readonly=True)
	partner_id = fields.Many2one('res.partner',string="Auxiliar",readonly=True)
	name_account_move = fields.Char(string="N° Registro",readonly=True)
	date = fields.Date(string="Fecha Registro",readonly=True)
	document_type = fields.Char(string="Tipo Doc",readonly=True)
	l10n_pe_prefix_code = fields.Char(string="N° Serie",readonly=True)
	l10n_pe_invoice_number = fields.Char(string="Correlativo",readonly=True)
	comment = fields.Char(string="Glosa",readonly=True)
	account_analytic_account_names = fields.Char(string="Cuenta Analítica",readonly=True)
	account_id = fields.Many2one('account.account',string="Cuenta",readonly=True)
	debit_mn = fields.Float(string="Debe MN",readonly=True)
	credit_mn = fields.Float(string="Haber MN",readonly=True)
	second_currency_id = fields.Many2one('res.currency',string="Segunda Moneda",readonly=True)
	rate = fields.Float(string="Tipo Cambio",digits=(12,4),readonly=True)
	debit_me = fields.Float(string="Debe ME",readonly=True)
	credit_me = fields.Float(string="Haber ME",readonly=True)
	ref = fields.Char(string="Referencia",readonly=True)
	date_emission = fields.Date(string="Fecha Emisión",readonly=True)
	date_maturity = fields.Date(string="Fecha Vencimiento",readonly=True)

	##############################################################

	def _convert_object_date(self, date):
		if date:
			return date.strftime('%d/%m/%Y')
		else:
			return ''