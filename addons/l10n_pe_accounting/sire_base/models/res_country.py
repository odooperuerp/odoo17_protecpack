from odoo import models, fields, api, _
class ResCountry(models.Model):
	_inherit = 'res.country'

	code_sunat = fields.Char(string="Código Sunat" , size = 4)

	_sql_constraints = [
		('Código_Sunat','UNIQUE (code_sunat)','El código ingresado para este pais ya existe !')]