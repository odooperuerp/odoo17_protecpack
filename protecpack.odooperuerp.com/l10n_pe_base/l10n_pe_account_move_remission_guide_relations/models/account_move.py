from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError,RedirectWarning
from datetime import datetime, timedelta
import re
import logging

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'

    remission_guide_ids = fields.Many2many('stock.picking',string="Movimientos Stock Asociados")

    correlative_remission_guides = fields.Char(string="Guías Remisión Asociadas",
        compute="compute_field_correlative_remission_guides",store=True)


    def search_and_set_stock_picking(self):
        for rec in self:
            if rec.move_type in ['out_invoice','out_refund'] and not rec.remission_guide_ids:
                query = """
                    select 
                        sp.id as picking_id
                        from
                        account_move_line as aml
                        join account_move am on am.id = aml.move_id 
                        join sale_order_line_invoice_rel solir on solir.invoice_line_id = aml.id 
                        join sale_order_line sol on sol.id = solir.order_line_id 
                        join stock_move sm on sm.sale_line_id = sol.id 
                        join stock_picking sp on sp.id = sm.picking_id 
                        where sp.state = 'done' and am.move_type in ('out_invoice','out_refund') and am.id=%s """%(rec.id)

                self.env.cr.execute(query)
                records = self.env.cr.dictfetchall()
                if records:
                    rec.remission_guide_ids = [i['picking_id'] for i in records if i['picking_id']]


    @api.depends(
        'remission_guide_ids')
    def compute_field_correlative_remission_guides(self):
        for rec in self:
            rec.correlative_remission_guides = ''
            if rec.remission_guide_ids:
                array_guides = list(rec.remission_guide_ids.filtered(lambda t:t.l10n_latam_document_number).\
                    mapped('l10n_latam_document_number'))

                if array_guides:
                    str_array_guides = ', '.join(array_guides)
                    rec.correlative_remission_guides = str_array_guides


    #####################################################################################

    @api.model
    def create(self, vals):
        res = super().create(vals)

        if res.move_type in ['out_invoice','out_refund']:

            res.search_and_set_stock_picking()
        return res