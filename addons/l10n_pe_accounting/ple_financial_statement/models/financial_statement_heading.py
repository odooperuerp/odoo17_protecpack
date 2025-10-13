# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError , ValidationError

class FinancialStatementHeading(models.Model):
	_name = 'financial.statement.heading'
	_description = "Rubros de Estados Financieros"
	_rec_name = "name"

	company_id = fields.Many2one('res.company',
		string="Compañia", 
		default=lambda self: self.env['res.company']._company_default_get('account.invoice'),
		domain = lambda self: [('id', 'in',[i.id for i in self.env['res.users'].browse(self.env.user.id).company_ids] )])

	name=fields.Char(string="Nombre del Informe Financiero")
	code_report_ple=fields.Char(string="Código del Informe Financiero")
	economic_sector_sunat_id=fields.Many2one('economic.sector.sunat', string="Sector Económico")

	financial_statement_heading_line_ids=fields.One2many('financial.statement.heading.line',
		'financial_statement_heading_id',
		string="Detalle Rubros del Informe Financiero",
		ondelete="cascade")

	type_format_report=fields.Selection(selection=[('1','Formato Electrónico'),('2','Formato Impreso')],string="Formato de Reporte", required=True)