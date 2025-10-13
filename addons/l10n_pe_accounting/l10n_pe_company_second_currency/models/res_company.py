from odoo import fields, models, api, _

class ResCompany(models.Model):
    _inherit = 'res.company'

    @api.model
    def _default_second_currency_id(self):
        currency = self.env['res.currency'].search([('name', '=', 'USD')], limit=1)
        return currency

    second_currency_id = fields.Many2one('res.currency', string='Segunda Moneda',
        default=_default_second_currency_id)
    #extend_currency = fields.Boolean(string="Mostrar segunda Moneda en movimientos",default=False)
