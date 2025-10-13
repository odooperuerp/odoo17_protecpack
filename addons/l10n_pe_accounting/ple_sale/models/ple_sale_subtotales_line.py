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
class PleSaleSubtotalesLine(models.Model):
	_name='ple.sale.subtotales.line'

	ple_sale_id=fields.Many2one("ple.sale",string="id PLE",ondelete='cascade',readonly=True)


	tipo_comprobante_id = fields.Many2one('l10n_latam.document.type',readonly=True)

	ventas_valor_facturado_exportacion = fields.Float(string="Valor Facturado Exportación",
		readonly=True,default=0.00)
	ventas_base_imponible_operacion_gravada = fields.Float(string="Base Imponible Operación Gravada",
		readonly=True,default=0.00)
	ventas_descuento_base_imponible = fields.Float(string="Descuento Base Imponible",
		readonly=True,default=0.00)
	ventas_igv = fields.Float(string="IGV y/o Impuesto Promoción Municipal",
		readonly=True,default=0.00)
	ventas_descuento_igv = fields.Float(string="Descuento del IGV",
		readonly=True,default=0.00)
	ventas_importe_operacion_exonerada = fields.Float(string="Importe total operación exonerada",
		readonly=True,default=0.00)
	ventas_importe_operacion_inafecta = fields.Float(string="Importe total operación inafecta",
		readonly=True,default=0.00)
	isc = fields.Float(string="ISC",readonly=True,default=0.00)
	ventas_base_imponible_arroz_pilado = fields.Float(string="Base Imponible Arroz Pilado",
		readonly=True,default=0.00)
	ventas_impuesto_arroz_pilado = fields.Float(string="Impuesto Arroz Pilado",
		readonly=True,default=0.00)
	impuesto_consumo_bolsas_plastico = fields.Float(string="Impuesto al Consumo de las Bolsas de Plástico",
		readonly=True,default=0.00)
	otros_impuestos = fields.Float(string="Otros conceptos tributarios",readonly=True,
		default=0.00)
	importe_total_comprobante = fields.Float(string="Importe Total comprobante",readonly=True,
		default=0.00)