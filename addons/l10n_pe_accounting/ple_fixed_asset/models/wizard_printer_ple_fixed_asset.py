# -*- coding: utf-8 -*-
import calendar
from io import BytesIO, StringIO
from odoo import models, fields, api, _
from datetime import datetime, timedelta
import xlsxwriter
from odoo.exceptions import UserError , ValidationError

import logging
_logger=logging.getLogger(__name__)


class WizardPrinterPleFixedAsset(models.TransientModel):
	_name='wizard.printer.ple.fixed.asset'
	_inherit='wizard.printer.ple.base'
	_description = "Modulo Formulario Impresión PLE Libros de Registro de Activos Fijos"

	ple_fixed_asset_id = fields.Many2one('ple.fixed.asset',string="PLE ACTIVOS FIJOS",
		readonly=True,required=True)

	identificador_operaciones = fields.Selection(
		selection=[('0','Cierre de operaciones'),('1','Empresa operativa'),('2','Cierre de libro')],
		string="Identificador de operaciones",default="1",required=True)


	identificador_libro = fields.Selection(selection='available_formats_fixed_asset_sunat',
		string="Identificador de libro",required=True)

	########################################################
	## CAMPO PARA IMPRIMIR RECIBO POR HONORARIOS EN LOS REPORTES DE DOMICILIADOS
	imprimir_recibo_honorarios=fields.Boolean(string="Incluir Recibos por Honorarios", default=False)
	#############################################################
		
	print_order = fields.Selection(default="date") 



	def criterios_impresion(self):
		res = super(WizardPrinterPleFixedAsset, self).criterios_impresion() or []
		res += [('codigo_cuenta_desagregado','Código Cuenta Desagregado')]
		
		return res


	def action_print(self):
		if (self.print_format and self.identificador_libro and self.identificador_operaciones) :
			if self.print_format =='pdf':
				pass
			else:
				return super(WizardPrinterPleFixedAsset , self).action_print()
		else:
			raise UserError(_('NO SE PUEDE IMPRIMIR , Los campos: Formato Impresión , Identificador de operaciones y Identificador de libro son obligatorios, llene esos campos !!!'))

	#############################################################

	def available_formats_fixed_asset_sunat(self):
		formats=[
			('070100','Registro Activos Fijos-Detalle de los Activos Fijos Revaluados y no Revaluados')
			]
		return formats



	def _get_order_print(self,object):

		if self.print_order == 'date': # ORDENAMIENTO POR LA FECHA CONTABLE
			total=sorted(object, key=lambda PleFixedAssetLine: (PleFixedAssetLine.asiento_contable,PleFixedAssetLine.codigo_cuenta_desagregado , PleFixedAssetLine.fecha_adquisicion_activo) )
		elif self.print_order == 'nro_documento':
			total=sorted(object , key=lambda PleFixedAssetLine: (PleFixedAssetLine.asiento_contable)) # ,PleFixedAssetLine.asiento_contable)) #ORDENAMIENTO POR EL NUMERO DEASIENTO CONTABLE
		elif self.print_order == 'codigo_cuenta_desagregado':
			total=sorted(object , key=lambda PleFixedAssetLine: (PleFixedAssetLine.asiento_contable,PleFixedAssetLine.fecha_adquisicion_activo ,  PleFixedAssetLine.codigo_cuenta_desagregado ) ) # ORDENAMIENTO POR EL CODIGO DE CUENTA DESAGREGADO

		return total



	def file_name(self, file_format): ## ASSET
		nro_de_registros = '1' if len(self.ple_fixed_asset_id.ple_fixed_asset_line_ids)>0 else '0'

		file_name = "LE%s%s%s00%s%s%s1.%s" % (self.ple_fixed_asset_id.company_id.vat, self.ple_fixed_asset_id._periodo_fiscal(),
			self.identificador_libro, self.identificador_operaciones, nro_de_registros,
			self.ple_fixed_asset_id.currency_id.code_sunat or '1', file_format)
		
		return file_name



	def _init_buffer(self, output):

		if self.print_format == 'xlsx':
			if self.identificador_libro == '070100':
				self._generate_xlsx_fixed_assets(output)
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
	
		for line in self._get_order_print(self.ple_fixed_asset_id.ple_fixed_asset_line_ids) :

			escritura="%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|\n" % (
				line.periodo_apunte or '',
				line.asiento_contable or '',
				line.m_correlativo_asiento_contable or '',
				line.codigo_catalogo_existencias_utilizado or '',
				line.codigo_propio_activo or '',
				line.codigo_existencias_OSCE or '',
				line.codigo_tipo_activo_fijo or '',
				line.codigo_cuenta_desagregado or '',
				line.estado_activo_fijo or '',
				line.descripcion_activo_fijo or '',
				line.marca_activo_fijo or '',
				line.modelo_activo_fijo or '',
				line.numero_serie_placa_activo or '',
				line.importe_saldo_inicial_activo_fijo or 0.00,
				line.importe_adquisiciones_adiciones or 0.00,
				line.importe_mejoras or 0.00,
				line.importe_retiros_bajas or 0.00,
				line.importe_otros_ajustes or 0.00,
				line.valor_revaluacion_voluntaria_efectuada or 0.00,
				line.valor_revaluacion_efectuada_reorganizacion_sociedades or 0.00,
				line.valor_otras_revaluaciones_efectuadas or 0.00,
				line.importe_valor_ajuste_por_inflacion or 0.00,
				line.fecha_adquisicion_activo or '',
				line.fecha_inicio_uso_activo_fijo or '',
				line.codigo_metodo_aplicado_calculo_depreciacion or '',
				line.numero_documento_cambio_metodo_depreciacion or '',
				line.porcentaje_depreciacion or 0.00,
				line.depreciacion_acumulada_cierre_ejercicio_anterior or 0.00,
				line.valor_depreciacion_ejercicio_sin_considerar_revaluacion or 0.00,
				line.valor_depreciacion_ejercicio_relacionada_con_retiros_bajas or 0.00,
				line.valor_depreciacion_relacionada_con_otros_ajustes or 0.00,
				line.valor_depreci_de_revaluaci_efectuada_reorgani_soci or 0.00,
				line.valor_depreciacion_otras_revaluaciones_efectuadas or 0.00,
				line.valor_ajuste_por_inflacion_de_depreciacion or 0.00,
				line.estado_operacion or '')

			output.write(escritura.encode())

	#############################################################################

	def _generate_xlsx_fixed_assets(self, output): ## ASSET
		workbook = xlsxwriter.Workbook(output)
		ws = workbook.add_worksheet('F 7.1 Det bs AF')
		style = {
			'font_size': 10,
			'font_name':'Arial',
			'bold': True,
		}

		table_styles = dict(
			style,
			border=1,
			align='center'
		)

		cell_styles = {
			'no_top': workbook.add_format(dict(table_styles,top=0)),
			'no_bottom': workbook.add_format(dict(table_styles,bottom=0)),
			'no_y': workbook.add_format(dict(table_styles,top=0,bottom=0)),
		}

		titulo_1 = workbook.add_format({'font_size': 14, 'font_name':'Arial', 'bold': True})
		titulo_2 = workbook.add_format(style)
		titulo_3 = workbook.add_format(table_styles)
		titulo_4 = workbook.add_format(dict(table_styles,fg_color='#C4C4C4'))

		ws.set_column('A:A',18,titulo_2)
		ws.set_column('B:B',18,titulo_2)
		ws.set_column('C:C',18,titulo_2)
		ws.set_column('D:D',15,titulo_2)
		ws.set_column('E:E',15,titulo_2)
		ws.set_column('F:F',18,titulo_2)
		ws.set_column('G:G',15,titulo_2)
		ws.set_column('H:H',18,titulo_2)
		ws.set_column('I:I',15,titulo_2)
		ws.set_column('J:J',15,titulo_2)
		ws.set_column('K:K',15,titulo_2)
		ws.set_column('L:L',18,titulo_2)
		ws.set_column('M:M',15,titulo_2)
		ws.set_column('N:N',18,titulo_2)
		ws.set_column('O:O',15,titulo_2)
		ws.set_column('P:P',18,titulo_2)
		ws.set_column('Q:Q',15,titulo_2)
		ws.set_column('R:R',18,titulo_2)
		ws.set_column('S:S',18,titulo_2)
		ws.set_column('T:T',23,titulo_2)
		ws.set_column('U:U',15,titulo_2)
		ws.set_column('V:V',23,titulo_2)
		ws.set_column('W:W',15,titulo_2)
		ws.set_column('X:X',15,titulo_2)
		ws.set_column('Y:Y',15,titulo_2)
		ws.set_column('Z:Z',15,titulo_2)

		ws.set_row(6,20,titulo_2)
		ws.set_row(7,20,titulo_2)
		ws.set_row(8,20,titulo_2)
		ws.set_row(9,20,titulo_2)

		ws.write(0,0,'FORMATO 7.1',titulo_1)
		ws.write(0,1,'REGISTRO DE ACTIVOS FIJOS-DETALLE DE LOS ACTIVOS FIJOS',titulo_1)

		ws.write(2,0,'PERIODO:',titulo_2)
		ws.write(2,1,self.ple_fixed_asset_id._periodo_fiscal(),titulo_2)

		ws.write(3,0,'RUC:',titulo_2)
		ws.write(3,1,self.ple_fixed_asset_id.company_id.vat,titulo_2)

		ws.merge_range('A5:C5','APELLIDOS Y NOMBRES, DENOMINACIÓN O RAZÓN SOCIAL:', titulo_2)
		ws.write(4,3,self.ple_fixed_asset_id.company_id.name,titulo_2)

		ws.write(5,0,'CÓDIGO', cell_styles['no_bottom'])
		ws.write(6,0,'RELACIONADO', cell_styles['no_y'])
		ws.write(7,0,'CON EL', cell_styles['no_y'])
		ws.write(8,0,'ACTIVO FIJO', cell_styles['no_top'])

		ws.write(5,1,'CUENTA', cell_styles['no_bottom'])
		ws.write(6,1,'CONTABLE', cell_styles['no_y'])
		ws.write(7,1,'DEL', cell_styles['no_y'])
		ws.write(8,1,'ACTIVO FIJO', cell_styles['no_top'])

		ws.merge_range('C6:F6', 'DETALLE DEL ACTIVO FIJO', titulo_3)

		ws.write(6,2,'',cell_styles['no_bottom'])
		ws.write(7,2,'DESCRIPCIÓN',cell_styles['no_y'])
		ws.write(8,2,'',cell_styles['no_top'])

		ws.write(6,3,'MARCA',cell_styles['no_bottom'])
		ws.write(7,3,'DEL',cell_styles['no_y'])
		ws.write(8,3,'ACTIVO FIJO',cell_styles['no_top'])

		ws.write(6,4,'MODELO',cell_styles['no_bottom'])
		ws.write(7,4,'DEL',cell_styles['no_y'])
		ws.write(8,4,'ACTIVO FIJO',cell_styles['no_top'])

		ws.write(6,5,'NÚMERO DE SERIE',cell_styles['no_bottom'])
		ws.write(7,5,'Y/O PLACA DEL',cell_styles['no_y'])
		ws.write(8,5,'ACTIVO FIJO',cell_styles['no_top'])


		ws.write(5,6,'',cell_styles['no_bottom'])
		ws.write(6,6,'SALDO',cell_styles['no_y'])
		ws.write(7,6,'INICIO',cell_styles['no_y'])
		ws.write(8,6,'',cell_styles['no_top'])

		ws.write(5,7,'',cell_styles['no_bottom'])
		ws.write(6,7,'ADQUISICIONES',cell_styles['no_y'])
		ws.write(7,7,'ADICIONES',cell_styles['no_y'])
		ws.write(8,7,'',cell_styles['no_top'])

		ws.write(5,8,'',cell_styles['no_bottom'])
		ws.write(6,8,'MEJORAS',cell_styles['no_y'])
		ws.write(7,8,'',cell_styles['no_y'])
		ws.write(8,8,'',cell_styles['no_top'])

		ws.write(5,9,'',cell_styles['no_bottom'])
		ws.write(6,9,'RETIROS',cell_styles['no_y'])
		ws.write(7,9,'Y/O',cell_styles['no_y'])
		ws.write(8,9,'BAJAS',cell_styles['no_top'])

		ws.write(5,10,'',cell_styles['no_bottom'])
		ws.write(6,10,'OTROS',cell_styles['no_y'])
		ws.write(7,10,'AJUSTES',cell_styles['no_y'])
		ws.write(8,10,'',cell_styles['no_top'])

		ws.write(5,11,'VALOR',cell_styles['no_bottom'])
		ws.write(6,11,'HISTÓRICO',cell_styles['no_y'])
		ws.write(7,11,'DEL ACTIVO FIJO',cell_styles['no_y'])
		ws.write(8,11,'AL 31.12',cell_styles['no_top'])

		ws.write(5,12,'',cell_styles['no_bottom'])
		ws.write(6,12,'AJUSTE POR',cell_styles['no_y'])
		ws.write(7,12,'INFLACIÓN',cell_styles['no_y'])
		ws.write(8,12,'',cell_styles['no_top'])

		ws.write(5,13,'VALOR',cell_styles['no_bottom'])
		ws.write(6,13,'AJUSTADO',cell_styles['no_y'])
		ws.write(7,13,'DEL ACTIVO FIJO',cell_styles['no_y'])
		ws.write(8,13,'AL 31.12',cell_styles['no_top'])

		ws.write(5,14,'',cell_styles['no_bottom'])
		ws.write(6,14,'FECHA DE',cell_styles['no_y'])
		ws.write(7,14,'ADQUISICIÓN',cell_styles['no_y'])
		ws.write(8,14,'',cell_styles['no_top'])

		ws.write(5,15,'FECHA DE INICIO',cell_styles['no_bottom'])
		ws.write(6,15,'DEL USO',cell_styles['no_y'])
		ws.write(7,15,'DEL ACTIVO FIJO',cell_styles['no_y'])
		ws.write(8,15,'',cell_styles['no_top'])


		ws.merge_range('Q6:R6', 'DEPRECIACIÓN', titulo_3)

		ws.write(6,16,'MÉTODO',cell_styles['no_bottom'])
		ws.write(7,16,'APLICADO',cell_styles['no_y'])
		ws.write(8,16,'',cell_styles['no_top'])

		ws.write(6,17,'N° DE DOCUMENTO',cell_styles['no_bottom'])
		ws.write(7,17,'DE',cell_styles['no_y'])
		ws.write(8,17,'AUTORIZACION',cell_styles['no_top'])


		ws.write(5,18,'',cell_styles['no_bottom'])
		ws.write(6,18,'PORCENTAJE',cell_styles['no_y'])
		ws.write(7,18,'DE',cell_styles['no_y'])
		ws.write(8,18,'DEPRECIACIÓN',cell_styles['no_top'])

		ws.write(5,19,'DEPRECIACIÓN',cell_styles['no_bottom'])
		ws.write(6,19,'ACUMULADA AL',cell_styles['no_y'])
		ws.write(7,19,'CIERRE DEL',cell_styles['no_y'])
		ws.write(8,19,'EJERCICIO ANTERIOR',cell_styles['no_top'])

		ws.write(5,20,'',cell_styles['no_bottom'])
		ws.write(6,20,'DEPRECIACIÓN',cell_styles['no_y'])
		ws.write(7,20,'DEL EJERCICIO',cell_styles['no_y'])
		ws.write(8,20,'',cell_styles['no_top'])

		ws.write(5,21,'DEPRECIACIÓN',cell_styles['no_bottom'])
		ws.write(6,21,'DEL EJERCICIO',cell_styles['no_y'])
		ws.write(7,21,'RELACIONADA CON LOS',cell_styles['no_y'])
		ws.write(8,21,'RETIROS Y/O BAJAS',cell_styles['no_top'])

		ws.write(5,22,'DEPRECIACIÓN',cell_styles['no_bottom'])
		ws.write(6,22,'RELACIONADA',cell_styles['no_y'])
		ws.write(7,22,'CON OTROS',cell_styles['no_y'])
		ws.write(8,22,'AJUSTES',cell_styles['no_top'])

		ws.write(5,23,'DEPRECIACIÓN',cell_styles['no_bottom'])
		ws.write(6,23,'ACUMULADA',cell_styles['no_y'])
		ws.write(7,23,'HISTÓRICA',cell_styles['no_y'])
		ws.write(8,23,'',cell_styles['no_top'])

		ws.write(5,24,'AJUSTE POR',cell_styles['no_bottom'])
		ws.write(6,24,'INFLACIÓN',cell_styles['no_y'])
		ws.write(7,24,'DE LA',cell_styles['no_y'])
		ws.write(8,24,'DEPRECIACIÓN',cell_styles['no_top'])

		ws.write(5,25,'DEPRECIACIÓN',cell_styles['no_bottom'])
		ws.write(6,25,'ACUMULADA',cell_styles['no_y'])
		ws.write(7,25,'AJUSTADA POR',cell_styles['no_y'])
		ws.write(8,25,'INFLACIÓN',cell_styles['no_top'])

		row = 9

		for line in self.ple_fixed_asset_id.ple_fixed_asset_line_ids:
			ws.set_row(row,20,titulo_2)

			ws.write(row,0,line.codigo_propio_activo,titulo_3)
			ws.write(row,1,line.codigo_cuenta_desagregado,titulo_3)
			ws.write(row,2,line.descripcion_activo_fijo,titulo_3)
			ws.write(row,3,line.marca_activo_fijo,titulo_3)
			ws.write(row,4,line.modelo_activo_fijo,titulo_3)
			ws.write(row,5,line.numero_serie_placa_activo,titulo_3)
			ws.write(row,6,line.importe_saldo_inicial_activo_fijo,titulo_3)
			ws.write(row,7,line.importe_adquisiciones_adiciones,titulo_3)
			ws.write(row,8,line.importe_mejoras,titulo_3)
			ws.write(row,9,line.importe_retiros_bajas,titulo_3)
			ws.write(row,10,line.importe_otros_ajustes,titulo_3)
			ws.write(row,11,'',titulo_3) # falta
			ws.write(row,12,line.importe_valor_ajuste_por_inflacion,titulo_3)
			ws.write(row,13,'',titulo_3) # falta
			ws.write(row,14,self._convert_object_date(line.fecha_adquisicion_activo),titulo_3)
			ws.write(row,15,self._convert_object_date(line.fecha_inicio_uso_activo_fijo),titulo_3)
			ws.write(row,16,line.codigo_metodo_aplicado_calculo_depreciacion,titulo_3)
			ws.write(row,17,line.numero_documento_cambio_metodo_depreciacion,titulo_3)
			ws.write(row,18,str(line.porcentaje_depreciacion) + ' %',titulo_3)
			ws.write(row,19,line.depreciacion_acumulada_cierre_ejercicio_anterior,titulo_3)
			ws.write(row,20,line.valor_depreciacion_ejercicio_sin_considerar_revaluacion,titulo_3)
			ws.write(row,21,line.valor_depreciacion_ejercicio_relacionada_con_retiros_bajas,titulo_3)
			ws.write(row,22,line.valor_depreciacion_relacionada_con_otros_ajustes,titulo_3)
			ws.write(row,23,'',titulo_3) # falta
			ws.write(row,24,line.valor_ajuste_por_inflacion_de_depreciacion,titulo_3)
			ws.write(row,25,'',titulo_3) # falta
			row += 1
		ws.set_row(row,20,titulo_2)
		ws.write(row,5,'TOTALES', titulo_2)
		ws.write(row,6,sum([i.importe_saldo_inicial_activo_fijo for i in self.ple_fixed_asset_id.ple_fixed_asset_line_ids]),titulo_3)
		ws.write(row,7,sum([i.importe_adquisiciones_adiciones for i in self.ple_fixed_asset_id.ple_fixed_asset_line_ids]),titulo_3)
		ws.write(row,8,sum([i.importe_mejoras for i in self.ple_fixed_asset_id.ple_fixed_asset_line_ids]),titulo_3)
		ws.write(row,9,sum([i.importe_retiros_bajas for i in self.ple_fixed_asset_id.ple_fixed_asset_line_ids]),titulo_3)
		ws.write(row,10,sum([i.importe_otros_ajustes for i in self.ple_fixed_asset_id.ple_fixed_asset_line_ids]),titulo_3)
		ws.write(row,11,'',titulo_3) # falta
		ws.write(row,12,sum([i.importe_valor_ajuste_por_inflacion for i in self.ple_fixed_asset_id.ple_fixed_asset_line_ids]),titulo_3)
		ws.write(row,13,'',titulo_3) # falta
		ws.write(row,14,'',titulo_4)
		ws.write(row,15,'',titulo_4)
		ws.write(row,16,'',titulo_4)
		ws.write(row,17,'',titulo_4)
		ws.write(row,18,'',titulo_3) # falta
		ws.write(row,19,sum([i.depreciacion_acumulada_cierre_ejercicio_anterior for i in self.ple_fixed_asset_id.ple_fixed_asset_line_ids]),titulo_4)
		ws.write(row,20,sum([i.valor_depreciacion_ejercicio_sin_considerar_revaluacion for i in self.ple_fixed_asset_id.ple_fixed_asset_line_ids]),titulo_3)
		ws.write(row,21,sum([i.valor_depreciacion_ejercicio_relacionada_con_retiros_bajas for i in self.ple_fixed_asset_id.ple_fixed_asset_line_ids]),titulo_3)
		ws.write(row,22,sum([i.valor_depreciacion_relacionada_con_otros_ajustes for i in self.ple_fixed_asset_id.ple_fixed_asset_line_ids]),titulo_3)
		ws.write(row,23,'',titulo_3) # falta
		ws.write(row,24,sum([i.valor_ajuste_por_inflacion_de_depreciacion for i in self.ple_fixed_asset_id.ple_fixed_asset_line_ids]),titulo_3)
		ws.write(row,25,'',titulo_3) # falta

		workbook.close()
