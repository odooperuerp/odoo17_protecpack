# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError , ValidationError

class GroupHeadingFinantialStatement(models.Model):
	_name = 'group.heading.financial.statement'
	_description = "Grupo de Rubros de Estados Financieros"
	_rec_name = "name"

	name=fields.Char(string="Nombre del Grupo de Rubros")
	code=fields.Char(string="Código del Grupo de Rubros")

	_sql_constraints = [
	 	('code', 'unique(code)',  'Este código para el Grupo de Rubros ya existe, revise sus registros creados!'),
	]