# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import calendar
from datetime import datetime, timedelta
import logging
from io import BytesIO, StringIO
import xlsxwriter
from odoo.exceptions import UserError

class WizardReceiptOfFeesReport(models.TransientModel):
    _name = 'wizard.receipt.of.fees.report'
    _description = 'Reporte de Recibos por Honorarios'

    company_id = fields.Many2one('res.company', string="Compañia", 
        default=lambda self: self.env['res.company']._company_default_get('account.invoice'),
        domain = lambda self:[('id','in',[i.id for i in self.env['res.users'].browse(self.env.user.id).company_ids])],
        readonly=True)
    
    date_from = fields.Date(string="Fecha Documento Desde")
    date_to = fields.Date(string="Fecha Documento Hasta")

    print_format = fields.Selection(selection='_get_print_format',
        string='Formato Impresión',default='xlsx')


    @api.model
    def _get_print_format(self):
        option = [
            ('xlsx','xlsx')
        ]
        return option


    def file_name(self, file_format):
        file_name = "Reporte_recibos_honorarios_%s_del_%s_al_%s.%s"%(
            self.company_id.vat or '',
            self.date_from.strftime("%d-%m-%Y"),
            self.date_to.strftime("%d-%m-%Y"),
            file_format)

        return file_name


    def _init_buffer(self, output):
        # output parametro de buffer que ingresa vacio
        if self.print_format == 'xlsx':
            self._generate_xlsx(output)
        return output



    def document_print(self):
        output = BytesIO()
        output = self._init_buffer(output)
        output.seek(0)
        return output.read()


    def action_print(self):
        if not(self.date_from and self.date_to):
            raise UserError(_('Debe espeficar el intervalo de Fechas !'))

        if (self.print_format) :
            if self.print_format in ['xlsx']:
                return {
                    'type': 'ir.actions.act_url',
                    'url': 'reports/format/{}/{}/{}'.format(self._name, self.print_format, self.id),
                    'target': 'new'}
        else:
            raise UserError(_('Debe indicar el Formato de Impresión!'))



    def get_records(self):
        if self.date_from or self.date_to:
            domain = [('state','in',['posted']),('is_receipt_of_fees_flag','=',True),
                ('company_id','=',self.company_id.id)]

            if self.date_from:
                domain += [('invoice_date','>=',self.date_from)]
            if self.date_to:
                domain += [('invoice_date','<=',self.date_to)]

            invoice_ids = self.env['account.move'].search(domain)

            return invoice_ids


    ################################## GENERAR EXCEL
    def _generate_xlsx(self, output):

        workbook = xlsxwriter.Workbook(output)
        ws = workbook.add_worksheet('Reporte de Recibos por Honorarios')
        styles = {'font_size': 10, 'font_name':'Arial', 'bold': True}
        styles_table = dict(styles,font_size=8,align='center',border=1)

        titulo_1 = workbook.add_format(styles)
        titulo_2 = workbook.add_format(dict(styles,font_size=8))
        titulo_3 = workbook.add_format(styles_table)
        titulo_4 = workbook.add_format(dict(styles_table,align=''))
        titulo_5 = workbook.add_format(dict(styles_table,align='',bold=False))

        ws.set_column('A:A',14,titulo_2)
        ws.set_column('B:B',18,titulo_2)
        ws.set_column('C:C',13,titulo_2)
        ws.set_column('D:D',30,titulo_2)
        ws.set_column('E:E',28,titulo_2)
        ws.set_column('F:F',12,titulo_2)
        ws.set_column('G:G',12,titulo_2)
        ws.set_column('H:H',12,titulo_2)

        ws.write(0,0,'REPORTE DE RECIBOS POR HONORARIOS',titulo_1)

        ws.write(2,0,'FECHA DOCUMENTO DESDE:',titulo_2)
        ws.write(2,1,"%s"%(self.date_from and self.date_from.strftime("%d-%m-%Y") or ''),titulo_2)

        ws.write(3,0,'FECHA DOCUMENTO HASTA:',titulo_2)
        ws.write(3,1,"%s"%(self.date_to and self.date_to.strftime("%d-%m-%Y") or ''),titulo_2)

        ws.write(4,0,'RUC:',titulo_2)
        ws.write(4,1,self.company_id.vat or '',titulo_2)
        #ws.merge_range('A6:B6','RAZÓN SOCIAL:',titulo_2)
        ws.write(5,0,'RAZÓN SOCIAL:',titulo_2)
        ws.write(5,1,self.company_id.name or '',titulo_2)

        #Cabecera del detalle
        ws.write(7,0,'FECHA',titulo_3)
        ws.write(7,1,'NÚMERO',titulo_3)
        ws.write(7,2,'R.U.C',titulo_3)
        ws.write(7,3,'BENEFICIARIO',titulo_3)
        ws.write(7,4,'GLOSA',titulo_3)
        ws.write(7,5,'MONTO TOTAL' + self.company_id.currency_id.symbol,titulo_3)
        ws.write(7,6,'RETENCIÓN' + self.company_id.currency_id.symbol,titulo_3)
        ws.write(7,7,'PAGO' + self.company_id.currency_id.symbol,titulo_3)
        

        lines = self.get_records()

        row = 8

        #Detalle en moneda de la companía
        total_pago = 0.00
        monto_total = 0.00
        total_retencion_4ta = 0.00

        for line in lines:

            total_pago = total_pago + abs(line.amount_total_signed - line.amount_residual_signed)
            monto_total = monto_total + abs(line.amount_total_signed)
            
            total_retencion_4ta = total_retencion_4ta + abs(line.retencion_4ta)

            ws.write(row,0,line.invoice_date or '',titulo_5)

            ws.write(row,1,
                "%s-%s"%(line.l10n_pe_prefix_code or '',line.l10n_pe_invoice_number or '') or line.name or '',titulo_5)

            ws.write(row,2,line.partner_id.vat or ' ',titulo_5)

            ws.write(row,3,line.partner_id.name or ' ',titulo_5)

            ws.write(row,4,line.name or line.name or '',titulo_5)

            ws.write(row,5,abs(line.amount_total_signed or 0.00) or '',titulo_5)

            ws.write(row,6,abs(line.retencion_4ta or 0.00),titulo_5)

            ws.write(row,7,abs(line.amount_total_signed - line.amount_residual_signed) or 0.00, titulo_5)
            
            
            
            row += 1

        ws.write(row,4,"TOTALES",titulo_5)
        ws.write(row,5,monto_total,titulo_5)

        ws.write(row,6,total_retencion_4ta,titulo_5)

        ws.write(row,7,total_pago,titulo_5)

        workbook.close()
