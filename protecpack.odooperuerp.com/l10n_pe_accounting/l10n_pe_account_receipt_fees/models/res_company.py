# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    receipt_of_fees_account_id = fields.Many2one("account.account",
    	string="Cuenta de Retención de 4ta Categoría")
