from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError, RedirectWarning
import re
import logging
_logger = logging.getLogger(__name__)

class SetupBarBankConfigWizard(models.TransientModel):
    _inherit = 'account.setup.bank.manual.config'


    def set_linked_journal_id(self):

        super(SetupBarBankConfigWizard, self).set_linked_journal_id()

        for record in self:

            if record.linked_journal_id and record.linked_journal_id.inbound_payment_method_line_ids:

                account_id = record.linked_journal_id.default_account_id or False
                
                record.linked_journal_id.inbound_payment_method_line_ids[0].\
                    write({'payment_account_id':account_id and account_id.id or False})


            if record.linked_journal_id and record.linked_journal_id.outbound_payment_method_line_ids:

                account_id = record.linked_journal_id.default_account_id or False
                record.linked_journal_id.outbound_payment_method_line_ids[0].\
                    write({'payment_account_id':account_id and account_id.id or False})