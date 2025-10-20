from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError,RedirectWarning
from datetime import datetime, timedelta
import re
import logging


_logger = logging.getLogger(__name__)

class AccountJournal(models.Model):
    _inherit = "account.journal"

    allow_edit_prefix_code_invoice_number = fields.Boolean(string="Permitir editar Serie y Correlativo",
        default=False)