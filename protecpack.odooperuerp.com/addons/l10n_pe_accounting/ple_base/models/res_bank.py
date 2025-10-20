# -*- coding: utf-8 -*-
from odoo import fields, models

class ResBank(models.Model):
	_inherit = "res.bank"
	
	code_sunat= fields.Char(string="Código Sunat")