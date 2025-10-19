import re

from odoo import models
from odoo.tools import html2plaintext, cleanup_xml_node

class AccountEdiXmlUBLPE(models.AbstractModel):
    _inherit = 'account.edi.xml.ubl_pe'

    def _get_note_vals_list(self, invoice):
        return [{'note': re.sub(r'[^\w ]|[áéíóúÁÉÍÓÚ]','',html2plaintext(invoice.narration)).strip()[:190]}] if invoice.narration else []

    def _get_invoice_line_price_vals(self, line):
        vals = super(AccountEdiXmlUBLPE,self)._get_invoice_line_price_vals(line)
        if len(line.tax_ids.filtered(lambda ta: ta.l10n_pe_edi_tax_code == "9996")) > 0:
            vals.update(price_amount=0)
        return vals

    def _get_invoice_tax_totals_vals_list(self, invoice, taxes_vals):
        # EXTENDS account.edi.xml.ubl_21
        vals = super()._get_invoice_tax_totals_vals_list(invoice, taxes_vals)

        def grouping_key_generator(base_line, tax_values):
            tax = tax_values['tax_repartition_line'].tax_id
            return {
                'l10n_pe_edi_code': tax.tax_group_id.l10n_pe_edi_code,
                'l10n_pe_edi_international_code': tax.l10n_pe_edi_international_code,
                'l10n_pe_edi_tax_code': tax.l10n_pe_edi_tax_code,
            }

        tax_details_grouped = invoice._prepare_edi_tax_details(grouping_key_generator=grouping_key_generator)
        isc_tax_amount = abs(sum([
            line.amount_currency
            for line in invoice.line_ids.filtered(lambda l: l.tax_line_id.tax_group_id.l10n_pe_edi_code == 'ISC')
        ]))
        vals[0]['tax_subtotal_vals'] = []
        for grouping_vals in tax_details_grouped['tax_details'].values():
            if grouping_vals["l10n_pe_edi_tax_code"] == "9996":
                taxable_amount = sum([line.quantity*line.price_unit for line in grouping_vals["records"] if line.flag_free_line])
                tax_amount = taxable_amount*1.18
            else:
                taxable_amount = (
                        grouping_vals['base_amount_currency']
                        - (isc_tax_amount if grouping_vals['l10n_pe_edi_code'] != 'ISC' else 0)
                    )
                tax_amount = grouping_vals['tax_amount_currency'] or 0.0

            vals[0]['tax_subtotal_vals'].append({
                'currency': invoice.currency_id,
                'currency_dp': invoice.currency_id.decimal_places,
                'taxable_amount': taxable_amount,
                'tax_amount': tax_amount,
                'tax_category_vals': {
                    'tax_scheme_vals': {
                        'id': grouping_vals['l10n_pe_edi_tax_code'],
                        'name': grouping_vals['l10n_pe_edi_code'],
                        'tax_type_code': grouping_vals['l10n_pe_edi_international_code'],
                    },
                },
            })

        return vals

    def _get_invoice_line_tax_totals_vals_list(self, line, taxes_vals):
        # OVERRIDES account.edi.xml.ubl_21
        vals = {
            'currency': line.currency_id,
            'currency_dp': line.currency_id.decimal_places,
            'tax_amount': line.price_total - line.price_subtotal,
            'tax_subtotal_vals': [],
        }
        for tax_detail_vals in taxes_vals['tax_details'].values():
            tax = self.env['account.tax'].browse(tax_detail_vals['group_tax_details'][0]['id'])

            if line.flag_free_line:
                taxable_amount = line.quantity*line.price_unit
                percent = tax.amount
                tax_amount = taxable_amount*(1+percent/100)
            else:
                taxable_amount = tax_detail_vals['base_amount_currency'] if tax.tax_group_id.l10n_pe_edi_code != 'ICBPER' else None
                percent = tax.amount if tax.amount_type == 'percent' else None
                tax_amount = tax_detail_vals['tax_amount_currency'] or 0.0

            vals['tax_subtotal_vals'].append({
                'currency': line.currency_id,
                'currency_dp': line.currency_id.decimal_places,
                'taxable_amount': taxable_amount,
                'tax_amount': tax_amount,
                'base_unit_measure_attrs': {
                    'unitCode': line.product_uom_id.l10n_pe_edi_measure_unit_code,
                },
                'base_unit_measure': int(line.quantity) if tax.tax_group_id.l10n_pe_edi_code == 'ICBPER' else None,
                'tax_category_vals': {
                    'percent': percent,
                    'tax_exemption_reason_code': (
                        line.l10n_pe_edi_affectation_reason
                        if tax.tax_group_id.l10n_pe_edi_code not in ('ISC', 'ICBPER') and line.l10n_pe_edi_affectation_reason
                        else None
                    ),
                    'tier_range': tax.l10n_pe_edi_isc_type if tax.tax_group_id.l10n_pe_edi_code == 'ISC' and tax.l10n_pe_edi_isc_type else None,
                    'tax_scheme_vals': {
                        'id': tax.l10n_pe_edi_tax_code,
                        'name': tax.tax_group_id.l10n_pe_edi_code,
                        'tax_type_code': tax.l10n_pe_edi_international_code,
                    },
                },
            })
        return [vals]

    def _get_invoice_line_vals(self, line, line_id, taxes_vals):
        if len(line.tax_ids.filtered(lambda ta: ta.l10n_pe_edi_tax_code == "9996")) > 0:

            vals = super(AccountEdiXmlUBLPE, self)._get_invoice_line_vals(line, line_id, taxes_vals)
            vals.update(allowance_charge_vals=[])

            vals['pricing_reference_vals'] = {
                'alternative_condition_price_vals': [{
                    'currency': line.currency_id,
                    'price_amount': line.price_unit,
                    'price_amount_dp': self.env['decimal.precision'].precision_get('Product Price'),
                    'price_type_code': '02'
                }]
            }
            vals.update(line_extension_amount=line.price_unit * line.quantity)

            return vals
        else:
            return super(AccountEdiXmlUBLPE, self)._get_invoice_line_vals(line, line_id, taxes_vals)

    def _get_document_allowance_charge_vals_list(self, invoice):
        vals_list = super(AccountEdiXmlUBLPE, self)._get_document_allowance_charge_vals_list(invoice)
        global_discount_subtotal = sum(
            [abs(line.price_subtotal) for line in invoice.invoice_line_ids if line.flag_discount_global])
        if global_discount_subtotal > 0:
            vals_list.append({
                'charge_indicator': 'false',
                'allowance_charge_reason_code': '02',
                'base_amount': abs(invoice.subtotal_venta) + abs(global_discount_subtotal),
                'amount': abs(global_discount_subtotal),
                'currency_dp': 2,
                'currency_name': invoice.currency_id.name,
            })

        return vals_list

    def _export_invoice_vals(self, invoice):
        vals = super(AccountEdiXmlUBLPE, self)._export_invoice_vals(invoice)
        order_reference = vals["vals"]["order_reference"]
        order_reference = re.sub(r'\W+', '', order_reference)
        taxes_vals = vals.get('taxes_vals', [])
        document_allowance_charge_vals_list = vals.get("allowance_charge_vals", [])

        # Compute values for invoice lines.
        line_extension_amount = 0.0
        invoice_lines = invoice.invoice_line_ids.filtered(
            lambda line: line.display_type not in ('line_note', 'line_section'))

        invoice_line_vals_list = []
        for line_id, line in enumerate(invoice_lines):
            line_taxes_vals = taxes_vals['tax_details_per_record'][line]
            line_vals = self._get_invoice_line_vals(line, line_id, line_taxes_vals)

            if not line.flag_discount_global:
                invoice_line_vals_list.append(line_vals)

            if line.flag_free_line == False:
                line_extension_amount += line_vals['line_extension_amount']

        # Compute the total allowance/charge amounts.
        allowance_total_amount = 0.0
        charge_total_amount = 0.0
        for allowance_charge_vals in document_allowance_charge_vals_list:
            if allowance_charge_vals['charge_indicator'] == 'false' and \
                    allowance_charge_vals['allowance_charge_reason_code'] in ('00', '01', '47', '48'):
                allowance_total_amount += allowance_charge_vals['amount']
            elif allowance_charge_vals['charge_indicator'] == 'true':
                charge_total_amount += allowance_charge_vals['amount']

        vals["vals"]["line_vals"] = invoice_line_vals_list
        vals["vals"]["order_reference"] = order_reference[:20]
        vals["vals"]["monetary_total_vals"] = self._get_invoice_monetary_total_vals(
            invoice,
            taxes_vals,
            line_extension_amount,
            allowance_total_amount,
            charge_total_amount,
        )
        
        
        if vals['document_type'] == 'credit_note':
            if invoice.l10n_latam_document_type_id.code == '07':
                vals['vals'].update({
                    'discrepancy_response_vals': [{
                        'response_code': invoice.l10n_pe_edi_refund_reason,
                        'description': invoice.l10n_pe_edi_cancel_reason
                    }]
                })
            if invoice.reversed_entry_id:
                vals['vals'].update({
                    'billing_reference_vals': {
                        'id': invoice.reversed_entry_id.name.replace(' ', ''),
                        'document_type_code': invoice.reversed_entry_id.l10n_latam_document_type_id.code,
                    },
                })
        
        if invoice.despatch_document_reference_ids.exists():
            vals['vals'].update({
                'despatch_document_reference_vals': [{
                    'id': ref.l10n_pe_document_number,
                    'document_type_code': ref.l10n_pe_document_code,
                } for ref in invoice.despatch_document_reference_ids],
            })
        if invoice.document_reference_ids.exists():
            vals['vals'].update({
                'additional_document_reference_list': [{
                    'id': ref.l10n_pe_document_number,
                    'document_type_code': ref.l10n_pe_document_code,
                } for ref in invoice.document_reference_ids],
            })
        
        return vals
