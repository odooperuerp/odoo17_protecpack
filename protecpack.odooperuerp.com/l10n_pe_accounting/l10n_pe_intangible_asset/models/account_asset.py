from odoo import models, fields, api, _
from datetime import datetime, timedelta

import logging
_logger=logging.getLogger(__name__)


class AccountAsset(models.Model):
	_inherit='account.asset'
	
	is_category_intangible = fields.Boolean(string="Es Modelo de Activos Intangibles",default=False)

	is_intangible = fields.Boolean(string="Es Activo Intangible",default=False)


	@api.onchange('model_id')
	def onchange_is_category_intangible(self):
		for rec in self:
			if rec.model_id and rec.model_id.is_category_intangible:
				rec.is_intangible = True
			else:
				rec.is_intangible = False
	
