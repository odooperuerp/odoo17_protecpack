from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    flag_discount_global = fields.Boolean(string='Flag Descuento Global', compute="_compute_flag_discount_global",
                                          store=True)

    discount_amount = fields.Float(string='Desc.', compute="_compute_discount_amount",
                                   inverse="_inverse_discount_amount")

    flag_free_line = fields.Boolean(string='Flag Free', compute="_compute_flag_free_line", store=True)


    @api.depends('tax_ids')
    def _compute_flag_free_line(self):
        for record in self:
            flag_free_line = False
            for tax in record.tax_ids:
                if tax.l10n_pe_edi_tax_code in ["9996"]:
                    flag_free_line = True

            record.flag_free_line = flag_free_line

    @api.onchange('tax_ids','flag_free_line')
    def _onchange_flag_free_line(self):
        for record in self:
            if record.flag_free_line:
                record.discount = 0
                record.discount_amount = 0

    @api.depends('discount')
    def _compute_discount_amount(self):
        for record in self:
            record.discount_amount = record.price_unit * record.quantity * record.discount / 100

    def _inverse_discount_amount(self):
        if self.price_unit * self.discount_amount > 0:
            self.discount = 100 * self.discount_amount / (self.price_unit * self.quantity)
        else:
            self.discount = 0

    @api.onchange('discount_amount')
    def onchange_discount(self):
        for record in self:
            if self.price_unit * self.discount_amount > 0:
                record.discount = 100 * self.discount_amount / (self.price_unit * self.quantity)
            else:
                record.discount = 0

    @api.depends("product_id")
    def _compute_flag_discount_global(self):
        for record in self:
            if record.product_id:
                record.flag_discount_global = record.product_id == record.company_id.sale_discount_product_id
            else:
                record.flag_discount_global = False

            if record.flag_discount_global:
                record.discount = 0
                record.discount_amount = 0

    """
    @api.constrains("price_unit", "flag_discount_global", "discount")
    def _check_line_global_discount(self):
        for record in self:
            if record.discount != 0 and record.flag_discount_global:
                raise UserError("La línea de descuento global no debe tener un descuento de línea")
            if record.price_unit >= 0 and record.flag_discount_global:
                raise UserError("El precio de la línea debe ser negativo debido a que se trata de un descuento global")
    """
