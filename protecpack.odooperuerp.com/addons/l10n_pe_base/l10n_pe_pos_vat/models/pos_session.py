# -*- coding: utf-8 -*-
from odoo import api, models


class PosSession(models.Model):
    _inherit = 'pos.session'

    @api.model
    def _pos_ui_models_to_load(self):
        res = super()._pos_ui_models_to_load()
        if self.company_id.country_code == 'PE':
            res += ['l10n_latam.identification.type','res.city','l10n_pe.res.city.district']
        return res

    def _loader_params_res_partner(self):
        vals = super()._loader_params_res_partner()
        if self.company_id.country_code == 'PE':
            vals['search_params']['fields'] += ['l10n_latam_identification_type_id','city_id','l10n_pe_district','anonymous_customer']
        return vals

    def _loader_params_l10n_latam_identification_type(self):
        return {
            'search_params': {
                'domain': [('active', '=', True)],
                'fields': ['name','l10n_pe_vat_code']},
        }

    def _get_pos_ui_l10n_latam_identification_type(self, params):
        return self.env['l10n_latam.identification.type'].search_read(**params['search_params'])

    def _loader_params_res_city(self):
        return {
            'search_params': {
                'domain': [],
                'fields': ['name','country_id','state_id']},
        }

    def _get_pos_ui_res_city(self, params):
        return self.env['res.city'].search_read(**params['search_params'])

    def _loader_params_l10n_pe_res_city_district(self):
        return {
            'search_params': {
                'domain': [],
                'fields': ['name', "code",'city_id']},
        }

    def _get_pos_ui_l10n_pe_res_city_district(self, params):
        return self.env['l10n_pe.res.city.district'].search_read(**params['search_params'])