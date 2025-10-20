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



class SirePurchaseLine(models.Model):
	_name='sire.purchase.line'
	_description = "SIRE PURCHASE LINE"

	sire_purchase_id=fields.Many2one("sire.purchase",string="ID SIRE" , ondelete='cascade' , readonly=True )

	invoice_id=fields.Many2one("account.move" , string="Documento" , ondelete="cascade",readonly= True)

	invoice_id_2=fields.Many2one("account.move", string="Documento de origen",
		compute='compute_invoice_id_2',store=True,readonly=True)
	#####################################################################################################################################
	partner_id=fields.Many2one("res.partner",string="Proveedor",compute='compute_partner_id',store=True) 
	currency_id=fields.Many2one("res.currency",string="C󤩧o moneda",compute='compute_currency_id',store=True) 

	fecha_emision_comprobante=fields.Date(string="Fecha emisi󮠃omprobante") ##
	fecha_vencimiento=fields.Date(string="Fecha de vencimiento") ##
	tipo_comprobante=fields.Char(string="Tipo de Comprobante",readonly=True) ## 
	serie_comprobante=fields.Char(string="Serie del Comprobante") ##
	anio_emision_DUA=fields.Char(string="A񯠅misi󮠄UA",
		compute='_compute_campo_anio_emision_DUA',store=True,default='') ## 
	numero_comprobante=fields.Char(string="N򭥲o Comprobante") ##
	operaciones_sin_igv=fields.Float(string="Operaciones sin igv",default=0.00)
	tipo_documento_proveedor=fields.Char(string="Tipo Documento Proveedor",readonly=True) ##
	ruc_dni=fields.Char(string="RUC o DNI Proveedor") ##
	razon_social=fields.Char(string="Raz󮠓ocial") ##
	base_imponible_igv_gravadas=fields.Float(string="Base crꥩto fiscal gravadas",
		compute='_compute_campo_base_imponible_igv_gravadas',store=True,readonly=True) ##
	monto_igv_1=fields.Float(string="Monto IGV",compute='_compute_campo_impuestos',store=True,readonly = True) ##
	base_imponible_igv_no_gravadas=fields.Float(string="base crꥩto fiscal no gravadas",default=0.00) ##
	monto_igv_2=fields.Float(string="Monto IGV",default=0.00) ##
	base_imponible_no_igv=fields.Float(string="Base sin Crꥩto fiscal",default=0.00) ## 
	monto_igv_3=fields.Float(string="Monto IGV",default=0.00) ##
	valor_no_gravadas=fields.Float(string="Valor adquisiciones no gravadas",
		compute='_compute_campo_valor_no_gravadas',store=True) ##
	isc=fields.Float(string="ISC",default=0.00 ) ##
	impuesto_consumo_bolsas_plastico=fields.Float(string="Impuesto al Consumo de las Bolsas de Plⴴico",default=0.00,
		readonly=True,compute='_compute_campo_impuestos',store=True) ##

	otros_impuestos=fields.Float(string="Otros Impuestos",compute='_compute_campo_impuestos',store=True) ##
	importe_adquisiciones_registradas=fields.Float(string="Importe Adquisiciones Registradas",
		compute='_compute_campo_importe_adquisiciones_registradas',store=True,readonly=True) ##
	codigo_moneda=fields.Char(string="C󤩧o Moneda",compute='_compute_campo_codigo_moneda',store=True,readonly=True) ##
	tipo_cambio=fields.Float(string="Tipo de Cambio",compute='_compute_campo_tipo_cambio',store=True,digits=(12,3)) ##
	fecha_emision_original=fields.Date(string="Fecha Emision Comprobante Original",
		compute='_compute_campo_fecha_emision_original',store=True) ##
	tipo_comprobante_original=fields.Char(string="Tipo Comprobante Original",
		compute='_compute_campo_tipo_comprobante_original',store=True,readonly=True) ##
	serie_comprobante_original=fields.Char(string="Serie Comprobante Original",
		compute='_compute_campo_serie_comprobante_original',store=True) ##
	dua_doc_modificado = fields.Char(string="DUA Comprobante Original",default='') ##
	numero_comprobante_original=fields.Char(string="N򭥲o Comprobante Original",
		compute='_compute_campo_numero_comprobante_original',store=True) ##
	clasificacion_bienes=fields.Char(string="Clasificaci󮠂ienes Adquiridos") ##
	identificacion_contrato=fields.Char(string="Identificaci󮠃ontrato") ##
	participacion_contrato = fields.Char(string="Partic. del Contrato") ##
	imp_mat_beneficio = fields.Char(string="Imp.Mat.de Contrato") ##
	indicador_exclusion_inclusion = fields.Boolean(string="Indicador Excl/Incl") ##
	car = fields.Char(string="CAR",compute="_compute_campo_car",store=True) ##
	################################################################


	@api.depends('invoice_id','ruc_dni','tipo_comprobante','serie_comprobante','numero_comprobante')
	def _compute_campo_car(self):
		for rec in self:
			if rec.invoice_id:
				rec.car = "%s%s%s%s"%(
					rec.ruc_dni or '',
					rec.tipo_comprobante or '',
					rec.serie_comprobante or '',
					(rec.numero_comprobante or '').zfill(10))


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



	@api.depends('invoice_id')
	def compute_invoice_id_2(self):
		for rec in self:
			if rec.invoice_id:
				if rec.invoice_id.reversed_entry_id:
					rec.invoice_id_2= rec.invoice_id.reversed_entry_id

	############################################################################################

	#---------------------------------------------------------------------			
	@api.depends('invoice_id','tipo_comprobante')
	def _compute_campo_anio_emision_DUA(self):
		for rec in self:
			if rec.invoice_id.journal_id and (rec.tipo_comprobante in ['50']):
				rec.anio_emision_DUA=str(rec.invoice_id.invoice_date.year)
			else:
				rec.anio_emision_DUA = ''
	

	#---------------------------------------------------------------------
	@api.depends('invoice_id','tipo_cambio')
	def _compute_campo_base_imponible_igv_gravadas(self):
		for rec in self:
			if rec.invoice_id:
				rec.base_imponible_igv_gravadas= format(rec.invoice_id.total_sale_taxed*rec.tipo_cambio*( (rec.invoice_id.move_type=="in_refund")*(-2)+1 ),".2f")



	#----------------------------------------------------------------------
	@api.depends('invoice_id','tipo_cambio')
	def _compute_campo_impuestos(self):
		for rec in self:
			if rec.invoice_id:
				rec.monto_igv_1= format(rec.invoice_id.total_sale_igv*rec.tipo_cambio*( (rec.invoice_id.move_type=="in_refund")*(-2)+1 ),".2f")
				rec.otros_impuestos= 0.00
				rec.impuesto_consumo_bolsas_plastico = 0.00

	#----------------------------------------------------------------------
	@api.depends('invoice_id','tipo_cambio')
	def _compute_campo_valor_no_gravadas(self):
		for rec in self:
			if rec.invoice_id:
				rec.valor_no_gravadas = \
					(rec.invoice_id.total_sale_free or rec.invoice_id.total_sale_unaffected or rec.invoice_id.total_sale_exonerated or 0.00)*rec.tipo_cambio*((rec.invoice_id.move_type=="in_refund")*(-2)+1 )


	######################################################
	@api.depends('invoice_id')
	def _compute_campo_otros_impuestos(self):
		for rec in self:
			rec.otros_impuestos=0.00

	######################################################

	@api.depends('invoice_id','tipo_cambio')
	def _compute_campo_importe_adquisiciones_registradas(self):
		for rec in self:
			if rec.invoice_id:
				rec.importe_adquisiciones_registradas=format(rec.invoice_id.amount_total*rec.tipo_cambio*( (rec.invoice_id.move_type=="in_refund")*(-2)+1 ),".2f")


	#---------------------------------------------------------------

	@api.depends('invoice_id')
	def _compute_campo_tipo_cambio(self):
		for rec in self:
			if rec.invoice_id.move_type=="in_refund":
				if rec.invoice_id.reversed_entry_id:
					rec.tipo_cambio=format(rec.invoice_id.reversed_entry_id.currency_tc or 1.000,".3f")
				else:
					rec.tipo_cambio=format(rec.invoice_id.currency_tc or 1.000,".3f")
			else:
				rec.tipo_cambio=format(rec.invoice_id.currency_tc or 1.000,".3f")


	##############################################################################
	@api.depends('invoice_id')
	def _compute_campo_codigo_moneda(self):
		for rec in self:
			if rec.invoice_id:
				rec.codigo_moneda=rec.invoice_id.currency_id.name or ''

	#----------------------------------------------------------------
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

	################################################################################################
