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

class PleInventariosBalancesEstadoSituacionFinanciera(models.Model):
	_name='ple.inventarios.balances.3.1'
	_inherit='ple.base'
	_description = "Modulo PLE Inventarios Balances 3.1 -Estado Situación Financiera"
	_rec_name = 'periodo_ple'


	ple_inventarios_balances_3_1_line_ids=fields.One2many('ple.inventarios.balances.3.1.line','ple_inventarios_balances_3_1_id',
		string="Libro Inventarios y Balances 3.1",readonly=True)

	fecha_inicio=fields.Date(string="Fecha Inicio",required=True)
	fecha_final=fields.Date(string="Fecha Final",required=True)

	#### FILTROS DINAMICOS !!
	partner_ids = fields.Many2many('res.partner','ple_inventarios_balances_3_1_partner_rel',
		'partner_id','ple_inventarios_balances_3_1_id' ,string="Socios")
	partner_option=fields.Selection(selection=options , string="")#,default='in')

	account_ids = fields.Many2many('account.account','ple_inventarios_balances_3_1_account_rel',
		'account_id','ple_inventarios_balances_3_1_id',string='Cuentas')
	account_option=fields.Selection(selection=options , string="")#,default='in')

	journal_ids = fields.Many2many('account.journal','ple_inventarios_balances_3_1_journal_rel',
		'journal_id','ple_inventarios_balances_3_1_id',string="Diarios")
	journal_option=fields.Selection(selection=options , string="")#,default='in')

	move_ids = fields.Many2many('account.move','ple_inventarios_balances_3_1_move_rel',
		'move_id','ple_inventarios_balances_3_1_id',string='Asientos Contables')
	move_option=fields.Selection(selection=options , string="")#,default='in')


	financial_statement_heading_id = fields.Many2one('financial.statement.heading',
		string="Reporte de Estado Financiero Electrónico",
		default=lambda self:self.env['financial.statement.heading'].search([('code_report_ple','=','3.1'),('type_format_report','=','1')],limit=1))

	imprimible_financial_statement_heading_id = fields.Many2one('financial.statement.heading',
		string="Reporte de Estado Financiero Impreso",
		default=lambda self:self.env['financial.statement.heading'].search([('code_report_ple','=','3.1'),('type_format_report','=','2')],limit=1))

	########################################################
	periodo_ple=fields.Char(string="Periodo",compute="compute_campo_periodo",store=True)
	

	@api.depends('fecha_final','fecha_inicio')
	def compute_campo_periodo(self):
		for ple in self:
			if ple.fecha_inicio and ple.fecha_final:
				ple.periodo_ple = "PLE 3.1 del %s al %s"%(
					ple.fecha_inicio.strftime("%d/%m/%Y") or 'YYYY',
					ple.fecha_final.strftime("%d/%m/%Y") or 'YYYY')

			else:
				ple.periodo_ple = 'Nuevo Registro PLE 3.1'

	########################################################

	def open_wizard_print_form(self):
		res = super(PleInventariosBalancesEstadoSituacionFinanciera,self).open_wizard_print_form()

		view = self.env.ref('ple_inventarios_balances_3_1.view_wizard_printer_ple_inventarios_balances_3_1_form')
		if view:

			return {
				'name': _('FORMULARIO DE IMPRESIÓN DEL LIBRO PLE'),
				'type': 'ir.actions.act_window',
				'view_type': 'form',
				'view_mode': 'form',
				'res_model': 'wizard.printer.ple.inventarios.balances.3.1',
				'views': [(view.id,'form')],
				'view_id': view.id,
				'target': 'new',
				'context': {
					'default_ple_inventarios_balances_3_1_line_id': self.id,
					'default_company_id' : self.company_id.id,}}



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


	
	def query_balance_of_sums_and_balances(self,str_account_ids,fecha_movimiento_debe,fecha_movimiento_haber):

		filter_clause = ""
		partners=tuple(self.partner_ids.mapped('id'))
		len_partners = len(partners or '')
		if len_partners:
			filter_clause += " and aml.partner_id %s %s" % ('in' or self.partner_option , str(partners) if len_partners!=1 else str(partners)[0:len(str(partners))-2] + ')')

		journals = tuple(self.journal_ids.mapped('id'))
		len_journals = len(journals or '')
		if len(self.journal_ids):
			filter_clause += " and aml.journal_id %s %s " % ('in' or self.journal_option , str(journals) if len_journals!=1 else str(journals)[0:len(str(journals))-2] + ')')

		moves = tuple(self.move_ids.mapped('id'))
		len_moves = len(moves or '')
		if len(moves):
			filter_clause += " and aml.move_id %s %s " % ('in' or self.move_option , str(moves) if len_moves!=1 else str(moves)[0:len(str(moves))-2] + ')')


		accounts = tuple(self.account_ids.mapped('id'))
		len_accounts = len(accounts or '')
		if len(accounts):
			filter_clause += " and aml.account_id %s %s " % ('in' or self.account_option , str(accounts) if len_accounts!=1 else str(accounts)[0:len(str(accounts))-2] + ')')

		query = unique_queries.query_account_amount_balances_with_period_group_account_cum(str_account_ids , fecha_movimiento_debe , fecha_movimiento_haber , filter_clause)


		self.env.cr.execute(query)
		records = self.env.cr.dictfetchall()
		return records



	def _periodo_fiscal(self):
		periodo = "%s%s00" % (self.fiscal_year or 'YYYY', self.fiscal_month or 'MM')
		return periodo


	
	def generar_libro(self):

		self.state='open'
		self.ple_inventarios_balances_3_1_line_ids.unlink()
		registro=[]

		k=0
		fecha_saldo_inicial = (self.fecha_inicio-timedelta(days=1)).strftime('%Y-%m-%d')
		######################################################################
		# Total Activos Corrientes	1D01ST
		# Total Activos No Corrientes	1D02ST
		# TOTAL DE ACTIVOS	1D020T
		# Total Pasivos Corrientes	1D03ST
		# Total Pasivos No Corrientes	1D04ST
		# Total Pasivos 	1D040T
		# Total Patrimonio 	1D07ST
		# TOTAL PASIVO Y PATRIMONIO	1D070T
		#####################################################################
		rubros_de_catalogo_3_1 = self.financial_statement_heading_id.financial_statement_heading_line_ids
		rubros_sumas = rubros_de_catalogo_3_1.filtered(lambda r:r.code_sunat in ['1D01ST','1D02ST','1D020T','1D03ST','1D04ST','1D040T','1D07ST','1D070T']).mapped('code_sunat')

		suma=0.00
		
		for rubro in rubros_de_catalogo_3_1:

			if rubro.code_sunat not in rubros_sumas and rubro.calculation_type =='accounts' and rubro.account_ids:
				suma= self.query_balance_of_sums_and_balances(rubro.account_ids.mapped('id'),self.fecha_inicio.strftime('%Y-%m-%d'),self.fecha_final.strftime('%Y-%m-%d'))

				saldo_rubro_contable = 0.00

				if suma and suma[0]['balance']:
					if rubro.group_heading_financial_statement_id.code in ['01','02']:
						saldo_rubro_contable = suma[0]['balance']
					elif rubro.group_heading_financial_statement_id.code in ['03','04','05']:
						saldo_rubro_contable = (-1)*suma[0]['balance']

				registro.append((0,0,{
					'periodo':self.fecha_final.strftime('%Y%m%d'),
					'codigo_catalogo_id':rubro.financial_statement_heading_id.id,
					'codigo_catalogo':rubro.financial_statement_heading_id.code_report_ple or '',
					'codigo_rubro_estado_financiero':rubro.code_sunat,
					'rubro_estado_financiero':rubro.id,
					'grupo_del_rubro_id':rubro.group_heading_financial_statement_id.id,
					'saldo_rubro_contable':saldo_rubro_contable,
					'indicador_estado_operacion':'1',
					}))

			elif rubro.code_sunat not in rubros_sumas and rubro.calculation_type =='manual':

				saldo_rubro_contable = rubro.movements_period

				registro.append((0,0,{
					'periodo':self.fecha_final.strftime('%Y%m%d'),
					'codigo_catalogo_id':rubro.financial_statement_heading_id.id,
					'codigo_catalogo':rubro.financial_statement_heading_id.code_report_ple or '',
					'codigo_rubro_estado_financiero':rubro.code_sunat,
					'rubro_estado_financiero':rubro.id,
					'grupo_del_rubro_id':rubro.group_heading_financial_statement_id.id,
					'saldo_rubro_contable':saldo_rubro_contable,
					'indicador_estado_operacion':'1',
					}))

			else:
				registro.append((0,0,{
					'periodo':self.fecha_final.strftime('%Y%m%d'),
					'codigo_catalogo_id':rubro.financial_statement_heading_id.id,
					'codigo_catalogo':rubro.financial_statement_heading_id.code_report_ple or '',
					'codigo_rubro_estado_financiero':rubro.code_sunat,
					'rubro_estado_financiero':rubro.id,
					'grupo_del_rubro_id':rubro.group_heading_financial_statement_id.id,
					'saldo_rubro_contable':0.00,
					'indicador_estado_operacion':'1',
					}))


		
		self.ple_inventarios_balances_3_1_line_ids = registro

		### CALCULANDO TOTALES DE GRUPOS
		# "id","name","code"
		# "1","Activo Corriente o Circulante","01"
		# "2","Activo no Corriente","02"
		# "3","Pasivo Corriente","03"
		# "4","Pasivo no Corriente","04"
		# "5","Patrimonio Neto","05"
		
		total_activos_corrientes = sum(self.ple_inventarios_balances_3_1_line_ids.filtered(lambda y:y.grupo_del_rubro_id.code=='01').mapped('saldo_rubro_contable'))
		self.ple_inventarios_balances_3_1_line_ids.filtered(lambda e:e.codigo_rubro_estado_financiero=='1D01ST').write({'saldo_rubro_contable':total_activos_corrientes})

		total_activos_no_corrientes = sum(self.ple_inventarios_balances_3_1_line_ids.filtered(lambda y:y.grupo_del_rubro_id.code=='02').mapped('saldo_rubro_contable'))
		self.ple_inventarios_balances_3_1_line_ids.filtered(lambda e:e.codigo_rubro_estado_financiero=='1D02ST').write({'saldo_rubro_contable':total_activos_no_corrientes})

		total_activos = total_activos_corrientes + total_activos_no_corrientes
		self.ple_inventarios_balances_3_1_line_ids.filtered(lambda e:e.codigo_rubro_estado_financiero=='1D020T').write({'saldo_rubro_contable':total_activos})

		total_pasivos_corrientes=sum(self.ple_inventarios_balances_3_1_line_ids.filtered(lambda y:y.grupo_del_rubro_id.code=='03').mapped('saldo_rubro_contable'))
		self.ple_inventarios_balances_3_1_line_ids.filtered(lambda e:e.codigo_rubro_estado_financiero=='1D03ST').write({'saldo_rubro_contable':total_pasivos_corrientes})

		total_pasivos_no_corrientes=sum(self.ple_inventarios_balances_3_1_line_ids.filtered(lambda y:y.grupo_del_rubro_id.code=='04').mapped('saldo_rubro_contable'))
		self.ple_inventarios_balances_3_1_line_ids.filtered(lambda e:e.codigo_rubro_estado_financiero=='1D04ST').write({'saldo_rubro_contable':total_pasivos_no_corrientes})

		total_pasivos = total_pasivos_corrientes + total_pasivos_no_corrientes
		self.ple_inventarios_balances_3_1_line_ids.filtered(lambda e:e.codigo_rubro_estado_financiero=='1D040T').write({'saldo_rubro_contable':total_pasivos})

		total_patrimonio=sum(self.ple_inventarios_balances_3_1_line_ids.filtered(lambda y:y.grupo_del_rubro_id.code=='05').mapped('saldo_rubro_contable'))

		total_pasivo_patrimonio= total_pasivos + total_patrimonio
		self.ple_inventarios_balances_3_1_line_ids.filtered(lambda e:e.codigo_rubro_estado_financiero=='1D070T').write({'saldo_rubro_contable':total_activos})

		################################ ESCRIBIEDO EL SALDO EN EL RUBRO DE RESULTADO DEL EJERCICIO ################################
		rubro_resultado_ejercicio_id = self.ple_inventarios_balances_3_1_line_ids.filtered(
			lambda e:e.rubro_estado_financiero and e.rubro_estado_financiero.calculation_type == 'result_excersice')

		if rubro_resultado_ejercicio_id:
			rubro_resultado_ejercicio_id.write({'saldo_rubro_contable':total_activos - total_pasivo_patrimonio})
			total_patrimonio += total_activos - total_pasivo_patrimonio


		self.ple_inventarios_balances_3_1_line_ids.filtered(lambda e:e.codigo_rubro_estado_financiero=='1D07ST').write({'saldo_rubro_contable':total_patrimonio})


	################################################################################################################

	def _convert_object_date(self, date):
		if date:
			return date.strftime('%d/%m/%Y')
		else:
			return ''



	
	def _generate_xlsx_analitico(self, output):
		workbook = xlsxwriter.Workbook(output)
		ws = workbook.add_worksheet('3.1 BALANCE GENERAL ANALÍTICO')
		titulo1 = workbook.add_format({'font_size': 12,'valign': 'vcenter', 'align': 'center', 'text_wrap': True, 'bold': True, 'font_name':'Arial'})
		titulo_1 = workbook.add_format({'font_size': 8, 'align': 'left', 'text_wrap': True, 'bold': True, 'font_name':'Arial'})
		titulo2 = workbook.add_format({'font_size': 8, 'align': 'center','valign': 'vcenter','color':'black', 'text_wrap': True,'bold':True , 'font_name':'Arial'})
		titulo2_left = workbook.add_format({'font_size': 8, 'align': 'left','valign': 'vcenter','color':'black', 'text_wrap': True, 'bold':True , 'font_name':'Arial'})
		titulo2_right = workbook.add_format({'font_size': 8, 'align': 'right','valign': 'vcenter','color':'black', 'text_wrap': True,'bold':True , 'font_name':'Arial'})
		titulo2_heads = workbook.add_format({'font_size': 8, 'align': 'center','valign': 'vcenter','color':'black', 'text_wrap': True, 'left':True, 'right':True,'bottom': True, 'top': True, 'bold':True , 'font_name':'Arial'})

		#######################################################
		titulo_2 = workbook.add_format({'font_size': 8, 'align': 'center', 'text_wrap': True, 'bold': True, 'font_name':'Arial'})
		##################################################################
		number_left = workbook.add_format({'font_size': 8, 'align': 'left', 'num_format': '#,##0.00', 'font_name':'Arial'})
		number_right = workbook.add_format({'font_size': 8, 'align': 'right', 'num_format': '#,##0.00', 'font_name':'Arial'})
		number_right_tax_rate = workbook.add_format({'font_size': 8, 'align': 'right', 'num_format': '#,##0.000', 'font_name':'Arial'})
		
		letter1 = workbook.add_format({'font_size': 7, 'align': 'left', 'font_name':'Arial'})
		letter3_negrita = workbook.add_format({'font_size': 7, 'align': 'right','num_format': '#,##0.00', 'font_name':'Arial','bold': True})

		ws.set_column('A:A', 15,letter1)
		ws.set_column('B:B', 34,letter1)
		ws.set_column('C:C', 54,letter1)
		ws.set_column('D:D', 18,letter3_negrita)
		ws.set_column('E:E', 18,letter3_negrita)
		ws.set_column('F:F', 15,letter3_negrita)

		ws.set_column('G:G', 15,letter1)
		ws.set_column('H:H', 15,letter1)
		ws.set_column('I:I', 15,letter1)

		ws.merge_range('A1:I2','BALANCE GENERAL ANALÍTICO ' + 'DEL 01.01 AL ' +  self.fecha_final.strftime('%d.%m'),titulo1)
	
		ws.merge_range('A4:D4','EJERCICIO:', titulo_1)
		ws.merge_range('E4:F4',self.fecha_final.split('-')[0] or '', titulo_1)
		
		ws.merge_range('A5:D5','RUC:', titulo_1)
		ws.merge_range('E5:F5',self.company_id.vat or '', titulo_1)

		ws.merge_range('A6:D6','APELLIDOS Y NOMBRES, DENOMINACIÓN O RAZÓN SOCIAL:', titulo_1)
		ws.merge_range('E6:F6',self.company_id.name or '', titulo_1)

		################# CABECERAS #################
		ws.merge_range('A8:A9','CUENTA', titulo2_heads)
		ws.merge_range('B8:B9','', titulo2_heads)
		ws.merge_range('C8:C9','DESCRIPCIÓN', titulo2_heads)
		ws.merge_range('D8:E8','********** SALDO ACTUAL ************', titulo2_heads)
		ws.write(8,3,'DEUDOR', titulo2_heads)
		ws.write(8,4,'ACREEDOR', titulo2_heads)
		############################################

		rubros_de_catalogo_3_1 = self.ple_inventarios_balances_3_1_line_ids

		TOTAL = 0.00
		SUBTOTAL = 0.00
		#######################################################################

		fila = 9
		fila +=1
		k=0
		interruptor=1
		for line in rubros_de_catalogo_3_1:
			k += 1
			fila +=1
			if interruptor==0:
				break

			if line.rubro_estado_financiero.is_title:
				ws.write(fila,1,line.rubro_estado_financiero.title or '',titulo2_left)
				fila += 1

			elif line.rubro_estado_financiero.is_total:
				if line.rubro_estado_financiero.code_sunat not in ['1D020T']:
					ws.write(fila,1,line.rubro_estado_financiero.name or '',titulo2)
					ws.write(fila,3,SUBTOTAL if SUBTOTAL >=0.00 else '',titulo2_right)
					ws.write(fila,4,abs(SUBTOTAL) if SUBTOTAL < 0.00 else '',titulo2_right)

					SUBTOTAL = 0.00
					fila +=2

				else:
					fila +=1
					ws.write(fila,1,line.rubro_estado_financiero.name or '',titulo2)
					ws.write(fila,3,TOTAL if TOTAL >=0.00 else '',titulo2_right)
					ws.write(fila,4,abs(TOTAL) if TOTAL < 0.00 else '',titulo2_right)
					interruptor=0

			elif line.rubro_estado_financiero.is_title==False and line.rubro_estado_financiero.is_total==False:
					
				total = line.saldo_rubro_contable
				TOTAL += total or 0.00
				SUBTOTAL += total or 0.00

				ws.write(fila,1,line.rubro_estado_financiero.name or '',titulo2_left)
				fila += 1
				#######################################################################
				if line.rubro_estado_financiero.account_ids:
					records = self.query_balance_of_sums_and_balances(line.rubro_estado_financiero.account_ids.mapped('id'),self.fecha_inicio,self.fecha_final,'2')
					## cuenta - descripcion - deudor - acreedor
					for record in records:
						saldos_finales_deudor=(record['debit_saldo_inicial'] or 0.00) + (record['debit_movimiento_periodo'] or 0.00)
						saldos_finales_acreedor=(record['credit_saldo_inicial'] or 0.00) + (record['credit_movimiento_periodo'] or 0.00)

						balance=saldos_finales_deudor - saldos_finales_acreedor
						ws.write(fila,1,record['code'] or '',titulo2_right)
						ws.write(fila,2,record['name'] or '',titulo2_right)
						ws.write(fila,3,balance if balance >=0.00 else '',titulo2_right)
						ws.write(fila,4,abs(balance) if balance < 0.00 else '',titulo2_right)
						fila +=1
				#######################################################################
				ws.write(fila,3,total if total >=0.00 else '',titulo2_right)
				ws.write(fila,4,abs(total) if total < 0.00 else '',titulo2_right)


		fila +=1
		SUBTOTAL = 0.00
		TOTAL = 0.00

		for line in rubros_de_catalogo_3_1[k:]:
			fila +=1
			if line.rubro_estado_financiero.is_title:
				ws.write(fila,1,line.rubro_estado_financiero.title or '',titulo2_left)
				fila +=1

			elif line.rubro_estado_financiero.is_total:
				if line.rubro_estado_financiero.code_sunat not in ['1D070T']:
					ws.write(fila,1,line.rubro_estado_financiero.name or '',titulo2)
					ws.write(fila,3,SUBTOTAL if SUBTOTAL >=0.00 else '',titulo2_right)
					ws.write(fila,4,abs(SUBTOTAL) if SUBTOTAL < 0.00 else '',titulo2_right)
					SUBTOTAL = 0.00
					fila +=2
				else:
					fila +=1
					ws.write(fila,1,line.rubro_estado_financiero.name or '',titulo2)
					ws.write(fila,3,TOTAL if TOTAL >=0.00 else '',titulo2_right)
					ws.write(fila,4,abs(TOTAL) if TOTAL < 0.00 else '',titulo2_right)
					interruptor=0

			elif line.rubro_estado_financiero.is_title==False and line.rubro_estado_financiero.is_total==False:
				
				total = line.saldo_rubro_contable
				TOTAL += total or 0.00
				SUBTOTAL += total or 0.00

				ws.write(fila,1,line.rubro_estado_financiero.name or '',titulo2_left)
				fila += 1
				#######################################################################
				if line.rubro_estado_financiero.account_ids:

					records = self.query_balance_of_sums_and_balances(line.rubro_estado_financiero.account_ids.mapped('id'),self.fecha_inicio,self.fecha_final,'2')
						
					## cuenta - descripcion - deudor - acreedor
					for record in records:
						saldos_finales_deudor=(record['debit_saldo_inicial'] or 0.00) + (record['debit_movimiento_periodo'] or 0.00)
						saldos_finales_acreedor=(record['credit_saldo_inicial'] or 0.00) + (record['credit_movimiento_periodo'] or 0.00)

						balance=saldos_finales_deudor - saldos_finales_acreedor
						ws.write(fila,1,record['code'] or '',titulo2_right)
						ws.write(fila,2,record['name'] or '',titulo2_right)
						ws.write(fila,3,balance if balance >=0.00 else '',titulo2_right)
						ws.write(fila,4,abs(balance) if balance < 0.00 else '',titulo2_right)
						fila +=1
					#######################################################################
				ws.write(fila,3,total if total >=0.00 else '',titulo2_right)
				ws.write(fila,4,abs(total) if total < 0.00 else '',titulo2_right)

		workbook.close()