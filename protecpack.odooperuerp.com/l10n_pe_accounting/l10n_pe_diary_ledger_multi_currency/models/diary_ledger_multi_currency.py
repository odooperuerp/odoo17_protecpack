import calendar
from io import BytesIO, StringIO
from odoo import models, fields, api, _
from datetime import datetime, timedelta
import xlsxwriter
from odoo.exceptions import UserError , ValidationError
from odoo.addons import unique_library_accounting_queries as unique_queries

import logging
_logger=logging.getLogger(__name__)

months=[
	('01','Enero'),
	('02','Febrero'),
	('03','Marzo'),
	('04','Abril'),
	('05','Mayo'),
	('06','Junio'),
	('07','Julio'),
	('08','Agosto'),
	('09','Septiembre'),
	('10','Octubre'),
	('11','Noviembre'),
	('12','Diciembre')]


options=[
	('in','esta en'),
	('not in','no esta en')
	]


class DiaryLedgerMultiCurrency(models.TransientModel):
	_name='diary.ledger.multi.currency'
	_description = "Modulo Libro Mayor Multi-Moneda"

	diary_ledger_multi_currency_line_ids = fields.One2many('diary.ledger.multi.currency.line','diary_ledger_multi_currency_id',
		string="Libro Diario Mayor Multi-Moneda",
		readonly=True)

	##########################################################################################

	state = fields.Selection(selection=[('draft','Borrador'),('generated','Generado')],
		readonly=True,string="Estado",default="draft")

	company_id = fields.Many2one('res.company',
		string="Compañia", 
		default=lambda self: self.env['res.company']._company_default_get('account.invoice'),
		domain = lambda self: [('id', 'in',[i.id for i in self.env['res.users'].browse(self.env.user.id).company_ids])],
		readonly=True)
	###########################################################################################
	name = fields.Char(string="Nombre")

	fiscal_year = fields.Selection(selection=[(str(num), str(num)) for num in reversed(range(2000, (datetime.now().year) + 1 ))],
		string="Año fiscal")
	fiscal_month = fields.Selection(selection=months, string="Mes fiscal")
	
	print_format = fields.Selection(selection='available_formats' , string='Formato Impresión:',default='xlsx')
		
	print_order = fields.Selection(selection='impression_options',string="Criterio impresión",default="codigo_cuenta_desagregado") 


	######################### FILTROS DINAMICOS ###########################
	partner_ids = fields.Many2many('res.partner','diary_ledger_multi_currency_partner_rel','partner_id','diary_ledger_multi_currency_id' ,string="Socios")
	partner_option=fields.Selection(selection=options , string="")

	account_ids = fields.Many2many('account.account','diary_ledger_multi_currency_account_rel','account_id','diary_ledger_multi_currency_id',string='Cuentas')
	account_option=fields.Selection(selection=options , string="")

	journal_ids = fields.Many2many('account.journal','diary_ledger_multi_currency_journal_rel','journal_id','diary_ledger_multi_currency_id',string="Diarios")
	journal_option=fields.Selection(selection=options , string="")

	move_ids = fields.Many2many('account.move','diary_ledger_multi_currency_move_rel','move_id','diary_ledger_multi_currency_id',string='Asientos Contables')
	move_option=fields.Selection(selection=options , string="")

	########################################################
	type_residue_in_me = fields.Selection(selection=[('real','Saldo de Registro'),('virtual','Saldo de Referencia')],
		string="Tipo de Saldo en ME",default='real')

	date = fields.Boolean(string="Fecha")
	period = fields.Boolean(string="Periodo")

	date_from=fields.Date(string="Desde:")
	date_to=fields.Date(string="Hasta:")

	buffer_date_from=fields.Date(string="Fecha Inicio:" ,readonly=True)
	buffer_date_to=fields.Date(string="Fecha Fin:" ,readonly=True)

	################# SALDOS INICIALES #################
	initial_balance_mn = fields.Float(string="SALDO ANTERIOR en MN",readonly=True)
	initial_balance_me = fields.Float(string="SALDO ANTERIOR en ME",readonly=True)
	#####################################
	
	def available_formats(self):
		formats=[
			('xlsx','xlsx')]
		return formats


	@api.model
	def impression_options(self): 
		criterios = [
			('number_account_move','N° de Registro'),
			('date','Fecha de Registro'),
			('l10n_pe_invoice_number','N° de documento'),
			('l10n_pe_prefix_code','N° de serie'),
			('table10_id','Tipo de documento'),
			('codigo_cuenta_desagregado','Código Cuenta Desagregado'),
			]
		return criterios


	def button_view_tree(self):	
		if self.diary_ledger_multi_currency_line_ids:
			diccionario = {
				'name': 'Libro Diario-Mayor Multi-Moneda',
				'view_type': 'form',
				'view_mode': 'tree,form',
				'res_model': 'diary.ledger.multi.currency.line',
				'view_id': False,
				'type': 'ir.actions.act_window',
				'domain': [('id', 'in', [i.id for i in self.diary_ledger_multi_currency_line_ids] or [])],
				'context':{
					'search_default_filter_account':1}
			}
			return diccionario
	##############################################################

	def name_get(self):
		result = []
		for rec in self:
			if rec.period:
				result.append((rec.id, rec._fiscal_period() or 'New'))
			elif rec.date:
				result.append((rec.id,"%s-%s"%(self._convert_object_date(rec.date_from),self._convert_object_date(rec.date_to)) or 'New'))
			else:
				result.append((rec.id,'New'))
		return result


	@api.model
	def name_search(self, name, args=None, operator='ilike', limit=100):
		args = args or []
		if self.period:
			recs = self.search([('fiscal_month', operator, name),('fiscal_year', operator, name)] + args, limit=limit)
		elif self.date:
			recs = self.search([('date_from', operator, name),('date_to', operator, name)] + args, limit=limit)
		return recs.name_get()


	def action_draft(self):
		self.state="draft"


	##############################################################################
	@api.onchange('date')
	def onchange_date(self):
		for rec in self:
			if rec.date:
				rec.period=False

	
	@api.onchange('period')
	def onchange_period(self):
		for rec in self:
			if rec.period:
				rec.date=False

	
	def _get_star_date(self):
		buffer_date_from = "%s-%s-01" %(
			self.fiscal_year,
			self.fiscal_month)
		return buffer_date_from

	def _get_end_date(self):
		buffer_date_to = "%s-%s-%s" %(
			self.fiscal_year,
			self.fiscal_month,
			calendar.monthrange(int(self.fiscal_year),int(self.fiscal_month))[1])
		return buffer_date_to


	def action_print(self):
		if (self.print_format) :
			if self.print_format in ['xlsx']:
				return {
					'type': 'ir.actions.act_url',
					'url': 'reports/format/{}/{}/{}'.format(self._name, self.print_format, self.id),
					'target': 'new'}
		else:
			raise UserError(_('No se pudo imprimir, el campo Formato Impresión es obligatorio, llene dicho campo !'))



	def document_print(self):
		output = BytesIO()
		output = self._init_buffer(output)
		output.seek(0)
		return output.read()



	def file_name(self, file_format):
		len_records = '1' if len(self.diary_ledger_multi_currency_line_ids)>0 else '0'

		if self.period:
			file_name = "LIBRO_MAYOR_%s_%s_%s.%s" % (self.company_id.vat,self._fiscal_period(),len_records,file_format)

		elif self.date:
			file_name = "LIBRO_MAYOR_%s_DEL_%s_AL_%s_%s.%s" % (self.company_id.vat,self.date_from.strftime("%d_%m_%Y"),
				self.date_to.strftime("%d_%m_%Y"),len_records,file_format)

		return file_name



	def _fiscal_period(self):
		period = "%s%s00" % (self.fiscal_year or 'YYYY', self.fiscal_month or 'MM')
		return period



	def _get_order_print(self , object):

		if self.print_order == 'date':
			total=sorted(object, key=lambda DiaryLedgerMultiCurrencyLine: (DiaryLedgerMultiCurrencyLine.asiento_contable , DiaryLedgerMultiCurrencyLine.codigo_cuenta_desagregado , DiaryLedgerMultiCurrencyLine.date_contable) )
		elif self.print_order == 'number_account_move':
			total=sorted(object , key=lambda DiaryLedgerMultiCurrencyLine: (DiaryLedgerMultiCurrencyLine.asiento_contable))
		elif self.print_order == 'codigo_cuenta_desagregado':
			total=sorted(object , key=lambda DiaryLedgerMultiCurrencyLine: (DiaryLedgerMultiCurrencyLine.asiento_contable , DiaryLedgerMultiCurrencyLine.date_contable ,  DiaryLedgerMultiCurrencyLine.codigo_cuenta_desagregado ) ) # ORDENAMIENTO POR EL CODIGO DE CUENTA DESAGREGADO
		return total

	##########################################################################################################

	def get_query_initial_movements(self):		
		buffer_date_from = ""

		if self.date:
			buffer_date_from=self.date_from.strftime("%Y-%m-%d")
		elif self.period:
			buffer_date_from= self._get_star_date()

		filter_clause = " and aml.company_id = %s "%(self.company_id.id)

		query = unique_queries.query_account_amount_balances_opening_balances(
			buffer_date_from,
			filter_clause)

		return query
	############################################################################################################


	def get_query_movements(self):

		query="""select 
					aml.id as account_move_line_id, 
					am.id as move_id,
					aml.partner_id as partner_id,
					aml.journal_id as journal_id,
					am.name as name_account_move,
					aml.date as date,
					lldy.code as document_type,
					coalesce(aml.l10n_pe_prefix_code,'') as l10n_pe_prefix_code,
					coalesce(aml.l10n_pe_invoice_number,'') as l10n_pe_invoice_number,
					coalesce(aml.name,'') as comment,
					acac.id as account_id,
					aml.debit as debit_mn,
					aml.credit as credit_mn, """


		query_me = ""

		if self.type_residue_in_me == 'real':

			query_me = """
						aml.currency_id as second_currency_id,
						aml.currency_tc as rate,
						case
							when coalesce(aml.amount_currency,0.00) >=0.00 then coalesce(aml.amount_currency,0.00)
							else 0.00
						end debit_me,
						case
							when coalesce(aml.amount_currency,0.00) <0.00 then abs(coalesce(aml.amount_currency,0.00))
							else 0.00
						end credit_me, """

		#elif self.type_residue_in_me == 'virtual':

		#	query_me = """
		#				am.second_currency_id as second_currency_id,
		#				aml.currency_tc as rate,
		#				aml.debit_currency as debit_me,
		#				aml.credit_currency as credit_me, """


		query_2 = """
					aml.ref as ref,

					(select string_agg(distinct(aaa_init.name->>'es_PE'::text),',')
					 	from account_analytic_line as aal 
						left join account_analytic_account aaa_init on aaa_init.id = aal.account_id 
						where aal.move_line_id = aml.id and aal.company_id = %s) as account_analytic_account_names,

					case when aml.date_emission is not null then aml.date_emission
						else aml.date
						end date_emission,
					aml.date_maturity as date_maturity
				from account_move_line as aml 
				join account_move am on am.id=aml.move_id
				join account_account acac on acac.id=aml.account_id
				left join l10n_latam_document_type lldy on lldy.id = aml.l10n_latam_document_type_id
				where am.state='posted' """ %(self.company_id.id)

		final_query = query + query_me + query_2

		_logger.info('\n\nCONSULTA LIBRO MAYOR MULTIMONEDA\n\n')
		_logger.info(final_query)

		if self.date:
			self.buffer_date_from=self.date_from
			self.buffer_date_to=self.date_to
		elif self.period:
			self.buffer_date_from= self._get_star_date()
			self.buffer_date_to= self._get_end_date()

		if self.date:
			filter_clause_date = " and aml.date<='%s' and aml.date>='%s' "%(self.buffer_date_to.strftime("%Y-%m-%d"),self.buffer_date_from.strftime("%Y-%m-%d"))
		elif self.period:
			filter_clause_date = " and aml.date<='%s' and aml.date>='%s' "%(self.buffer_date_to,self.buffer_date_from)

		if self.company_id:
			filter_clause_date += " and aml.company_id = %s" %(self.company_id.id)
		
		final_query += filter_clause_date		

		return final_query



	def _get_domain(self):

		filter_clause = ""

		#######################################################################
		partners=tuple(self.partner_ids.mapped('id'))
		len_partners = len(partners or '')
		if len_partners:
			filter_clause += " and aml.partner_id %s %s" % (self.partner_option or 'in', str(partners) if len_partners!=1 else str(partners)[0:len(str(partners))-2] + ')')

		journals = tuple(self.journal_ids.mapped('id'))
		len_journals = len(journals or '')
		if len(self.journal_ids):
			filter_clause += " and aml.journal_id %s %s " % (self.journal_option or 'in', str(journals) if len_journals!=1 else str(journals)[0:len(str(journals))-2] + ')')

		moves = tuple(self.move_ids.mapped('id'))
		len_moves = len(moves or '')
		if len(moves):
			filter_clause += " and aml.move_id %s %s " % (self.move_option or 'in', str(moves) if len_moves!=1 else str(moves)[0:len(str(moves))-2] + ')')

		accounts = tuple(self.account_ids.mapped('id'))
		len_accounts = len(accounts or '')
		if len(accounts):
			filter_clause += " and aml.account_id %s %s " % (self.account_option or 'in', str(accounts) if len_accounts!=1 else str(accounts)[0:len(str(accounts))-2] + ')')
			
		return filter_clause



	def generated_book(self):
		if not self.date and not self.period:
			raise UserError(_("ELIJA UN PARÁMETRO DE FECHA-PERIODO !"))
		else:
			if self.date:
				if not (self.date_to and self.date_from):
					raise UserError(_("ELIJA LOS PARÁMETROS FECHA-DESDE , FECHA-HASTA !"))
			elif self.period:
				if not (self.fiscal_year and self.fiscal_month):
					raise UserError(_("ELIJA UN AÑO Y UN MES FISCAL !"))

		self.state='generated'
		self.diary_ledger_multi_currency_line_ids.unlink()
		registro=[]

		query_aml_ids = self.get_query_movements()
		query_domain = self._get_domain()

		query_aml_ids += query_domain

		self.env.cr.execute(query_aml_ids)
		records = self.env.cr.dictfetchall()


		for line in records:
			registro.append((0,0,{
				'account_move_line_id':line['account_move_line_id'] or False,
				'move_id':line['move_id'] or False,
				'name_account_move':line['name_account_move'] or False,
				'journal_id':line['journal_id'] or False,
				'partner_id':line['partner_id'] or False,
				'date':line['date'] or False,
				'document_type':line['document_type'] or False,
				'l10n_pe_prefix_code':line['l10n_pe_prefix_code'] or False,
				'l10n_pe_invoice_number':line['l10n_pe_invoice_number'] or False,
				'comment':line['comment'] or False,
				'account_analytic_account_names':line['account_analytic_account_names'] or '',
				'account_id':line['account_id'] or False,
				'debit_mn':line['debit_mn'] or False,
				'credit_mn':line['credit_mn'] or False,
				'second_currency_id':line['second_currency_id'] or False,
				'rate':line['rate'] or False,
				'debit_me':line['debit_me'] or False,
				'credit_me':line['credit_me'] or False,
				'ref':line['ref'] or False,
				'date_emission':line['date_emission'] or False,
				'date_maturity':line['date_maturity'] or False,
				}))

		self.diary_ledger_multi_currency_line_ids = registro

		###### CALCULO DE SALDOS INICIALES POR EL TOTAL DE CUENTAS.
		initial_query_aml_ids = self.get_query_initial_movements()
		initial_query_domain = self._get_domain()

		initial_query_aml_ids += initial_query_domain

		self.env.cr.execute(initial_query_aml_ids)
		records = self.env.cr.dictfetchall()



	def _init_buffer(self, output):
		if self.print_format == 'xlsx':
			self._generate_xlsx(output)			
		return output



	def _convert_object_date(self, date):
		if date:
			return date.strftime('%d/%m/%Y')
		else:
			return ''


	################################
	def _generate_xlsx(self, output):
		workbook = xlsxwriter.Workbook(output)
		ws = workbook.add_worksheet('Libro Mayor Multi-Moneda')
		styles = {'font_size': 10, 'font_name':'Arial', 'bold': True}
		styles_table = dict(styles,font_size=8,align='center',border=1)
		titulo_1 = workbook.add_format(styles)
		titulo_2 = workbook.add_format(dict(styles,font_size=8))

		titulo_principal = workbook.add_format(dict(styles,font_size=11))

		titulo_3 = workbook.add_format(styles_table)
		titulo_4 = workbook.add_format(dict(styles_table,align=''))
		titulo_5 = workbook.add_format(dict(styles_table,align='',bold=False))

		ws.set_column('A:A',14,titulo_2)
		ws.set_column('B:B',13,titulo_2)
		ws.set_column('C:C',9,titulo_2)
		ws.set_column('D:D',12,titulo_2)
		ws.set_column('E:E',5,titulo_2)
		ws.set_column('F:F',7,titulo_2)
		ws.set_column('G:G',14,titulo_2)
		ws.set_column('H:H',14,titulo_2)
		ws.set_column('I:I',20,titulo_2)
		ws.set_column('J:J',35,titulo_2)
		ws.set_column('K:K',16,titulo_2)
		ws.set_column('L:L',15,titulo_2)
		ws.set_column('M:M',10,titulo_2)
		ws.set_column('N:N',18,titulo_2)
		ws.set_column('O:O',9,titulo_2)
		ws.set_column('P:P',9,titulo_2)
		ws.set_column('Q:Q',9,titulo_2)
		ws.set_column('R:R',9,titulo_2)
		ws.set_column('S:S',9,titulo_2)


		ws.merge_range("A1:F1","LIBRO MAYOR MULTIMONEDA" or '',titulo_principal)

		ws.merge_range("A2:F2","COMPAÑIA: %s"%(self.company_id.name or ''),titulo_principal)

		ws.merge_range("A3:B3","ANÁLISIS DE CUENTA" or '',titulo_2)

		if self.period:
			ws.merge_range("C3:F3","PERIODO DEL %s/%s AL %s/%s"%(self.fiscal_month,self.fiscal_year,self.fiscal_month,self.fiscal_year),titulo_2)
		elif self.date:
			ws.merge_range("C3:F3","FECHA DEL %s AL %s"%(self.date_from.strftime("%d-%m-%Y"),self.date_to.strftime("%d-%m-%Y")),titulo_2)


		account_ids = list(set(self.diary_ledger_multi_currency_line_ids.mapped('account_id.code')))
		account_name_ids = list(set(self.diary_ledger_multi_currency_line_ids.mapped('account_id.name')))
		if len(account_ids or '') == 1:
			ws.merge_range("A5:F5","CUENTA : %s - %s"%(account_ids[0],account_name_ids[0])  or '',titulo_2)
		elif len(account_ids or '')>1:
			ws.merge_range("A5:F5","CUENTAS VARIAS" or '',titulo_2)

		################################################################################
		row = 6
		ws.write(row,0,'REGISTRO',titulo_1)
		ws.write(row,1,'FECHA REGISTRO',titulo_1)
		ws.write(row,2,'F EMISIÓN',titulo_1)
		ws.write(row,3,'F VENCIMIENTO',titulo_1)
		ws.write(row,4,'TIPO',titulo_1)
		ws.write(row,5,'N° SERIE',titulo_1)
		ws.write(row,6,'CORRELATIVO',titulo_1)
		ws.write(row,7,'DIARIO',titulo_1)
		ws.write(row,8,'AUXILIAR',titulo_1)
		ws.write(row,9,'GLOSA',titulo_1)
		ws.write(row,10,'REFERENCIA',titulo_1)
		ws.write(row,11,'CC',titulo_1)
		ws.write(row,12,'CUENTA',titulo_1)
		ws.write(row,13,'NOMBRE CTA CONTABLE',titulo_1)
		ws.write(row,14,'DEBE MN',titulo_1)
		ws.write(row,15,'HABER MN',titulo_1)
		ws.write(row,16,'T CAMBIO',titulo_1)
		ws.write(row,17,'DEBE ME',titulo_1)
		ws.write(row,18,'HABER ME',titulo_1)


		lines = self.diary_ledger_multi_currency_line_ids
		initial_account = ''

		row += 1

		ws.write(row,0,'-',titulo_5)
		ws.write(row,1,'//',titulo_5)
		ws.write(row,2,' ',titulo_5)
		ws.write(row,3,' ',titulo_5)
		ws.write(row,4,' ',titulo_5)
		ws.write(row,5,' ',titulo_5)
		ws.write(row,6,"SALDO ANTERIOR",titulo_5)
		ws.write(row,7,'',titulo_5)
		ws.write(row,8,'',titulo_5)
		ws.write(row,9,'',titulo_5)
		ws.write(row,10,0,titulo_5)
		#ws.write(row,11,self.initial_balance_me if self.initial_balance_me>=0.00 else 0.00,titulo_5)
		#ws.write(row,12,abs(self.initial_balance_me) if self.initial_balance_me<0.00 else 0.00,titulo_5)
		#ws.write(row,13,self.initial_balance_mn if self.initial_balance_mn>=0.00 else 0.00,titulo_5)
		#ws.write(row,14,abs(self.initial_balance_mn) if self.initial_balance_mn<0.00 else 0.00,titulo_5)
		ws.write(row,15,'',titulo_5)
		ws.write(row,16,'',titulo_5)
		ws.write(row,17,'',titulo_5)
		ws.write(row,18,'//',titulo_5)

		row += 1

		total_debit_me = 0.00
		total_credit_me = 0.00

		total_debit_mn = 0.00
		total_credit_mn = 0.00

		for line in lines:
			ws.write(row,0,line.move_id.name or '',titulo_5)
			ws.write(row,1,line.date and line.date.strftime("%d/%m/%Y") or '',titulo_5)
			ws.write(row,2,line.date_emission and line.date_emission.strftime("%d/%m/%Y") or '',titulo_5)
			ws.write(row,3,line.date_maturity and line.date_maturity.strftime("%d/%m/%Y"),titulo_5)
			ws.write(row,4,line.document_type or '',titulo_5)
			ws.write(row,5,line.l10n_pe_prefix_code or '',titulo_5)
			ws.write(row,6,line.l10n_pe_invoice_number or '',titulo_5)
			ws.write(row,7,line.journal_id and line.journal_id.name or '',titulo_5)
			ws.write(row,8,line.partner_id and line.partner_id.name or '',titulo_5)
			ws.write(row,9,line.comment or '',titulo_5)
			ws.write(row,10,line.ref or '',titulo_5)
			ws.write(row,11,line.account_analytic_account_names or '',titulo_5)
			ws.write(row,12,line.account_id and line.account_id.code or '',titulo_5)
			ws.write(row,13,line.account_id and line.account_id.name or '',titulo_5)
			ws.write(row,14,line.debit_mn or 0.00,titulo_5)
			ws.write(row,15,line.credit_mn or 0.00,titulo_5)
			ws.write(row,16,line.rate or 0.000,titulo_5)
			ws.write(row,17,line.debit_me or 0.00,titulo_5)
			ws.write(row,18,line.credit_me or 0.00,titulo_5)
			
			#####################################
			total_debit_mn += line.debit_mn
			total_credit_mn += line.credit_mn

			total_debit_me += line.debit_me
			total_credit_me += line.credit_me

			#####################################
			row += 1


		########################### TOTALES ###################
		ws.write(row,10,'TOTAL CUENTA',titulo_5)

		ws.write(row,14,total_debit_mn or 0.00,titulo_5)
		ws.write(row,15,total_credit_mn or 0.00,titulo_5)

		ws.write(row,17,total_debit_me or 0.00,titulo_5)
		ws.write(row,18,total_credit_me or 0.00,titulo_5)

		########################### SALDO ###################
		row += 1

		ws.write(row,4,'SALDO',titulo_5)

		saldo_debit_me=0.00
		saldo_credit_me=0.00
		saldo_debit_mn=0.00
		saldo_credit_mn=0.00


		if self.initial_balance_mn>=0.00:
			saldo_debit_mn = self.initial_balance_mn + total_debit_mn
		else:
			saldo_credit_mn = abs(self.initial_balance_mn) + total_credit_mn

		###################################
		#if self.initial_balance_me>=0.00:
		#	saldo_debit_me = self.initial_balance_me + total_debit_me
		#else:
		#	saldo_credit_me = abs(self.initial_balance_me) + total_credit_me

		ws.write(row,14,saldo_debit_mn or 0.00,titulo_5)
		ws.write(row,15,saldo_credit_mn or 0.00,titulo_5)

		ws.write(row,17,saldo_debit_me or 0.00,titulo_5)
		ws.write(row,18,saldo_credit_me or 0.00,titulo_5)
	
		workbook.close()
