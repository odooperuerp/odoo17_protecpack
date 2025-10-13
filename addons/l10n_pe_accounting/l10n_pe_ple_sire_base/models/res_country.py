# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class ResCountry(models.Model):
	_inherit = 'res.country'

	code_sunat = fields.Char(string="Código SUNAT",size=4)

	_sql_constraints = [
		('Código_Sunat','UNIQUE (code_sunat)','El código de país debe ser único !')]