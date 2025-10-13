from odoo import tools
from odoo import api, fields, models


class AccountReceivableReportCurrentDateLine(models.TransientModel):
    _name = "account.receivable.report.current.date.line"
    _description = "Reporte de Cuentas por Cobrar a la Fecha"
    _rec_name = 'move_line_id'
    _order = "date_maturity desc"


    wizard_account_receivable_report_current_date_id = fields.Many2one('wizard.account.receivable.report.current.date',
        string="reporte de CxP a la Fecha",ondelete="cascade",readonly=True)


    company_id = fields.Many2one('res.company',string="Compañia",readonly=True)
    move_id = fields.Many2one('account.move',string="Asiento Contable",readonly=True)
    move_line_id = fields.Many2one('account.move.line',string="Apunte Contable",readonly=True)
    date_maturity = fields.Date(string="Fecha Vencimiento",readonly=True)
    date_emission = fields.Date(string="Fecha Emisión",readonly=True)
    date = fields.Date(string="Fecha Registro",readonly=True)
    currency_id = fields.Many2one('res.currency',string="Moneda",readonly=True)
    company_id = fields.Many2one('res.company',string="Compañia",readonly=True)
    company_currency_id = fields.Many2one('res.currency',string="",readonly=True)
    balance = fields.Monetary(string="Monto MN",readonly=True,currency_field='company_currency_id')
    amount_currency = fields.Monetary(string="Monto ME",readonly=True,currency_field='currency_id')
    amount_residual = fields.Monetary(string="Saldo MN",readonly=True,currency_field='company_currency_id')
    amount_residual_currency = fields.Monetary(string="Saldo ME",readonly=True,currency_field='currency_id')
    journal_id = fields.Many2one('account.journal',string="Diario",readonly=True)
    partner_id = fields.Many2one('res.partner',string="Socio",readonly=True)
    account_id = fields.Many2one('account.account',string="Cuenta",readonly=True)
    ref = fields.Char(string="Referencia",readonly=True)
    l10n_latam_document_type_id = fields.Many2one('l10n_latam.document.type',string="Tipo Doc",
        related='move_line_id.l10n_latam_document_type_id',store=True,readonly=True)
    l10n_pe_prefix_code = fields.Char(string="N° Serie",readonly=True)
    l10n_pe_invoice_number = fields.Char(string="Correlativo",readonly=True)
    fecha_actual = fields.Monetary(string="A Fecha Actual",readonly=True,currency_field='company_currency_id')
    rango_1_30 = fields.Monetary(string="1-30",readonly=True,currency_field='company_currency_id')
    rango_31_60 = fields.Monetary(string="31-60",readonly=True,currency_field='company_currency_id')
    rango_61_90 = fields.Monetary(string="61-90",readonly=True,currency_field='company_currency_id')
    rango_91_120 = fields.Monetary(string="91-120",readonly=True,currency_field='company_currency_id')
    rango_mas_antiguos = fields.Monetary(string="Más Antiguos",readonly=True,currency_field='company_currency_id')


    def button_view_account_move(self):
        if self.move_id:
            return {
               'name': 'Asiento Contable',
                'view_mode': 'form',
                'res_model': 'account.move',
                'res_id': self.move_id.id,
                'type': 'ir.actions.act_window',
                'context': {
                    'company_id': self.company_id.id,
                }
            }