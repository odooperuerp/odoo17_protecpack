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

color_red='#F90620'
color_green='#0FEC37'

class SunatSireSaleLine(models.Model):
	_name='sunat.sire.sale.line'
	_description = "SUNAT SIRE Sale Line"

	sire_sale_id=fields.Many2one("sire.sale",string="ID SIRE" , ondelete='cascade' , readonly=True)

	ruc = fields.Char(string="RUC", readonly=True)
	razon_social = fields.Char(string="Apellidos y Nombres o Razón social",readonly=True)
	periodo = fields.Char(string="Periodo",readonly=True)
	car_sunat = fields.Char(string="CAR SUNAT",readonly=True)
	##################################################################################
	fecha_emision = fields.Date(string="Fecha de emisión",readonly=True)
	fecha_vencimiento = fields.Date(string="Fecha Vcto/Pago",readonly=True)
	tipo_documento_cp = fields.Char(string="Tipo CP/Doc.",readonly=True)
	serie_documento_cp = fields.Char(string="Serie del CDP",readonly=True)
	numero_documento_cp = fields.Char(string="Nro CP o Doc. Nro Inicial (Rango)",readonly=True)
	nro_final_rango = fields.Char(string="Nro Final (Rango)",readonly=True)
	tipo_doc_cliente = fields.Char(string="Tipo Doc Identidad",readonly=True)
	nro_doc_identidad_cliente = fields.Char(string="Nro Doc Identidad",readonly=True)
	razon_social = fields.Char(string="Apellidos Nombres/ Razón Social",readonly=True)
	valor_fcturado_exportacion = fields.Float(string="Valor Facturado Exportación",readonly=True)
	base_imponible_grabada = fields.Float(string="BI Gravada",readonly=True)
	descuento_base_imponible = fields.Float(string="Dscto BI",readonly=True)
	igv = fields.Float(string="IGV / IPM",readonly=True)
	descuento_igv = fields.Float(string="Dscto IGV / IPM",readonly=True)
	monto_exonerado = fields.Float(string="Mto Exonerado",readonly=True)
	monto_inafecto = fields.Float(string="Mto Inafecto",readonly=True)
	isc = fields.Float(string="ISC",readonly=True)
	base_imponible_ivap = fields.Float(string="BI Grav IVAP",readonly=True)
	ivap = fields.Float(string="IVAP",readonly=True)
	icbper = fields.Float(string="ICBPER",readonly=True)
	otros_tributos = fields.Float(string="Otros Tributos",readonly=True)
	total_cp = fields.Float(string="Total CP",readonly=True)
	moneda = fields.Char(string="Moneda",readonly=True)
	tipo_cambio = fields.Char(string="Tipo Cambio",readonly=True)
	fecha_emision_doc_modificado = fields.Date(string="Fecha Emisión Doc Modificado",readonly=True)
	tipo_cp_modificado = fields.Char(string="Tipo CP Modificado",readonly=True)
	serie_cp_modificado = fields.Char(string="Serie CP Modificado",readonly=True)
	nro_cp_modificado = fields.Char(string="Nro CP Modificado",readonly=True)
	id_proyecto_operadores_atribucion = fields.Char(string="ID Proyecto Operadores Atribución",readonly=True)
	tipo_nota = fields.Char(string="Tipo de Nota",readonly=True)
	estado_comprobante = fields.Char(string="Est. Comp",readonly=True)
	valor_fob_embarcado = fields.Char(string="Valor FOB Embarcado",readonly=True)
	valor_op_gratuitas = fields.Char(string="Valor OP Gratuitas",readonly=True)
	tipo_operacion = fields.Char(string="Tipo Operación",readonly=True)
	dam_cp = fields.Char(string="DAM / CP",readonly=True)
	clu = fields.Char(string="CLU",readonly=True)