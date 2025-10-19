from odoo import models
from odoo.addons.base.models import res_currency


class CurrencyRate(models.Model):
    _inherit = 'res.currency.rate'
    _order = 'name desc, write_date desc'

    res_currency.CurrencyRate._sql_constraints = [
        ('unique_name_per_day', 'CHECK (1=1)', 'Only one currency rate per day allowed!'),
        ('currency_rate_check', 'CHECK (rate>0)', 'The currency rate must be strictly positive.'),
    ]
