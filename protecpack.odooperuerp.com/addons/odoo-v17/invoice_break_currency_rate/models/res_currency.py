from odoo import api, models


class ResCurrency(models.Model):
    _inherit = 'res.currency'

    def _get_query_rates(self):
        query = """SELECT c.id,
                        COALESCE((SELECT r.rate FROM res_currency_rate r
                                WHERE r.currency_id = c.id AND r.name <= %s
                                    AND (r.company_id IS NULL OR r.company_id = %s)
                            ORDER BY r.company_id, r.name DESC, r.write_date DESC
                                LIMIT 1), 1.0) AS rate
                FROM res_currency c
                WHERE c.id IN %s"""
        return query

    def _get_rates(self, company, date):
        if not self.ids:
            return {}
        self.env['res.currency.rate'].flush_model(['rate', 'currency_id', 'company_id', 'name'])
        query = self._get_query_rates()
        self._cr.execute(query, (date, company.root_id.id, tuple(self.ids)))
        currency_rates = dict(self._cr.fetchall())
        return currency_rates
