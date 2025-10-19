# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import Command, api, fields, models, _

class SaleOrderTemplateLine(models.Model):
    _inherit = "sale.order.template.line"

    tax_id = fields.Many2many("account.tax", string="Impuestos")
    price_unit = fields.Float("Precio")
    discount_amount = fields.Float(string="Monto descuento",compute="_compute_discount_amount", inverse="_inverse_discount_amount",store=True)
    discount = fields.Float(string="Dscto %")

    def _prepare_order_line_values(self):
        res = super(SaleOrderTemplateLine,self)._prepare_order_line_values()
        tax_ids = self.tax_id.ids if self.tax_id else []
        res.update(tax_id=[Command.set(tax_ids)])
        res.update(price_unit=self.price_unit)
        res.update(discount_amount=self.discount_amount)
        res.update(discount=self.discount)
        res.update(sale_template_id=self.id)
        return res

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

