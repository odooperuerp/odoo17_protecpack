import calendar
from io import BytesIO, StringIO
from odoo import models, fields, api, _

from odoo.exceptions import UserError , ValidationError

import logging
_logger=logging.getLogger(__name__)

class AccountAsset(models.Model):
	_inherit='account.asset'
	
	brand_id=fields.Many2one('asset.asset.brand',string="Marca del Activo")
	serial_number_plate=fields.Char(string="Número de serie/placa")
	asset_encoding_type_sunat=fields.Selection(
		selection=[('3','GS1 (EAN-UCC)'),('9','OTROS')],string="Tipo Codificación del Activo")
	asset_code=fields.Char(string="Código del Activo")
	fixed_asset_type_code_sunat=fields.Selection(string="Tipo de Activo Fijo",
		selection=[('1','NO REVALUADO O REVALUADO SIN EFECTO TRIBUTARIO'),('2','REVALUADO CON EFECTO TRIBUTARIO')])

	document_number_for_depreciation_method_change=fields.Char(
		string="Número de Documento de autorización para cambio de método de depreciación")
	declared_ple_0701 = fields.Boolean(string="Registro declarado en PLE 0701")