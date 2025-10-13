# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError , ValidationError

class EconomicSectorSunat(models.Model):
	_name = 'economic.sector.sunat'
	_description = "Sector Económico según Sunat"
	_rec_name = "name"

	name=fields.Char(string="Nombre del Sector Económico")
	code=fields.Char(string="Código del sector Económico")

	_sql_constraints = [
		('code', 'unique(code)',  'Este código de Sector Económico ya existe, revise sus registros creados!'),
	]

