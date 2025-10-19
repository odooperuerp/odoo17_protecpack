from odoo.exceptions import UserError , ValidationError
from odoo import models, fields, api, _
from odoo.exceptions import UserError , ValidationError
import logging
_logger=logging.getLogger(__name__)

class AssetAssetBrand(models.Model):
	_name='asset.asset.brand'
	_description = "Marca del Activo"
	
	name=fields.Char(string="Nombre de la Marca")

	_sql_constraints = [
		('Nombre', 'UNIQUE (name)','El nombre de la marca del activo ya existe !!')
	]
