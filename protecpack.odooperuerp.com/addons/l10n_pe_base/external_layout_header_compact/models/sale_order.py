from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = "sale.order"

    display_document_type = fields.Char(compute="_compute_display_document_type")
    is_sale_note = fields.Boolean(string="Nota de venta", default=False)

    def _compute_display_document_type(self):
        for record in self:
            STATES = {
                "draft": "Cotización",
                "sent": "Cotización",
                "to_approve":"Cotización",
                "sale": "Orden de Venta",
                "cancel": "Orden de Venta Cancelada",
            }
            record.display_document_type = STATES.get(record.state,"Cotización")

    def data_report(self):
        return {
            "salesman_name": self.user_id.name or "" if self.user_id else "",
            "salesman_email": self.user_id.email if self.user_id else "",
            "salesman_mobile": self.user_id.mobile if self.user_id else "",
        }

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"
    
    image_128 = fields.Binary(string="Imagen",related='product_id.image_128',store=False)
    image_256 = fields.Binary(string="Imagen",related='product_id.image_256',store=False)