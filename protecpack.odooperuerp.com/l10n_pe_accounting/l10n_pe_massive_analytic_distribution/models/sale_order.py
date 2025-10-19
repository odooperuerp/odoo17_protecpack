from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError,RedirectWarning
from datetime import datetime, timedelta
import re
import logging


_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = "sale.order"


    massive_analytic_distribution = fields.Json(
        'Distribución Analítica Masiva',
        compute="_compute_analytic_distribution", store=True, copy=True, readonly=False,
        precompute=True
    )
    # Json non stored to be able to search on analytic_distribution.
    analytic_distribution_search = fields.Json(
        store=False,
        search="_search_analytic_distribution"
    )
    analytic_precision = fields.Integer(
        store=False,
        default=lambda self: self.env['decimal.precision'].precision_get("Percentage Analytic"),
    )

    ######################################################################

    def aplication_massive_analytic_distribution(self):
        if self.massive_analytic_distribution and self.order_line:

            self.order_line.write({'analytic_distribution':self.massive_analytic_distribution})


    ######################################################################
    def _compute_analytic_distribution(self):
        pass

    def _search_analytic_distribution(self, operator, value):
        if operator not in ['=', '!=', 'ilike', 'not ilike'] or not isinstance(value, (str, bool)):
            raise UserError(_('Operation not supported'))
        operator_name_search = '=' if operator in ('=', '!=') else 'ilike'
        account_ids = list(self.env['account.analytic.account']._name_search(name=value, operator=operator_name_search))

        query = f"""
            SELECT id
            FROM {self._table}
            WHERE analytic_distribution ?| array[%s]
        """
        operator_inselect = 'inselect' if operator in ('=', 'ilike') else 'not inselect'
        return [('id', operator_inselect, (query, [[str(account_id) for account_id in account_ids]]))]