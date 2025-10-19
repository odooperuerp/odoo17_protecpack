# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
import re
import logging
_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    ubigeo = fields.Char(string='Ubigeo')


    @api.onchange('l10n_latam_identification_type_id', 'vat')
    def change_vat(self):
        for record in self:
            #record.update(record.search_partner_by_vat())
            record.update(self.api_search_partner_by_vat(record.l10n_latam_identification_type_id.l10n_pe_vat_code,record.vat))

    def search_partner_by_vat(self):
        self.ensure_one()
        result = {}
        ICPSudo = self.env["ir.config_parameter"].sudo()
        provider = ICPSudo.get_param("provider_search_partner_by_vat", default="")
        if provider or provider != "none":
            result = self._search_partner_by_vat(provider)
            if result != {}:
                result = self._process_values_partner(provider,result)
        return result

    def _search_partner_by_vat(self,provider = ""):
        result = {}
        func_search_partner_by_vat = getattr(self,"_search_partner_by_vat_%s" % provider,None)
        if func_search_partner_by_vat:
            result = func_search_partner_by_vat()
        return result

    @api.model
    def _process_values_partner(self,provider = "", vals={}):
        match = self._match_fields(provider)
        result = {match[key]:"" for key in match}
        for key in vals:
            if match.get(key,False):
                result[match[key]] = vals.get(key,False)

        ubigeo = result.get("ubigeo",False)
        if ubigeo:
            district_id = self.env["l10n_pe.res.city.district"].search([("code","=",ubigeo)])
            city_id = district_id.city_id
            state_id = city_id.state_id
            country_id = city_id.country_id
            result.update({
                "l10n_pe_district":district_id.id,
                "city_id":city_id.id,
                "state_id":state_id.id,
                "country_id":country_id.id
            })
        
        func_process_values_partner = getattr(self,"_process_values_partner_%s" % provider,None)
        if func_process_values_partner:
            result = func_process_values_partner(result,vals)
        return result

    @api.model
    def _match_fields(self,provider = ""):
        match = {}
        if provider or provider != "none":
            func_match_fields_provider = getattr(self,"_match_fields_%s" % provider ,None)
            if func_match_fields_provider:
                match = func_match_fields_provider()
                if match == {}:
                    raise ValidationError("_match_fields debe ser implementada para el proveedor %s" % provider)
        return match

    #apis
    @api.model
    def api_search_partner_by_vat(self,l10n_pe_vat_code,vat):
        result = {}
        ICPSudo = self.env["ir.config_parameter"].sudo()
        provider = ICPSudo.get_param("provider_search_partner_by_vat", default="")
        if provider or provider != "none":
            result = self._api_search_partner_by_vat(provider,l10n_pe_vat_code,vat)
            if result != {}:
                result = self._process_values_partner(provider,result)
        return result


    @api.model
    def _api_search_partner_by_vat(self,provider,l10n_pe_vat_code,vat):
        result = {}
        func_api_search_partner_by_vat = getattr(self,"_api_search_partner_by_vat_%s" % provider,None)
        if func_api_search_partner_by_vat:
            result = func_api_search_partner_by_vat(l10n_pe_vat_code,vat)
        return result


