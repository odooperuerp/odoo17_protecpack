# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError , ValidationError

class AccountMove(models.Model):
	_inherit = 'account.move'


	sunat_table_25_id = fields.Many2one('l10n.pe.catalogs.sunat',
		string="Convenios para evitar doble tributación",
		domain="[('associated_table_id.name','=','TABLA 25'),('active_concept','=',True)]")


	sunat_table_32_id = fields.Many2one('l10n.pe.catalogs.sunat',
		string="Modalidad Servicio prestado por el No Domiciliado",
		domain="[('associated_table_id.name','=','TABLA 32'),('active_concept','=',True)]")
