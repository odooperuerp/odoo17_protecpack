from odoo.exceptions import UserError , ValidationError
from odoo import models, fields, api, _
from odoo.exceptions import UserError , ValidationError
import logging
_logger=logging.getLogger(__name__)

class AssetAssetModel(models.Model):
	_name='asset.asset.model'
	_description = "Modelo del Activo"
	
	name=fields.Char(string="Nombre del Modelo")

	_sql_constraints = [
		('Nombre', 'UNIQUE (name)','El nombre del modelo del activo ya existe !!')

	]
