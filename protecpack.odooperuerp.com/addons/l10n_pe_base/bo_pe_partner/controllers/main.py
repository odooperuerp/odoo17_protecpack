from odoo.http import request
from odoo import http
import json


class RequestVatController(http.Controller):
    @http.route('/request/vat', type='http', auth='public',methods=['POST'], csrf=False)
    def request_vat_http(self, **post):
        l10n_latam_identification_type_id,vat = post['l10n_latam_identification_type_id'],post['vat']
        l10n_pe_vat_code = request.env["l10n_latam.identification.type"].sudo().browse(int(l10n_latam_identification_type_id)).sudo().l10n_pe_vat_code
        result = request.env["res.partner"].sudo().api_search_partner_by_vat(l10n_pe_vat_code,vat)
        return json.dumps(result)

    @http.route('/request/vat/json', type='json', auth='public', website=True)
    def request_vat_json(self, l10n_latam_identification_type_id,vat):
        l10n_pe_vat_code = request.env["l10n_latam.identification.type"].sudo().browse(int(l10n_latam_identification_type_id)).l10n_pe_vat_code
        return request.env["res.partner"].sudo().api_search_partner_by_vat(l10n_pe_vat_code,vat)