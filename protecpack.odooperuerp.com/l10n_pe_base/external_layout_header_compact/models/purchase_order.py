from odoo import models, fields, api

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    display_document_type = fields.Char(compute="_compute_display_document_type")

    def _compute_display_document_type(self):
        for record in self:
            STATES = {
                "draft": "Solicitud de cotización de compra",
                "sent": "Solicitud de cotización de compra",
                "to approve":"Solicitud de cotización de compra",
                "purchase":"Orden de compra",
                "done":"Orden de compra",
                "cancel": "Orden de compra cancelada",
            }
            record.display_document_type = STATES[record.state]