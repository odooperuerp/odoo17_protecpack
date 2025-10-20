# -*- coding: utf-8 -*-
import calendar
from io import BytesIO, StringIO
from odoo import models, fields, api, _
from datetime import datetime, timedelta
import xlsxwriter
from odoo.exceptions import UserError , ValidationError
from itertools import *

import logging
_logger=logging.getLogger(__name__)


class WizardPrinterPleDiaryCashBoxAndBanks(models.TransientModel):
	_name='wizard.printer.ple.diary.cash.box.and.banks'
	_inherit='wizard.printer.ple.base'
	_description = "Modulo Formulario Impresión PLE Libro Diario Caja-Bancos"


	ple_diary_cash_box_and_banks_id = fields.Many2one('ple.diary.cash.box.and.banks',string="PLE DIARIO",
		readonly=True,required=True)

	identificador_operaciones = fields.Selection(
		selection=[('0','Cierre de operaciones'),('1','Empresa operativa'),('2','Cierre de libro')],
		string="Identificador de operaciones", required=True, default="1")
	
	identificador_libro = fields.Selection(selection='available_formats_diary_sunat', string="Identificador de libro")

	print_order = fields.Selection(default="codigo_cuenta_desagregado")

	imprimir_columna_saldos = fields.Boolean(string="Imprimir Columna de Saldo",
		default=True)

	fecha_impresion=fields.Date(string="Fecha de Impresión manual",
		default=datetime(datetime.now().year,datetime.now().month,datetime.now().day).date())
	#################################################

	def action_print(self):
		if (self.print_format and self.identificador_libro and self.identificador_operaciones) :
			return super(WizardPrinterPleDiaryCashBoxAndBanks , self).action_print()
		else:
			raise UserError(_('NO SE PUEDE IMPRIMIR , Los campos: Formato Impresión , Identificador de operaciones y Identificador de libro son obligatorios, llene esos campos !!!'))
		

	def available_formats_diary_sunat(self):
		formats=[
				('010100','Libro Caja y Bancos-Detalle movimientos Efectivo'),
				('010200','Libro Caja y Bancos-Detalle movimientos Cta.Cte.')
			]
		return formats


	def criterios_impresion(self):
		res = super(WizardPrinterPleDiaryCashBoxAndBanks, self).criterios_impresion() or []
		res += [('codigo_cuenta_desagregado','Código Cuenta Desagregado')]
		return res


	
	def _get_order_print(self,object):

		if self.print_order == 'date':
			total=sorted(object, key=lambda WizardPrinterPleDiaryCashBoxAndBanksLine: (WizardPrinterPleDiaryCashBoxAndBanksLine.asiento_contable , WizardPrinterPleDiaryCashBoxAndBanksLine.codigo_cuenta_desagregado , WizardPrinterPleDiaryCashBoxAndBanksLine.fecha_contable))
		elif self.print_order == 'nro_documento':
			total=sorted(object , key=lambda WizardPrinterPleDiaryCashBoxAndBanksLine: (WizardPrinterPleDiaryCashBoxAndBanksLine.asiento_contable))
		elif self.print_order == 'codigo_cuenta_desagregado':
			total=sorted(object , key=lambda WizardPrinterPleDiaryCashBoxAndBanksLine: (WizardPrinterPleDiaryCashBoxAndBanksLine.asiento_contable , WizardPrinterPleDiaryCashBoxAndBanksLine.fecha_contable ,  WizardPrinterPleDiaryCashBoxAndBanksLine.codigo_cuenta_desagregado))
		return total

	

	def file_name(self, file_format):
		if self.identificador_libro == '010100':
			nro_de_registros = '1' if len(self.ple_diary_cash_box_and_banks_id.ple_diary_cash_box_and_banks_cash_line_ids)>0 else '0'
		elif self.identificador_libro == '010200':
			nro_de_registros = '1' if len(self.ple_diary_cash_box_and_banks_id.ple_diary_cash_box_and_banks_bank_line_ids)>0 else '0'

		if self.ple_diary_cash_box_and_banks_id.periodo:
			file_name = "LE%s%s%s00%s%s%s1.%s" % (self.company_id.vat, self.ple_diary_cash_box_and_banks_id._periodo_fiscal(),
									self.identificador_libro, self.identificador_operaciones, nro_de_registros,
									self.ple_diary_cash_box_and_banks_id.currency_id.code_sunat or '1', file_format)
		elif self.fecha:
			file_name = "LE%s%s%s00%s%s%s1.%s" % (self.company_id.vat, "%s00" %(self.date_to.strftime('%Y%m')),
									self.identificador_libro, self.identificador_operaciones, nro_de_registros,
									self.ple_diary_cash_box_and_banks_id.currency_id.code_sunat or '1', file_format)
		return file_name
	

	def _init_buffer(self, output):
		if self.print_format == 'xlsx':
			if self.identificador_libro == '010100':
				self._generate_caja_bancos_efectivo_xlsx(output)
			elif self.identificador_libro == '010200':
				self._generate_caja_bancos_cta_cte_xlsx(output)

		elif self.print_format == 'txt':
			if self.identificador_libro == '010100':
				self._generate_txt_cash(output)
			elif self.identificador_libro == '010200':
				self._generate_txt_bank(output)			
		return output


	def _convert_object_date(self, date):
		if date:
			return date.strftime("%d/%m/%Y")
		else:
			return ''


	def _generate_txt_cash(self, output):
	
		for line in self._get_order_print(self.ple_diary_cash_box_and_banks_id.ple_diary_cash_box_and_banks_cash_line_ids) :
			escritura="%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|\n" % (
				line.periodo_apunte,
				line.asiento_contable[:40] ,
				line.m_correlativo_asiento_contable[:10] ,
				line.codigo_cuenta_desagregado[:24] ,
				line.codigo_unidad_operacion[:24]  ,
				line.codigo_centro_costos[:24] ,
				line.tipo_moneda_origen[:3] ,
				line.tipo_comprobante_pago[:2] ,
				line.num_serie_comprobante_pago[:20] ,
				line.num_comprobante_pago[:20],
				self._convert_object_date(line.fecha_contable) ,
				self._convert_object_date(line.fecha_vencimiento) ,
				self._convert_object_date(line.fecha_operacion) ,
				line.glosa[:200] ,
				line.glosa_referencial[:200],
				format(line.movimientos_debe,".2f") ,
				format(line.movimientos_haber,".2f") ,
				line.dato_estructurado[:92] , 
				line.indicador_estado_operacion)

			output.write(escritura.encode())



	def _generate_txt_bank(self, output):
	
		for line in self._get_order_print(self.ple_diary_cash_box_and_banks_id.ple_diary_cash_box_and_banks_bank_line_ids) :
			escritura="%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|\n" % (
				line.periodo_apunte,
				line.asiento_contable[:40] ,
				line.m_correlativo_asiento_contable[:10] ,
				line.codigo_entidad_financiera,
                line.codigo_cuenta_bancaria_contribuyente,
                self._convert_object_date(line.fecha_operacion) ,
                line.medio_pago_utilizado,
                line.descripcion_operacion_bancaria,
               	line.tipo_doc_iden_emisor[:1] ,
				line.num_doc_iden_emisor[:15] ,
                line.apellidos_nombre_o_razon_social_girador_o_beneficiario,
                line.numero_transaccion_bancaria,
                format(line.movimientos_debe,".2f") ,
				format(line.movimientos_haber,".2f") ,
                line.indicador_estado_operacion)

			output.write(escritura.encode())
	
	#############################################################
	def _get_arbol_diarios_banks(self):
		tuplas_diarios=[]
		movimientos = self.ple_diary_cash_box_and_banks_id.ple_diary_cash_box_and_banks_bank_line_ids

		for line in movimientos:
			tuplas_diarios += [(
				line.diario.id,
				line.asiento_contable or '',
				line.fecha_operacion,
				line.medio_pago_utilizado,
				line.descripcion_operacion_bancaria,
				line.apellidos_nombre_o_razon_social_girador_o_beneficiario,
				line.numero_transaccion_bancaria,
				line.codigo_cuenta_desagregado_id.code,
				line.codigo_cuenta_desagregado_id.name or '',
				line.movimientos_debe,
				line.movimientos_haber,
				line.currency_movimientos_haber,
				line.currency_movimientos_debe,
				line.diario,
				line
				)]

		diccionario_diarios={}
		grupos_de_diarios = groupby(sorted(tuplas_diarios),lambda x : x[0] )



		for k , v in grupos_de_diarios:
			diccionario_diarios[k]=sorted(list(v), key=lambda u :u[7])

		return diccionario_diarios


	def _get_arbol_diarios_cash(self):
		tuplas_diarios=[]
		movimientos = self.ple_diary_cash_box_and_banks_id.ple_diary_cash_box_and_banks_cash_line_ids
		#movimientos = self.cash_impreso_line_ids

		for line in movimientos:
			tuplas_diarios += [(
				line.diario.id or '',
				line.asiento_contable or '',
				line.fecha_operacion or '',
				line.glosa or '',
				line.codigo_cuenta_desagregado_id.code or '',
				line.codigo_cuenta_desagregado_id.name or '',
				line.movimientos_debe,
				line.movimientos_haber,
				line.currency_movimientos_haber,
				line.currency_movimientos_debe,
				line.diario,
				line
				)]

		diccionario_diarios={}
		grupos_de_diarios = groupby(sorted(tuplas_diarios),lambda x : x[0] )

		for k , v in grupos_de_diarios:
			diccionario_diarios[k]=sorted(list(v), key=lambda u :u[4])
		return diccionario_diarios
	################################################################

	def get_diarios_cash_sin_movimientos_periodo(self):
		account_journal_cash_ids=self.env['account.journal'].search([('type','in',['cash']),('is_ple_caja_bancos','=',True)])
		account_journal_cash_period_ids = self.ple_diary_cash_box_and_banks_id.ple_diary_cash_box_and_banks_cash_line_ids.mapped('diario')

		if account_journal_cash_ids:
			return account_journal_cash_ids - account_journal_cash_period_ids



	def get_diarios_bank_sin_movimientos_periodo(self):
		account_journal_bank_ids=self.env['account.journal'].search([('type','in',['bank']),('is_ple_caja_bancos','=',True)])

		account_journal_bank_period_ids = self.ple_diary_cash_box_and_banks_id.ple_diary_cash_box_and_banks_bank_line_ids.mapped('diario')

		if account_journal_bank_ids:
			return account_journal_bank_ids - account_journal_bank_period_ids


	##########################################################################################

	def _generate_caja_bancos_efectivo_xlsx(self, output):
		workbook = xlsxwriter.Workbook(output)
		ws = workbook.add_worksheet('Libro Caja Bancos-Detalle Movimientos del Efectivo')

		titulo1 = workbook.add_format({'font_size': 16, 'align': 'center', 'text_wrap': True, 'bold': True, 'font_name':'Arial'})
		titulo_1 = workbook.add_format({'font_size': 8, 'align': 'left', 'text_wrap': True, 'bold': True, 'font_name':'Arial'})
		titulo2 = workbook.add_format({'font_size': 8, 'align': 'center','valign': 'vcenter','color':'black', 'text_wrap': True,
			'left':True, 'right':True,'bottom': True, 'top': True, 'bold':True , 'font_name':'Arial'})
		titulo_2 = workbook.add_format({'font_size': 8, 'align': 'left', 'text_wrap': True, 'bold': True, 'font_name':'Arial'})
		titulo5 = workbook.add_format({'font_size': 10, 'align': 'left', 'text_wrap':True, 'font_name':'Arial', 'bold':True})
		titulo6 = workbook.add_format({'font_size': 8, 'align': 'right', 'text_wrap': True, 'top': True, 'bold':True , 'font_name':'Arial'})
		number_left = workbook.add_format({'font_size': 8, 'align': 'left', 'num_format': '#,##0.00', 'font_name':'Arial'})
		number_right = workbook.add_format({'font_size': 8, 'align': 'right', 'num_format': '#,##0.00', 'font_name':'Arial'})

		letter1 = workbook.add_format({'font_size': 7, 'align': 'left', 'font_name':'Arial'})
		letter3 = workbook.add_format({'font_size': 7, 'align': 'right','num_format': '#,##0.00', 'font_name':'Arial'})
		letter3_negrita = workbook.add_format({'font_size': 7, 'align': 'right','num_format': '#,##0.00', 'font_name':'Arial','bold': True})

		ws.set_column('A:A', 2,letter1)
		ws.set_column('B:B', 22.14,letter1)
		ws.set_column('C:C', 12.71,letter1)
		ws.set_column('D:D', 37.86,letter1)
		ws.set_column('E:E', 17,letter1)
		ws.set_column('F:F', 23,letter1)
		ws.set_column('G:G',17,number_right)
		ws.set_column('H:H',17,number_right)
		ws.set_column('I:I',17,number_right)

		ws.merge_range('A1:I1','FORMATO 1.1: LIBRO CAJA BANCOS-DETALLE DE LOS MOVIMIENTOS DEL EFECTIVO',titulo1)
		ws.merge_range('B11:B12','NÚMERO CORRELATIVO DEL REGISTRO O CÓDIGO ÚNICO DE LA OPERACIÓN', titulo2)

		ws.merge_range('C11:C12','FECHA DE LA OPERACIÓN', titulo2)
		ws.merge_range('D11:D12','DESCRIPCIÓN DE LA OPERACIÓN', titulo2)

		ws.merge_range('E11:F11','CUENTA CONTABLE ASOCIADA', titulo2)

		ws.write('E12','CÓDIGO', titulo2)
		ws.write('F12','DENOMINACIÓN', titulo2)


		ws.merge_range('G11:H11','SALDOS Y MOVIMIENTOS', titulo2)
		ws.write('G12','DEUDOR', titulo2)
		ws.write('H12','ACREEDOR', titulo2)

		ws.write(2,1,"PERIODO : ", titulo_2)
		ws.write(2,2 , (self.ple_diary_cash_box_and_banks_id.fiscal_month +  " del " + self.ple_diary_cash_box_and_banks_id.fiscal_year if self.ple_diary_cash_box_and_banks_id.periodo else "%s - %s"%(
			self.ple_diary_cash_box_and_banks_id.fecha_inicio.strftime('%Y-%m-%d'),self.fecha_fin.strftime('%Y-%m-%d'))) , titulo_2)

		ws.write(3,1,'RUC : ',titulo_2)
		ws.merge_range('B5:D5','APELLIDO Y NOMBRES, DENOMINACIÓN O RAZÓN SOCIAL:',titulo_2)
		ws.write(3,2,self.company_id.vat ,titulo_2)
		ws.merge_range('E5:F5',self.company_id.name ,titulo_2)


		if self.ple_diary_cash_box_and_banks_id.cash_journal_id:
			ws.merge_range('B7:D7',"CAJA : " + ','.join(list(self.ple_diary_cash_box_and_banks_id.cash_journal_id.mapped('name'))) , titulo_2)

		fila=12
		haber_asiento_contable=0
		deber_asiento_contable=0
		total_deber=0
		total_haber=0


		if self.ple_diary_cash_box_and_banks_id.ple_diary_cash_box_and_banks_cash_line_ids:
			diccionario_diarios = self._get_arbol_diarios_cash()

			total_conjunto_haber = 0.00
			total_conjunto_debe = 0.00


			for elemento_diario in diccionario_diarios:
				fila += 1
				
				total_haber = 0.00
				total_deber = 0.00
				total_currency = 0.00
				
				journal_id = self.env['account.journal'].browse(elemento_diario)

				_logger.info(elemento_diario)
				ws.merge_range("B%s:D%s"%(fila+1,fila+1),"CAJA : " + (journal_id.name or '') + '-' + (journal_id.default_account_id.code or '') , titulo_2)
				
				fila += 1

				ws.write(fila,1,"PERIODO :" + self.ple_diary_cash_box_and_banks_id.fiscal_month)
				ws.write(fila,5,"** SALDO INICIAL **")

				saldo_inicial_diario = 0.00
				saldo_inicial_calculado = self.ple_diary_cash_box_and_banks_id._hallar_saldo_inicial(journal_id.default_account_id,self.ple_diary_cash_box_and_banks_id.fecha_inicio)

				saldo_inicial_debe = 0.00
				saldo_inicial_haber = 0.00
				saldo_inicial_currency = 0.00
				#######################################################
				
				if saldo_inicial_calculado:
					saldo_inicial_diario = saldo_inicial_calculado[0]['balance_total']

				if saldo_inicial_diario >= 0.00:
					ws.write(fila,6,abs(saldo_inicial_diario))
					saldo_inicial_debe = abs(saldo_inicial_diario)

				else:
					ws.write(fila,7,abs(saldo_inicial_diario))
					saldo_inicial_haber = abs(saldo_inicial_diario)

				################## CAMPO ME SI JOURNAL LO ES ##########
				is_journal_in_me = False
				is_journal_in_me = journal_id.currency_id and self.company_id.currency_id != journal_id.currency_id
				
				if is_journal_in_me:
					record_initial_cash = self.ple_diary_cash_box_and_banks_id._hallar_saldo_inicial_currency(journal_id.default_account_id,self.ple_diary_cash_box_and_banks_id.fecha_inicio)
					if record_initial_cash:
						initial_balance_cash = record_initial_cash[0]['balance_total_currency']

						ws.write(fila,8,initial_balance_cash)
						saldo_inicial_currency = initial_balance_cash
				############################################################################
				if is_journal_in_me:

					saldo_actual = 0.00

					for line3 in diccionario_diarios[elemento_diario]:
						fila += 1
						ws.write(fila,1, line3[11].asiento_contable or '')
						ws.write(fila,2,self._convert_object_date(line3[11].fecha_operacion) or '' )
						ws.write(fila,3,line3[11].glosa or '' )
						ws.write(fila,4,line3[11].codigo_cuenta_desagregado_id.code or '')
						ws.write(fila,5,line3[11].codigo_cuenta_desagregado_id.name or '')
						ws.write(fila,6,line3[11].movimientos_debe)
						ws.write(fila,7,line3[11].movimientos_haber)
						ws.write(fila,8,(line3[11].currency_movimientos_debe or 0.00) - (line3[11].currency_movimientos_haber or 0.00))

						total_haber += line3[11].movimientos_haber
						total_deber += line3[11].movimientos_debe
						total_currency += (line3[11].currency_movimientos_debe or 0.00) - (line3[11].currency_movimientos_haber or 0.00)

						if self.ple_diary_cash_box_and_banks_id.cash_journal_id and self.imprimir_columna_saldos:
							saldo_actual += line3[11].movimientos_debe - line3[11].movimientos_haber
							ws.write(fila,8,saldo_actual)


					fila += 1
					ws.write(fila,5,"TOTAL EN CAJA %s"%(journal_id.name or ''), titulo_2)
					ws.write(fila,6,total_deber)
					ws.write(fila,7,total_haber)
					ws.write(fila,8,total_currency)
					#####################################################
					fila += 1
					ws.write(fila , 5,"SALDO FINAL CAJA %s"%(journal_id.name or ''), titulo_2)
					saldo_final_caja = total_deber - total_haber + saldo_inicial_diario
					if saldo_final_caja >= 0.00:
						ws.write(fila,6,abs(saldo_final_caja))
					else:
						ws.write(fila,7,abs(saldo_final_caja))

				else:

					saldo_actual= 0.00

					for line3 in diccionario_diarios[elemento_diario]:
						fila += 1
						ws.write(fila,1, line3[11].asiento_contable or '')
						ws.write(fila,2,self._convert_object_date(line3[11].fecha_operacion) or '' )
						ws.write(fila,3,line3[11].glosa or '' )
						ws.write(fila,4,line3[11].codigo_cuenta_desagregado_id.code or '')
						ws.write(fila,5,line3[11].codigo_cuenta_desagregado_id.name or '')
						ws.write(fila,6,line3[11].movimientos_debe)
						ws.write(fila,7,line3[11].movimientos_haber)

						total_haber += line3[11].movimientos_haber
						total_deber += line3[11].movimientos_debe
						total_conjunto_debe += total_deber
						total_conjunto_haber += total_haber
						if self.ple_diary_cash_box_and_banks_id.cash_journal_id and self.imprimir_columna_saldos:
							saldo_actual += line3[11].movimientos_debe - line3[11].movimientos_haber
							ws.write(fila,8,saldo_actual)

					fila += 1
					ws.write(fila , 5,"TOTAL EN CAJA %s"%(journal_id.name or ''), titulo_2)
					ws.write(fila  , 6 ,  total_deber)
					ws.write(fila  , 7 ,  total_haber)
					#####################################################
					fila += 1
					ws.write(fila ,5,"SALDO FINAL CAJA %s"%(journal_id.name or ''), titulo_2)
					saldo_final_caja = total_deber - total_haber + saldo_inicial_diario
					if saldo_final_caja >= 0.00:
						ws.write(fila,6,abs(saldo_final_caja))
					else:
						ws.write(fila,7,abs(saldo_final_caja))
				###############################################################################

		####################### ADICIONANDO DIARIOS CON SALDOS INICIALES PERO SIN MOVIMIENTO EN EL PERIODO ##########
		fila += 1

		diarios_faltantes = self.get_diarios_cash_sin_movimientos_periodo()

		if diarios_faltantes:
			for elemento_diario in diarios_faltantes:
					
				total_haber = 0.00
				total_deber = 0.00
				total_currency = 0.00
					
				journal_id = elemento_diario

				saldo_inicial_diario = 0.00
				saldo_inicial_calculado = self.ple_diary_cash_box_and_banks_id._hallar_saldo_inicial(journal_id.default_account_id,self.ple_diary_cash_box_and_banks_id.fecha_inicio)

				saldo_inicial_debe = 0.00
				saldo_inicial_haber = 0.00
				saldo_inicial_currency = 0.00
					#######################################################
					
				if saldo_inicial_calculado:
					saldo_inicial_diario = saldo_inicial_calculado[0]['balance_total']

				if saldo_inicial_diario != 0.00:
					fila += 1

					ws.merge_range("B%s:D%s"%(fila+1,fila+1),"CAJA : " + (journal_id.name or '') + '-' + (journal_id.default_account_id.code or '') , titulo_2)
					
					fila += 1

					ws.write(fila,1,"PERIODO :" + self.ple_diary_cash_box_and_banks_id.fiscal_month)
					ws.write(fila,5,"** SALDO INICIAL **")

					if saldo_inicial_diario >= 0.00:
						ws.write(fila,6,abs(saldo_inicial_diario))
						saldo_inicial_debe = abs(saldo_inicial_diario)

					else:
						ws.write(fila,7,abs(saldo_inicial_diario))
						saldo_inicial_haber = abs(saldo_inicial_diario)

						################## CAMPO ME SI JOURNAL LO ES ##########
					is_journal_in_me = False
					is_journal_in_me = journal_id.currency_id and self.company_id.currency_id != journal_id.currency_id
						
					if is_journal_in_me:
						record_initial_cash = self.ple_diary_cash_box_and_banks_id._hallar_saldo_inicial_currency(journal_id.default_account_id,self.ple_diary_cash_box_and_banks_id.fecha_inicio)
						if record_initial_cash:
							initial_balance_cash = record_initial_cash[0]['balance_total_currency']

							ws.write(fila,8,initial_balance_cash)
							saldo_inicial_currency = initial_balance_cash
						############################################################################
					if is_journal_in_me:

						fila += 1
						ws.write(fila,5,"TOTAL EN CAJA %s"%(journal_id.name or ''), titulo_2)
						ws.write(fila,6,saldo_inicial_debe)
						ws.write(fila,7,saldo_inicial_haber)
						ws.write(fila,8,saldo_inicial_currency)

							#####################################################
						fila += 1
						ws.write(fila ,5,"SALDO FINAL CAJA %s"%(journal_id.name or ''), titulo_2)
						saldo_final_caja = saldo_inicial_debe - saldo_inicial_haber

						if saldo_final_caja >= 0.00:
							ws.write(fila,6,abs(saldo_final_caja))
						else:
							ws.write(fila,7,abs(saldo_final_caja))

					else:

						fila += 1
						ws.write(fila , 5,"TOTAL EN CAJA %s"%(journal_id.name or ''), titulo_2)
						ws.write(fila  , 6 ,saldo_inicial_debe)
						ws.write(fila  , 7 ,saldo_inicial_haber)
						#####################################################
						fila += 1
						ws.write(fila ,5,"SALDO FINAL CAJA %s"%(journal_id.name or ''), titulo_2)
						saldo_final_caja = saldo_inicial_debe - saldo_inicial_haber
						if saldo_final_caja >= 0.00:
							ws.write(fila,6,abs(saldo_final_caja))
						else:
							ws.write(fila,7,abs(saldo_final_caja))
				###############################################################################


		fila += 1
		ws.write(fila , 5,"TOTAL EN PERIODO " + (self.ple_diary_cash_box_and_banks_id.fiscal_month if self.ple_diary_cash_box_and_banks_id.periodo else "%s - %s"%(self.ple_diary_cash_box_and_banks_id.fecha_inicio.strftime('%Y-%m-%d'),self.fecha_fin.strftime('%Y-%m-%d'))), titulo_2)

		if self.ple_diary_cash_box_and_banks_id.end_balance_cash >=0.00:
			ws.write(fila,6,abs(self.ple_diary_cash_box_and_banks_id.end_balance_cash))
		else:
			ws.write(fila,7,abs(self.ple_diary_cash_box_and_banks_id.end_balance_cash))

		fila += 1
		workbook.close()



	def _generate_caja_bancos_cta_cte_xlsx(self, output):
		workbook = xlsxwriter.Workbook(output)
		ws = workbook.add_worksheet('Libro diario caja bancos-detalle movimientos cuenta cte')

		titulo1 = workbook.add_format({'font_size': 16, 'align': 'center', 'text_wrap': True, 'bold': True, 'font_name':'Arial'})
		titulo_1 = workbook.add_format({'font_size': 8, 'align': 'left', 'text_wrap': True, 'bold': True, 'font_name':'Arial'})
		titulo2 = workbook.add_format({'font_size': 8, 'align': 'center','valign': 'vcenter','color':'black', 'text_wrap': True, 'left':True, 'right':True,'bottom': True, 'top': True, 'bold':True , 'font_name':'Arial'})
		titulo_2 = workbook.add_format({'font_size': 8, 'align': 'left', 'text_wrap': True, 'bold': True, 'font_name':'Arial'})
		titulo5 = workbook.add_format({'font_size': 10, 'align': 'left', 'text_wrap':True, 'font_name':'Arial', 'bold':True})
		titulo6 = workbook.add_format({'font_size': 8, 'align': 'right', 'text_wrap': True, 'top': True, 'bold':True , 'font_name':'Arial'})
		
		number_left = workbook.add_format({'font_size': 8, 'align': 'left', 'num_format': '#,##0.00', 'font_name':'Arial'})
		number_right = workbook.add_format({'font_size': 8, 'align': 'right', 'num_format': '#,##0.00', 'font_name':'Arial'})

		letter1 = workbook.add_format({'font_size': 7, 'align': 'left', 'font_name':'Arial'})
		letter3 = workbook.add_format({'font_size': 7, 'align': 'right','num_format': '#,##0.00', 'font_name':'Arial'})
		letter3_negrita = workbook.add_format({'font_size': 7, 'align': 'right','num_format': '#,##0.00', 'font_name':'Arial','bold': True})

		ws.set_column('A:A', 2,letter1)
		ws.set_column('B:B', 22.14,letter1)
		ws.set_column('C:C', 12.71,letter1)
		ws.set_column('D:D', 19,letter1)
		ws.set_column('E:E', 23,letter1)
		ws.set_column('F:F', 24,letter1)
		ws.set_column('G:G',17,letter3)
		ws.set_column('H:H',17,letter3)
		ws.set_column('I:I',20,letter1)
		ws.set_column('J:J',12.71,number_right)
		ws.set_column('K:K',12.71,number_right)
		ws.set_column('L:L',12.71,number_right)

		
		ws.merge_range('A1:I1','FORMATO 1.2: LIBRO CAJA BANCOS-DETALLE DE LOS MOVIMIENTOS DE LA CUENTA CORRIENTE',titulo1)
		
		ws.merge_range('B10:B13','NÚMERO CORRELATIVO DEL REGISTRO O CÓDIGO ÚNICO DE LA OPERACIÓN', titulo2)
	
		ws.merge_range('C10:C13','FECHA DE LA OPERACIÓN', titulo2)
		
		ws.merge_range('D10:G11','OPERACIONES BANCARIAS', titulo2)

		ws.merge_range('D12:D13','MEDIO DE PAGO (COD)', titulo2)

		ws.merge_range('E12:E13','DESCRIPCIÓN DE LA OPERACIÓN', titulo2)

		ws.merge_range('F12:F13','APELLIDO Y NOMBRES, DENOMINACIÓN O RAZÓN SOCIAL:',titulo2)

		ws.merge_range('G12:G13','NÚMERO DE TRANSACCIÓN BANCARIA DE DOCUMENTO SUSTENTATORIO O DE CONTROL INTERNO DE LA OPERACIÓN',titulo2)

		ws.merge_range('H10:I11','CUENTA CONTABLE ASOCIADA', titulo2)

		ws.merge_range('H12:H13','CÓDIGO', titulo2)
		
		ws.merge_range('I12:I13','DENOMINACIÓN', titulo2)

		ws.merge_range('J10:K11','SALDOS Y MOVIMIENTOS', titulo2)
		ws.merge_range('J12:J13','DEUDOR', titulo2)
		ws.merge_range('K12:K13','ACREEDOR', titulo2)


		ws.write(2,1,"PERIODO : ", titulo_2)
		ws.write(2,2 , (self.ple_diary_cash_box_and_banks_id.fiscal_month +  " al " + self.ple_diary_cash_box_and_banks_id.fiscal_month + " del " + self.ple_diary_cash_box_and_banks_id.fiscal_year) if self.ple_diary_cash_box_and_banks_id.periodo else "%s-%s"%(self.ple_diary_cash_box_and_banks_id.fecha_inicio.strftime('%Y-%m-%d'),self.fecha_fin.strftime('%Y-%m-%d')), titulo_2)
		ws.write(3,1,'RUC : ',titulo_2)
		ws.merge_range('B5:D5','APELLIDO Y NOMBRES, DENOMINACIÓN O RAZÓN SOCIAL: ',titulo_2)
		ws.write(3,2,self.company_id.vat ,titulo_2)
		ws.merge_range('E5:F5',self.company_id.name ,titulo_2)

		if self.ple_diary_cash_box_and_banks_id.bank_journal_id:
			ws.merge_range('B7:E7',','.join(list(self.ple_diary_cash_box_and_banks_id.bank_journal_id.mapped('name'))),titulo_2)
			ws.merge_range('B8:C8','Código de la cuenta corriente: ',titulo_2)
			ws.merge_range('D8:E8',','.join(list(self.ple_diary_cash_box_and_banks_id.bank_journal_id.mapped('bank_account_id.acc_number'))) or '',titulo_2)

		fila=13

		total_haber=0
		total_deber=0
		total_currency = 0.00


		if self.ple_diary_cash_box_and_banks_id.ple_diary_cash_box_and_banks_bank_line_ids:
			diccionario_diarios = self._get_arbol_diarios_banks()
			
			total_conjunto_haber = 0.00
			total_conjunto_debe = 0.00

			for elemento_diario in diccionario_diarios:
				fila += 1

				total_haber = 0.00
				total_deber = 0.00
				total_currency = 0.00

				journal_id = self.env['account.journal'].browse(elemento_diario)

				ws.merge_range("B%s:D%s"%(fila+1,fila+1),"CTA.CTE : " + (journal_id.name or '') + '-' + (journal_id.default_account_id.code or '') , titulo_2)

				########################################################
				fila += 1

				ws.write(fila,1,"PERIODO :" + self.ple_diary_cash_box_and_banks_id.fiscal_month)
				ws.write(fila,8,"** SALDO INICIAL **")

				saldo_inicial_diario = 0.00

				_logger.info('\n\nFECHA INICIO\n\n')
				_logger.info(self.ple_diary_cash_box_and_banks_id.fecha_inicio)

				saldo_inicial_calculado = self.ple_diary_cash_box_and_banks_id._hallar_saldo_inicial(journal_id.default_account_id,self.ple_diary_cash_box_and_banks_id.fecha_inicio)
				_logger.info('\n\nSALDO INICIAL CALCULADO\n\n')
				_logger.info(saldo_inicial_calculado)
				
				if saldo_inicial_calculado:
					saldo_inicial_diario = saldo_inicial_calculado[0]['balance_total']

				saldo_inicial_debe = 0.00
				saldo_inicial_haber = 0.00
				if saldo_inicial_diario >= 0.00:
					ws.write(fila,9,abs(saldo_inicial_diario))
					saldo_inicial_debe = abs(saldo_inicial_diario)
				else:
					ws.write(fila,10,abs(saldo_inicial_diario))
					saldo_inicial_haber = abs(saldo_inicial_diario)

				################## CAMPO ME SI JOURNAL LO ES ##########
				is_journal_in_me = False
				is_journal_in_me = journal_id.currency_id and self.company_id.currency_id != journal_id.currency_id
				
				if is_journal_in_me:
					record_initial_bank = self.ple_diary_cash_box_and_banks_id._hallar_saldo_inicial_currency(journal_id.default_account_id,self.ple_diary_cash_box_and_banks_id.fecha_inicio)
					if record_initial_bank:
						initial_balance_bank = record_initial_bank[0]['balance_total_currency']

						ws.write(fila,11,initial_balance_bank)
						saldo_inicial_currency = initial_balance_bank
				############################################################################
				if is_journal_in_me:

					saldo_actual = 0.00

					for line3 in diccionario_diarios[elemento_diario]:
						fila += 1
						ws.write(fila,1,line3[14].asiento_contable or '')
						ws.write(fila,2,self._convert_object_date(line3[14].fecha_operacion) or '' )
						ws.write(fila,3,line3[3] or '999' )
						
						ws.write(fila,4,line3[14].descripcion_operacion_bancaria or '' )
						ws.write(fila, 5 ,line3[14].apellidos_nombre_o_razon_social_girador_o_beneficiario or '')
						ws.write(fila,6,line3[14].numero_transaccion_bancaria or '')	
						ws.write(fila,7,line3[14].codigo_cuenta_desagregado_id.code or '')
						ws.write(fila,8,line3[14].codigo_cuenta_desagregado_id.name or '')

						ws.write(fila,9,line3[14].movimientos_debe)
						ws.write(fila,10,line3[14].movimientos_haber)
						ws.write(fila,11,(line3[14].currency_movimientos_debe or 0.00) - (line3[14].currency_movimientos_haber or 0.00))

						total_haber += line3[14].movimientos_haber
						total_deber += line3[14].movimientos_debe
						total_currency += (line3[14].currency_movimientos_debe or 0.00) - (line3[14].currency_movimientos_haber or 0.00)

						total_conjunto_debe += total_deber
						total_conjunto_haber += total_haber
						
						if  self.ple_diary_cash_box_and_banks_id.bank_journal_id and self.imprimir_columna_saldos:
							saldo_actual += line3[14].movimientos_debe - line3[14].movimientos_haber
							ws.write(fila,11,saldo_actual)

					fila += 1
					ws.write(fila,7,"TOTAL CTA.CTE %s"%(journal_id.name or ''), titulo_2)
					ws.write(fila,9,total_deber)
					ws.write(fila,10,total_haber)
					ws.write(fila,11,total_currency)
					#####################################################
					fila += 1
					ws.write(fila , 7,"SALDO FINAL CTA.CTE %s"%(journal_id.name or ''), titulo_2)
					saldo_final_banco = total_deber - total_haber + saldo_inicial_diario
					if saldo_final_banco >= 0.00:
						ws.write(fila,9,abs(saldo_final_banco))
					else:
						ws.write(fila,10,abs(saldo_final_banco))

				else:
					saldo_actual = 0.00
					
					for line3 in diccionario_diarios[elemento_diario]:
						fila += 1
						ws.write(fila,1,line3[14].asiento_contable or '')
						ws.write(fila,2,self._convert_object_date(line3[14].fecha_operacion) or '' )
						ws.write(fila,3,line3[3] or '999' )
						
						ws.write(fila,4,line3[14].descripcion_operacion_bancaria or '' )
						ws.write(fila, 5 ,line3[14].apellidos_nombre_o_razon_social_girador_o_beneficiario or '')
						ws.write(fila,6,line3[14].numero_transaccion_bancaria or '')	
						ws.write(fila,7,line3[14].codigo_cuenta_desagregado_id.code or '')
						ws.write(fila,8,line3[14].codigo_cuenta_desagregado_id.name or '')

						ws.write(fila,9,line3[14].movimientos_debe)
						ws.write(fila,10,line3[14].movimientos_haber)

						total_haber += line3[14].movimientos_haber
						total_deber += line3[14].movimientos_debe
						total_conjunto_debe += total_deber
						total_conjunto_haber += total_haber
						
						if self.ple_diary_cash_box_and_banks_id.bank_journal_id and self.imprimir_columna_saldos:
							saldo_actual += line3[14].movimientos_debe - line3[14].movimientos_haber
							ws.write(fila,11,saldo_actual)

					fila += 1
					ws.write(fila , 7,"TOTAL MOV CTA.CTE %s"%(journal_id.name or ''), titulo_2)
					ws.write(fila  , 9 ,  total_deber)
					ws.write(fila  , 10 ,  total_haber)
					#####################################################
					fila += 1
					ws.write(fila , 7,"SALDO FINAL CTA.CTE %s"%(journal_id.name or ''), titulo_2)
					saldo_final_banco = total_deber - total_haber + saldo_inicial_diario
					if saldo_final_banco >= 0.00:
						ws.write(fila,9,abs(saldo_final_banco))
					else:
						ws.write(fila,10,abs(saldo_final_banco))


			fila += 1
			ws.write(fila , 7,"TOTAL EN PERIODO " + (self.ple_diary_cash_box_and_banks_id.fiscal_month if self.ple_diary_cash_box_and_banks_id.periodo else "%s - %s"%(self.ple_diary_cash_box_and_banks_id.fecha_inicio.strftime('%Y-%m-%d'),self.fecha_fin.strftime('%Y-%m-%d'))), titulo_2)
			if self.ple_diary_cash_box_and_banks_id.end_balance_bank >=0.00:
				ws.write(fila,9,abs(self.ple_diary_cash_box_and_banks_id.end_balance_bank))
			else:
				ws.write(fila,10,abs(self.ple_diary_cash_box_and_banks_id.end_balance_bank))

		fila += 1

		workbook.close()
