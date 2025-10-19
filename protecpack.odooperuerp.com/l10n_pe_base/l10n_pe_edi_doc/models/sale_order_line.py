from odoo import Command, _, models, fields, api

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    discount_amount = fields.Float(string='Desc.', compute="_compute_discount_amount",
                                   inverse="_inverse_discount_amount", store=True)

    flag_discount_global = fields.Boolean(string='Flag Descuento Global', compute="_compute_flag_discount_global",
                                          store=True)
    flag_free_line = fields.Boolean(string='Flag Free', compute="_compute_flag_free_line", store=True)

    @api.depends('tax_id')
    def _compute_flag_free_line(self):
        for record in self:
            record.flag_free_line = False
            if record.tax_id.l10n_pe_edi_tax_code in ["9996"]:
                record.flag_free_line = True

    @api.onchange('flag_free_line')
    def _onchange_flag_free_line(self):
        for record in self:
            if record.flag_free_line:
                record.discount = 0
                record.discount_amount = 0

    @api.depends('discount')
    def _compute_discount_amount(self):
        for record in self:
            record.discount_amount = record.price_unit * record.product_uom_qty * record.discount / 100

    @api.onchange('discount_amount')
    def _inverse_discount_amount(self):
        for record in self:
            if record.price_unit * record.discount_amount > 0:
                record.discount = 100 * record.discount_amount / (record.price_unit * record.product_uom_qty)
            else:
                record.discount = 0

    @api.depends("product_id")
    def _compute_flag_discount_global(self):
        for record in self:
            record.flag_discount_global = record.product_id == record.company_id.sale_discount_product_id

