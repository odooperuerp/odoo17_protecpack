from odoo import fields, models, api, _

class AccountMove(models.Model):
    _inherit = 'account.move'

    #extend_currency = fields.Boolean(string="Mostrar segunda Moneda",
    #    related="company_id.extend_currency",store=True)

    second_currency_id = fields.Many2one('res.currency', string='Segunda Moneda',
        related="company_id.second_currency_id",store=True)