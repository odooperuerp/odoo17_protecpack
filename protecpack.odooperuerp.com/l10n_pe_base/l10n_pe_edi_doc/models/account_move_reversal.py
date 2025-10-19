from odoo import models, fields, api
from odoo.tools.translate import _

class AccountMoveReversal(models.TransientModel):
    _inherit = "account.move.reversal"
    
    @api.depends('move_ids', 'journal_id')
    def _compute_documents_info(self):
        super()._compute_documents_info()
        for record in self:
            move = record.move_ids[0]
            if move.l10n_latam_document_type_id and record.l10n_latam_use_documents:
                if move.l10n_latam_document_type_id.code == '03':
                    record.l10n_latam_available_document_type_ids = self.env['l10n_latam.document.type'].search([('code', '=', '07'),('doc_code_prefix','=','B')]).ids
                elif move.l10n_latam_document_type_id.code == '07':
                    record.l10n_latam_available_document_type_ids = self.env['l10n_latam.document.type'].search([('code', '=', '03'),('doc_code_prefix','=','F')]).ids
                    

    def _prepare_default_reversal(self, move):
        res = super()._prepare_default_reversal(move)
        res.update(l10n_pe_edi_cancel_reason = self.reason,            
                   ref = ('Reversión de: {} | {}'.format((move.name or "").replace(" ","") , self.reason) 
                        if self.reason else ('Reversión de: {}'.format((move.name or "").replace(" ","")))))
        
        return res    