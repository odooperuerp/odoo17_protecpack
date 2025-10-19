# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError , ValidationError

class ResCompany(models.Model):
	_inherit = 'res.company'

	economic_sector_sunat_id = fields.Many2one('economic.sector.sunat',string="Tipo de Sector Económico")

