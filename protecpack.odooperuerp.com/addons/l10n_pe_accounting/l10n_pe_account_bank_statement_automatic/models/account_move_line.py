from odoo import fields,models,api
import calendar
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError , ValidationError
import logging

_logger = logging.getLogger(__name__)

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"


    def action_account_bank_statement_automatic(self):
        action = self.env['ir.actions.act_window']._for_xml_id(
            'l10n_pe_account_bank_statement_automatic.account_bank_statement_automatic_wizard_action')
        # Force the values of the move line in the context to avoid issues
        ctx = dict(self.env.context)
        ctx.pop('active_id', None)
        ctx['active_ids'] = self.ids
        ctx['active_model'] = 'account.move.line'
        action['context'] = ctx
        return action