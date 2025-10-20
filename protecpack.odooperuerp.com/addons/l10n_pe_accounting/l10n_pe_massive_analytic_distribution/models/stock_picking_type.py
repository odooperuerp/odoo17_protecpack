# -*- coding: utf-8 -*-
from odoo import api, exceptions, fields, models, _

class StockPickingType(models.Model):
	_inherit = 'stock.picking.type'

	has_analytic_distribution = fields.Boolean(string="Distribución Analítica")