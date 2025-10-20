# -*- coding: utf-8 -*-
from odoo import fields, models

class ResBank(models.Model):
	_inherit = "res.bank"
	
	code_sunat = fields.Char(string="Código SUNAT")

	_sql_constraints = [
		('Código_Sunat','UNIQUE (code_sunat)','El código de banco debe ser único !')]