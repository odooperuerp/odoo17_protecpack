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


class SirePurchaseNoDomiciliadoLine(models.Model):
	_name='sire.purchase.no.domiciliado.line'
	_description = "SIRE PURCHASE NO DOMICILIADO LINE"

	sire_purchase_id=fields.Many2one("sire.purchase",string="ID SIRE" , ondelete='cascade' , readonly=True )

	invoice_id=fields.Many2one("account.move" , string="Documento" , ondelete="cascade",readonly= True)

	#########################################################################################################

	partner_id=fields.Many2one("res.partner", string="Proveedor",compute='compute_partner_id',store=True) 
	currency_id=fields.Many2one("res.currency",string="Código moneda",compute='compute_currency_id',store=True) 
	fecha_emision_comprobante=fields.Date(string="Fecha emisión Comprobante") ##
	tipo_comprobante=fields.Char(string="Tipo de Comprobante",readonly=True) ## 
	serie_comprobante=fields.Char(string="Serie del Comprobante") ##
	numero_comprobante=fields.Char(string="Número Comprobante") ##
	valor_adquisiciones=fields.Float(string="Valor Adquisiciones" ,default=0.00)
	otros_conceptos_adicionales=fields.Float(string="Conceptos Adicionales",default=0.00) 
	importe_total=fields.Float(string="Importe Adquisiciones Registradas",
		compute='compute_campo_importe_total',store=True,readonly=True)
	tipo_comprobante_credito_fiscal=fields.Char(string="Tipo Comprobante Crédito fiscal")
	serie_comprobante_credito_fiscal=fields.Char(string="Serie Comprobante Crédito fiscal")
	anio_emision_DUA=fields.Char(string="Año Emisión DUA",default='0') ## 
	numero_comprobante_pago_impuesto=fields.Char(string="Número Comprobante Pago Impuesto")
	retencion_igv = fields.Float(string="Retención IGV",default=0.00)
	codigo_moneda=fields.Char(string="Código Moneda",compute='compute_campo_codigo_moneda',store=True,readonly=True) ##
	tipo_cambio=fields.Float(string="Tipo de Cambio",compute='compute_campo_tipo_cambio',store=True,digits=(12,3)) ##
	pais_residencia = fields.Char(string="Pais residencia", compute='compute_campo_pais_residencia',store=True)
	razon_social = fields.Char(string="Razón Social no domiciliado") ##
	domicilio_extranjero = fields.Char(string="Domicilio en Extranjero",
		compute='compute_campo_domicilio_extranjero',store=True)
	numero_identificacion = fields.Char(string="Número Identificación") ##
	identificacion_beneficiario=fields.Char(string="Número Identificación beneficiario")
	razon_social_beneficiario=fields.Char(string="Razón social beneficiario")
	pais_beneficiario=fields.Char(string="Pais residencia beneficiario")
	vinculo_sujeto_beneficiario = fields.Char(string="Vinculo sujeto-beneficiario")
	renta_bruta = fields.Float(string="Renta Bruta",default=0.00) 
	deduccion_costo_capital = fields.Float(string="Deducción/Costo capital",default = 0.00) 
	renta_neta = fields.Float(string="Renta Neta",default=0.00) 
	tasa_retencion = fields.Float(string="Tasa de retención",default=0.00) 
	impuesto_retenido = fields.Float(string="Impuesto retenido",default=0.00)
	convenios_evitar_doble_imposicion =  fields.Char(string="Convenios para evitar doble imposición",default='00') 
	exoneracion_aplicada = fields.Char(string="Exoneración aplicada") 
	tipo_renta = fields.Char(string="Tipo Renta" , default='00') 
	modalidad_servicio_sujeto= fields.Char(string="Modalidad del servicio") 
	aplicacion_ley_impuesto_renta = fields.Char(string="Aplicación Art.76° L.I.R") 
	car = fields.Char(string="CAR",compute="compute_campo_car",store=True) ##
	
	################################################################

	@api.depends('invoice_id','numero_identificacion','tipo_comprobante','serie_comprobante','numero_comprobante')
	def compute_campo_car(self):
		for rec in self:
			if self.invoice_id:
				self.car = "%s%s%s%s"%(
					self.numero_identificacion or '',
					self.tipo_comprobante,
					self.serie_comprobante,
					(self.numero_comprobante or '').zfill(10))



	@api.depends('invoice_id')
	def compute_partner_id(self):
		for rec in self:
			if rec.invoice_id:
				rec.partner_id= rec.invoice_id.partner_id



	@api.depends('invoice_id')
	def compute_currency_id(self):
		for rec in self:
			if rec.invoice_id:
				rec.currency_id= rec.invoice_id.currency_id



	######################################################
	@api.depends('invoice_id','valor_adquisiciones','otros_conceptos_adicionales')
	def compute_campo_importe_total(self):
		for rec in self:
			if rec.invoice_id:
				rec.importe_total=format((rec.valor_adquisiciones + rec.otros_conceptos_adicionales)*rec.tipo_cambio*( (rec.invoice_id.move_type=="in_refund")*(-2)+1 ),".2f")
		

	###################################################################################################################
	
	@api.depends('invoice_id')
	def compute_campo_tipo_cambio(self):
		for rec in self:
			if rec.invoice_id.move_type=="in_refund":

				if rec.invoice_id.reversed_entry_id:
					rec.tipo_cambio=format(rec.invoice_id.reversed_entry_id.currency_tc or 1.000,".3f")
				else:
					rec.tipo_cambio=format(rec.invoice_id.currency_tc or 1.000,".3f")
			else:
				rec.tipo_cambio=format(rec.invoice_id.currency_tc,".3f")



	@api.depends('partner_id')
	def compute_campo_pais_residencia(self):
		for rec in self:
			rec.pais_residencia=rec.partner_id.country_id and rec.partner_id.country_id.code_sunat or ''



	@api.depends('partner_id')
	def compute_campo_domicilio_extranjero(self):
		for rec in self:
			domicilio = ''
			
			if rec.partner_id.country_id:
				domicilio += rec.partner_id.country_id.name or ''

			if rec.partner_id.street:
				domicilio += " %s"%(rec.partner_id.street or '')

			rec.domicilio_extranjero = domicilio



	@api.depends('invoice_id')
	def compute_campo_codigo_moneda(self):
		for rec in self:
			if rec.invoice_id:
				rec.codigo_moneda=rec.invoice_id.currency_id and rec.invoice_id.currency_id.code_sunat or ''

	#####################################################################################################