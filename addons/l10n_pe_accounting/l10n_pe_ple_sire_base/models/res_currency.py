# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class ResCurrency(models.Model):
	_inherit = 'res.currency'

	code_sunat = fields.Char(string="Código SUNAT")