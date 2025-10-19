# -*- coding: utf-8 -*-
from odoo import api, fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    receipt_of_fees_account_id = fields.Many2one("account.account",
    	string="Cuenta de Retención de 4ta Categoría",
        related='company_id.receipt_of_fees_account_id',readonly=False)
