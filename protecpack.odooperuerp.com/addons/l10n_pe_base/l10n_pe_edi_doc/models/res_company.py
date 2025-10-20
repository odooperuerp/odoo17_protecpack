from odoo import api, fields, models

class ResCompany(models.Model):
    _inherit = "res.company"
    
    l10n_pe_trade_name = fields.Char(string="Nombre comercial", help="Nombre comercial de la empresa.")