# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ResPartner(models.Model):
	_inherit = 'res.partner'

	is_retention_agent = fields.Boolean(string="Es Agente Retención", default=False)
	is_perception_agent = fields.Boolean(string="Es Agente Percepción", default=False)
	is_good_taxpayer = fields.Boolean(string="Es Buen Contribuyente", default=False)
	