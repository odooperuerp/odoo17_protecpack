# -*- coding: utf-8 -*-
import calendar
from io import BytesIO, StringIO
from odoo import models, fields, api, _
from datetime import datetime, timedelta
import xlsxwriter
from odoo.exceptions import UserError , ValidationError

import logging
_logger=logging.getLogger(__name__)


class WizardPrinterPleInventariosBalancesDetalleSaldoCuenta10(models.TransientModel):
	_name='wizard.printer.ple.inventarios.balances.3.2'
	_inherit='wizard.printer.ple.base'
	_description = "Modulo Formulario Impresión PLE Libro Inventarios y Balances 3.2"


	ple_inventarios_balances_3_2_line_id = fields.Many2one('ple.inventarios.balances.3.2',
		string="PLE INVENTARIOS BALANCES 3.2",
		readonly=True,required=True)


	identificador_operaciones = fields.Selection(
		selection=[('0','Cierre de operaciones'),('1','Empresa operativa'),('2','Cierre de libro')],
		string="Identificador de operaciones", required=True, default="1")


	identificador_libro = fields.Selection(selection='available_formats_diary_sunat',
		string="Identificador de libro" , default='030200')

		
	print_order = fields.Selection(default="date")


	def available_formats_diary_sunat(self):
		formats=[('030200','Libro Inventarios y Balances-Detalle Saldo Cuenta 10-Efectivo y Equivalentes de Efectivo')]
		return formats


	def criterios_impresion(self):
		res = super(WizardPrinterPleInventariosBalancesDetalleSaldoCuenta10, self).criterios_impresion() or []
		res += [('codigo_cuenta_desagregado','Código Cuenta Desagregado')]
		return res


	def action_print(self):

		if (self.print_format and self.identificador_libro and self.identificador_operaciones) :
			return super(WizardPrinterPleInventariosBalancesDetalleSaldoCuenta10 , self).action_print()
		else:
			raise UserError(_('NO SE PUEDE IMPRIMIR , Los campos: Formato Impresión , Identificador de operaciones y Identificador de libro son obligatorios, llene esos campos !'))
		

	#############################################################

	def file_name(self, file_format):
		nro_de_registros = '1' if len(self.ple_inventarios_balances_3_2_line_id.ple_inventarios_balances_3_2_line_ids)>0 else '0'

		file_name = "LE%s%s%s00%s%s%s1.%s"%(
			self.ple_inventarios_balances_3_2_line_id.company_id.vat,
			"%s00" %(self.ple_inventarios_balances_3_2_line_id.fecha_final.strftime('%Y%m')),
			self.identificador_libro,
			self.identificador_operaciones,
			nro_de_registros,
			self.ple_inventarios_balances_3_2_line_id.currency_id.code_sunat or '1',
			file_format)

		return file_name


	########################################################

	def _init_buffer(self, output):

		if self.print_format == 'xlsx':
			self._generate_xlsx_inventories_balances_3_2(output)
		elif self.print_format == 'txt':
			self._generate_txt(output)
		return output



	def _convert_object_date(self, date):

		if date:
			return date.strftime('%d/%m/%Y')
		else:
			return ''


	def _generate_txt(self, output):
	
		for line in self.ple_inventarios_balances_3_2_line_id.ple_inventarios_balances_3_2_line_ids:

			escritura="%s|%s|%s|%s|%s|%s|%s|%s|\n" % (
				line.periodo or '',
				line.codigo_cuenta_desagregado or '',
				line.codigo_entidad_financiera or '',
				line.numero_cuenta_entidad or '',
				line.tipo_moneda_de_cuenta or '',
				line.saldo_deudor_cuenta or 0.00,
				line.saldo_acreedor_cuenta or 0.00,
				line.indicador_estado_operacion or '',)

			output.write(escritura.encode())
	
	####################################################################################################

	def _generate_xlsx_inventories_balances_3_2(self, output):

		workbook = xlsxwriter.Workbook(output)
		ws = workbook.add_worksheet('F3.2 Detalle saldo cuenta 10')
		styles = {'font_size': 12, 'font_name': 'Arial', 'bold': True}
		table_styles = dict(styles, font_size=8, align='center', border=1)
		titulo_1 = workbook.add_format(styles)
		titulo_2 = workbook.add_format(dict(styles, font_size=9))
		titulo_3 = workbook.add_format(table_styles)
		titulo_4 = workbook.add_format(dict(table_styles, align='', bold=False))

		cell_styles = {
			'no_top': workbook.add_format(dict(table_styles, top=0)),
			'no_bottom': workbook.add_format(dict(table_styles, bottom=0)),
			'no_y': workbook.add_format(dict(table_styles, bottom=0, top=0)),}

		ws.set_column('A:A', 15, titulo_2)
		ws.set_column('B:B', 18, titulo_2)
		ws.set_column('C:C', 20, titulo_2)
		ws.set_column('D:D', 25, titulo_2)
		ws.set_column('E:E', 20, titulo_2)
		ws.set_column('F:F', 18, titulo_2)
		ws.set_column('G:G', 18, titulo_2)
		ws.write(0, 0,'FORMATO 3.2: "LIBRO DE INVENTARIOS Y BALANCES - DETALLE DEL SALDO DE LA CUENTA 10 - CAJA Y BANCOS"',titulo_1)
		ws.write(2, 0, 'EJERCICIO:' + '  ' + 'Valor', titulo_2)
		ws.write(3, 0, 'RUC:' + '  ' + self.ple_inventarios_balances_3_2_line_id.company_id.vat, titulo_2)
		ws.merge_range('A5:D5', 'APELLIDO Y NOMBRES, DENOMINACIÓN O RAZÓN SOCIAL:' + '  ' + self.ple_inventarios_balances_3_2_line_id.company_id.name,titulo_2)
			# ws.write(4,2,self.company_id.name,titulo_2)
		row = 6
		ws.merge_range("A%s:B%s"%(row+1,row+1), 'CUENTA CONTABLE DIVISIONARIA', titulo_3)
		ws.merge_range("C%s:E%s"%(row+1,row+1), 'REFERENCIA DE LA CUENTA', titulo_3)
		ws.merge_range("F%s:G%s"%(row+1,row+1), 'SALDO CONTABLE FINAL', titulo_3)
		row += 1
		ws.write(row, 0, 'CÓDIGO', cell_styles['no_bottom'])
		ws.write(row + 1, 0, '', cell_styles['no_y'])
		ws.write(row + 2, 0, '', cell_styles['no_top'])
		ws.write(row, 1, 'DENOMINACIÓN', cell_styles['no_bottom'])
		ws.write(row + 1, 1, '', cell_styles['no_y'])
		ws.write(row + 2, 1, '', cell_styles['no_top'])
		ws.write(row, 2, 'ENTIDAD', cell_styles['no_bottom'])
		ws.write(row + 1, 2, 'FINANCIERA', cell_styles['no_y'])
		ws.write(row + 2, 2, '(TABLA 3)', cell_styles['no_top'])
		ws.write(row, 3, 'NÚMERO DE LA', cell_styles['no_bottom'])
		ws.write(row + 1, 3, 'CUENTA', cell_styles['no_y'])
		ws.write(row + 2, 3, '', cell_styles['no_top'])
		ws.write(row, 4, 'TIPO DE', cell_styles['no_bottom'])
		ws.write(row + 1, 4, 'MONEDA', cell_styles['no_y'])
		ws.write(row + 2, 4, '(TABLA 4)', cell_styles['no_top'])
		ws.write(row, 5, 'DEUDOR', cell_styles['no_bottom'])
		ws.write(row + 1, 5, '', cell_styles['no_y'])
		ws.write(row + 2, 5, '', cell_styles['no_top'])
		ws.write(row, 6, 'ACRREDOR', cell_styles['no_bottom'])
		ws.write(row + 1, 6, '', cell_styles['no_y'])
		ws.write(row + 2, 6, '', cell_styles['no_top'])
		row = 10

		total_debe = 0.00
		total_haber = 0.00

		for line in self.ple_inventarios_balances_3_2_line_id.ple_inventarios_balances_3_2_line_ids:
			ws.write(row, 0, line.codigo_cuenta_desagregado, titulo_4)
			ws.write(row, 1, line.denominacion_cuenta, titulo_4)
			ws.write(row, 2, line.codigo_entidad_financiera, titulo_4)
			ws.write(row, 3, line.numero_cuenta_entidad, titulo_4)
			ws.write(row, 4, line.tipo_moneda_de_cuenta, titulo_4)
			ws.write(row, 5, line.saldo_deudor_cuenta, titulo_4)
			ws.write(row, 6, line.saldo_acreedor_cuenta, titulo_4)
			total_debe += line.saldo_deudor_cuenta
			total_haber += line.saldo_acreedor_cuenta

			row += 1

		ws.write(row, 4, 'TOTALES', titulo_2)
		ws.write(row, 5, total_debe, titulo_4)
		ws.write(row, 6, total_haber, titulo_4)
		workbook.close()