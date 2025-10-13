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


class PlePurchaseLine(models.Model):
	_name='ple.purchase.line'

	ple_purchase_id=fields.Many2one("ple.purchase",string="id PLE", ondelete="cascade")

	ple_purchase_id_no_domiciliados = fields.Many2one("ple.purchase",string="id PLE" , ondelete="cascade")
	ple_purchase_id_recibo_honorarios=fields.Many2one("ple.purchase",string="id PLE",ondelete="cascade")

	fiscal_year = fields.Char(string="Año Fiscal",readonly=True)
	fiscal_month = fields.Char(string="Mes Fiscal",readonly=True)

	###### CAMPO PRINCIPAL O CAMPO ROOT !!!
	move_id=fields.Many2one("account.move",string="Documento",readonly= True)

	journal_id=fields.Many2one("account.journal",string="Diario",readonly=True)
	partner_id=fields.Many2one("res.partner", string="Proveedor" ,readonly=True)
	currency_id=fields.Many2one("res.currency",string="Código moneda",readonly=True) 
	move_id_2=fields.Many2one("account.move",string="Documento de origen",readonly=True) 

	asiento_contable=fields.Char(string="Nombre del asiento contable",readonly=True)
	m_correlativo_asiento_contable=fields.Char(string="M-correlativo asiento contable",readonly=True)
	fecha_emision_comprobante=fields.Date(string="Fecha emisión Comprobante",readonly=True)
	fecha_vencimiento=fields.Date(string="Fecha de vencimiento",readonly=True)
		
	tipo_comprobante=fields.Char(string="Tipo de Comprobante",readonly=True)
	serie_comprobante=fields.Char(string="Serie del Comprobante",readonly=True)

	anio_emision_dua=fields.Char(string="Año Emisión DUA",default='0')
	numero_comprobante=fields.Char(string="Número Comprobante",readonly=True)
		
	operaciones_sin_igv=fields.Float(string="Operaciones sin igv" ,default=0.00, digits=(16, 2))
	tipo_documento_proveedor=fields.Char(string="Tipo Documento Proveedor",readonly=True)#
	ruc_dni=fields.Char(string="RUC o DNI Proveedor",readonly=True)
		
	razon_social=fields.Char(string="Razón Social",readonly=True) # ,
		
	base_imponible_igv_gravadas=fields.Float(string="Base crédito fiscal gravadas",readonly = True, digits=(16, 2))
	monto_igv_1=fields.Float(string="Monto IGV",readonly=True, digits=(16, 2))
	base_imponible_igv_no_gravadas=fields.Float(string="base crédito fiscal no gravadas",default=0.00, digits=(16, 2))
	monto_igv_2=fields.Float(string="Monto IGV 2",default=0.00, digits=(16, 2))
	base_imponible_no_igv=fields.Float(string="Base sin Crédito fiscal",default=0.00, digits=(16, 2)) 
	monto_igv_3=fields.Float(string="Monto IGV 3",default=0.00, digits=(16, 2)) 
	valor_no_gravadas=fields.Float(string="Valor adquisiciones no gravadas",default=0.00, digits=(16, 2)) 
	isc=fields.Float(string="ISC",default=0.00, digits=(16, 2)) 

	impuesto_consumo_bolsas_plastico=fields.Float(string="Impuesto Consumo Bolsas de Plástico",default=0.00, digits=(16, 2))

	otros_impuestos=fields.Float(string="Otros Impuestos",default=0.00, digits=(16, 2))

	importe_adquisiciones_registradas=fields.Float(string="Importe Adquisiciones Registradas",readonly=True, digits=(16, 2))

	codigo_moneda=fields.Char(string="Código Moneda",readonly=True)
	tipo_cambio=fields.Float(string="Tipo de Cambio",digits = (12,3),readonly=True)
	fecha_emision_original=fields.Date(string="Fecha Emision Comprobante Original",readonly=True)
	tipo_comprobante_original=fields.Char(string="Tipo Comprobante Original",readonly=True)
	serie_comprobante_original=fields.Char(string="Serie Comprobante Original",readonly=True)
	codigo_dep_aduanera=fields.Char(string="Código Dependencia Aduanera" )
	numero_comprobante_original=fields.Char(string="Número Comprobante Original",readonly=True )
	fecha_detraccion=fields.Date(string="Fecha Detracción")
	numero_detraccion=fields.Char(string="Número Detracción")
	marca_retencion=fields.Char(string="Marca Retención")
	clasificacion_bienes=fields.Char(string="Clasificación Bienes Adquiridos")
	identificacion_contrato=fields.Char(string="Identificación Contrato")
	error_1=fields.Char(string="Error Tipo 1")
	error_2=fields.Char(string="Error Tipo 2")
	error_3=fields.Char(string="Error Tipo 3") 
	error_4=fields.Char(string="Error Tipo 4") 
	indicador_comprobantes=fields.Char(string="Indicador Comprobantes") 
	oportunidad_anotacion=fields.Char(string="Oportunidad Anotación Domiciliado",readonly=True) 
	############################################################################################################
	partner_country_id=fields.Many2one('res.country',string="Pais residencia sujeto no domiciliado",
		readonly=True) #
	

	############## CAMPOS EXCLUSIVOS DE NO DOMICILIADOS !!!!!
	no_domiciliado_m_correlativo_asiento_contable=fields.Char(string="M-correlativo asiento contable",readonly=True) #,
		
	no_domiciliado_valor_adquisiciones=fields.Float(string="Valor Adquisiciones",default=0.00, digits=(16, 2))#,
		
	no_domiciliado_otros_conceptos_adicionales=fields.Float(string="Conceptos Adicionales",default=0.00, digits=(16, 2)) #,
		
	no_domiciliado_tipo_comprobante_credito_fiscal=fields.Char(string="Tipo Comprobante Crédito fiscal")#,
		
	no_domiciliado_serie_comprobante_credito_fiscal=fields.Char(string="Serie Comprobante Crédito fiscal")#,
		
	no_domiciliado_numero_comprobante_pago_impuesto=fields.Char(string="Número Comprobante Pago Impuesto")#,
		
	no_domiciliado_pais_residencia=fields.Char(string="Código pais residencia del no domiciliado",
		readonly=True)

	no_domiciliado_domicilio=fields.Char(string="Domicilio en el extranjero",readonly=True)
		
	no_domiciliado_numero_identificacion=fields.Char(string="Número Identificación del no domiciliado",readonly=True)

	no_domiciliado_identificacion_beneficiario=fields.Char(string="Número Identificación beneficiario")
	no_domiciliado_razon_social_beneficiario=fields.Char(string="Razón social beneficiario")
	no_domiciliado_pais_beneficiario=fields.Char(string="Pais residencia beneficiario")
	no_domiciliado_vinculo_entre_contribuyente_residente=fields.Char(
		string="Vinculo contribuyente-residente extranjero") 
	no_domiciliado_renta_bruta = fields.Float(string="Renta Bruta",default=0.00, digits=(16, 2)) 
	no_domiciliado_deduccion_bienes = fields.Float(string="Deducción/Costo bienes capital",default = 0.00, digits=(16, 2)) 
	no_domiciliado_renta_neta = fields.Float(string="Renta Neta",default=0.00, digits=(16, 2)) 
	no_domiciliado_tasa_retencion = fields.Float(string="Tasa de retención",default=0.00, digits=(16, 2)) 
	no_domiciliado_impuesto_retenido = fields.Float(string="Impuesto retenido",default=0.00, digits=(16, 2))
	no_domiciliado_convenios =  fields.Char(string="Convenios para evitar doble imposición",default='00') 
	no_domiciliado_exoneracion = fields.Char(string="Exoneración aplicada") 
	no_domiciliado_tipo_renta = fields.Char(string="Tipo de Renta" , default='00') 
	no_domiciliado_modalidad_servicio_prestado= fields.Char(string="Modalidad servicio prestado") 
	no_domiciliado_aplicacion_ley_impuesto_renta = fields.Char(string="Aplicación Art. 76°") 
	no_domiciliado_oportunidad_anotacion= fields.Char(string="Oportunidad Anotación no Domiciliado",readonly=True)

	##################################################################


	def pertenece_periodo(self,date_1,date_2):
		if date_1 and date_2:
			
			if date_1.year == date_2.year and date_1.month == date_2.month:
				return 1
			
			elif date_1 + timedelta(days=365) >= date_2:
				return 2
			
			elif date_1 + timedelta(days=365) < date_2:
				return 3

	###########################
	## LA CONSULTA DEBERIA EVITAR QUE SE FILTREN DOCUMENTOS CON MAS DE 12 MESES DE ANTIGUEDAD

	def get_campo_oportunidad_anotacion(self):

		for rec in self:
			valor_campo_3 = '-'

			if rec.move_id:
				if rec.fiscal_year and rec.fiscal_month:

					date_periodo = datetime.strptime("%s-%s-01"%(rec.fiscal_year,rec.fiscal_month),"%Y-%m-%d").date()
					if rec.pertenece_periodo(date_periodo,rec.move_id.invoice_date)==1 and (rec.move_id.total_sale_igv==0):
						valor_campo_3='0'
					elif rec.pertenece_periodo(date_periodo,rec.move_id.invoice_date)==1 and (rec.move_id.total_sale_igv>0):
						valor_campo_3='1'

					elif rec.pertenece_periodo(rec.move_id.invoice_date,date_periodo) in [1,2] and (rec.move_id.total_sale_igv>0 or rec.move_id.total_sale_igv==0):
						valor_campo_3='6'

					elif rec.pertenece_periodo(rec.move_id.invoice_date,date_periodo)==3 and (rec.move_id.total_sale_igv==0):
						valor_campo_3='7'
			
			else:
				valor_campo_3='-'
			
			rec.oportunidad_anotacion = valor_campo_3

			rec.no_domiciliado_oportunidad_anotacion='0'
