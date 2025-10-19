from odoo import models, fields, api

class StockPicking(models.Model):
    _inherit = "stock.picking"

    display_document_type = fields.Char(compute="_compute_display_document_type")

    def _compute_display_document_type(self):
        for record in self:
            display_document_type = ""
            if record.l10n_latam_document_number:
                display_document_type = "GUÍA DE REMISIÓN ELECTRÓNICA REMITENTE"
            else:
                if record.picking_type_id.code == "incomming":
                    display_document_type = "Recibo de Ingreso"
                if record.picking_type_id.code == "outgoing":
                    display_document_type = "Recibo de Salida"
                if record.picking_type_id.code == "interna":
                    display_document_type = "Transferencia Interna"

            record.display_document_type = display_document_type

    def _compute_display_name(self):
        for record in self:
            record.display_name = record.l10n_latam_document_number if record.l10n_latam_document_number else record.name