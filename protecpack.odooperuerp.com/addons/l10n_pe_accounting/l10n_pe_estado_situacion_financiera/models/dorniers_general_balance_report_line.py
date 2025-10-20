import pytz
import calendar
import base64
from io import BytesIO, StringIO
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta
from . import arrays_general_balance_report as agbr
from odoo.addons import unique_library_accounting_queries as unique_queries
import logging
from itertools import *
_logger=logging.getLogger(__name__)


class DorniersGeneralBalanceReportLine(models.Model):
	_name='dorniers.general.balance.report.line'

	dorniers_general_balance_report_id = fields.Many2one('dorniers.general.balance.report',
		string="Reporte de Estado Situación Financiera",ondelete="cascade",readonly=True)


	name = fields.Char(string="Nombre del Rubro",readonly=True)
	account_ids = fields.Many2many("account.account",
		string="Cuentas Asociadas al Rubro",readonly=True)
	
	grupo_informe = fields.Selection(selection=agbr.array_report_groups,readonly=True)
	grupo_elemento = fields.Selection(selection=agbr.array_element_groups,readonly=True)
	sub_grupo_elemento = fields.Selection(selection=agbr.array_element_sub_groups,readonly=True)

	saldo_rubro_contable = fields.Float(string="Saldo Rubro",readonly=True)

	######## campo flag para iden rubro variation ##
	is_variation = fields.Boolean(string="Es Rubro de Cuadre",default=False)


	def _convert_object_date(self, date):
		if date:
			return date.strftime('%d/%m/%Y')
		else:
			return ''

	################################################################################
	def get_account_move_line_ids(self,str_account_ids,fecha_movimiento_debe,fecha_movimiento_haber):

		filter_clause = ""
		partners=tuple(self.dorniers_general_balance_report_id.partner_ids.mapped('id'))
		len_partners = len(partners or '')
		if len_partners:
			filter_clause += " and aml.partner_id %s %s" % ('in' or self.dorniers_general_balance_report_id.partner_option,str(partners) if len_partners!=1 else str(partners)[0:len(str(partners))-2] + ')')

		journals = tuple(self.dorniers_general_balance_report_id.journal_ids.mapped('id'))
		len_journals = len(journals or '')
		if len_journals:
			filter_clause += " and aml.journal_id %s %s " % ('in' or self.dorniers_general_balance_report_id.journal_option , str(journals) if len_journals!=1 else str(journals)[0:len(str(journals))-2] + ')')

		moves = tuple(self.dorniers_general_balance_report_id.move_ids.mapped('id'))
		len_moves = len(moves or '')
		if len_moves:
			filter_clause += " and aml.move_id %s %s " % ('in' or self.dorniers_general_balance_report_id.move_option , str(moves) if len_moves!=1 else str(moves)[0:len(str(moves))-2] + ')')

		
		accounts = tuple(self.dorniers_general_balance_report_id.account_ids.mapped('id'))
		len_accounts = len(accounts or '')
		if len_accounts:
			filter_clause += " and aml.account_id %s %s " % ('in' or self.dorniers_general_balance_report_id.account_option , str(accounts) if len_accounts!=1 else str(accounts)[0:len(str(accounts))-2] + ')')

		filter_clause += " and aml.company_id = %s"%(self.dorniers_general_balance_report_id.company_id.id) 

		query = unique_queries.query_account_amount_balances_with_period_group_account_move_line(
			str_account_ids,
			fecha_movimiento_debe,
			fecha_movimiento_haber,
			filter_clause)

		_logger.info('\n\nQUERY\n\n')
		_logger.info(query)
	
		self.env.cr.execute(query)
		records = self.env.cr.dictfetchall()
		return records
	################################################################################

	def get_aml_ids(self):
		for rec in self:
			if rec.dorniers_general_balance_report_id and rec.account_ids and not rec.is_variation:

				move_line_ids = self.get_account_move_line_ids(
					rec.account_ids.mapped('id'),
					rec.dorniers_general_balance_report_id.fecha_inicio.strftime('%Y-%m-%d'),
					rec.dorniers_general_balance_report_id.fecha_final.strftime('%Y-%m-%d'))

				list_move_line_ids = [i['aml_id'] for i in move_line_ids]

				if list_move_line_ids:
					return {
						'name': 'Apuntes Contables del Rubro %s'%(rec.name or ''),
						'view_type': 'form',
						'view_mode': 'tree,form',
						'res_model': 'account.move.line',
						'view_id': False,
						'type': 'ir.actions.act_window',
						'domain': [('id','in', list_move_line_ids or [])],
						'context': {
							'company_id': self.dorniers_general_balance_report_id.company_id.id,
						}
					} 
