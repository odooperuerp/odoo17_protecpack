from odoo import Command, _, models, fields, api
from collections import defaultdict


class SaleOrderDiscount(models.TransientModel):
    _inherit = 'sale.order.discount'

    def _prepare_discount_line_values(self, product, amount, taxes, description=None):
        res = super(SaleOrderDiscount, self)._prepare_discount_line_values(product, amount, taxes, description)
        if self.sale_order_id.order_line.exists():
            res.update(sequence=max(self.sale_order_id.order_line.mapped("sequence"))+ 1)
        return res

    """
    Sobrecarga de _create_discount_lines:  calculo del descuento en base al total, de forma original se encontraba con el subtotal
    """
    def _create_discount_lines(self):
        """Create SOline(s) according to wizard configuration"""
        self.ensure_one()
        discount_product = self._get_discount_product()

        if self.discount_type == 'amount':
            vals_list = [
                self._prepare_discount_line_values(
                    product=discount_product,
                    amount=self.discount_amount,
                    taxes=self.env['account.tax'] or discount_product.taxes_id,
                )
            ]
        else:  # so_discount
            total_price_per_tax_groups = defaultdict(float)
            for line in self.sale_order_id.order_line:
                if not line.product_uom_qty or not line.price_unit:
                    continue

                total_price_per_tax_groups[line.tax_id] += line.price_total

            if not total_price_per_tax_groups:
                # No valid lines on which the discount can be applied
                return
            elif len(total_price_per_tax_groups) == 1:
                # No taxes, or all lines have the exact same taxes
                taxes = next(iter(total_price_per_tax_groups.keys()))
                total = total_price_per_tax_groups[taxes]
                vals_list = [{
                    **self._prepare_discount_line_values(
                        product=discount_product,
                        amount=total * self.discount_percentage,
                        taxes=taxes,
                        description=_(
                            "Descuento: %(percent)s%%",
                            percent=self.discount_percentage * 100
                        ),
                    ),
                }]
            else:
                vals_list = [
                    self._prepare_discount_line_values(
                        product=discount_product,
                        amount=total * self.discount_percentage,
                        taxes=taxes,
                        description=_(
                            "Descuento: %(percent)s%%"
                            "- On products with the following taxes %(taxes)s",
                            percent=self.discount_percentage * 100,
                            taxes=", ".join(taxes.mapped('name'))
                        ),
                    ) for taxes, total in total_price_per_tax_groups.items()
                ]
        return self.env['sale.order.line'].create(vals_list)
