from odoo import models, fields, api
from odoo.exceptions import UserError

class AccountJournal(models.Model):
    _inherit = 'account.journal'


    is_sale_note = fields.Boolean(string='Nota de Venta')
