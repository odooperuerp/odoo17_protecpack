from odoo import models,fields
from odoo.tools.zeep.wsse.username import UsernameToken

class AccountEdiFormat(models.Model):
    _inherit = 'account.edi.format'


    def _l10n_pe_edi_sign_invoices_nubefact(self, invoice, edi_filename, edi_str):
        """This method calls _l10n_pe_edi_sign_service_nubefact() to allow inherit this second from other models"""
        return self._l10n_pe_edi_sign_service_nubefact(invoice.company_id, edi_filename, edi_str, invoice.l10n_latam_document_type_id.code)

    def _l10n_pe_edi_sign_service_nubefact(self, company, edi_filename, edi_str, latam_document_type):
        credentials = self._l10n_pe_edi_get_nubefact_credentials(company)
        return self._l10n_pe_edi_sign_service_sunat_digiflow_common(
            company, edi_filename, edi_str, credentials, latam_document_type)

    def _l10n_pe_edi_get_nubefact_credentials(self, company):
        self.ensure_one()
        res = {'fault_ns': 'soap-env'}
        if company.l10n_pe_edi_test_env:
            res.update({
                'wsdl': 'https://demo-ose.nubefact.com/ol-ti-itcpe/billService?wsdl',
                'token': UsernameToken(company.sudo().l10n_pe_edi_provider_username, company.sudo().l10n_pe_edi_provider_password),
            })
        else:
            res.update({
                'wsdl': 'https://ose.nubefact.com/ol-ti-itcpe/billService?wsdl',
                'token': UsernameToken(company.sudo().l10n_pe_edi_provider_username, company.sudo().l10n_pe_edi_provider_password),
            })
        return res


    def _l10n_pe_edi_cancel_invoices_step_1_nubefact(self, company, invoices, void_filename, void_str):
        credentials = self._l10n_pe_edi_get_nubefact_credentials(company)
        return self._l10n_pe_edi_cancel_invoices_step_1_sunat_digiflow_common(company, invoices, void_filename, void_str, credentials)

    def _l10n_pe_edi_cancel_invoices_step_2_nubefact(self, company, edi_values, cdr_number):
        credentials = self._l10n_pe_edi_get_nubefact_credentials(company)
        return self._l10n_pe_edi_cancel_invoices_step_2_sunat_digiflow_common(company, edi_values, cdr_number, credentials)
