from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    currency_rates_autoupdate = fields.Boolean(
        string="Currency Rates Autoupdate",
        default=True,
        help="Enable automatic currency rates updates in this company.",
    )
