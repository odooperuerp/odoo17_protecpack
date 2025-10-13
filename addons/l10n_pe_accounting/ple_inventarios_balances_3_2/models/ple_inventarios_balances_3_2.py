import calendar
from io import BytesIO, StringIO
from odoo import models, fields, api, _
from datetime import datetime, timedelta
import xlsxwriter
from odoo.exceptions import UserError , ValidationError
from odoo.addons import unique_library_accounting_queries as unique_queries
import logging
from itertools import *
_logger=logging.getLogger(__name__)

options=[
	('in','esta en'),
	('not in','no esta en')
	]

class PleInventariosBalancesDetalleSaldoCuenta10(models.Model):
	_name='ple.inventarios.balances.3.2'
	_inherit='ple.base'
	_description = "Modulo PLE Inventarios Balances-Detalle Saldo cuenta 10"
	_rec_name = 'periodo_ple'

	ple_inventarios_balances_3_2_line_ids=fields.One2many('ple.inventarios.balances.3.2.line','ple_inventarios_balances_3_2_id',
		string="Libro Inventarios y Balances 3.2",readonly=True)
	
	fecha_inicio=fields.Date(string="Fecha Inicio",required=True)
	fecha_final=fields.Date(string="Fecha Final",required=True)

	#### FILTROS DINAMICOS !!
	partner_ids = fields.Many2many('res.partner','ple_inventarios_balances_3_2_partner_rel',
		'partner_id','ple_inventarios_balances_3_2_id' ,string="Socios")
	partner_option=fields.Selection(selection=options , string="")

	account_ids = fields.Many2many('account.account','ple_inventarios_balances_3_2_account_rel',
		'account_id','ple_inventarios_balances_3_2_id',string='Cuentas')
	account_option=fields.Selection(selection=options , string="")

	journal_ids = fields.Many2many('account.journal','ple_inventarios_balances_3_2_journal_rel',
		'journal_id','ple_inventarios_balances_3_2_id',string="Diarios")
	journal_option=fields.Selection(selection=options , string="")

	move_ids = fields.Many2many('account.move','ple_inventarios_balances_3_2_move_rel',
		'move_id','ple_inventarios_balances_3_2_id',string='Asientos Contables')
	move_option=fields.Selection(selection=options , string="")

	########################################################
	periodo_ple=fields.Char(string="Periodo",compute="compute_campo_periodo",store=True)
	

	@api.depends('fecha_final','fecha_inicio')
	def compute_campo_periodo(self):
		for ple in self:
			if ple.fecha_inicio and ple.fecha_final:
				ple.periodo_ple = "PLE 3.2 del %s al %s"%(
					ple.fecha_inicio.strftime("%d/%m/%Y") or 'YYYY',
					ple.fecha_final.strftime("%d/%m/%Y") or 'YYYY')

			else:
				ple.periodo_ple = 'Nuevo Registro PLE 3.2'

	########################################################

	def open_wizard_print_form(self):
		res = super(PleInventariosBalancesDetalleSaldoCuenta10,self).open_wizard_print_form()

		view = self.env.ref('ple_inventarios_balances_3_2.view_wizard_printer_ple_inventarios_balances_3_2_form')
		if view:

			return {
				'name': _('FORMULARIO DE IMPRESIÓN DEL LIBRO PLE'),
				'type': 'ir.actions.act_window',
				'view_type': 'form',
				'view_mode': 'form',
				'res_model': 'wizard.printer.ple.inventarios.balances.3.2',
				'views': [(view.id,'form')],
				'view_id': view.id,
				'target': 'new',
				'context': {
					'default_ple_inventarios_balances_3_2_line_id': self.id,
					'default_company_id' : self.company_id.id,}}


	########################################################
	def name_get(self):
		result = []
		for ple in self:
			result.append((ple.id,"%s-%s"%(self._convert_object_date(ple.fecha_inicio),self._convert_object_date(ple.fecha_final)) or 'New'))
		return result


	@api.model
	def name_search(self, name, args=None, operator='ilike', limit=100):
		args = args or []
		recs = self.search([('fecha_inicio', operator, name),('fecha_final', operator, name)] + args, limit=limit)
		return recs.name_get()
	##########################################################


	def generate_tree_records_groups_accounts(self):
		array_total=[]
		for item in self.ple_inventarios_balances_3_2_line_ids:
			array_total += [(item.grupo_cuentas_id.id,item)]

		diccionario_cuentas={}
		grupos_de_cuentas=groupby(sorted(array_total),lambda x:x[0])

		for k , v in grupos_de_cuentas:
			diccionario_cuentas[k]=[i[1] for i in list(v)]
		return diccionario_cuentas



	def query_balance_of_sums_and_balances(self,str_account_ids,fecha_movimiento_debe,fecha_movimiento_haber):

		filter_clause = ""

		partners=tuple(self.partner_ids.mapped('id'))
		len_partners = len(partners or '')
		if len_partners:
			filter_clause += " and aml.partner_id %s %s" % (self.partner_option , str(partners) if len_partners!=1 else str(partners)[0:len(str(partners))-2] + ')')

		journals = tuple(self.journal_ids.mapped('id'))
		len_journals = len(journals or '')
		if len(self.journal_ids):
			filter_clause += " and aml.journal_id %s %s " % (self.journal_option , str(journals) if len_journals!=1 else str(journals)[0:len(str(journals))-2] + ')')

		moves = tuple(self.move_ids.mapped('id'))
		len_moves = len(moves or '')
		if len(moves):
			filter_clause += " and aml.move_id %s %s " % (self.move_option , str(moves) if len_moves!=1 else str(moves)[0:len(str(moves))-2] + ')')

		accounts = tuple(self.account_ids.mapped('id'))
		len_accounts = len(accounts or '')
		if len(accounts):
			filter_clause += " and aml.account_id %s %s " % (self.account_option , str(accounts) if len_accounts!=1 else str(accounts)[0:len(str(accounts))-2] + ')')

		query = unique_queries.query_account_amount_balances_group_account(
			str_account_ids,
			fecha_movimiento_debe,
			fecha_movimiento_haber,
			filter_clause)

		self.env.cr.execute(query)
		records = self.env.cr.dictfetchall()
		return records



	def _periodo_fiscal(self):
		periodo = "%s%s00" % (self.fiscal_year or 'YYYY', self.fiscal_month or 'MM')
		return periodo


	def generar_libro(self):
		self.state='open'
		self.ple_inventarios_balances_3_2_line_ids.unlink()
		registro=[]

		k=0
		#####################################################################
		query_accounts_group_10 = unique_queries.query_account_group_accounts('10')
		self.env.cr.execute(query_accounts_group_10)
		accounts_group_10 = [i['id'] or '' for i in self.env.cr.dictfetchall()]

		records=self.query_balance_of_sums_and_balances(
			accounts_group_10,
			self.fecha_inicio.strftime('%Y-%m-%d'),
			self.fecha_final.strftime('%Y-%m-%d'))

		for line in records:

			balance = line['balance'] or 0.00
			
			registro.append((0,0,{
				'periodo':self.fecha_final.strftime('%Y%m%d'),
				'account_id':line['account_id'],
				'saldo_deudor_cuenta': abs(balance) if balance>=0 else 0.00,
				'saldo_acreedor_cuenta': abs(balance) if balance<0 else 0.00,
			}))
		
		self.ple_inventarios_balances_3_2_line_ids = registro



	def _convert_object_date(self, date):
		# parametro date que retorna un valor vacio o el foramto 01/01/2100 dia/mes/año
		if date:
			return date.strftime('%d/%m/%Y')
		else:
			return ''