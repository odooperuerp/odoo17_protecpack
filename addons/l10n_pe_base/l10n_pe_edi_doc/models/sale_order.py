from odoo import Command, _, models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    total_discounts = fields.Monetary(string="Total descuentos", store=True, compute='_compute_amounts', tracking=True)
    total_discounts_untaxed = fields.Monetary(string="Total descuentos (Sin impuestos)", store=True, compute='_compute_amounts', tracking=True)
    total_gravado = fields.Monetary(string="Total gravado", store=True, compute='_compute_amounts', tracking=True)
    total_gratuito = fields.Monetary(string="Total gratuito", store=True, compute='_compute_amounts', tracking=True)
    total_igv = fields.Monetary(string="Total IGV", store=True, compute='_compute_amounts', tracking=True)


    global_discount = fields.Monetary(string="Descuento global", store=True, compute='_compute_amounts', tracking=True)
    global_discount_untaxed = fields.Monetary(string="Descuento global (Sin impuestos)", store=True, compute='_compute_amounts', tracking=True)
    total_discount_lines = fields.Monetary(string="Descuento por línea", store=True, compute='_compute_amounts', tracking=True)
    
    subtotal_before_discount = fields.Monetary(string='Subtotal', store=True, readonly=True, compute='_compute_amounts')
    subtotal_before_discount_untaxed = fields.Monetary(string='Subtotal (Sin impuestos)', store=True, readonly=True, compute='_compute_amounts')

    @api.depends('order_line.price_subtotal', 'order_line.price_tax', 'order_line.price_total')
    def _compute_amounts(self):
        super(SaleOrder, self)._compute_amounts()
        for order in self:

            order.total_gravado = sum(line.price_subtotal for line in order.order_line if line.tax_id.filtered(lambda r: r.l10n_pe_edi_tax_code in ['1000']))
            order.total_gratuito = sum(line.product_uom_qty*line.price_unit for line in order.order_line if line.tax_id.filtered(lambda r: r.l10n_pe_edi_tax_code == '9996'))
            order.total_igv = sum(line.price_total - line.price_subtotal for line in order.order_line if line.tax_id.filtered(lambda r: r.l10n_pe_edi_tax_code in ['1000']))
            
            order.global_discount = abs(sum(order.order_line.filtered(lambda r: r.flag_discount_global).mapped('price_total')))
            order.global_discount_untaxed = abs(sum(order.order_line.filtered(lambda r: r.flag_discount_global).mapped('price_subtotal')))
            order.total_discount_lines = abs(sum(order.order_line.filtered(lambda r: not r.flag_free_line and not r.flag_discount_global).mapped('discount_amount')))
            
            order.total_discounts = order.global_discount + order.total_discount_lines
            order.total_discounts_untaxed = order.global_discount_untaxed + order.total_discount_lines

            
            order.subtotal_before_discount = order.total_discounts + order.total_gravado + order.total_igv
            order.subtotal_before_discount_untaxed = order.total_discounts_untaxed + order.total_gravado
            


    @api.depends('partner_id')
    def _compute_partner_invoice_id(self):
        for order in self:
            if order.partner_id:
                if order.partner_id.parent_id:
                    order.partner_invoice_id = order.partner_id.parent_id
                else:
                    order.partner_invoice_id = order.partner_id.address_get(['invoice'])['invoice'] if order.partner_id else False
