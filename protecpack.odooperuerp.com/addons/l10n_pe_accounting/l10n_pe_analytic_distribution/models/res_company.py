# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    distribution_journal_id = fields.Many2one("account.journal",
        string="Diario para la Generación de Asientos Destino")
