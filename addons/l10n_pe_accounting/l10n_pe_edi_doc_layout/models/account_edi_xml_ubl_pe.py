import re
import logging
from odoo import models

_logger = logging.getLogger(__name__)


class AccountEdiXmlUBLPE(models.AbstractModel):
    _inherit = 'account.edi.xml.ubl_pe'


    def _get_invoice_payment_terms_vals_list(self, invoice):

        vals = super(AccountEdiXmlUBLPE,self)._get_invoice_payment_terms_vals_list(invoice)
        # OVERRIDES account.edi.xml.ubl_21
        spot = invoice._l10n_pe_edi_get_spot()
        spot_amount = 0
        
        if invoice.is_retention:
            spot_amount = invoice.retention_amount 
        elif spot:
            spot_amount = spot['amount'] if invoice.currency_id == invoice.company_id.currency_id else spot['spot_amount']

        invoice_date_due_vals_list = []


        #for line in invoice.line_ids.filtered(lambda l: l.display_type == 'payment_term').sorted('date_maturity'):
        for rec_line in invoice.line_ids.filtered(lambda l: l.account_type == 'asset_receivable').sorted('date_maturity'):
            
            amount = rec_line.amount_currency
            
            if spot or invoice.is_retention:
                line_percentaje = abs(rec_line.amount_currency/invoice.amount_total)
                cuota_detraccion = line_percentaje*spot_amount
                amount -= cuota_detraccion
            
            invoice_date_due_vals_list.append({
                'currency_name': rec_line.currency_id.name,
                'currency_dp': rec_line.currency_id.decimal_places,
                'amount': amount,
                'date_maturity': rec_line.date_maturity,
            })

        if not (spot or invoice.is_retention):
            total_after_spot = abs(invoice.amount_total)
        else:
            total_after_spot = abs(invoice.amount_total) - spot_amount
        payment_means_id = invoice._l10n_pe_edi_get_payment_means()
        vals = []
        if spot:
            vals.append({
                'id': spot['id'],
                'currency_name': 'PEN',
                'currency_dp': 2,
                'payment_means_id': spot['payment_means_id'],
                'payment_percent': spot['payment_percent'],
                'amount': spot['amount'],
            })
        if invoice.move_type not in ('out_refund', 'in_refund'):
            if payment_means_id == 'Contado':
                vals.append({
                    'id': 'FormaPago',
                    'payment_means_id': payment_means_id,
                })
            else:
                vals.append({
                    'id': 'FormaPago',
                    'currency_name': invoice.currency_id.name,
                    'currency_dp': invoice.currency_id.decimal_places,
                    'payment_means_id': payment_means_id,
                    'amount': total_after_spot,
                })
                for i, due_vals in enumerate(invoice_date_due_vals_list):
                    vals.append({
                        'id': 'FormaPago',
                        'currency_name': due_vals['currency_name'],
                        'currency_dp': due_vals['currency_dp'],
                        'payment_means_id': 'Cuota' + '{0:03d}'.format(i + 1),
                        'amount': due_vals['amount'],
                        'payment_due_date': due_vals['date_maturity'],
                    })

        return vals