# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, fields, models


class PaymentToken(models.Model):
    _inherit = 'payment.token'

    niubiz_transaction_token = fields.Char(
        string="Niubiz Transaction Token",
        help="Token returned from the payment form. In the case of PagoEfectivo, this will be the CIP.")
    niubiz_expire_on = fields.Datetime(string="Niubiz Expire on")

    def _build_display_name(self, *args, max_length=34, should_pad=True, **kwargs):
        if self.provider_id.code != 'niubiz':
            return super()._build_display_name(*args, max_length, should_pad, **kwargs)
        return self.payment_details