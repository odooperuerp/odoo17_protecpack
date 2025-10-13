# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError
from odoo.tools import float_is_zero, float_compare
from odoo.tools import (
    date_utils,
    email_re,
    email_split,
    float_compare,
    float_is_zero,
    float_repr,
    float_round,
    format_amount,
    format_date,
    formatLang,
    frozendict,
    get_lang,
    groupby,
    index_exists,
    is_html_empty,
    create_index,
)

import logging
_logger = logging.getLogger(__name__)


DICCIONARIO_DETRACCION = {
      '001':'Azúcar y melaza de caña',
      '002':'Arroz',
      '003':'Alcohol etílico',
      '004':'Recursos hidrobiológicos',
      '005':'Maíz amarillo duro',
      '006':'Algodón (Obsoleto)',
      '007':'Caña de azúcar',
      '008':'Madera',
      '009':'Arena y piedra',
      '010':'Residuos, subproductos, desechos, recortes y desperdicios',
      '011':'Bienes gravados con el IGV, o renuncia a la exoneración',
      '012':'Intermediación laboral y tercerización',
      '013':'Animales vivos',
      '014':'Carnes y despojos comestibles',
      '015':'Abonos, cueros y pieles de origen animal',
      '016':'Aceite de pescado',
      '017':'Harina, polvo y “pellets” de pescado, crustáceos, moluscos y demás invertebrados acuáticos',
      '018':'Embarcaciones pesqueras (Obsoleto)',
      '019':'Arrendamiento de bienes muebles',
      '020':'Mantenimiento y reparación de bienes muebles',
      '021':'Movimiento de carga',
      '022':'Otros servicios empresariales',
      '023':'Leche',
      '024':'Comisión mercantil',
      '025':'Fabricación de bienes por encargo',
      '026':'Servicio de transporte de personas',
      '027':'Servicio de transporte de carga',
      '028':'Transporte de pasajeros',
      '029':'Algodón en rama sin desmontar (Obsoleto)',
      '030':'Contratos de construcción',
      '031':'Oro gravado con el IGV',
      '032':'Páprika y otros frutos de los géneros capsicum o pimienta',
      '033':'Espárragos (Obsoleto)',
      '034':'Minerales metálicos no auríferos',
      '035':'Bienes exonerados del IGV',
      '036':'Oro y demás minerales metálicos exonerados del IGV',
      '037':'Demás servicios gravados con el IGV',
      '039':'Minerales no metálicos',
      '040':'Bien inmueble gravado con IGV',
      '041':'Plomo',
      '099':'Ley 30737',
      }

class AccountMove(models.Model):
      _inherit = 'account.move'

      has_multi_code_detraccion = fields.Boolean(string="Tiene mas de un concepto de Detracción",
            compute="compute_campo_has_multi_code_detraccion",store=True)

      codigo_detraccion = fields.Char(string="Código Detracción",
            compute="compute_campo_has_multi_code_detraccion",store=True)

      porcentaje_detraccion = fields.Float(string="% Detracción",
            compute="compute_campo_has_multi_code_detraccion",store=True)

      monto_detraccion = fields.Float(string="Monto Detracción",currency_field="company_currency_id",
            compute="compute_campo_has_multi_code_detraccion",store=True)

      cuenta_detraccion = fields.Char(string="Cuenta Detracción",
            compute="compute_campo_has_multi_code_detraccion",store=True)


      @api.depends(
            'invoice_line_ids',
            'invoice_line_ids.product_id',
            'state',
            'l10n_pe_edi_operation_type')
      def compute_campo_has_multi_code_detraccion(self):
            for rec in self:
                  rec.has_multi_code_detraccion = False

                  max_percent = max(rec.invoice_line_ids.mapped('product_id.l10n_pe_withhold_percentage'), default=0)
                  if max_percent and rec.l10n_pe_edi_operation_type in ['1001', '1002', '1003', '1004'] and rec.move_type == 'out_invoice':

                        if rec.invoice_line_ids:
                              detraccion_codes = rec.invoice_line_ids.mapped('product_id.l10n_pe_withhold_code')
                              if len(detraccion_codes or '')>1:
                                    rec.has_multi_code_detraccion = True
                        ##########################################################################
                        line = rec.invoice_line_ids.filtered(lambda r: r.product_id.l10n_pe_withhold_percentage == max_percent)[0]
                        
                        rec.codigo_detraccion = "%s-%s"%(
                              line.product_id.l10n_pe_withhold_code,
                              rec.get_concept_detraccion(line.product_id.l10n_pe_withhold_code))

                        rec.porcentaje_detraccion = max_percent or 0.00

                        rec.monto_detraccion = float_round(rec.amount_total_signed * (max_percent / 100.0), precision_rounding=1)

                        national_bank = rec.env.ref('l10n_pe.peruvian_national_bank')
                        national_bank_account = rec.company_id.bank_ids.filtered(lambda b: b.bank_id == national_bank)
                        national_bank_account_number = national_bank_account[0].acc_number if national_bank_account else False

                        rec.cuenta_detraccion = national_bank_account_number or ''
      ################################################################################################

      def get_concept_detraccion(self,code):
            if code:
                  if code in DICCIONARIO_DETRACCION:
                        return DICCIONARIO_DETRACCION[code] or ''
                  else:
                        return ''


      @api.depends('show_payment_term_details','monto_detraccion')
      def _compute_payment_term_details(self):
            super(AccountMove,self)._compute_payment_term_details()

            for invoice in self:
                  spot = invoice._l10n_pe_edi_get_spot()
                  spot_amount = 0
                  if invoice.is_retention:
                        spot_amount = invoice.retention_amount
                  elif spot:
                        spot_amount = spot['amount'] if invoice.currency_id == invoice.company_id.currency_id else spot['spot_amount']

                  invoice.payment_term_details = False
                  if invoice.show_payment_term_details:
                        
                        sign = 1 if invoice.is_inbound(include_receipts=True) else -1
                        payment_term_details = []
                        
                        for line in invoice.line_ids.filtered(lambda l: l.display_type == 'payment_term').sorted('date_maturity'):
                              
                              line_percentaje = abs(line.amount_currency/invoice.amount_total)
                              cuota_detraccion = line_percentaje*spot_amount

                              payment_term_details.append({
                                    'date': format_date(self.env, line.date_maturity),
                                    'amount': sign * line.amount_currency - cuota_detraccion,
                              })
                        
                        invoice.payment_term_details = payment_term_details