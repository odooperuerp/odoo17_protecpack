from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError


class AccountMove(models.Model):
    _inherit = "account.move"
    
    #CAMPO OBSOLETO
    l10n_pe_refund_reason = fields.Selection(
        selection=[
            ('01', 'Cancelación de la operación'),
            ('02', 'Cancelación por error en el RUC'),
            ('03', 'Corrección por error en la descripción'),
            ('04', 'Descuento global'),
            ('05', 'Descuento por item'),
            ('06', 'Reembolso total'),
            ('07', 'Reembolso por item'),
            ('08', 'Bonificación'),
            ('09', 'Disminución en el valor'),
            ('10', 'Otros conceptos'),
            ('11', 'Ajuste en operaciones de exportación'),
            ('12', 'Ajuste afectos al IVAP'),
            ('13', 'Ajuste en montos y/o fechas de pago'),
        ],
        string="Razón de nota de crédito (obsoleto)")

    l10n_pe_reason = fields.Char(string="Sustento")
    l10n_pe_reversed_date=fields.Date(related="reversed_entry_id.invoice_date", string="Fecha de comprobante")

    def action_post(self):
        if self.l10n_latam_document_type_id and self.l10n_latam_document_type_id.id == self.env.ref(
                "l10n_pe.document_type01").id and \
                self.partner_id.l10n_latam_identification_type_id and \
                self.partner_id.l10n_latam_identification_type_id.id != self.env.ref("l10n_pe.it_RUC").id:
            raise ValidationError("Solo se puede publicar facturas para empresas con RUC o empresas no domiciliadas")
        super(AccountMove, self).action_post()

    ##############################################
    total_sale_taxed = fields.Monetary(
        string="Gravado",
        default=0.0,
        compute="_compute_amount",
        store=True)

    total_sale_igv = fields.Monetary(
        string="IGV",
        default=0.0,
        compute="_compute_amount",
        store=True)

    total_sale_export = fields.Monetary(
        string="Exportación",
        default=0.0,
        compute="_compute_amount",
        store=True)

    total_sale_unaffected = fields.Monetary(
        string="Inafecto",
        default=0.0,
        compute="_compute_amount",
        store=True)

    total_sale_exonerated = fields.Monetary(
        string="Exonerado",
        default=0.0,
        compute="_compute_amount",
        store=True)

    total_sale_free = fields.Monetary(
        string="Gratuita",
        default=0.0,
        compute="_compute_amount",
        store=True)

    total_selective_tax = fields.Monetary(
        string="Impuesto selectivo",
        default=0.0,
        compute="_compute_amount",
        store=True)

    subtotal_venta = fields.Monetary(
        string="Sub Total",
        default=0.0,
        compute="_compute_amount",
        store=True)

    total_venta = fields.Monetary(
        string="Total",
        default=0.0,
        compute="_compute_amount",
        store=True)

    total_sale_icbper = fields.Monetary(
        string="ICBPER",
        default=0.0,
        compute="_compute_amount",
        store=True)

    global_discount_total = fields.Monetary(
        string="Descuento Global - Imp. Incl",
        default=0.0,
        compute="_compute_amount",
        store=True
    )

    global_discount_subtotal = fields.Monetary(
        string="Descuento Global - Imp. Excl",
        default=0.0,
        compute="_compute_amount",
        store=True
    )

    total_discounts = fields.Monetary(
        string="Total de descuentos",
        default=0.0,
        compute="_compute_amount",
        store=True
    )

    ##############################################

    @api.depends('invoice_line_ids', 'invoice_line_ids.quantity',
                 'invoice_line_ids.price_unit', 'invoice_line_ids.tax_ids')
    def _compute_amount(self):
        super(AccountMove, self)._compute_amount()

        for move in self:
            total_free = 0
            total_taxed = 0
            total_unaffected = 0
            total_exonerated = 0
            selective_tax = 0
            total_export = 0
            total_igv = 0
            #global_discount_total = 0
            #global_discount_subtotal = 0
            total_icbper = 0

            for line in move.invoice_line_ids:
                for line_tax in line.tax_ids:
                    if line_tax.l10n_pe_edi_tax_code == "9996":
                        total_free += line.quantity*line.price_unit
                    elif line_tax.l10n_pe_edi_tax_code == "9998":
                        total_unaffected += line.price_subtotal
                    elif line_tax.l10n_pe_edi_tax_code == "9997":
                        total_exonerated += line.price_subtotal
                    elif line_tax.l10n_pe_edi_tax_code == "9995":
                        total_export += line.price_subtotal
                    elif line_tax.l10n_pe_edi_tax_code == "2000":
                        selective_tax += line.price_subtotal
                    elif line_tax.l10n_pe_edi_tax_code == "7152":
                        total_icbper += (line_tax.amount or 0.00) * (line.quantity or 0.00)
                    elif line_tax.l10n_pe_edi_tax_code == "1000":
                        total_taxed += line.price_subtotal

                        ##################### IGV ######################
                        #if move.company_id.tax_calculation_rounding_method == 'round_per_line':
                        #    total_igv += (line.price_total - line.price_subtotal)
                        #elif move.company_id.tax_calculation_rounding_method == 'round_globally':
                        #    total_igv += (line.price_subtotal * line_tax.amount * 0.01)
                        ##############################################################

            # CALCULO DE IMPUESTO SEGÚN METODO REDONDEO DE LA CONFIG:
            if move.company_id.tax_calculation_rounding_method == 'round_per_line':
                for line in move.invoice_line_ids:
                    for line_tax in line.tax_ids:
                        if line_tax.l10n_pe_edi_tax_code == "1000":
                            total_igv += line.price_subtotal * (line_tax.amount * 0.01)

            elif move.company_id.tax_calculation_rounding_method == 'round_globally':
                total_igv = sum([
                    line.price_subtotal * [line_tax.amount for line_tax in line.tax_ids
                                           if line_tax.l10n_pe_edi_tax_code == "1000"][0] * 0.01

                    for line in move.invoice_line_ids
                    if len([line.price_subtotal for line_tax in line.tax_ids
                            if line_tax.l10n_pe_edi_tax_code == "1000"])
                ])



            move.total_discounts = sum(
                [abs(line.discount_amount if not line.flag_free_line and not line.flag_discount_global else 0) + abs(line.price_total if line.flag_discount_global else 0) for line in
                 move.invoice_line_ids])
            move.global_discount_total = sum([line.price_total for line in move.invoice_line_ids if line.flag_discount_global ])
            move.global_discount_subtotal = sum([line.price_subtotal for line in move.invoice_line_ids if line.flag_discount_global ])
            move.total_sale_free = total_free
            move.total_sale_taxed = total_taxed
            move.total_sale_unaffected = total_unaffected
            move.total_sale_exonerated = total_exonerated
            move.total_sale_export = total_export
            move.total_selective_tax = selective_tax
            move.total_sale_igv = total_igv
            move.total_sale_icbper = total_icbper
            
            if move.tax_totals:
                subtotal = move.tax_totals.get('subtotals', [])
                move.total_venta = move.tax_totals.get('amount_total', 0)
                if subtotal:
                    move.subtotal_venta = subtotal[0]['amount'] if subtotal else 0


    remission_guide_ids = fields.Many2many('stock.picking',string="Movimientos Stock Asociados")

    correlative_remission_guides = fields.Char(string="Guías Remisión Asociadas",
        compute="compute_field_correlative_remission_guides",store=True)

    document_reference_ids = fields.One2many("account.move.document.reference", "move_id", string="Otros documentos relacionados")
    despatch_document_reference_ids = fields.One2many("despatch.document.reference", "move_id", string="Guías de Remisión")
    
    def search_and_set_stock_picking(self):
        for rec in self:
            if rec.move_type in ['out_invoice','out_refund'] and not rec.remission_guide_ids:
                query = """
                    select 
                        sp.id as picking_id
                        from account_move_line as aml
                        left join account_move am on am.id = aml.move_id 
                        left join sale_order_line_invoice_rel solir on solir.invoice_line_id = aml.id 
                        left join sale_order_line sol on sol.id = solir.order_line_id 
                        left join stock_move sm on sm.sale_line_id = sol.id 
                        left join stock_picking sp on sp.id = sm.picking_id 
                        where sp.state = 'done' and am.move_type in ('out_invoice','out_refund') and am.id=%s """%(rec.id)

                self.env.cr.execute(query)
                records = self.env.cr.dictfetchall()
                if records:
                    rec.remission_guide_ids = [i['picking_id'] for i in records if i['picking_id']]
                    
                    for doc in rec.remission_guide_ids:
                        if doc.l10n_latam_document_number:
                            self.env['despatch.document.reference'].create({
                                'move_id': rec.id,
                                'l10n_pe_document_number': doc.l10n_latam_document_number,
                                'l10n_pe_document_code': '09'
                            })


    @api.depends(
        'remission_guide_ids')
    def compute_field_correlative_remission_guides(self):
        for rec in self:
            rec.correlative_remission_guides = ''
            if rec.remission_guide_ids:
                array_guides = list(rec.remission_guide_ids.filtered(lambda t:t.l10n_latam_document_number).\
                    mapped('l10n_latam_document_number'))

                if array_guides:
                    str_array_guides = ', '.join(array_guides)
                    rec.correlative_remission_guides = str_array_guides


    #####################################################################################

    @api.model
    def create(self, vals_list):
        res = super().create(vals_list)

        if res.move_type in ['out_invoice','out_refund']:

            res.search_and_set_stock_picking()
        return res