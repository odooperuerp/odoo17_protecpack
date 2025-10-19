from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError, RedirectWarning
import re
import logging


_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = "account.move"


    @api.onchange('partner_id')
    def _onchange_partner_id(self):

        res = super(AccountMove,self)._onchange_partner_id()

        warning = {}

        rec_account = False
        pay_account = False

        if self.partner_id:
            if self.currency_id and self.currency_id != self.company_id.currency_id:
                if self.l10n_latam_document_type_id.code == '02':
                    pay_account = self.partner_id.property_account_payable_me_fees_id    
                else:
                    rec_account = self.partner_id.property_account_receivable_me_id
                    pay_account = self.partner_id.property_account_payable_me_id
            else:
                if self.l10n_latam_document_type_id.code=='02':
                    pay_account = self.partner_id.property_account_payable_fees_id
                else:
                    rec_account = self.partner_id.property_account_receivable_id
                    pay_account = self.partner_id.property_account_payable_id

                    
            if not rec_account and not pay_account:
                action = self.env.ref('account.action_account_config')
                msg = _('Cannot find a chart of accounts for this company, You should configure it. \nPlease go to Account Configuration.')
                raise RedirectWarning(msg, action.id, _('Go to the configuration panel'))
            p = self.partner_id
            if p.invoice_warn == 'no-message' and p.parent_id:
                p = p.parent_id
            if p.invoice_warn and p.invoice_warn != 'no-message':
                # Block if partner only has warning but parent company is blocked
                if p.invoice_warn != 'block' and p.parent_id and p.parent_id.invoice_warn == 'block':
                    p = p.parent_id
                warning = {
                    'title': _("Warning for %s", p.name),
                    'message': p.invoice_warn_msg
                }
                if p.invoice_warn == 'block':
                    self.partner_id = False
                return {'warning': warning}

        ###########################################################
        new_term_account = False

        if self.is_sale_document(include_receipts=True) and self.partner_id:

            if self.currency_id and self.currency_id != self.company_id.currency_id:
                new_term_account = self.partner_id.commercial_partner_id.property_account_receivable_me_id
            else:
                new_term_account = self.partner_id.commercial_partner_id.property_account_receivable_id

        elif self.is_purchase_document(include_receipts=True) and self.partner_id:

            if self.currency_id and self.currency_id != self.company_id.currency_id:
                if self.l10n_latam_document_type_id.code=='02':
                    new_term_account = self.partner_id.commercial_partner_id.property_account_payable_me_fees_id
                else:
                    new_term_account = self.partner_id.commercial_partner_id.property_account_payable_me_id
            else:
                if self.l10n_latam_document_type_id.code=='02':
                    new_term_account = self.partner_id.commercial_partner_id.property_account_payable_fees_id
                else:
                    new_term_account = self.partner_id.commercial_partner_id.property_account_payable_id


        if new_term_account:
            for line in self.line_ids:

                if new_term_account and line.account_id.account_type in ('asset_receivable', 'liability_payable'):
                    line.account_id = new_term_account

    ################################################################################################

    @api.onchange('journal_id','currency_id','l10n_latam_document_type_id')
    def _onchange_journal_id_currency_id(self):
        self._onchange_partner_id()

