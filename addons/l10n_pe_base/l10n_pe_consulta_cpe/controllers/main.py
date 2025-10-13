# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class ConsultaCPE(http.Controller):

    @http.route('/consulta_cpe', auth='public', method=["GET"], website=True)
    def get_consulta_cpe(self, **kwargs):
        return request.render('l10n_pe_consulta_cpe.web_view_form_consulta_cpe')

    @http.route('/consulta_cpe', type='http', auth='public', method=["POST"], csrf=False)
    def consulta(self, **post):
        l10n_pe_prefix_code = post.get('serie').upper()
        l10n_pe_invoice_number = post.get("correlativo", "")
        invoice_date = post.get("invoice_date")
        vat = post.get("vat")
        amount_total = post.get("total")

        try:
            l10n_pe_invoice_number = (str(int(l10n_pe_invoice_number))).zfill(8)
        except Exception as e:
            return "El número correlativo es erróneo"

        try:
            amount_total = float(amount_total)
        except Exception as e:
            return "El monto total es erróneo"

        move = request.env["account.move"].sudo().search([['l10n_pe_prefix_code', "=", l10n_pe_prefix_code],
                                                               ['l10n_pe_invoice_number', "=", l10n_pe_invoice_number],
                                                                ['partner_id.vat', "=", vat],
                                                                ['invoice_date', '=', invoice_date],
                                                                ['amount_total', '=', amount_total]], limit=1)
        return request.render('l10n_pe_consulta_cpe.web_view_form_consulta_cpe_resultados', {'move': move})
