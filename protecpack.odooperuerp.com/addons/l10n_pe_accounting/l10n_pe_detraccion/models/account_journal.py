# -*- coding: utf-8 -*-
from odoo import models, fields, api

class AccountJournalPe(models.Model):
	_inherit = 'account.journal'

	detraction = fields.Boolean(string="Detraccion", default=False)

	detraction_account_id = fields.Many2one('account.account',
		string="Cuenta de Detracciones")