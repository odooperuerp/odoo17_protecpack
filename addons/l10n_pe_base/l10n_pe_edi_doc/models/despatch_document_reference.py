from odoo import models, fields, api

class DespatchDocumentReference(models.Model):
    _name = "despatch.document.reference"
    _description = "Documentos de guía de remisión"
    
    move_id = fields.Many2one("account.move", required=True)
    
    l10n_pe_document_number = fields.Char("Número de documento", required=True)
    l10n_pe_document_code = fields.Selection(selection=[('09','Guía de Remisión Remitente'),('31','Guía de Remisión Transportista')], string="Código de documento", required=True)
    
