from odoo import models,fields,api

class BaseDocumentLayout(models.TransientModel):
    _inherit = "base.document.layout"

    street = fields.Char('Dirección', related='company_id.street') 