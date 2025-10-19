import calendar
from io import BytesIO, StringIO
from odoo import models, fields, api, _
from datetime import datetime, timedelta
import xlsxwriter
from odoo.exceptions import UserError , ValidationError
from itertools import *

import logging
_logger=logging.getLogger(__name__)

options=[
	('in','esta en'),
	('not in','no esta en')]


################################################

class PleDiaryCashBoxAndBanks(models.Model):
	_name='ple.diary.cash.box.and.banks'
	_inherit='ple.base'
	_description = "Modulo PLE Libros Caja y Bancos"
	_rec_name='periodo_ple'

	ple_diary_cash_box_and_banks_bank_line_ids = fields.One2many('ple.diary.cash.box.and.banks.line',
		'ple_diary_cash_box_and_banks_bank_id' , string="",readonly=True)

	ple_diary_cash_box_and_banks_cash_line_ids = fields.One2many('ple.diary.cash.box.and.banks.line',
		'ple_diary_cash_box_and_banks_cash_id' , string="",readonly=True)


	## ESTO ES PARA IMPRESIÓN POR DIARIO O TODOS LOS DIARIOS EN CASO NO SE ELIJA ALGUNO !!
	cash_journal_id = fields.Many2one('account.journal',string="Diario de Caja",
		domain="[('type','in',['cash']),('is_ple_caja_bancos','=',True)]")

	bank_journal_id = fields.Many2one('account.journal',string="Diario de Banco",
		domain="[('type','in',['bank']),('is_ple_caja_bancos','=',True)]")


	fecha=fields.Boolean(string="Fecha",default=False)
	periodo=fields.Boolean(string="Periodo",default=True)

	date_from=fields.Date(string="Desde:")
	date_to=fields.Date(string="Hasta:")

	fecha_inicio=fields.Date(string="Fecha inicio")
	fecha_fin=fields.Date(string="Fecha fin")

	initial_balance_cash = fields.Float(string="Saldo Inicial Caja", readonly=True)
	initial_balance_bank = fields.Float(string="Saldo Inicial Banco", readonly=True)

	end_balance_cash = fields.Float(string="Saldo Final Caja", readonly=True)
	end_balance_bank = fields.Float(string="Saldo Final Banco", readonly=True)
	exist_diario_anterior_cash=fields.Boolean(string="Existe diario anterior Caja?", default=False)#, compute="compute_campo_exist_diario_anterior_cash")
	exist_diario_anterior_bank=fields.Boolean(string="Existe diario anterior Banco?", default=False)#, compute="compute_campo_exist_diario_anterior_bank")

	periodo_ple=fields.Char(string="Periodo",compute="compute_campo_periodo",store=True)

	############## CHECK para indicar si se incluye o no registros anteriores no declarados
	incluir_anteriores_no_declarados = fields.Boolean(string="Incluir registros anteriores no declarados", default=False)

	_sql_constraints = [
		('fiscal_month', 'unique(fiscal_month,fiscal_year,cash_journal_id,bank_journal_id,company_id)',  'Este periodo para el PLE ya existe , revise sus registros de PLE creados!!!'),
	]

	###########################################################################

	def open_wizard_print_form(self):
		res = super(PleDiaryCashBoxAndBanks,self).open_wizard_print_form()

		view = self.env.ref('ple_diary_cash_box_and_banks.view_wizard_printer_ple_diary_cash_box_and_banks_form')
		if view:

			return {
				'name': _('FORMULARIO DE IMPRESIÓN DEL LIBRO PLE'),
				'type': 'ir.actions.act_window',
				'view_type': 'form',
				'view_mode': 'form',
				'res_model': 'wizard.printer.ple.diary.cash.box.and.banks',
				'views': [(view.id,'form')],
				'view_id': view.id,
				'target': 'new',
				'context': {
					'default_ple_diary_cash_box_and_banks_id': self.id,
					'default_company_id' : self.company_id.id,}}

	#################################################################

	def button_view_tree_cta_cte(self):
		self.ensure_one()
		view = self.env.ref('ple_diary_cash_box_and_banks.view_ple_diary_cash_box_and_banks_bank_line_tree')
		if self.ple_diary_cash_box_and_banks_bank_line_ids:
			diccionario = {
				'name': 'Libro PLE Caja-Bancos Detalle movimientos Cta.Cte.',
				'view_mode': 'tree,form',
				'res_model': 'ple.diary.cash.box.and.banks.line',
				'view_id': view.id,
				'views': [(view.id,'tree')],
				'type': 'ir.actions.act_window',
				'domain': [('id', 'in', [i.id for i in self.ple_diary_cash_box_and_banks_bank_line_ids] or [])],
				'context':{
					'search_default_filter_cuenta':1,
					}
			}
			return diccionario



	def button_view_tree_efectivo(self):
		self.ensure_one()
		view = self.env.ref('ple_diary_cash_box_and_banks.view_ple_diary_cash_box_and_banks_cash_line_tree')
		if self.ple_diary_cash_box_and_banks_cash_line_ids:
			diccionario = {
				'name': 'Libro PLE Caja-Bancos Detalle movimientos Efectivo',
				'view_mode': 'tree,form',
				'res_model': 'ple.diary.cash.box.and.banks.line',
				'view_id': view.id,
				'views': [(view.id,'tree')],
				'type': 'ir.actions.act_window',
				'domain': [('id', 'in', [i.id for i in self.ple_diary_cash_box_and_banks_cash_line_ids] or [])],
				'context':{
					'search_default_filter_cuenta':1,
					}
			}
			return diccionario


	##################################################################

	@api.depends('fiscal_year','fiscal_month')
	def compute_campo_periodo(self):
		for ple in self:
			if ple.fiscal_year and ple.fiscal_month:
				ple.periodo_ple = "%s-%s-00" % (ple.fiscal_year or 'YYYY', ple.fiscal_month or 'MM') 
			else:
				ple.periodo_ple = 'Nuevo Registro'


	def name_get(self):
		result = []
		for ple in self:
			if ple.periodo:
				result.append((ple.id, ple._periodo_fiscal() or 'New'))
			elif ple.fecha:
				result.append((ple.id,"%s-%s"%(self._convert_object_date(ple.date_from),self._convert_object_date(ple.date_to)) or 'New'))
			else:
				result.append((ple.id,'New'))
		return result


	@api.model
	def name_search(self, name, args=None, operator='ilike', limit=100):
		args = args or []
		if self.periodo:
			recs = self.search([('fiscal_month', operator, name),('fiscal_year', operator, name)] + args, limit=limit)
		elif self.fecha:
			recs = self.search([('date_from', operator, name),('date_to', operator, name)] + args, limit=limit)
		return recs.name_get()


	######################################################################
	def _hallar_saldo_inicial(self,account_ids,fecha_inicio):
		#account_internal_ids=self.get_accounts_of_journals(type,journals)

		accounts = tuple(account_ids.mapped('id'))
		len_accounts = len(accounts or '')
		tuple_accounts = ""

		if len_accounts >1:
			tuple_accounts = str(accounts)
		elif len_accounts ==1:
			tuple_accounts = str(accounts)[0:len(str(accounts))-2] + ')'
		else:
			return False		

		query_balance = """ select aml.account_id as account_id,sum(aml.balance) as balance_total 
							from account_move_line as aml
							join account_move am on am.id=aml.move_id 
							where aml.account_id in %s and am.state = 'posted' and aml.date <'%s' 
							group by aml.account_id
						"""%(tuple_accounts,fecha_inicio)

		self.env.cr.execute(query_balance)
		records = self.env.cr.dictfetchall()
		return records

	#####################################################################
	def _hallar_saldo_inicial_currency(self,account_ids,fecha_inicio):
		#account_internal_ids=self.get_accounts_of_journals(type,journals)

		accounts = tuple(account_ids.mapped('id'))
		len_accounts = len(accounts or '')
		tuple_accounts = ""

		if len_accounts >1:
			tuple_accounts = str(accounts)
		elif len_accounts ==1:
			tuple_accounts = str(accounts)[0:len(str(accounts))-2] + ')'
		else:
			return False		

		query_balance = """ select aml.account_id as account_id,sum(aml.amount_currency) as balance_total_currency 
							from account_move_line as aml
							join account_move am on am.id=aml.move_id 
							where aml.account_id in %s and am.state = 'posted' and aml.date <'%s' 
							group by aml.account_id
						"""%(tuple_accounts,fecha_inicio)

		self.env.cr.execute(query_balance)
		records = self.env.cr.dictfetchall()
		return records

	#####################################################################


	@api.onchange('fiscal_year','fiscal_month','cash_journal_id')
	def onchange_initial_balance_cash(self):
		for rec in self:
			if rec.fiscal_year and rec.fiscal_month and rec.cash_journal_id:
				ple_cash_box_anterior= None
				if rec.fiscal_month=='01':
					ple_cash_box_anterior = self.env['ple.diary.cash.box.and.banks'].\
						search([('fiscal_month','=','12'),('fiscal_year','=',str(int(rec.fiscal_year)-1)),('cash_journal_id','=',rec.cash_journal_id.id)],
							limit=1)
				else:
					ple_cash_box_anterior = self.env['ple.diary.cash.box.and.banks'].\
						search([('fiscal_month','=',"{:02}".format(int(rec.fiscal_month)-1)),('fiscal_year','=',rec.fiscal_year),('cash_journal_id','=',rec.cash_journal_id.id)],
							limit=1)

				if ple_cash_box_anterior:
					rec.initial_balance_cash=ple_cash_box_anterior[0].end_balance_cash
					rec.exist_diario_anterior_cash=True
				else:
					rec.exist_diario_anterior_cash=False


			elif rec.fiscal_year and rec.fiscal_month and not rec.cash_journal_id:
				ple_cash_box_anterior= None
				if rec.fiscal_month=='01':
					ple_cash_box_anterior = self.env['ple.diary.cash.box.and.banks'].\
						search([('fiscal_month','=','12'),('fiscal_year','=',str(int(rec.fiscal_year)-1)),('cash_journal_id','in',['',False,None])],
							limit=1)
				else:
					ple_cash_box_anterior = self.env['ple.diary.cash.box.and.banks'].\
						search([('fiscal_month','=',"{:02}".format(int(rec.fiscal_month)-1)),('fiscal_year','=',rec.fiscal_year),('cash_journal_id','in',['',False,None])],
							limit=1)

				if ple_cash_box_anterior:
					rec.initial_balance_cash=ple_cash_box_anterior[0].end_balance_cash
					rec.exist_diario_anterior_cash=True
				else:
					rec.exist_diario_anterior_cash=False


	@api.onchange('fiscal_year','fiscal_month','bank_journal_id')
	def onchange_initial_balance_bank(self):
		for rec in self:
			if rec.fiscal_year and rec.fiscal_month and rec.bank_journal_id:
				ple_cash_box_anterior= None
				if rec.fiscal_month=='01':
					ple_cash_box_anterior = self.env['ple.diary.cash.box.and.banks'].\
						search([('fiscal_month','=','12'),('fiscal_year','=',str(int(rec.fiscal_year)-1)),('bank_journal_id','=',rec.bank_journal_id.id)],
							limit=1)
				else:
					ple_cash_box_anterior = self.env['ple.diary.cash.box.and.banks'].\
						search([('fiscal_month','=',"{:02}".format(int(rec.fiscal_month)-1)),('fiscal_year','=',rec.fiscal_year),('bank_journal_id','=',rec.bank_journal_id.id)],
							limit=1)
				
				if ple_cash_box_anterior:
					rec.initial_balance_bank=ple_cash_box_anterior[0].end_balance_bank
					rec.exist_diario_anterior_bank=True
				else:
					rec.exist_diario_anterior_bank=False

			elif rec.fiscal_year and rec.fiscal_month and not rec.bank_journal_id:
				ple_cash_box_anterior= None
				if rec.fiscal_month=='01':
					ple_cash_box_anterior = self.env['ple.diary.cash.box.and.banks'].\
						search([('fiscal_month','=','12'),('fiscal_year','=',str(int(rec.fiscal_year)-1)),('bank_journal_id','in',['',False,None])],
							limit=1)
				else:
					ple_cash_box_anterior = self.env['ple.diary.cash.box.and.banks'].\
						search([('fiscal_month','=',"{:02}".format(int(rec.fiscal_month)-1)),('fiscal_year','=',rec.fiscal_year),('bank_journal_id','in',['',False,None])],
							limit=1)
				
				if ple_cash_box_anterior:
					rec.initial_balance_bank=ple_cash_box_anterior[0].end_balance_bank
					rec.exist_diario_anterior_bank=True
				else:
					rec.exist_diario_anterior_bank=False

	#####################################################################
	
	@api.onchange('fecha')
	def onchange_fecha(self):
		for rec in self:
			if rec.fecha:
				rec.periodo=False


	@api.onchange('periodo')
	def onchange_periodo(self):
		for rec in self:
			if rec.periodo:
				rec.fecha=False
	###############################################################################


	@api.onchange('identificador_libro')
	def set_domain_for_journal_id(self):
		for rec in self:
			if len(rec.identificador_libro or ''):
				journal_obj = []
				if rec.identificador_libro == '010100':
					journal_obj = self.env['account.journal'].search([('type','in',['cash']),('is_ple_caja_bancos','=',True)])
				elif rec.identificador_libro == '010200':
					journal_obj = self.env['account.journal'].search([('type','in',['bank']),('is_ple_caja_bancos','=',True)])
				journal_list = []
				for data in journal_obj:
					journal_list.append(data.id)
				res = {}
				res['domain'] = {'journal_id':[('id','in',journal_list)]}
				return res

	

	

	def _action_confirm_ple(self):
		for line in self.ple_diary_cash_box_and_banks_bank_line_ids + self.ple_diary_cash_box_and_banks_cash_line_ids:
			if(line.move_line_id.declared_ple_0101_0102 != True):
				super(PleDiaryCashBoxAndBanks,self)._action_confirm_ple('account.move.line' , line.move_line_id.id ,{'declared_ple_0101_0102':True})


	def _get_datas(self, domain):
		orden=""
		if self.print_order == 'date':
			orden = 'date asc , move_id asc , account_id asc '		
		elif self.print_order == 'codigo_cuenta_desagregado':
			orden =  ' account_id asc , move_id asc , date asc '		
		elif self.print_order == 'nro_documento':
			orden = ' move_id asc , account_id asc ,date asc '
		return self._get_query_datas('account.move.line', domain, orden)



	def get_accounts_of_journals(self,type,journals):
		if journals:
			return list(self.env['account.journal'].search([('type','=',type),('id','in',journals),('is_ple_caja_bancos','=',True)]).\
				mapped('default_account_id').mapped('id'))
		else:
			return list(self.env['account.journal'].search([('type','=',type),('is_ple_caja_bancos','=',True)]).\
				mapped('default_account_id').mapped('id'))


	def _get_domain(self):
		domain=[
			('state','!=','draft'),
			('date','>=',self.fecha_inicio),
			('date','<=',self.fecha_fin)]
		return domain
	



	def _periodo_fiscal(self):
		periodo = "%s%s00" % (self.fiscal_year or 'YYYY', self.fiscal_month or 'MM')
		return periodo

	#####################################################################
	def search_account_journal(self,account_id,type):
		if account_id:
			query = """
				select id from account_journal where default_account_id = %s and type = '%s' limit 1 """%(account_id.id,type)

			self.env.cr.execute(query)
			records = self.env.cr.dictfetchall()
			return records
	
	######################################################################

	def generar_libro(self):
		if not self.fecha and not self.periodo:
			raise UserError(_("ELIJA UN PARÁMETRO DE FECHA-PERIODO !!"))
		else:
			if self.fecha:
				if not(self.date_to and self.date_from):
					raise UserError(_("ELIJA LOS PARÁMETROS FECHA-DESDE , FECHA-HASTA !!"))
			elif self.periodo:
				if not(self.fiscal_year and self.fiscal_month):
					raise UserError(_("ELIJA UN AÑO Y UN MES FISCAL !!"))

		self.state='open'

		self.ple_diary_cash_box_and_banks_cash_line_ids.unlink()
		self.ple_diary_cash_box_and_banks_bank_line_ids.unlink()

		registro=[]
		registro_efectivo_txt=[]
		registro_banco_txt=[]

		#######################################################
		domain=[('state','=','posted')]

		if self.fecha:

			self.fecha_inicio=self.date_from
			self.fecha_fin=self.date_to

			if self.incluir_anteriores_no_declarados:
				domain += [('date','<=',self.fecha_fin)]
			else:
				domain += [('date','>=',self.fecha_inicio),('date','<=',self.fecha_fin)]

		elif self.periodo:

			self.fecha_inicio= self._get_star_date()
			self.fecha_fin= self._get_end_date()

			if self.incluir_anteriores_no_declarados:
				domain += [('date','<=',self.fecha_fin)]
			else:
				domain += [('date','>=',self.fecha_inicio),('date','<=',self.fecha_fin)]
		###########################################################

		move_ids_origin = self.env['account.move'].search(domain , order="date desc")


		self.fiscal_year=self.fecha_inicio.strftime("%Y")

		################################# LIBRO CAJA !!! #########################################################
		account_journal_cash_ids = []

		record_initial_cash = 0.00

		if self.cash_journal_id and self.cash_journal_id.is_ple_caja_bancos:

			account_journal_cash_ids= self.cash_journal_id.default_account_id

			#### CALCULANDO SALDOS INICIALES ####
			if self.cash_journal_id.currency_id and self.company_id.currency_id != self.cash_journal_id.currency_id:
				record_initial_cash = self._hallar_saldo_inicial_currency(account_journal_cash_ids,self.fecha_inicio)
				if record_initial_cash:
					self.initial_balance_cash = record_initial_cash[0]['balance_total_currency']

			else:
				record_initial_cash = self._hallar_saldo_inicial(account_journal_cash_ids,self.fecha_inicio)
				if record_initial_cash:
					self.initial_balance_cash = record_initial_cash[0]['balance_total']

		else:
			account_journal_cash_ids=self.env['account.journal'].search([('type','in',['cash']),('is_ple_caja_bancos','=',True)]).\
				mapped('default_account_id')

			#### CALCULANDO SALDOS INICIALES ####
			record_initial_cash = self._hallar_saldo_inicial(account_journal_cash_ids,self.fecha_inicio)
			if record_initial_cash:
				self.initial_balance_cash = sum([i['balance_total'] for i in record_initial_cash])


		move_ids = move_ids_origin.filtered(lambda t:t.mapped('line_ids').mapped('account_id') & account_journal_cash_ids)
		cash_move_line_txt_ids = move_ids.mapped('line_ids').filtered(lambda y:y.declared_ple_0101_0102 != True and (y.account_id in list(account_journal_cash_ids)))
		########################################

		for line1 in cash_move_line_txt_ids:
			record_journal_id = self.search_account_journal(line1.account_id,'cash')
			if record_journal_id:
				record_journal_id = record_journal_id[0]['id']

			registro_efectivo_txt.append((0,0,{
				'move_id':line1.move_id.id,
				'move_line_id':line1.id,
				'conjunto':'010100',
				'periodo':self._periodo_fiscal(),
				'diario':record_journal_id or line1.journal_id.id,
				'm_correlativo_asiento_contable':"M%s"%(str(line1.id))
				}))

		self.ple_diary_cash_box_and_banks_cash_line_ids= registro_efectivo_txt

		
		if self.cash_journal_id.currency_id and self.company_id.currency_id != self.cash_journal_id.currency_id:
			self.end_balance_cash=sum(self.ple_diary_cash_box_and_banks_cash_line_ids.mapped('amount_currency')) + self.initial_balance_cash
		else:
			self.end_balance_cash=sum(self.ple_diary_cash_box_and_banks_cash_line_ids.mapped('balance')) + self.initial_balance_cash

		
		################################# LIBRO BANCO !!! #########################################################

		account_journal_bank_ids = []
		record_initial_bank = 0.00

		if self.bank_journal_id:
			account_journal_bank_ids=self.bank_journal_id.default_account_id

			#### CALCULANDO SALDOS INICIALES ####
			if self.bank_journal_id.currency_id and self.company_id.currency_id != self.bank_journal_id.currency_id:
				record_initial_bank = self._hallar_saldo_inicial_currency(account_journal_bank_ids,self.fecha_inicio)
				if record_initial_bank:
					self.initial_balance_bank = record_initial_bank[0]['balance_total_currency']

			else:
				record_initial_bank = self._hallar_saldo_inicial(account_journal_bank_ids,self.fecha_inicio)
				if record_initial_bank:
					self.initial_balance_bank = record_initial_bank[0]['balance_total']

		else:
			account_journal_bank_ids=self.env['account.journal'].search([('type','in',['bank']),('is_ple_caja_bancos','=',True)]).\
				mapped('default_account_id')

			#### CALCULANDO SALDOS INICIALES ####
			record_initial_bank = self._hallar_saldo_inicial(account_journal_bank_ids,self.fecha_inicio)
			if record_initial_bank:
				self.initial_balance_bank = sum([i['balance_total'] for i in record_initial_bank])
				_logger.info('\n\nSALDOS INICIALES\n\n')
				_logger.info(record_initial_bank)


		move_ids = move_ids_origin.filtered(lambda t:t.mapped('line_ids').mapped('account_id') & account_journal_bank_ids)
		bank_move_line_txt_ids = move_ids.mapped('line_ids').filtered(lambda y:y.declared_ple_0101_0102!=True and (y.account_id in list(account_journal_bank_ids)))

		for line2 in bank_move_line_txt_ids:

			record_journal_id = self.search_account_journal(line2.account_id,'bank')

			if record_journal_id:
				record_journal_id = record_journal_id[0]['id']

			registro_banco_txt.append((0,0,{'move_id':line2.move_id.id,
				'move_line_id':line2.id,
				'conjunto':'010200',
				'periodo':self._periodo_fiscal(),
				'diario':record_journal_id or line2.journal_id.id,
				'm_correlativo_asiento_contable':"M%s"%(str(line2.id))
				}))

		self.ple_diary_cash_box_and_banks_bank_line_ids= registro_banco_txt


		if self.bank_journal_id.currency_id and self.company_id.currency_id != self.bank_journal_id.currency_id:
			self.end_balance_bank=sum(self.ple_diary_cash_box_and_banks_bank_line_ids.mapped('amount_currency')) + self.initial_balance_bank
		else:
			self.end_balance_bank=sum(self.ple_diary_cash_box_and_banks_bank_line_ids.mapped('balance')) + self.initial_balance_bank



	

	def _is_menor(self,a,b):
		return a<b
