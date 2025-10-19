import pytz
import calendar
import base64
from io import BytesIO, StringIO
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta
from odoo.addons import ple_base as tools

import logging
_logger=logging.getLogger(__name__)
class PleSaleLine(models.Model):
	_name='ple.sale.line'

	ple_sale_id=fields.Many2one("ple.sale",string="id PLE",ondelete='cascade',readonly=True)

	invoice_id=fields.Many2one("account.move",string="Documento",ondelete="cascade",readonly=True)
	invoice_id_2=fields.Many2one("account.move",string="Documento de origen",readonly=True)

	partner_id=fields.Many2one("res.partner",string="Proveedor",readonly=True) 
	asiento_contable=fields.Char(string="Nombre del asiento contable",readonly=True) 
	m_correlativo_asiento_contable=fields.Char(string="M-correlativo asiento contable",readonly=True)
	fecha_emision_comprobante=fields.Date(string="Fecha emisión Comprobante",readonly=True) # YA
	fecha_vencimiento=fields.Date(string="Fecha de vencimiento",readonly=True) # YA 
	tipo_comprobante_id = fields.Many2one('l10n_latam.document.type',readonly=True) # YA
	tipo_comprobante=fields.Char(string="Tipo de Comprobante",readonly = True) ## YA
	serie_comprobante=fields.Char(string="Serie del Comprobante",readonly=True) ## YA
	numero_comprobante=fields.Char(string="Número Comprobante",readonly=True) # YA
	ventas_importe_total_maquina_registradora=fields.Float(string="Importe Máquina Registradora sin Crédito Fiscal",
		default=0.00,readonly=True) ##YA 
	tipo_documento_cliente=fields.Char(string="Tipo Documento Cliente",readonly=True)# YA !!!
	numero_documento_cliente=fields.Char(string="Número Documento Identidad Cliente",readonly=True) ## YA
	razon_social=fields.Char(string="Razón Social Cliente",readonly=True)# YA 

	ventas_valor_facturado_exportacion = fields.Float(string="Valor Facturado Exportación",readonly=True) # YA
	ventas_base_imponible_operacion_gravada = fields.Float(string="Base Imponible Operación Gravada",readonly=True) #YA
	ventas_descuento_base_imponible = fields.Float(string="Descuento Base Imponible",default=0.00,readonly=True) # YA
	ventas_igv = fields.Float(string="IGV y/o Impuesto Promoción Municipal",readonly=True) # YA
	ventas_descuento_igv = fields.Float(string="Descuento del IGV",default=0.00,readonly=True) # YA
	ventas_importe_operacion_exonerada = fields.Float(string="Importe total operación exonerada",readonly=True) # YA
	ventas_importe_operacion_inafecta = fields.Float(string="Importe total operación inafecta",readonly=True) # YA
	isc=fields.Float(string="ISC",default=0.00,readonly=False) # YA 
	ventas_base_imponible_arroz_pilado=fields.Float(string="Base Imponible Arroz Pilado",default=0.00,readonly=True) # YA
	ventas_impuesto_arroz_pilado = fields.Float(string="Impuesto Arroz Pilado",default=0.00,readonly=True)# YA
	
	impuesto_consumo_bolsas_plastico=fields.Float(string="Impuesto al Consumo de las Bolsas de Plástico",default=0.00,
		readonly=True) # YA
	otros_impuestos=fields.Float(string="Otros conceptos tributarios",default=0.00) # YA
	importe_total_comprobante=fields.Float(string="Importe Total comprobante",readonly=True) # YA 
	codigo_moneda=fields.Char(string="Código Moneda",readonly=True) #YA
	tipo_cambio=fields.Float(string="Tipo de Cambio",readonly=True,digits = (12,3))

	fecha_emision_original=fields.Date(string="Fecha Emision Comprobante Original",readonly=True)
	tipo_comprobante_original=fields.Char(string="Tipo Comprobante Original",readonly=True)
	serie_comprobante_original=fields.Char(string="Serie Comprobante Original",readonly=True)
	numero_comprobante_original=fields.Char(string="Número Comprobante Original",readonly=True)
	
	ventas_identificacion_contrato_operadores = fields.Char(string="Identificación Contrato Operadores Irregulares",
		readonly=True)
	error_1 = fields.Char(string="Error Tipo 1",readonly=True)
	ventas_indicador_comprobantes_medios_pago = fields.Char(string="Indicador Comprobantes cancelados con medios de pago",
		readonly=True)
	oportunidad_anotacion=fields.Char(string="Oportunidad Anotación",default="1",readonly=True)

	###############################################################################################
	"""@api.depends('invoice_id','ple_sale_id',
		'tipo_comprobante','ventas_igv',
		'ventas_valor_facturado_exportacion')
	def _compute_campo_oportunidad_anotacion(self):
		for rec in self:
			if rec.invoice_id:
				valor_campo=''

				if rec.invoice_id.state not in ['cancel'] and rec.invoice_id.date and rec.invoice_id.invoice_date and \
					tools.getDateYYYYMM(rec.invoice_id.date) == tools.getDateYYYYMM(rec.invoice_id.invoice_date):
					
					if rec.tipo_comprobante == '03':
						valor_campo='1'
					else:

						if rec.ventas_igv==0.00:
							if rec.ventas_valor_facturado_exportacion:
								valor_campo='1'
							else:
								valor_campo='0'

						elif rec.ventas_igv>0.00:
							valor_campo='1'

				elif rec.invoice_id.state not in ['cancel'] and rec.invoice_id.date and rec.invoice_id.invoice_date and \
					tools.getDateYYYYMM(rec.invoice_id.date) > tools.getDateYYYYMM(rec.invoice_id.invoice_date):
					valor_campo='8'

				elif rec.invoice_id.state=='cancel' and rec.invoice_id.invoice_date and rec.ple_sale_id:

					anio=rec.ple_sale_id.fiscal_year
					mes = rec.ple_sale_id.fiscal_month
					
					if len(mes or '')==1:
						mes="0%s"%(mes)
					
					if "%s%s"%(anio,mes)==tools.getDateYYYYMM(rec.invoice_id.invoice_date):
						valor_campo='2'
				
				rec.oportunidad_anotacion=valor_campo """
