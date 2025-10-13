from odoo import api, fields, models, _
from datetime import datetime, timedelta
from odoo import tools
from odoo.exceptions import UserError , ValidationError

class WizardAccountPayableReportCurrentDate(models.TransientModel):
    _name = "wizard.account.payable.report.current.date"
    _description = "Reporte de Cuentas por Pagar a la Fecha"

    #######################################
    company_id = fields.Many2one('res.company',
        string="Compañia", 
        default=lambda self: self.env['res.company']._company_default_get('account.invoice'),
        domain = lambda self: [('id', 'in',[i.id for i in self.env['res.users'].browse(self.env.user.id).company_ids] )],readonly=True)
    
    type_report = fields.Selection(
        selection=[('partner','Agrupado por Socio'),('account','Agrupado por Cuenta'),('partner_account','Agrupado por Socio-Cuenta')],
        string="Criterio",default='partner_account',required=True)


    line_ids = fields.One2many('account.payable.report.current.date.line',
        'wizard_account_payable_report_current_date_id',string="Detalles de Reporte CxP a la Fecha")
    #######################################

    def get_query_account_payable(self):

        query = """
                select 
                aml.id as move_line_id,
                aml.company_id as company_id,
                aml.move_id as move_id,
                aml.date_maturity as date_maturity,
                aml.date_emission as date_emission,
                aml.date as date,
                aml.balance as balance,
                aml.amount_currency as amount_currency,
                aml.amount_residual as amount_residual,
                aml.company_id as company_id, 
                
                case 
                    when aml.currency_id != aml.company_currency_id then aml.amount_residual_currency
                    else 0.00
                end amount_residual_currency,

                aml.currency_id as currency_id,
                aml.company_currency_id as company_currency_id,
                aml.journal_id as journal_id,
                aml.partner_id as partner_id,
                aml.account_id as account_id,
                aml.ref as ref,
                aml.l10n_pe_prefix_code as l10n_pe_prefix_code,
                aml.l10n_pe_invoice_number as l10n_pe_invoice_number,
                
                case when aml.date_maturity is not null then 
                    case when CURRENT_DATE <= aml.date_maturity then aml.amount_residual
                    else 0.00 end
                else
                    case when CURRENT_DATE <= aml.date then aml.amount_residual
                    else 0.00 end
                end fecha_actual,
                        
                case when aml.date_maturity is not null then 
                    case when aml.date_maturity <= (current_date - interval '1 day')::DATE and 
                    aml.date_maturity >= (current_date - interval '30 day')::DATE then aml.amount_residual
                    else 0.00 end
                else
                    case when aml.date <= (current_date - interval '1 day')::DATE and 
                    aml.date >= (current_date - interval '30 day')::DATE then aml.amount_residual
                    else 0.00 end
                end rango_1_30,
                    
                case when aml.date_maturity is not null then 
                    case when aml.date_maturity <= (current_date - interval '31 day')::DATE and 
                        aml.date_maturity >= (current_date - interval '60 day')::DATE then aml.amount_residual
                        else 0.00 end
                else
                    case when aml.date <= (current_date - interval '31 day')::DATE and 
                        aml.date >= (current_date - interval '60 day')::DATE then aml.amount_residual
                        else 0.00 end 
                end rango_31_60,
                    
                case when aml.date_maturity is not null then 
                    case when aml.date_maturity <= (current_date - interval '61 day')::DATE and 
                        aml.date_maturity >= (current_date - interval '90 day')::DATE then aml.amount_residual
                        else 0.00 end
                else
                    case when aml.date <= (current_date - interval '61 day')::DATE and 
                        aml.date >= (current_date - interval '90 day')::DATE then aml.amount_residual
                        else 0.00 end 
                end rango_61_90,
                    
                case when aml.date_maturity is not null then 
                    case when aml.date_maturity <= (current_date - interval '91 day')::DATE and 
                        aml.date_maturity >= (current_date - interval '120 day')::DATE then aml.amount_residual
                        else 0.00 end
                else
                    case when aml.date <= (current_date - interval '91 day')::DATE and 
                        aml.date >= (current_date - interval '120 day')::DATE then aml.amount_residual
                        else 0.00 end 
                end rango_91_120,
                            
                case when aml.date_maturity is not null then 
                    case when aml.date_maturity <= (current_date - interval '121 day')::DATE then aml.amount_residual 
                        else 0.00 end
                else
                    case when aml.date <= (current_date - interval '121 day')::DATE then aml.amount_residual 
                        else 0.00 end 
                end rango_mas_antiguos
                    
                from account_move_line as aml 
                join account_move am on am.id=aml.move_id
                join account_account acac on acac.id = aml.account_id 
                where acac.account_type ='liability_payable' and 
                    am.state='posted' and 
                    (aml.amount_residual != 0.00 or aml.amount_residual_currency != 0.00) and
                    aml.company_id = %s """ % (self.company_id.id or False)

        return query



    def button_view_tree_account_payable(self):

        self.ensure_one()

        self.line_ids.unlink()
        
        query_payable = self.get_query_account_payable()
        self.env.cr.execute(query_payable)

        records_payable = self.env.cr.dictfetchall()

        registro=[]
        
        for line in records_payable:
            registro.append((0,0,{
                'move_id':line['move_id'] or False,
                'company_id':line['company_id'] or False,
                'move_line_id':line['move_line_id'] or False,
                'date_maturity':line['date_maturity'] or False,
                'date_emission':line['date_emission'] or False,
                'date':line['date'] or False,
                'currency_id':line['currency_id'] or False,
                'company_id':line['company_id'] or False,
                'company_currency_id':line['company_currency_id'] or False,
                'balance':line['balance'] or False,
                'amount_residual':line['amount_residual'] or False,
                'amount_residual_currency':line['amount_residual_currency'] or False,
                'journal_id':line['journal_id'] or False,
                'partner_id':line['partner_id'] or False,
                'account_id':line['account_id'] or False,
                'ref':line['ref'] or False,
                'l10n_pe_prefix_code':line['l10n_pe_prefix_code'] or False,
                'l10n_pe_invoice_number':line['l10n_pe_invoice_number'] or False,
                'fecha_actual':line['fecha_actual'] or False,
                'rango_1_30':line['rango_1_30'] or False,
                'rango_31_60':line['rango_31_60'] or False,
                'rango_61_90':line['rango_61_90'] or False,
                'rango_91_120':line['rango_91_120'] or False,
                'rango_mas_antiguos':line['rango_mas_antiguos'] or False
                }))
        
        self.line_ids = registro
        

        view = self.env.ref('account_receivable_and_payable_reports.view_tree_account_payable_report_current_date_line')

        if self.line_ids:
            if self.type_report=='partner':
                diccionario = {
                    'name': 'Cuentas por Pagar a la Fecha',
                    'view_type': 'form',
                    'view_mode': 'tree,form',
                    'res_model': 'account.payable.report.current.date.line',
                    'view_id': view.id,
                    'views': [(view.id,'tree')],
                    'type': 'ir.actions.act_window',
                    'domain': [('id', 'in', [i.id for i in self.line_ids] or [])],
                    'context':{
                        'search_default_group_partner_id':1,
                        }}
                return diccionario

            elif self.type_report=='account':
                diccionario = {
                    'name': 'Cuentas por Pagar a la Fecha',
                    'view_type': 'form',
                    'view_mode': 'tree,form',
                    'res_model': 'account.payable.report.current.date.line',
                    'view_id': view.id,
                    'views': [(view.id,'tree')],
                    'type': 'ir.actions.act_window',
                    'domain': [('id', 'in', [i.id for i in self.line_ids] or [])],
                    'context':{
                        'search_default_group_account_id':1,
                        }
                }
                return diccionario

            elif self.type_report=='partner_account':
                diccionario = {
                    'name': 'Cuentas por Pagar a la Fecha',
                    'view_type': 'form',
                    'view_mode': 'tree,form',
                    'res_model': 'account.payable.report.current.date.line',
                    'view_id': view.id,
                    'views': [(view.id,'tree')],
                    'type': 'ir.actions.act_window',
                    'domain': [('id', 'in', [i.id for i in self.line_ids] or [])],
                    'context':{
                        'search_default_group_partner_id':1,
                        'search_default_group_account_id':1,
                        }
                }
                return diccionario

