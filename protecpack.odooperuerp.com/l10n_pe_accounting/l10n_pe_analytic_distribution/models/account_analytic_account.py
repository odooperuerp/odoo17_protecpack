# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.osv import expression


class AccountAnalyticAccount(models.Model):
	_inherit = 'account.analytic.account'

	account_destino_id = fields.Many2one('account.account', string="Cuenta de Distribucion", required=False)
	account_contra_id = fields.Many2one('account.account', string="Cuenta Contrapartida")