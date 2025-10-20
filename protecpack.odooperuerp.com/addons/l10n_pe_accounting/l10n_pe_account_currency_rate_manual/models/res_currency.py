# -*- encoding: utf-8 -*-
from odoo import api, fields, models, tools, _


class ResCurrency(models.Model):
    _inherit = 'res.currency'


    @api.model
    def _get_conversion_rate(self, from_currency, to_currency, company=None, date=None):
        result = super(ResCurrency,self)._get_conversion_rate(from_currency,to_currency,company,date)

        if self.env.context.get('default_pen_rate'):
            result = (self.env.context.get('default_pen_rate') or 1.00)

        return result



    """@api.model
    def _get_conversion_rate(self, from_currency, to_currency, company=None, date=None):
        if from_currency == to_currency:
            return 1
        company = company or self.env.company
        date = date or fields.Date.context_today(self)
        return from_currency.with_company(company).with_context(to_currency=to_currency.id, date=str(date)).inverse_rate"""