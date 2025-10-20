import re

from odoo import models
from odoo.tools import html2plaintext, cleanup_xml_node

class AccountEdiXmlUBLPE(models.AbstractModel):
    _inherit = 'account.edi.xml.ubl_pe'
    
    def _get_document_allowance_charge_vals_list(self, invoice):
        vals_list = super(AccountEdiXmlUBLPE, self)._get_document_allowance_charge_vals_list(invoice)
        if invoice.is_retention:
            vals_list.append({
                'charge_indicator': 'false',
                'allowance_charge_reason_code': '62',
                'base_amount': abs(invoice.amount_total),
                'amount': abs(invoice.retention_amount),
                'multiplier_factor':invoice.retention_percentaje/100,
                'currency_dp': 2,
                'currency_name': invoice.currency_id.name,
            })

        return vals_list