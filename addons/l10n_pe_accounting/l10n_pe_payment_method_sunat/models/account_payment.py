from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError, RedirectWarning
import re
import logging
_logger = logging.getLogger(__name__)

class AccountPayment(models.Model):
    _inherit = "account.payment"

    sunat_table_01_id = fields.Many2one('l10n.pe.catalogs.sunat',string="Tipo de Medio de Pago SUNAT",
        domain="[('associated_table_id.name','=','TABLA 1'),('active_concept','=',True)]")