from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError, RedirectWarning
import re
import logging


_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = "account.move"


    @api.onchange(
        'partner_id',
        'currency_id',
        'l10n_latam_document_type_id')
    def _onchange_property_account_receivable_payable_me(self):
        for rec in self:
            if rec.move_type in ['out_invoice','out_refund','in_invoice','in_refund']:
                aml_term_line_ids = rec.line_ids.filtered(lambda line: line.display_type == 'payment_term')
                if aml_term_line_ids:
                    for aml in aml_term_line_ids:
                        aml._compute_account_id()