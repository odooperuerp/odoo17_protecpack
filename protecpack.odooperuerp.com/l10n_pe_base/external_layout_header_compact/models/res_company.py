from odoo import models, fields, api

DEFAULT_MESSAGE = """Representación impresa de la Facturación electrónica. Consulte el documento en https://consulta-validez. Autorizado mediante resolución SUNAT/2023"""


class ResCompany(models.Model):
    _inherit = 'res.company'

    l10n_pe_edi_qr_comment_report_invoice_document = fields.Text(string='Mensaje de representación impresa',
                                                                 default=DEFAULT_MESSAGE)
    
