from odoo import models,fields,api
import logging
_logger = logging.getLogger(__name__)



class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_confirm(self):
        for record in self:
            _logger.info(record.partner_id.company_name)
            if not record.partner_id.company_name in ("",False):
                record.partner_id.create_company()
                parent_id = record.partner_id.parent_id
                if parent_id:
                    record.partner_invoice_id = parent_id.id
        return super().action_confirm()

    def _get_invoiceable_lines(self, final=False):
        lines = super()._get_invoiceable_lines(final)
        return lines.filtered(lambda line: line.tax_id.exists() and line.price_unit > 0)
