# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError , ValidationError

class AccountJournal(models.Model):
	_inherit = 'account.journal'

	is_ple_caja_bancos = fields.Boolean(string="Habilitado para Libro PLE-Caja-Bancos")

	@api.onchange('type')
	def onchange_is_ple_caja_bancos(self):
		for rec in self:
			if rec.type in ['cash','bank']:
				rec.is_ple_caja_bancos = True
			else:
				rec.is_ple_caja_bancos = False