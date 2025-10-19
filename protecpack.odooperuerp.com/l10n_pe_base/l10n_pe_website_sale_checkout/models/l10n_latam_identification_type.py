from odoo import _, api, fields, models

import logging
_logger = logging.getLogger(__name__)

class l10n_latam_identification_type(models.Model):
    _inherit = "l10n_latam.identification.type"

    available_in_website = fields.Boolean("Disponible en website")
    sequence = fields.Integer("Secuencia")
