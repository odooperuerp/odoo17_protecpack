from odoo import models, api, fields, tools, _
from odoo.exceptions import UserError, ValidationError

import pytz
import logging
_logger = logging.getLogger(__name__)


class PosOrder(models.Model):
    _inherit = 'pos.order'

    document_invoice_type = fields.Integer(string="Tipo de documento")

     #CAMPO OBSOLETO
    l10n_pe_refund_reason = fields.Selection(
        selection=[
            ('01', 'Cancelación de la operación'),
            ('02', 'Cancelación por error en el RUC'),
            ('03', 'Corrección por error en la descripción'),
            ('04', 'Descuento global'),
            ('05', 'Descuento por item'),
            ('06', 'Reembolso total'),
            ('07', 'Reembolso por item'),
            ('08', 'Bonificación'),
            ('09', 'Disminución en el valor'),
            ('10', 'Otros conceptos'),
            ('11', 'Ajuste en operaciones de exportación'),
            ('12', 'Ajuste afectos al IVAP'),
            ('13', 'Ajuste en montos y/o fechas de pago'),
        ],
        string="Razón de nota de crédito (obsoleto)")
    
    l10n_pe_edi_refund_reason = fields.Selection(
        selection=[
            ('01', 'Cancelación de la operación'),
            ('02', 'Cancelación por error en el RUC'),
            ('03', 'Corrección por error en la descripción'),
            ('04', 'Descuento global'),
            ('05', 'Descuento por item'),
            ('06', 'Reembolso total'),
            ('07', 'Reembolso por item'),
            ('08', 'Bonificación'),
            ('09', 'Disminución en el valor'),
            ('10', 'Otros conceptos'),
            ('11', 'Ajuste en operaciones de exportación'),
            ('12', 'Ajuste afectos al IVAP'),
            ('13', 'Ajuste en montos y/o fechas de pago'),
        ],
        string="Razón de nota de crédito")
    
    l10n_pe_reason = fields.Char(string="Sustento")

    def _export_for_ui(self, order):
        result = super(PosOrder, self)._export_for_ui(order)
        result['document_invoice_type'] = order.document_invoice_type
        result['invoice_number'] = order.account_move.name
        result['l10n_pe_edi_refund_reason'] = order.l10n_pe_edi_refund_reason
        result['l10n_pe_reason'] = order.l10n_pe_reason
        result['comprobante_origen'] = order.account_move.reversed_entry_id.name
        result['fecha_origen'] = order.account_move.reversed_entry_id.invoice_date
        return result

    @api.model
    def _order_fields(self, ui_order):
        result = super(PosOrder, self)._order_fields(ui_order)   
        result.update({
            'document_invoice_type': ui_order.get("document_invoice_type",False),
            'l10n_pe_edi_refund_reason': ui_order.get("l10n_pe_edi_refund_reason",False),
            'l10n_pe_reason': ui_order.get("l10n_pe_reason",""),
        })
        return result


    def _prepare_invoice_vals(self):
        self.ensure_one()

        timezone = pytz.timezone(self._context.get('tz') or self.env.user.tz or 'UTC')
        invoice_date = fields.Datetime.now() if self.session_id.state == 'closed' else self.date_order
        pos_refunded_invoice_ids = []
        for orderline in self.lines:
            if orderline.refunded_orderline_id and orderline.refunded_orderline_id.order_id.account_move:
                pos_refunded_invoice_ids.append(orderline.refunded_orderline_id.order_id.account_move.id)
        
        #NOTE - Inicio de cambio para localización
        if self.amount_total >= 0:
            if self.document_invoice_type == 1:
                prefix = self.env["pos.config"].browse(self.config_id.id).pos_l10n_pe_seq_factura
                full_prefix = 'F %s-' % (prefix)
                number = self.env["pos.config"].browse(self.config_id.id).pos_l10n_pe_seqnum_factura
                l10n_latam_document_type_id = self.env.ref('l10n_pe.document_type01').id
            if self.document_invoice_type == 3:
                prefix = self.env["pos.config"].browse(self.config_id.id).pos_l10n_pe_seq_boleta
                full_prefix = 'B %s-' % (prefix)
                number = self.env["pos.config"].browse(self.config_id.id).pos_l10n_pe_seqnum_boleta
                l10n_latam_document_type_id = self.env.ref('l10n_pe.document_type02').id
        else:
            if self.document_invoice_type == 1:
                prefix = self.env["pos.config"].browse(self.config_id.id).pos_l10n_pe_seq_nota_factura
                full_prefix = 'F %s-' % (prefix)
                number = self.env["pos.config"].browse(self.config_id.id).pos_l10n_pe_seqnum_nota_factura
                l10n_latam_document_type_id = self.env.ref('l10n_pe.document_type07').id
            if self.document_invoice_type == 3:
                prefix = self.env["pos.config"].browse(self.config_id.id).pos_l10n_pe_seq_nota_boleta
                full_prefix = 'B %s-' % (prefix)
                number = self.env["pos.config"].browse(self.config_id.id).pos_l10n_pe_seqnum_nota_boleta
                l10n_latam_document_type_id = self.env.ref('l10n_pe.document_type07b').id

        # invoices_by_type = self.env['account.move'].search([('l10n_latam_document_type_id', '=', l10n_latam_document_type_id), 
        #                                                     ('state', '=', 'posted'), 
        #                                                     ('sequence_prefix', '=', full_prefix),
        #                                                     ('move_type','in',('out_invoice','out_refund'))],order="id desc", limit=1)

        # if invoices_by_type:
        #     number =invoices_by_type.sequence_number+1

        # name = "%s%s" % (full_prefix, str(number).zfill(8))

        vals = {
            # 'name': name,
            # 'sequence_prefix': full_prefix,
            # 'sequence_number': number,
            # 'l10n_latam_document_type_id': l10n_latam_document_type_id,
            'invoice_origin': self.name,
            'pos_refunded_invoice_ids': pos_refunded_invoice_ids,
            'journal_id': self.session_id.config_id.invoice_journal_id.id if self.document_invoice_type else self.session_id.config_id.nv_journal_id.id,
            'move_type': 'out_invoice' if self.amount_total >= 0 else 'out_refund',
            'ref': self.name,
            'partner_id': self.partner_id.id,
            'partner_bank_id': self._get_partner_bank_id(),
            'currency_id': self.currency_id.id,
            'invoice_user_id': self.user_id.id,
            'invoice_date': invoice_date.astimezone(timezone).date(),
            'fiscal_position_id': self.fiscal_position_id.id,
            'invoice_line_ids': self._prepare_invoice_lines(),
            'invoice_payment_term_id': self.partner_id.property_payment_term_id.id or False,
            'l10n_pe_edi_refund_reason': self.l10n_pe_edi_refund_reason,
            'l10n_pe_reason': self.l10n_pe_reason,
            'invoice_cash_rounding_id': self.config_id.rounding_method.id
            if self.config_id.cash_rounding and (not self.config_id.only_round_cash_method or any(p.payment_method_id.is_cash_count for p in self.payment_ids))
            else False
        }

        if self.document_invoice_type:
            invoices_by_type = self.env['account.move'].search([('l10n_latam_document_type_id', '=', l10n_latam_document_type_id), 
                                                            ('state', '=', 'posted'), 
                                                            ('sequence_prefix', '=', full_prefix),
                                                            ('move_type','in',('out_invoice','out_refund'))],order="name desc", limit=1)
            
            _logger.info({"invoices":invoices_by_type})
            
            if invoices_by_type:
                number =invoices_by_type.sequence_number+1

            name = "%s%s" % (full_prefix, str(number).zfill(8))
            
            vals.update({
                'name': name,
                'sequence_prefix': full_prefix,
                'sequence_number': number,
                'l10n_latam_document_type_id': l10n_latam_document_type_id,
            })

        #NOTE - Fin de cambio para localización
        if self.refunded_order_ids.account_move:
            vals['ref'] = _('Reversal of: %s', self.refunded_order_ids.account_move.name)
            vals['reversed_entry_id'] = self.refunded_order_ids.account_move.id
        if self.note:
            vals.update({'narration': self.note})
        return vals


    @api.model
    def create_from_ui(self, orders, draft=False):
        res = super(PosOrder, self).create_from_ui(orders=orders, draft=draft)
        for order in res:
            if order.get('account_move'):
                move = self.env['account.move'].sudo().browse(order.get('account_move'))
                order['invoice_number'] = move.name
                order['comprobante_origen'] = move.reversed_entry_id.name
                order['fecha_origen'] = move.reversed_entry_id.invoice_date
        return res