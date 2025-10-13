# -*- coding: utf-8 -*-
import calendar
from io import BytesIO, StringIO
from odoo import models, fields, api, _
from datetime import datetime, timedelta
import xlsxwriter
from odoo.exceptions import UserError , ValidationError

import logging
_logger=logging.getLogger(__name__)


class WizardPrinterPleInventariosBalancesEstadoSituacionFinanciera(models.TransientModel):
	_name='wizard.printer.ple.inventarios.balances.3.1'
	_inherit='wizard.printer.ple.base'
	_description = "Modulo Formulario Impresión PLE Libro Inventarios y Balances 3.1"


	ple_inventarios_balances_3_1_line_id = fields.Many2one('ple.inventarios.balances.3.1',
		string="PLE INVENTARIOS BALANCES 3.1",
		readonly=True,required=True)


	identificador_operaciones = fields.Selection(
		selection=[('0','Cierre de operaciones'),('1','Empresa operativa'),('2','Cierre de libro')],
		string="Identificador de operaciones", required=True, default="1")


	identificador_libro = fields.Selection(selection='available_formats_diary_sunat',
		string="Identificador de libro",default='030100')

		
	print_order = fields.Selection(default="date")


	def available_formats_diary_sunat(self):
		formats=[('030100','Libro Inventarios y Balances-Estado de Situación Financiera')]
		return formats


	def criterios_impresion(self):
		res = super(WizardPrinterPleInventariosBalancesEstadoSituacionFinanciera, self).criterios_impresion() or []
		res += [('codigo_cuenta_desagregado','Código Cuenta Desagregado')]
		return res



	def action_print(self):
		if (self.print_format and self.identificador_libro and self.identificador_operaciones) :
			return super(WizardPrinterPleInventariosBalancesEstadoSituacionFinanciera , self).action_print()
		else:
			raise UserError(_('NO SE PUEDE IMPRIMIR, Los campos: Formato Impresión , Identificador de operaciones y Identificador de libro son obligatorios, llene esos campos !!!'))
			
	#############################################################

	def file_name(self, file_format):
		nro_de_registros = '1' if len(self.ple_inventarios_balances_3_1_line_id.ple_inventarios_balances_3_1_line_ids)>0 else '0'

		file_name = "LE%s%s%s00%s%s%s1.%s"%(
			self.ple_inventarios_balances_3_1_line_id.company_id.vat,
			"%s00" %(self.ple_inventarios_balances_3_1_line_id.fecha_final.strftime('%Y%m')),
			self.identificador_libro,
			self.identificador_operaciones,
			nro_de_registros,
			self.ple_inventarios_balances_3_1_line_id.currency_id.code_sunat or '1',
			file_format)

		return file_name


	########################################################
	def _init_buffer(self, output):

		if self.print_format == 'xlsx':
			self._generate_xlsx(output)
		elif self.print_format == 'txt':
			self._generate_txt(output)
		return output


	def _convert_object_date(self, date):
		# parametro date que retorna un valor vacio o el formato 01/01/2100 dia/mes/año
		if date:
			return date.strftime('%d/%m/%Y')
		else:
			return ''


	def _generate_txt(self, output):
	
		for line in self.ple_inventarios_balances_3_1_line_id.ple_inventarios_balances_3_1_line_ids:
			escritura="%s|%s|%s|%s|%s|\n" % (
				line.periodo,
				line.codigo_catalogo,
				line.codigo_rubro_estado_financiero,
				line.saldo_rubro_contable,
				line.indicador_estado_operacion)

			output.write(escritura.encode())
	####################################################################

	def _generate_xlsx(self, output):

		workbook = xlsxwriter.Workbook(output)
		ws = workbook.add_worksheet('3.1 Estado de Situación Financiera')
		titulo1 = workbook.add_format({'font_size': 12,'valign': 'vcenter', 'align': 'center', 'text_wrap': True, 'bold': True, 'font_name':'Arial'})
		titulo_1 = workbook.add_format({'font_size': 8, 'align': 'left', 'text_wrap': True, 'bold': True, 'font_name':'Arial'})
		titulo2 = workbook.add_format({'font_size': 8, 'align': 'center','valign': 'vcenter','color':'black', 'text_wrap': True, 'left':True, 'right':True,'bottom': True, 'top': True, 'bold':True , 'font_name':'Arial'})
		titulo2_left = workbook.add_format({'font_size': 8, 'align': 'left','valign': 'vcenter','color':'black', 'text_wrap': True, 'left':True, 'right':True,'bottom': True, 'top': True, 'bold':True , 'font_name':'Arial'})
		titulo2_right = workbook.add_format({'font_size': 8, 'align': 'right','valign': 'vcenter','color':'black', 'text_wrap': True, 'left':True, 'right':True,'bottom': True, 'top': True, 'bold':True , 'font_name':'Arial'})

		#######################################################
		titulo_2 = workbook.add_format({'font_size': 8, 'align': 'center', 'text_wrap': True, 'bold': True, 'font_name':'Arial'})
		##################################################################
		number_left = workbook.add_format({'font_size': 8, 'align': 'left', 'num_format': '#,##0.00', 'font_name':'Arial'})
		number_right = workbook.add_format({'font_size': 8, 'align': 'right', 'num_format': '#,##0.00', 'font_name':'Arial'})
		number_right_tax_rate = workbook.add_format({'font_size': 8, 'align': 'right', 'num_format': '#,##0.000', 'font_name':'Arial'})
		
		letter1 = workbook.add_format({'font_size': 7, 'align': 'left', 'font_name':'Arial'})
		letter3_negrita = workbook.add_format({'font_size': 7, 'align': 'right','num_format': '#,##0.00', 'font_name':'Arial','bold': True})

		ws.set_column('A:A', 15,letter1)
		ws.set_column('B:B', 15,letter1)
		ws.set_column('C:C', 15,letter1)
		ws.set_column('D:D', 15,letter3_negrita)
		ws.set_column('E:E', 15,letter3_negrita)
		ws.set_column('F:F', 4,letter3_negrita)

		ws.set_column('G:G', 15,letter1)
		ws.set_column('H:H', 15,letter1)
		ws.set_column('I:I', 15,letter1)
		ws.set_column('J:J', 15,letter3_negrita)
		ws.set_column('K:K', 15,letter3_negrita)

		ws.merge_range('A1:I2','FORMATO 3.24: LIBRO DE INVENTARIOS Y BALANCES: ESTADO DE SITUACIÓN FINANCIERA-BALANCE GENERAL ' + 'DEL 01.01 AL ' + self.ple_inventarios_balances_3_1_line_id.fecha_final.strftime('%d.%m'),titulo1)
	
		ws.merge_range('A4:D4','EJERCICIO:', titulo_1)
		ws.merge_range('E4:F4',self.ple_inventarios_balances_3_1_line_id.fecha_final.strftime('%Y') or '', titulo_1)
		
		ws.merge_range('A5:D5','RUC:', titulo_1)
		ws.write('E5:F5',self.ple_inventarios_balances_3_1_line_id.company_id.vat or '', titulo_1)

		ws.merge_range('A6:D6','APELLIDOS Y NOMBRES, DENOMINACIÓN O RAZÓN SOCIAL:', titulo_1)
		ws.merge_range('E6:F6',self.ple_inventarios_balances_3_1_line_id.company_id.name or '', titulo_1)

		ws.merge_range('A8:C8','', titulo2)
		ws.merge_range('D8:E8','EJERCICIO O PERIODO', titulo2)

		ws.merge_range('G8:I8','', titulo2)
		ws.merge_range('J8:K8','EJERCICIO O PERIODO', titulo2)
		#######################################################################
		imprimible_rubros_de_catalogo_3_1 = self.ple_inventarios_balances_3_1_line_id.ple_inventarios_balances_3_1_line_ids

		#######################################################################

		fila = 9
		fila +=1
		k=0
		interruptor=1
		for line in imprimible_rubros_de_catalogo_3_1:
			k += 1
			fila +=1
			if interruptor==0:
				break

			if line.rubro_estado_financiero.is_title:
				ws.merge_range("A%s:C%s"%(fila,fila),line.rubro_estado_financiero.title or '',titulo2_left)
				ws.merge_range("D%s:E%s"%(fila,fila),'',titulo2_left)

			elif line.rubro_estado_financiero.is_total:
				if line.rubro_estado_financiero.code_sunat not in ['1D020T']:
					ws.merge_range("A%s:C%s"%(fila,fila),line.rubro_estado_financiero.name or '',titulo2)
					ws.merge_range("D%s:E%s"%(fila,fila),line.saldo_rubro_contable or '',titulo2_right)
					fila +=2

				else:
					for i in range(6):
						fila +=1
						ws.merge_range("A%s:C%s"%(fila,fila),'',titulo2_left)
						ws.merge_range("D%s:E%s"%(fila,fila),'',titulo2_left)
					fila +=1
					ws.merge_range("A%s:C%s"%(fila,fila),line.rubro_estado_financiero.name or '',titulo2)
					ws.merge_range("D%s:E%s"%(fila,fila),line.saldo_rubro_contable or '',titulo2_right)
					interruptor=0

			else:
				
				if line.rubro_estado_financiero.account_ids:

					ws.merge_range("A%s:C%s"%(fila,fila),line.rubro_estado_financiero.name or '',titulo2_left)
					ws.merge_range("D%s:E%s"%(fila,fila),line.saldo_rubro_contable or '',titulo2_right)
				else:
					ws.merge_range("A%s:C%s"%(fila,fila),line.rubro_estado_financiero.name or '',titulo2_left)
					ws.merge_range("D%s:E%s"%(fila,fila),line.saldo_rubro_contable or '',titulo2_right)



		fila = 9
		fila +=1

		for line in imprimible_rubros_de_catalogo_3_1[k:]:
			fila +=1
			if line.rubro_estado_financiero.is_title:
				ws.merge_range("G%s:I%s"%(fila,fila),line.rubro_estado_financiero.title or '',titulo2_left)
				ws.merge_range("J%s:K%s"%(fila,fila),'',titulo2_left)

			elif line.rubro_estado_financiero.is_total:
				if line.rubro_estado_financiero.code_sunat not in ['1D070T']:
					ws.merge_range("G%s:I%s"%(fila,fila),line.rubro_estado_financiero.name or '',titulo2)
					ws.merge_range("J%s:K%s"%(fila,fila),line.saldo_rubro_contable or '',titulo2_right)
					fila +=2
				else:
					ws.merge_range("G%s:I%s"%(fila,fila),line.rubro_estado_financiero.name or '',titulo2)
					ws.merge_range("J%s:K%s"%(fila,fila),line.saldo_rubro_contable or '',titulo2)

			else:
				if line.rubro_estado_financiero.account_ids:
		
					ws.merge_range("G%s:I%s"%(fila,fila),line.rubro_estado_financiero.name or '',titulo2_left)
					ws.merge_range("J%s:K%s"%(fila,fila),line.saldo_rubro_contable or '',titulo2_right)
				else:
					ws.merge_range("G%s:I%s"%(fila,fila),line.rubro_estado_financiero.name or '',titulo2_left)
					ws.merge_range("J%s:K%s"%(fila,fila),line.saldo_rubro_contable or '',titulo2_right)


		workbook.close()