# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
#import logging
#_logger=logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = "account.move"

    is_receipt_of_fees_flag = fields.Boolean(string="Es Recibo por Honorario",
        compute="compute_campo_is_receipt_of_fees_flag",store=True)
    #### CAMPOS EXTRA DE RXH ################
    retencion_4ta = fields.Float(string="Monto Retención 4ta",
        compute="compute_campo_retencion_4ta",store=True)


    @api.depends(
        'l10n_latam_document_type_id',
        'l10n_latam_document_type_id.code')
    def compute_campo_is_receipt_of_fees_flag(self):
        for rec in self:
            rec.is_receipt_of_fees_flag = False

            if rec.l10n_latam_document_type_id and rec.l10n_latam_document_type_id.code == '02':
                rec.is_receipt_of_fees_flag = True



    @api.depends(
        'l10n_latam_document_type_id',
        'l10n_latam_document_type_id.code',
        'company_id',
        'company_id.receipt_of_fees_account_id',
        'line_ids',
        'line_ids.account_id',
        'line_ids.balance',
        'is_receipt_of_fees_flag')
    def compute_campo_retencion_4ta(self):
        for rec in self:
            rec.retencion_4ta = 0.00

            if rec.line_ids and rec.company_id.receipt_of_fees_account_id and rec.is_receipt_of_fees_flag:
                move_line_retencion_id = rec.line_ids.filtered(lambda e:e.account_id == rec.company_id.receipt_of_fees_account_id)
                if move_line_retencion_id:
                    rec.retencion_4ta = abs(move_line_retencion_id[0].balance)
