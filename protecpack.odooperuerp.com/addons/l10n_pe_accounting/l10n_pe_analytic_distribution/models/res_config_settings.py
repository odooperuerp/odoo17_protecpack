# -*- coding: utf-8 -*-
from odoo import api, fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    distribution_journal_id = fields.Many2one("account.journal",
    	string="Diario para la generación de Asientos Destino",
        related='company_id.distribution_journal_id',readonly=False)
