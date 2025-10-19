from odoo import models, fields, api


class AccountTax(models.Model):
    _inherit = "account.tax"


    def compute_all(self, price_unit, currency=None, quantity=1.0, product=None, partner=None, is_refund=False,
                    handle_price_include=True, include_caba_tags=False, fixed_multiplicator=1):
        if self.filtered(lambda r: r.l10n_pe_edi_tax_code in ["9996"]):
            price_unit = 0

        return super(AccountTax, self).compute_all(price_unit, currency, quantity, product, partner, is_refund,
                                                   handle_price_include, include_caba_tags, fixed_multiplicator)
