# -*- coding: utf-8 -*-
import calendar
from io import BytesIO, StringIO
from odoo import models, fields, api, _
from datetime import datetime, timedelta
import xlsxwriter
from odoo.exceptions import UserError , ValidationError

import logging
_logger=logging.getLogger(__name__)


class WizardPrinterPleInventariosBalancesSaldoCuenta50(models.TransientModel):
	_name='wizard.printer.ple.inventarios.balances.3.16'
	_inherit='wizard.printer.ple.base'
	_description = "Modulo Formulario Impresión PLE Libro Inventarios y Balance 3.16"

	ple_inventarios_balances_3_16_line_id = fields.Many2one('ple.inventarios.balances.3.16',
		string="PLE INVENTARIOS Y BALANCES-SALDO CUENTA 50",readonly=True,required=True)

	identificador_operaciones = fields.Selection(
		selection=[('0','Cierre de operaciones'),('1','Empresa operativa'),('2','Cierre de libro')],
		string="Identificador de operaciones", required=True, default="1")

	identificador_libro = fields.Selection(selection='available_formats_diary_sunat',
		string="Identificador de libro",default='031601',required=True)
		
	print_order = fields.Selection(default="date") 

	######################################################################################

	def action_print(self):
		if (self.print_format and self.identificador_libro and self.identificador_operaciones) :
			if self.print_format =='pdf':
				pass
			else:
				return super(WizardPrinterPleInventariosBalancesSaldoCuenta50 , self).action_print()
		else:
			raise UserError(_('NO SE PUEDE IMPRIMIR , Los campos: Formato Impresión , Identificador de operaciones y Identificador de libro son obligatorios, llene esos campos !!!'))


	def available_formats_diary_sunat(self):
		formats=[('031601','Libro Inventarios y Balances-Detalle Saldo Cuenta 50'),
			('031602','Libro Inventarios y Balances-Estructura Participación Accionaria')]
		return formats



	def _get_order_print(self,object):

		if self.print_order == 'date':
			total=sorted(object, key=lambda PleInventariosBalances316: (PleInventariosBalances316.periodo))
	
		return total


	def file_name(self, file_format):
		if self.identificador_libro=='031601':
			nro_de_registros = '1' if len(self.ple_inventarios_balances_3_16_line_id.ple_inventarios_balances_3_16_1_line_ids)>0 else '0'
			
		elif self.identificador_libro=='031602':
			nro_de_registros = '1' if len(self.ple_inventarios_balances_3_16_line_id.ple_inventarios_balances_3_16_2_line_ids)>0 else '0'

		file_name = "LE%s%s%s00%s%s%s1.%s" % (
			self.ple_inventarios_balances_3_16_line_id.company_id.vat,
			"%s00" %(self.ple_inventarios_balances_3_16_line_id.fecha_final.strftime('%Y%m')),
			self.identificador_libro,
			self.identificador_operaciones,
			nro_de_registros,
			'1',
			file_format)

		return file_name



	def _init_buffer(self, output):

		if self.print_format == 'xlsx':
			self. _generate_xlsx_inventories_balances_3_16(output)
		elif self.print_format == 'txt':
			self._generate_txt(output)
		return output



	def _convert_object_date(self, date):
		# parametro date que retorna un valor vacio o el formato 01/01/2100 dia/mes/año
		if date:
			return date.strftime('%d/%m/%Y')
		else:
			return ''

	##########################################################################

	def _generate_txt(self, output):

		if self.identificador_libro=='031601':
			for line in self.ple_inventarios_balances_3_16_line_id.ple_inventarios_balances_3_16_1_line_ids:
				###########################################################
				escritura="%s|%s|%s|%s|%s|%s|\n" % (
					line.periodo or '',
					line.importe_capital_social_participaciones or 0.00,
					line.valor_nominal_por_accion or 0.00,
					line.numero_acciones_participaciones_sociales or 0.00,
					line.numero_acciones_participaciones_sociales_pagadas or 0.00,
					line.indicador_estado_operacion or '')

				output.write(escritura.encode())

		elif self.identificador_libro=='031602':
			for line in self.ple_inventarios_balances_3_16_line_id.ple_inventarios_balances_3_16_2_line_ids:
				###########################################################
				escritura="%s|%s|%s|%s|%s|%s|%s|%s|\n" % (
					line.periodo or '',
					line.tipo_documento_socio_accionista or '',
					line.numero_documento_socio_accionista or '',
					line.codigo_tipo_accion or '',
					line.razon_social_socio_accionista or '',
					line.numero_acciones or 0.00,
					line.porcentaje_total_participaciones or 0.00,
					line.indicador_estado_operacion or '')

				output.write(escritura.encode())


	##########################################################################################################
	def _generate_xlsx_inventories_balances_3_16(self, output):
		workbook = xlsxwriter.Workbook(output)
		ws = workbook.add_worksheet('F3.16 Det CXP Divers')
		styles = {'font_size': 12, 'font_name':'Arial', 'bold': True}
		table_styles = dict(styles,font_size=8,align='center',valign='vcenter',border=1,text_wrap=True)
		titulo_1 = workbook.add_format(styles)
		titulo_2 = workbook.add_format(dict(styles,font_size=9))
		titulo_3 = workbook.add_format(table_styles)
		titulo_4 = workbook.add_format(dict(table_styles,align=''))
		
		ws.set_column('A:A',14,titulo_2)
		ws.set_column('B:B',14,titulo_2)
		ws.set_column('C:C',14,titulo_2)
		ws.set_column('D:D',14,titulo_2)
		ws.set_column('E:E',14,titulo_2)
		ws.set_column('F:F',14,titulo_2)
		ws.set_column('G:G',14,titulo_2)
		ws.set_column('H:H',14,titulo_2)
		ws.set_column('I:I',14,titulo_2)
		ws.set_column('J:J',14,titulo_2)
		ws.set_column('K:K',14,titulo_2)

		ws.write(0,0,'FORMATO 3.16: "LIBRO DE INVENTARIOS Y BALANCES - DETALLE DEL SALDO DE',titulo_1)
		ws.write(1,0,'LA CUENTA 50 - CAPITAL"',titulo_1)
		ws.write(3,0,'EJERCICIO:' + '  ' + 'Valor',titulo_2)
		ws.write(4,0,'RUC:' + '  ' + self.ple_inventarios_balances_3_16_line_id.company_id.vat,titulo_2)
		ws.merge_range('A6:F6','APELLIDO Y NOMBRES, DENOMINACIÓN O RAZÓN SOCIAL:' + '  ' + self.ple_inventarios_balances_3_16_line_id.company_id.name,titulo_2)

		ws.merge_range('A8:F8','DETALLE DE LA PARTICIPACIÓN ACCIONARIA O DE PARTICIPANTES SOCIALES',titulo_2)
		row = 9

		data_16_1 = self.ple_inventarios_balances_3_16_line_id.ple_inventarios_balances_3_16_1_line_ids[0]
		ws.merge_range(f'A{row+1}:D{row+1}','CAPITAL SOCIAL O PARTICIPACIONES SOCIALES AL 31.12',titulo_3)
		ws.merge_range(f'E{row+1}:F{row+1}',data_16_1 and data_16_1.importe_capital_social_participaciones or '',titulo_3)
		
		ws.merge_range(f'A{row+2}:D{row+2}','VALOR NOMINAL POR ACCIÓN O PARTICIPACIÓN SOCIAL',titulo_3)
		ws.merge_range(f'E{row+2}:F{row+2}',data_16_1 and data_16_1.valor_nominal_por_accion or '',titulo_3)
		
		ws.merge_range(f'A{row+3}:D{row+3}','NÚMERO DE ACCIONES O PARTICIPACIONES SOCIALES SUSCRITAS',titulo_3)
		ws.merge_range(f'E{row+3}:F{row+3}',data_16_1 and data_16_1.numero_acciones_participaciones_sociales or '',titulo_3)

		ws.merge_range(f'A{row+4}:D{row+4}','NÚMERO DE ACCIONES O PARTICIPACIONES SOCIALES PAGADAS',titulo_3)
		ws.merge_range(f'E{row+4}:F{row+4}',data_16_1 and data_16_1.numero_acciones_participaciones_sociales_pagadas or '',titulo_3)

		ws.merge_range(f'A{row+6}:E{row+6}','ESTRUCTURA DE PARTICIPACIÓN ACCIONARIA O DE PARTICIPACIONES SOCIALES:',titulo_2)

		ws.merge_range(f'A17:C18','DOCUMENTO DE IDENTIDAD',titulo_3)
		ws.write(18,0,'TIPO',titulo_3)
		ws.merge_range('B19:C19','NÚMERO',titulo_3)

		ws.merge_range('D17:F19','APELLIDOS Y NOMBRES, DENOMINACIÓN O RAZON SOCIAL DEL ACCIONISTA O SOCIO',titulo_3)
		ws.merge_range('G17:H19','TIPO DE ACCIONES',titulo_3)
		ws.merge_range('I17:K19','NÚMERO DE ACCIONES PARTICIPACIONES SOCIALES',titulo_3)
		ws.merge_range('L17:M19','PORCENTAJE TOTAL DE PARTICIPACIÓN',titulo_3)


		row =20
		total_num_acciones= 0.00
		total_porcentaje= 0.00

		for line in self.ple_inventarios_balances_3_16_line_id.ple_inventarios_balances_3_16_2_line_ids:

			ws.write(row-1,0,line.tipo_documento_socio_accionista or '',titulo_4)
			ws.merge_range(f'B{row}:C{row}',line.numero_documento_socio_accionista or '',titulo_4)
			ws.merge_range(f'D{row}:F{row}',line.razon_social_socio_accionista or '',titulo_4)
			ws.merge_range(f'G{row}:H{row}',line.tipo_accion or '',titulo_4)
			ws.merge_range(f'I{row}:K{row}',line.numero_acciones or '',titulo_4)
			ws.merge_range(f'L{row}:M{row}',line.porcentaje_total_participaciones or '',titulo_4)
			row += 1
			
			total_num_acciones += line.numero_acciones
			total_porcentaje += line.porcentaje_total_participaciones

		ws.merge_range(f'G{row}:H{row}','TOTALES',titulo_3)
		ws.merge_range(f'I{row}:K{row}',total_num_acciones ,titulo_4)
		ws.merge_range(f'L{row}:M{row}',total_porcentaje ,titulo_4)

		workbook.close()
