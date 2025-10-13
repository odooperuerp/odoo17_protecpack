from odoo import Command, _, models, fields, api


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    sale_template_id = fields.Many2one("sale.order.template.line")

    @api.depends('product_id', 'company_id')
    def _compute_tax_id(self):
        for record in self:
            if not record.sale_template_id.exists():
                super(SaleOrderLine,self)._compute_tax_id()

    @api.depends('product_id', 'product_uom', 'product_uom_qty')
    def _compute_discount(self):
        for record in self:
            if not record.sale_template_id.exists():
                super(SaleOrderLine, self)._compute_discount()

    @api.depends('product_id', 'product_uom', 'product_uom_qty')
    def _compute_price_unit(self):
        for record in self:
            if not record.sale_template_id.exists():
                super(SaleOrderLine, self)._compute_price_unit()