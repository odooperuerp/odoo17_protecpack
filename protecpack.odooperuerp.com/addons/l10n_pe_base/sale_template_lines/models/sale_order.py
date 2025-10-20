from odoo import Command, _, models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    """
    @api.onchange('sale_order_template_id')
    def _onchange_sale_order_template_id(self):
        super(SaleOrder, self.with_context(skip_computes=True))._onchange_sale_order_template_id()
        self.order_line
        self.order_line.with_context(skip_computes=True)

    """