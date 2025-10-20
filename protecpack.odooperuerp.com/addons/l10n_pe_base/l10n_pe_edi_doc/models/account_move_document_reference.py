from odoo import models,api,fields

CATALOGO_12 = {
    "01": "Factura – emitida para corregir error en el RUC",
    "02": "Factura – emitida por anticipos",
    "03": "Boleta de Venta – emitida por anticipos",
    "04": "Ticket de Salida - ENAPU",
    "05": "Código SCOP",
    "06": "Factura electrónica remitente",
    "07": "Guia de remisión remitente",
    "08": "Declaración de salida del depósito franco",
    "09": "Declaración simplificada de importación",
    "10": "Liquidación de compra - emitida por anticipos",
    "99": "Otros"
}

class AccountMoveDocumentReference(models.Model):
    _name = "account.move.document.reference"
    _description = "Otros documentos relacionados con la operación"

    move_id = fields.Many2one("account.move", required=True)
    #l10n_pe_document_type_id = fields.Many2one("l10n_latam.document.type", string="Tipo de documento", required=True)
    l10n_pe_document_number = fields.Char("Número de documento", required=True)
    l10n_pe_document_code = fields.Selection(list(CATALOGO_12.items()), string="Código de documento", required=True)
    
