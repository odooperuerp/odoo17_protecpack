# -*- coding: utf-8 -*-
import pytz
import calendar
import base64
from io import BytesIO, StringIO
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta
from odoo.addons import sire_base as tools

import logging
_logger=logging.getLogger(__name__)


class SireSaleLine(models.Model):
	_name='sire.sale.line'
	_description = "SIRE Sale Line"

	sire_sale_id=fields.Many2one("sire.sale",string="ID SIRE" , ondelete='cascade' , readonly=True )

	invoice_id=fields.Many2one("account.move" , string="Documento" , ondelete="cascade",readonly= True)

	invoice_id_2=fields.Many2one("account.move", string="Documento de origen",
		compute='compute_invoice_id_2',store=True,readonly=True)

	fecha_emision_comprobante=fields.Date(string="Fecha emisión Comprobante",readonly=True) # !!
	fecha_vencimiento=fields.Date(string="Fecha de vencimiento",readonly=True) # !!
	tipo_comprobante=fields.Char(string="Tipo de Comprobante",readonly = True) # !!
	serie_comprobante=fields.Char(string="Serie del Comprobante",readonly=True) # !!
	numero_comprobante=fields.Char(string="Número Comprobante",readonly=True) # !!
	tipo_documento_cliente=fields.Char(string="Tipo Documento Cliente",readonly=True) # !!
	numero_documento_cliente=fields.Char(string="Número Documento Identidad Cliente",readonly=True) # !!
	razon_social=fields.Char(string="Razón Social Cliente",readonly=True) # !!

	ventas_valor_facturado_exportacion = fields.Float(string="Valor Facturado Exportación",
		compute='_compute_campo_ventas_valor_facturado_exportacion',store=True,readonly=True)  # !!
	ventas_base_imponible_operacion_gravada = fields.Float(string="Base Imponible Operación Gravada",
		compute='_compute_campo_ventas_base_imponible_operacion_gravada',store=True,readonly=True) # !!
	ventas_descuento_base_imponible = fields.Float(string="Descuento Base Imponible",default=0.00,
		readonly=True)  # !!
	ventas_igv = fields.Float(string="IGV y/o Impuesto Promoción Municipal",
		compute='_compute_campo_impuestos',store=True,readonly=True) 
	ventas_descuento_igv = fields.Float(string="Descuento del IGV" , default=0.00 ,readonly=True) 
	ventas_importe_operacion_exonerada = fields.Float(string="Importe total operación exonerada",
		compute='_compute_campo_ventas_importe_operacion_exonerada',store=True,readonly=True)  # !!
	ventas_importe_operacion_inafecta = fields.Float(string="Importe total operación inafecta",
		compute='_compute_campo_ventas_importe_operacion_inafecta' ,store=True,readonly=True)  # !!
	isc = fields.Float(string="ISC",default=0.00,readonly=False) # !!
	ventas_base_imponible_arroz_pilado=fields.Float(string="Base Imponible Arroz Pilado",
		default=0.00,readonly=True) # !!
	ventas_impuesto_arroz_pilado = fields.Float(string="Impuesto Arroz Pilado",default=0.00 ,readonly=True) # !!

	impuesto_consumo_bolsas_plastico=fields.Float(string="Impuesto al Consumo de las Bolsas de Plástico",
		default=0.00 ,readonly=True,compute='_compute_campo_impuestos',store=True)

	otros_impuestos=fields.Float(string="Otros conceptos tributarios",default=0.00,readonly=True,
		compute='_compute_campo_impuestos',store=True) # !!
	importe_total_comprobante=fields.Float(string="Importe Total comprobante",
		compute='_compute_campo_importe_total_comprobante',store=True,readonly=True) # !!
	codigo_moneda=fields.Char(string="Código Moneda",compute='_compute_campo_codigo_moneda',store=True,readonly=True) # !!
	tipo_cambio=fields.Float(string="Tipo de Cambio", compute='_compute_campo_tipo_cambio',store=True,readonly=True, digits = (12,3)) # !!

	fecha_emision_original=fields.Date(string="Fecha Emision Comprobante Original",
		compute='_compute_campo_fecha_emision_original' ,store=True , readonly=True)
	tipo_comprobante_original=fields.Char(string="Tipo Comprobante Original",
		compute='_compute_campo_tipo_comprobante_original' , store=True  , readonly=True)
	serie_comprobante_original=fields.Char(string="Serie Comprobante Original",
		compute='_compute_campo_serie_comprobante_original' ,store=True , readonly=True)
	numero_comprobante_original=fields.Char(string="Nùmero Comprobante Original",
		compute='_compute_campo_numero_comprobante_original', store=True , readonly=True)
	
	ventas_identificacion_contrato_operadores = fields.Char(string="Identificación Contrato Operadores Irregulares" ,readonly=True)
	error_1 = fields.Char(string="Error Tipo 1" , readonly=True)
	ventas_indicador_comprobantes_medios_pago = fields.Char(string="Indicador Comprobantes cancelados con medios de pago" ,readonly=True)
	estado_FE=fields.Char(string="Estado FE",readonly=True)
	################################################################
	#alert = fields.Char(string='Alerta',readonly=True)


	@api.depends('invoice_id')
	def _compute_campo_ventas_valor_facturado_exportacion(self):
		for rec in self:
			if rec.invoice_id:
				rec.ventas_valor_facturado_exportacion = \
					format(rec.invoice_id.total_sale_export*rec.tipo_cambio*((rec.invoice_id.move_type=="out_refund")*(-2)+1 )*((rec.invoice_id.state!='cancel')*1),".2f")


	
	@api.depends('invoice_id','tipo_cambio')
	def	_compute_campo_ventas_base_imponible_operacion_gravada(self):
		for rec in self:
			if rec.invoice_id:
				rec.ventas_base_imponible_operacion_gravada = \
					format(rec.invoice_id.total_sale_taxed*rec.tipo_cambio*( (rec.invoice_id.move_type=="out_refund")*(-2)+1 )*((rec.invoice_id.state!='cancel')*1),".2f")



	@api.depends('invoice_id')
	def _compute_campo_ventas_importe_operacion_exonerada(self):
		for rec in self:
			if rec.invoice_id:
				rec.ventas_importe_operacion_exonerada = \
					format(rec.invoice_id.total_sale_exonerated*rec.tipo_cambio*( (rec.invoice_id.move_type=="out_refund")*(-2)+1 )*((rec.invoice_id.state!='cancel')*1),".2f")



	@api.depends('invoice_id')
	def _compute_campo_ventas_importe_operacion_inafecta(self):
		for rec in self:
			if rec.invoice_id:
				rec.ventas_importe_operacion_inafecta = \
					format(rec.invoice_id.total_sale_unaffected*rec.tipo_cambio*( (rec.invoice_id.move_type=="out_refund")*(-2)+1 )*((rec.invoice_id.state!='cancel')*1),".2f")

	###################################################################################################################

	@api.depends('invoice_id','tipo_cambio')
	def _compute_campo_impuestos(self):
		for rec in self:
			if rec.invoice_id:
				rec.ventas_igv= \
					format(rec.invoice_id.total_sale_igv*rec.tipo_cambio*( (rec.invoice_id.move_type=="out_refund")*(-2)+1 )*((rec.invoice_id.state!='cancel')*1),".2f")
				rec.otros_impuestos= 0.00
				rec.impuesto_consumo_bolsas_plastico = 0.00


	@api.depends('invoice_id')
	def _compute_campo_tipo_cambio(self):
		for rec in self:
			if rec.invoice_id.move_type=="out_refund":

				if rec.invoice_id.reversed_entry_id:
					rec.tipo_cambio=format(rec.invoice_id.reversed_entry_id.currency_tc or 0.00,".3f")
				else:
					rec.tipo_cambio=format(rec.invoice_id.currency_tc or 0.00,".3f")
			else:
				rec.tipo_cambio=format(rec.invoice_id.currency_tc,".3f")


	####################################################################################################################

	@api.depends('invoice_id','tipo_cambio')
	def _compute_campo_importe_total_comprobante(self):
		for rec in self:
			if rec.invoice_id:
				rec.importe_total_comprobante=format(rec.invoice_id.amount_total*rec.tipo_cambio*( (rec.invoice_id.move_type=="out_refund")*(-2)+1 )*((rec.invoice_id.state!='cancel')*1),".2f")



	@api.depends('invoice_id')
	def _compute_campo_codigo_moneda(self):
		for rec in self:
			if rec.invoice_id:
				rec.codigo_moneda=rec.invoice_id.currency_id.name or ''



	@api.depends('invoice_id')
	def compute_invoice_id_2(self):
		for rec in self:
			if rec.invoice_id:
				if rec.invoice_id.reversed_entry_id:
					rec.invoice_id_2= rec.invoice_id.reversed_entry_id


	#####################################################################################

	@api.depends('invoice_id_2')
	def _compute_campo_fecha_emision_original(self):
		for rec in self:
			if rec.invoice_id_2:
				rec.fecha_emision_original= rec.invoice_id_2.invoice_date
			else:
				rec.fecha_emision_original= ''
			


	@api.depends('invoice_id_2')
	def _compute_campo_tipo_comprobante_original(self):
		for rec in self:
			rec.tipo_comprobante_original=''
			if rec.invoice_id_2 and rec.invoice_id_2.l10n_latam_document_type_id:
				rec.tipo_comprobante_original= rec.invoice_id_2.l10n_latam_document_type_id.code or ''
			else:
				rec.tipo_comprobante_original=''
			


	@api.depends('invoice_id_2')
	def _compute_campo_serie_comprobante_original(self):
		for rec in self:
			rec.serie_comprobante_original = ''

			if rec.invoice_id_2:
				rec.serie_comprobante_original = rec.invoice_id_2.l10n_pe_prefix_code or ''
			


	@api.depends('invoice_id_2')
	def _compute_campo_numero_comprobante_original(self):
		for rec in self:
			rec.numero_comprobante_original = ''

			if rec.invoice_id_2:
				rec.numero_comprobante_original= rec.invoice_id_2.l10n_pe_invoice_number or ''