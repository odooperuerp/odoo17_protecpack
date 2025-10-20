from odoo import fields,models,api
from datetime import datetime, timedelta
from io import BytesIO, StringIO
import xlsxwriter
from odoo.exceptions import UserError , ValidationError
import base64

import logging
_logger = logging.getLogger(__name__)


class AccountBankStatement(models.Model):
	_inherit = "account.bank.statement"

	def open_wizard_generator(self):

		return {
			'name': "Registro de Detracción",
			'view_mode': 'form',
			'view_type': 'form',
			'res_model': 'account.bank.statement.line.wizard',
			'type': 'ir.actions.act_window',
			'target': 'new',
			'context': {
				'default_company_id':self.company_id.id,
				'default_journal_id':self.journal_id.id,
				'default_statement_id':self.id,
						}
		}
		
	#################### IMPRIMIR ESTADO DE CUENTA DESDE EL EXTRACTO ##################################
	@api.model
	def _get_print_format(self):
		option = [
			('xlsx','xlsx')
		]
		return option


	def document_print(self):
		output = BytesIO()
		output = self._init_buffer(output)
		output.seek(0)
		return output.read()


	def action_print(self):
		return {
			'type': 'ir.actions.act_url',
			'url': 'reports/format/{}/{}/{}'.format(self._name,"xlsx", self.id),
			'target': 'new'}


	def file_name(self, file_format):
		
		file_name = "Extracto_Bancario_%s_%s.%s" % (self.company_id.vat,
			self.date.strftime('%d_%m_%Y'),file_format)
		
		return file_name


	def _init_buffer(self, output):
		self._generate_xlsx(output)
		return output



	def _convert_object_date(self, date):
		if date:
			return date.strftime('%d/%m/%Y')
		else:
			return ''

	#############################################################################


	def _generate_xlsx(self, output):
		workbook = xlsxwriter.Workbook(output)
		ws = workbook.add_worksheet(self.name)

		titulo1 = workbook.add_format({'font_size': 12, 'align': 'center', 'text_wrap': True, 'bold': True, 'font_name': 'Cambria'})
		titulo2 = workbook.add_format({'font_size': 9, 'align': 'left', 'text_wrap': True, 'bold': True, 'font_name': 'Cambria'})

		titulo2_campos = workbook.add_format({'font_size': 9, 'align': 'left', 'text_wrap': True, 'font_name': 'Cambria'})

		cabeceras = workbook.add_format({'font_size': 8, 'valign': 'vcenter', 'align': 'center',
			'text_wrap': True, 'bold': True, 'font_name': 'Cambria', 'text_wrap': True, 'left': True,
			'right': True, 'bottom': True, 'top': True, 'bg_color': 'black', 'font_color': 'white'})

		
		color = ['#D2CECE', '#FFFFFF']
		
		
		dict_letter1 = {'font_size': 12, 'align': 'center', 'font_name': 'Calibri', 'text_wrap': True, 'left': True,
			'right': True, 'bottom': True, 'top': True}
		
		cantidades_totales = workbook.add_format({'font_size': 14, 'align': 'center', 'font_name': 'Calibri', 'bold': True})
		totales = workbook.add_format({'font_size': 14, 'align': 'center', 'font_name': 'Cambria', 'bold': True, 'font_color': 'red'})
		number_right = workbook.add_format({'font_size': 12, 'align': 'right', 'num_format': '#,##0.00', 'font_name': 'Calibri'})
		center = workbook.add_format({'font_size': 12, 'align': 'center', 'font_name': 'Calibri'})

		symbol = self.journal_id.currency_id.symbol or self.journal_id.default_account_id.currency_id.symbol or '"S/."'

		number_right_mn = workbook.add_format({'font_size': 10, 'align': 'right', 'num_format': '"' + symbol + '" #,##0.00',
			'font_name': 'Calibri'})

		number_right_blue_mn = workbook.add_format({'font_size': 10, 'align': 'right', 'num_format': '"' + symbol + '" #,##0.00',
			'font_name': 'Calibri', 'font_color': '#0477BF', 'left': True, 'right': True, 'bottom': True, 'top': True})


		ws.set_column('A:A', 8)
		ws.set_column('B:B', 19)
		ws.set_column('C:C', 15)
		ws.set_column('D:D', 20)
		ws.set_column('E:E', 40)
		ws.set_column('F:F', 18)
		ws.set_column('G:G', 13)
		ws.set_column('H:H', 20)
		ws.set_column('I:I', 20)
		ws.set_column('J:J', 20)
		ws.set_column('K:K', 20)
		ws.set_column('L:L', 20)
		ws.set_column('M:M', 20)
		ws.set_column('N:N', 10)
		ws.set_column('O:O', 10)
		
		ws.set_row(0, 22)

		ws.set_row(9, 22)

		#### INSERTANDO IMAGEN ######
		if self.company_id.logo:
			company_image = BytesIO(base64.b64decode(self.company_id.logo))
			ws.insert_image(0,0,"image.png",{'image_data':company_image,'x_scale': 0.17, 'y_scale': 0.145})
		#############################

		ws.merge_range('C1:E1', self.name or '', titulo1)

		ws.write(4, 0, 'COMPAÑÍA',titulo2_campos)
		ws.merge_range('B5:D5', self.company_id.name or '', titulo2)

		ws.write(5, 0, 'DIARIO',titulo2_campos)
		ws.merge_range('B6:D6', self.journal_id.name or '', titulo2)
		
		ws.write(6, 0, 'FECHA',titulo2_campos)
		ws.merge_range('B7:D7', self._convert_object_date(self.date) or '', titulo2)

		#ws.write(6, 0, 'FECHA FIN',titulo2_campos)
		#ws.merge_range('B7:D7', self._convert_object_date(self.fecha_fin) or '', titulo2)

		#ws.write(7, 0, 'FECHA DE REGISTRO',titulo2_campos)
		#ws.merge_range('B8:D8', self._convert_object_date(self.accounting_date) or '', titulo2)

		# SALDO INICIAL Y FINAL !!
		ws.write(3, 4, 'SALDO INICIAL',titulo2_campos)
		ws.write(3, 5, self.balance_start or 0, number_right_mn)

		ws.write(4, 4, 'SALDO FINAL',titulo2_campos)
		ws.write(4, 5, self.balance_end or 0, number_right_mn)


		ws.write(9, 1 - 1, 'ITEM', cabeceras)
		ws.write(9, 2 - 1, 'NÚMERO DE OPERACIÓN', cabeceras)
		ws.write(9, 3 - 1, 'FECHA', cabeceras)
		ws.write(9, 4 - 1, 'DESCRIPCIÓN', cabeceras)
		ws.write(9, 5 - 1, 'SOCIO', cabeceras)
		ws.write(9, 6 - 1, 'REFERENCIA', cabeceras)
		ws.write(9, 7 - 1, 'IMPORTE', cabeceras)

		fila = 9

		item = 0

		totales = 0.00

		for line in self.line_ids:

			fila += 1
			item += 1

			ws.write(fila, 0, item or '', center)
			ws.write(fila, 1, line.operation_number or '')
			ws.write(fila, 2, self._convert_object_date(line.date) if line.date else '')
			ws.write(fila, 3, line.payment_ref or '')
			ws.write(fila, 4, line.partner_id and line.partner_id.name or '')
			ws.write(fila, 5, line.ref or '')
			ws.write(fila, 6, line.amount or 0, number_right_mn)

			totales += line.amount

		fila += 1
		ws.write(fila, 5, 'TOTALES', number_right_blue_mn)
		ws.write(fila, 6, totales , number_right_blue_mn)
		workbook.close()