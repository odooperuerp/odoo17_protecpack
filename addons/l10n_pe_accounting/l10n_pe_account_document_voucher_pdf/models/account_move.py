from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError,RedirectWarning
from datetime import datetime, timedelta
import re
import logging


_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = "account.move"


    def origin_documents(self):
        payment_ids = self.line_ids.mapped('payment_id')
        facturas = [(line.l10n_pe_prefix_code or '') + '-'*(len(line.l10n_pe_prefix_code or '')>0) + (line.l10n_pe_invoice_number or '') for line in self.line_ids]
        lista=[line.name for line in payment_ids]
        lista += list(set(facturas))
        origin=', '.join(lista)
        
        _logger.info('\n\nDOCUMENTOS DE ORIGEN\n\n')
        _logger.info(origin)

        return origin