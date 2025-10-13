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

class SireSaleCompareLine(models.Model):
	_name='sire.sale.compare.line'
	_description = "SUNAT SIRE Sale Compare Line"

	sire_sale_id=fields.Many2one("sire.sale",string="ID SIRE" , ondelete='cascade' , readonly=True )

	fecha_emision = fields.Char(string="Fecha de emisión",readonly=True)
	tipo_documento_cp = fields.Char(string="Tipo CP/Doc.",readonly=True)
	serie_documento_cp = fields.Char(string="Serie del CDP",readonly=True)
	numero_documento_cp = fields.Char(string="Nro CP o Doc. Nro Inicial (Rango)",readonly=True)
	nro_doc_identidad_cliente = fields.Char(string="Nro Doc Identidad",readonly=True)
	razon_social = fields.Char(string="Apellidos Nombres/ Razón Social",readonly=True)
	total_cp = fields.Char(string="Total CP",readonly=True)
	moneda = fields.Char(string="Moneda",readonly=True)
	estado_compare = fields.Selection(selection=[('0','En SIRE, no en Sistema'),('1','En sistema, no en SIRE')],
		string="Estado Comparación")
