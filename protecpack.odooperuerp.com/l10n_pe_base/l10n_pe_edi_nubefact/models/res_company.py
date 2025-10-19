from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    l10n_pe_edi_provider = fields.Selection(selection_add=[("nubefact", "Nubefact")])
