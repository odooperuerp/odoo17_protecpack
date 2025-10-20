from odoo import models, api, fields, tools, _
from odoo.exceptions import UserError, ValidationError

import logging
_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = "account.move"

    refund_moves_count = fields.Integer("Número de Notas de crédito", compute="_compute_refund_related_moves")
    is_refunded = fields.Boolean(compute="_compute_refund_related_moves")


    def _compute_refund_related_moves(self):
        for move in self:
            move.refund_moves_count = len(move.reversal_move_id)
            move.is_refunded = move.refund_moves_count > 0


    def action_view_refund_moves(self):
        return {
            "name": "Notas de crédito",
            "view_mode": "tree,form",
            "res_model": "account.move",
            "type": "ir.actions.act_window",
            "domain": [("id", "in", self.mapped("reversal_move_id").ids)],
        }


    def action_view_invoice_moves(self):
        return {
            "name": "Facturas",
            "view_mode": "tree,form",
            "res_model": "account.move",
            "type": "ir.actions.act_window",
            "domain": [("id", "in", self.mapped("reversed_entry_id").ids)],
        }