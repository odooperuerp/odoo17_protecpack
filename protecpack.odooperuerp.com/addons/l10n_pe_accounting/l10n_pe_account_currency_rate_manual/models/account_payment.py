# -*- encoding: utf-8 -*-
from odoo import api, fields, models, _


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    currency_tc= fields.Float(string='Tipo de Cambio',digits=(1,8))

    is_special_tc = fields.Boolean(string='Activar Tipo Cambio Manual',
        help='Activar el Tipo de Cambio personalizado por el usuario',default=False)

    is_payment_in_me = fields.Boolean(string="Es Documento en Moneda Extranjera",
        compute="compute_is_payment_in_me",store=True)

    ####################################################################################

    @api.depends(
        'company_id',
        'currency_id')
    def compute_is_payment_in_me(self):
        for rec in self:
            rec.is_payment_in_me = False
            if rec.currency_id and rec.currency_id != rec.company_id.currency_id:
                rec.is_payment_in_me = True
            else:
                rec.is_payment_in_me = False



    @api.onchange(
        'date',
        'currency_id',
        'partner_id',
        'journal_id')
    def get_currency_tc(self):

        for rec in self:    
            v_rate = 1

            if rec.currency_id and rec.currency_id != rec.company_id.currency_id:

                pay_date = datetime.now(tz=timezone("America/Lima")) if not rec.date else rec.date

                currency_company = self.env.company.currency_id
                rate = currency_company._convert(1, rec.currency_id , self.env.company, pay_date, round=False)

                v_rate = round(1/(rate if rate > 0 else 1), 4)

            rec.currency_tc = v_rate


    ############################################################################################
    def _prepare_move_line_default_vals(self, write_off_line_vals=None, force_balance=None):
        
        result = super(AccountPayment,self)._prepare_move_line_default_vals(write_off_line_vals,force_balance)

        self.ensure_one()
        write_off_line_vals = write_off_line_vals or {}

        if not self.outstanding_account_id:
            raise UserError(_(
                "You can't create a new payment without an outstanding payments/receipts account set either on the company or the %s payment method in the %s journal.",
                self.payment_method_line_id.name, self.journal_id.display_name))

        # Compute amounts.
        write_off_line_vals_list = write_off_line_vals or []
        write_off_amount_currency = sum(x['amount_currency'] for x in write_off_line_vals_list)
        write_off_balance = sum(x['balance'] for x in write_off_line_vals_list)

        if self.payment_type == 'inbound':
            # Receive money.
            liquidity_amount_currency = self.amount
        elif self.payment_type == 'outbound':
            # Send money.
            liquidity_amount_currency = -self.amount
        else:
            liquidity_amount_currency = 0.0

        if not write_off_line_vals and force_balance is not None:
            sign = 1 if liquidity_amount_currency > 0 else -1
            liquidity_balance = sign * abs(force_balance)

        else:

            if self.is_special_tc and self.currency_tc > 0 and self.is_payment_in_me:

                liquidity_balance = self.company_id.currency_id.with_context(default_pen_rate=self.currency_tc)._convert(
                    liquidity_amount_currency,
                    self.currency_id,
                    self.company_id,
                    self.date)

            else:
                liquidity_balance = self.currency_id._convert(
                    liquidity_amount_currency,
                    self.company_id.currency_id,
                    self.company_id,
                    self.date,
                )

        counterpart_amount_currency = -liquidity_amount_currency - write_off_amount_currency
        counterpart_balance = -liquidity_balance - write_off_balance
        currency_id = self.currency_id.id

        # Compute a default label to set on the journal items.
        liquidity_line_name = ''.join(x[1] for x in self._get_liquidity_aml_display_name_list())
        counterpart_line_name = ''.join(x[1] for x in self._get_counterpart_aml_display_name_list())

        line_vals_list = [
            # Liquidity line.
            {
                'name': liquidity_line_name,
                'date_maturity': self.date,
                'amount_currency': liquidity_amount_currency,
                'currency_id': currency_id,
                'debit': liquidity_balance if liquidity_balance > 0.0 else 0.0,
                'credit': -liquidity_balance if liquidity_balance < 0.0 else 0.0,
                'partner_id': self.partner_id.id,
                'account_id': self.outstanding_account_id.id,
            },
            # Receivable / Payable.
            {
                'name': counterpart_line_name,
                'date_maturity': self.date,
                'amount_currency': counterpart_amount_currency,
                'currency_id': currency_id,
                'debit': counterpart_balance if counterpart_balance > 0.0 else 0.0,
                'credit': -counterpart_balance if counterpart_balance < 0.0 else 0.0,
                'partner_id': self.partner_id.id,
                'account_id': self.destination_account_id.id,
            },
        ]
        return line_vals_list + write_off_line_vals_list