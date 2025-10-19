# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import defaultdict

from odoo import models, api,fields
from odoo.tools import float_is_zero, float_compare
from odoo.tools.misc import formatLang


class AccountMove(models.Model):
    _inherit = "account.move"

    display_document_type = fields.Char(compute="_compute_display_document_type")
    is_sale_note = fields.Boolean(string="Nota de venta", related='journal_id.is_sale_note', store=True)
  
    def _compute_display_document_type(self):
        for record in self:
            if record.l10n_latam_document_type_id:
                record.display_document_type = record.l10n_latam_document_type_id.report_name
            elif record.is_sale_note and record.move_type == 'out_invoice':
                record.display_document_type = "Nota de Venta"
            elif record.is_sale_note and record.move_type == 'out_refund':
                record.display_document_type = "Devolución de Nota de Venta"
            elif record.journal_id.type == "purchase":
                record.display_document_type = record.journal_id.name
            else:
                record.display_document_type = "Asiento Contable"

    def _compute_display_name(self):
        for move in self:
            if move.move_type in ('out_invoice', 'in_invoice'):
                move.display_name = (move.name or "").replace(" ", "")
            elif move.move_type  == 'out_refund':
                move.display_name = (move.name or "").replace(" ", "")
            else:
                move.display_name = move._get_move_display_name(show_ref=True)

    @api.depends('move_type', 'payment_state', 'invoice_payment_term_id')
    def _compute_show_payment_term_details(self):
        super(AccountMove,self)._compute_show_payment_term_details()
        for invoice in self:
            if invoice.move_type in ('out_invoice', 'out_receipt', 'in_invoice', 'in_receipt') and invoice.payment_state in ('not_paid', 'partial'):
                    payment_term_lines = invoice.line_ids.filtered(lambda l: l.display_type == 'payment_term')
                    invoice.show_discount_details = invoice.invoice_payment_term_id.early_discount
                    invoice.show_payment_term_details = len(payment_term_lines) >= 1 or invoice.show_discount_details
            else:
                invoice.show_discount_details = False
                invoice.show_payment_term_details = False

    def data_report(self):
        return {
            "salesman_name": self.user_id.name or "" if self.user_id else "",
            "salesman_email": self.user_id.email if self.user_id else "",
            "salesman_mobile": self.user_id.mobile if self.user_id else "",
        }

                
class AccountMoveLine(models.Model):
    _inherit = "account.move.line"
    
    image_128 = fields.Binary(string="Imagen",related='product_id.image_128',store=False)
    image_256 = fields.Binary(string="Imagen",related='product_id.image_256',store=False)