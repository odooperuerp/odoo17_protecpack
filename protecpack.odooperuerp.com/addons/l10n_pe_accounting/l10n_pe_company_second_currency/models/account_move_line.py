from odoo import fields, models, api, _

import logging
_logger = logging.getLogger(__name__)

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    second_currency_id = fields.Many2one('res.currency', string="Segunda Moneda",
        related="company_id.second_currency_id", store=True)

    second_currency_rate = fields.Float(string="T.C",digits=(16,12),compute="compute_campo_second_currency_rate",store=True)

    debit_currency = fields.Monetary(currency_field="second_currency_id",string="Débito ME",
        compute="compute_campo_fields_second_currency",store=True,default=0.00,digits=(16,2))
    
    credit_currency = fields.Monetary(currency_field="second_currency_id",string="Crédito ME",
        compute="compute_campo_fields_second_currency",store=True,default=0.00,digits=(16,2))

    balance_currency = fields.Monetary(currency_field="second_currency_id",string="Monto ME",
        compute="compute_campo_fields_second_currency",store=True,default=0.00,digits=(16,2))

    ###################################################################################################################################

    def _get_date_emission(self):
        date = self.invoice_date or self.date or fields.Date.today() or False
        return date


    @api.depends(
        'company_id',
        'currency_id',
        'second_currency_id',
        'amount_currency',
        'balance',
        'invoice_date',
        'date')
    def compute_campo_second_currency_rate(self):
        for rec in self:
            if rec.currency_id == rec.second_currency_id and rec.amount_currency:
                rec.second_currency_rate = abs(rec.balance/rec.amount_currency)
            else:
                date_tc = rec._get_date_emission()
                rec.second_currency_rate = rec.second_currency_id.with_context(date=date_tc).inverse_rate


    @api.depends(
        'company_id',
        'currency_id',
        'second_currency_id',
        'amount_currency',
        'balance',
        'invoice_date',
        'date')
    def compute_campo_fields_second_currency(self):
        for rec in self:
            if rec.currency_id == rec.second_currency_id and rec.amount_currency:
                rec.debit_currency = rec.amount_currency if rec.amount_currency >= 0.00 else 0.00
                rec.credit_currency = abs(rec.amount_currency) if rec.amount_currency < 0.00 else 0.00
                rec.balance_currency = rec.debit_currency - rec.credit_currency
            else:
                date_tc = rec._get_date_emission()
                amount_aux = rec.company_id.currency_id._convert(rec.balance, rec.second_currency_id, rec.company_id, date_tc)

                rec.debit_currency = amount_aux if amount_aux >= 0.00 else 0.00
                rec.credit_currency = abs(amount_aux) if amount_aux < 0.00 else 0.00
                rec.balance_currency = amount_aux