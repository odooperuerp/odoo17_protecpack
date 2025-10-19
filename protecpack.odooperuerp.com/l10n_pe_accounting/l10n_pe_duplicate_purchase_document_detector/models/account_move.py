from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError, RedirectWarning
import re
import logging


_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = "account.move"


    exist_in_invoice_document_duplicate = fields.Boolean(string="Existen Comprobantes de Compra Duplicados",
        compute="compute_campo_exist_in_invoice_document_duplicate",store=True)
    
    #exist_invoice_move_ids = fields.Many2many('account.move','exist_account_move_rel','move_id_1','move_id_2',
    #    string="Comprobante Registrado existente",
    #    compute="compute_campo_exist_in_invoice_document_duplicate",store=True)

    def get_exist_invoice_documents(self):
        for rec in self:

            if rec and rec.company_id and rec.l10n_pe_prefix_code and rec.l10n_pe_invoice_number and rec.move_type and \
                rec.move_type in ('in_invoice','in_refund') and rec.partner_id and rec.l10n_latam_document_type_id:
                
                query = """
                    select 
                    id
                    from account_move 
                    where 
                    move_type in ('in_invoice','in_refund') and 
                    l10n_pe_prefix_code='%s' and 
                    l10n_pe_invoice_number='%s' and 
                    l10n_latam_document_type_id = '%s' and 
                    partner_id = %s and 
                    company_id = %s 
                    """ % (rec.l10n_pe_prefix_code or '',
                        rec.l10n_pe_invoice_number or '',
                        rec.l10n_latam_document_type_id and rec.l10n_latam_document_type_id.id or False,
                        rec.partner_id and rec.partner_id.id or False,
                        rec.company_id and rec.company_id.id or False
                        )

                self.env.cr.execute(query)
                records = self.env.cr.dictfetchall()

                if records:
                    #move_id_id = records[0]['id']
                    move_id_id = [i['id'] for i in records if i['id'] != rec.id]

                    return move_id_id



    @api.depends(
        'l10n_pe_prefix_code',
        'l10n_pe_invoice_number',
        'partner_id',
        'move_type',
        'l10n_latam_document_type_id')
    def compute_campo_exist_in_invoice_document_duplicate(self):
        for rec in self:

            rec.exist_in_invoice_document_duplicate = False

            if rec and rec.l10n_pe_prefix_code and rec.l10n_pe_invoice_number and rec.move_type and rec.move_type in ('in_invoice','in_refund') \
                and rec.partner_id and rec.l10n_latam_document_type_id:
                
                query = """
                    select id 
                    from account_move 
                    where 
                    move_type in ('in_invoice','in_refund') and 
                    l10n_pe_prefix_code='%s' and 
                    l10n_pe_invoice_number='%s' and 
                    l10n_latam_document_type_id = '%s' and 
                    partner_id = %s and
                    company_id = %s 
                    """ % (rec.l10n_pe_prefix_code or '',
                        rec.l10n_pe_invoice_number or '',
                        rec.l10n_latam_document_type_id and rec.l10n_latam_document_type_id.id or False,
                        rec.partner_id and rec.partner_id.id or False,
                        rec.company_id and rec.company_id.id or False 
                        )

                self.env.cr.execute(query)
                records = self.env.cr.dictfetchall()

                if records:

                    move_id_id = [i['id'] for i in records if i['id'] != rec.id]

                    if move_id_id:
                        rec.exist_in_invoice_document_duplicate = True



    def open_exist_document_in_invoice(self):
        if self.exist_in_invoice_document_duplicate:
            move_ids = self.get_exist_invoice_documents()

            diccionario = {
                    'name': 'Documentos de Compra Duplicados Existentes',
                    'view_type': 'form',
                    'view_mode': 'tree,form',
                    'res_model': 'account.move',
                    'view_id': False,
                    'type': 'ir.actions.act_window',
                    'domain': [('id', 'in', move_ids or [])]
                }
            return diccionario