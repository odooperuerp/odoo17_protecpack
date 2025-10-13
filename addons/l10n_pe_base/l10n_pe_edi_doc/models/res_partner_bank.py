from odoo import models, fields, api

class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'
    
    cci_number = fields.Char(string='Número de cuenta interbancaria (CCI)')