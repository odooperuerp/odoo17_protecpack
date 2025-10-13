# -*- coding: utf-8 -*-
from odoo import api, models


class PosSession(models.Model):
    _inherit = 'pos.session'

    def _loader_params_res_company(self):
        vals = super()._loader_params_res_company()
        if self.company_id.country_code == 'PE':
            vals['search_params']['fields'] += ['street','l10n_pe_edi_qr_comment_report_invoice_document','l10n_pe_trade_name']
        return vals
    