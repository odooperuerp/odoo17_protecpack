# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
class ResCountry(models.Model):
	_inherit = 'res.country'

	code_sunat = fields.Char(string="Código Sunat",size = 4)