# -*- coding: utf-8 -*-
from collections import defaultdict

from odoo import Command, models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools import frozendict
import logging

_logger = logging.getLogger(__name__)


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    currency_tc= fields.Float(string='Tipo de Cambio',digits=(1,8))

    is_special_tc = fields.Boolean(string='Activar Tipo Cambio Manual',
        help='Activar el Tipo de Cambio personalizado por el usuario',default=False)

    is_payment_in_me = fields.Boolean(string="Es Documento en Moneda Extranjera",
        compute="compute_is_payment_in_me",store=True)

    amount_in_company_currency = fields.Monetary(currency_field='company_currency_id',string="Monto en MN Calculado",
        compute='compute_campo_amount_in_company_currency',store=True)

    manual_amount_in_company_currency = fields.Monetary(currency_field='company_currency_id',string="Monto en MN Manual")
    
    is_manual_amount_in_company_currency = fields.Boolean(string="Activar Monto en MN Manual",default=False)

    is_tc_same_account_invoice = fields.Boolean(string="Usar TC Fecha Emisión Documento",default=False)

    operation_number = fields.Char(string="Número de Operación")

    sunat_table_01_id = fields.Many2one('l10n.pe.catalogs.sunat',string="Tipo de Medio de Pago SUNAT",
        domain="[('associated_table_id.name','=','TABLA 1'),('active_concept','=',True)]")


    analytic_distribution = fields.Json('Distribución Analítica',
        compute="_compute_analytic_distribution", store=True, copy=True, readonly=False,
        precompute=True)

    analytic_distribution_search = fields.Json(store=False,search="_search_analytic_distribution")

    analytic_precision = fields.Integer(store=False,
        default=lambda self: self.env['decimal.precision'].precision_get("Percentage Analytic"))

    ################################################################################################

    def _compute_analytic_distribution(self):
        pass


    def _search_analytic_distribution(self, operator, value):
        if operator not in ['=', '!=', 'ilike', 'not ilike'] or not isinstance(value, (str, bool)):
            raise UserError(_('Operation not supported'))

        operator_name_search = '=' if operator in ('=', '!=') else 'ilike'
        account_ids = list(self.env['account.analytic.account']._name_search(name=value, operator=operator_name_search))

        query = f"""
            SELECT id
            FROM {self._table}
            WHERE analytic_distribution ?| array[%s]
            """
        operator_inselect = 'inselect' if operator in ('=', 'ilike') else 'not inselect'
        return [('id', operator_inselect, (query, [[str(account_id) for account_id in account_ids]]))]
    ################################################################################################


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
        'payment_date',
        'currency_id',
        'partner_id',
        'journal_id')
    def get_currency_tc(self):

        for rec in self:    
            v_rate = 1

            if rec.currency_id and rec.currency_id != rec.company_id.currency_id:

                pay_date = datetime.now(tz=timezone("America/Lima")) if not rec.payment_date else rec.payment_date

                currency_company = self.env.company.currency_id
                rate = currency_company._convert(1, rec.currency_id , self.env.company, pay_date, round=False)

                v_rate = round(1/(rate if rate > 0 else 1), 4)

            rec.currency_tc = v_rate



    @api.depends(
        'company_id',
        'currency_id',
        'amount',
        'payment_date',
        'currency_tc',
        'is_special_tc',
        'is_payment_in_me')
    def compute_campo_amount_in_company_currency(self):
        for rec in self:

            rec.amount_in_company_currency = 0.00

            if rec.is_payment_in_me:

                rec.amount_in_company_currency = self.currency_id.with_context(default_pen_rate=rec.currency_tc)._convert(
                    rec.amount,
                    rec.company_currency_id,
                    date=rec.payment_date)



    @api.onchange(
        'is_tc_same_account_invoice',
        'line_ids',
        'currency_id',
        'is_payment_in_me')
    def onchange_is_tc_same_account_invoice(self):
        for rec in self:

            if rec.is_payment_in_me and rec.line_ids and rec.is_tc_same_account_invoice:
                rec.currency_tc = rec.line_ids[0].move_id.currency_tc
                rec.is_manual_amount_in_company_currency = False



    @api.onchange(
    	'is_manual_amount_in_company_currency',
        'currency_id',
        'amount',
        'manual_amount_in_company_currency')
    def onchange_manual_amount_in_company_currency(self):
        for rec in self:

            if rec.is_payment_in_me and rec.is_manual_amount_in_company_currency:
                rec.currency_tc = round(rec.manual_amount_in_company_currency/(rec.amount),6)
                rec.is_tc_same_account_invoice = False


    ############################################################################################

    def _create_payment_vals_from_wizard(self, batch_result):
        result = super(AccountPaymentRegister,self)._create_payment_vals_from_wizard(batch_result)

        payment_vals = {
            'date': self.payment_date,
            'amount': self.amount,
            'payment_type': self.payment_type,
            'partner_type': self.partner_type,
            'ref': self.communication,
            'journal_id': self.journal_id.id,
            'company_id': self.company_id.id,
            'currency_id': self.currency_id.id,
            'partner_id': self.partner_id.id,
            'partner_bank_id': self.partner_bank_id.id,
            'payment_method_line_id': self.payment_method_line_id.id,
            'destination_account_id': self.line_ids[0].account_id.id,
            'write_off_line_vals': [],
            'operation_number':self.operation_number or '',
            'sunat_table_01_id':self.sunat_table_01_id and self.sunat_table_01_id.id or False,
        }

        #################################################################

        if self.is_special_tc and self.currency_tc > 0 and self.is_payment_in_me:

            payment_vals['currency_tc'] = self.currency_tc
            payment_vals['is_special_tc'] = self.is_special_tc
            payment_vals['is_payment_in_me'] = self.is_payment_in_me
                        
        #################################################################


        if self.payment_difference_handling == 'reconcile':

            if self.early_payment_discount_mode:
                epd_aml_values_list = []

                for aml in batch_result['lines']:
                    if aml.move_id._is_eligible_for_early_payment_discount(self.currency_id, self.payment_date):
    
                        balance = 0.00
                        if self.is_special_tc and self.currency_tc > 0 and self.is_payment_in_me:

                            #balance = self.company_id.currency_id.with_context(default_pen_rate=self.currency_tc)._convert(
                            #    liquidity_amount_currency,self.currency_id,self.company_id,self.date)

                            balance = aml.currency_id.with_context(default_pen_rate=self.currency_tc)._convert(
                                -aml.amount_residual_currency,
                                aml.company_currency_id,
                                date=self.payment_date)


                        else:
                            balance = aml.currency_id._convert(
                                -aml.amount_residual_currency,
                                aml.company_currency_id,
                                date=self.payment_date)
                        
                        #################################################################

                        epd_aml_values_list.append({
                            'aml': aml,
                            'amount_currency': -aml.amount_residual_currency,
                            'balance': balance,
                        })

                open_amount_currency = self.payment_difference * (-1 if self.payment_type == 'outbound' else 1)
                open_balance = self.currency_id._convert(open_amount_currency, self.company_id.currency_id, self.company_id, self.payment_date)
                early_payment_values = self.env['account.move']._get_invoice_counterpart_amls_for_early_payment_discount(epd_aml_values_list, open_balance)
                for aml_values_list in early_payment_values.values():
                    payment_vals['write_off_line_vals'] += aml_values_list

            elif not self.currency_id.is_zero(self.payment_difference):

                if self.writeoff_is_exchange_account:
                    # Force the rate when computing the 'balance' only when the payment has a foreign currency.
                    # If not, the rate is forced during the reconciliation to put the difference directly on the
                    # exchange difference.
                    if self.currency_id != self.company_currency_id:
                        payment_vals['force_balance'] = sum(batch_result['lines'].mapped('amount_residual'))
                else:
                    if self.payment_type == 'inbound':
                        # Receive money.
                        write_off_amount_currency = self.payment_difference
                    else:  # if self.payment_type == 'outbound':
                        # Send money.
                        write_off_amount_currency = -self.payment_difference

                    #################################################################
                    balance = 0.00
                    if self.is_special_tc and self.currency_tc > 0 and self.is_payment_in_me:

                        #balance = self.company_id.currency_id.with_context(default_pen_rate=self.currency_tc)._convert(
                        #    liquidity_amount_currency,self.currency_id,self.company_id,self.date)

                        balance = self.currency_id.with_context(default_pen_rate=self.currency_tc)._convert(
                            write_off_amount_currency,
                            self.company_id.currency_id,
                            self.company_id,
                            self.payment_date)

                    else:
                        balance = self.currency_id._convert(
                            write_off_amount_currency,
                            self.company_id.currency_id,
                            self.company_id,
                            self.payment_date)
                        
                    #################################################################

                    payment_vals['write_off_line_vals'].append({
                        'name': self.writeoff_label,
                        'account_id': self.writeoff_account_id.id,
                        'partner_id': self.partner_id.id,
                        'currency_id': self.currency_id.id,
                        'amount_currency': write_off_amount_currency,
                        'balance': balance,
                        'analytic_distribution':self.analytic_distribution or False,
                    })

        return payment_vals