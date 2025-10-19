# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError , ValidationError

class FinancialStatementHeadingLine(models.Model):
	_name = 'financial.statement.heading.line'
	_description = "Detalle de Rubros de Estados Financieros"
	_order = "nro_rubro asc"
	_rec_name = "name"


	financial_statement_heading_id=fields.Many2one("financial.statement.heading", 
		string="Informe Financiero",readonly=True,ondelete="cascade")

	nro_rubro = fields.Integer(string="N° Rubro",required=True)
	name=fields.Char(string="Nombre Rubro estado Financiero",required=True)

	is_total=fields.Boolean(string="Es total?")
	is_title=fields.Boolean(string="Es Título")
	title=fields.Char(string="Título")
	
	code_sunat=fields.Char(string="Código Rubro Estado Financiero")
	
	group_heading_financial_statement_id=fields.Many2one('group.heading.financial.statement', string="Grupo de Rubro")

	calculation_type = fields.Selection(selection=[('manual','Manual'),('accounts','Por Grupo de Cuentas Asociadas'),('result_excersice','Resultado del Ejercicio')], 
		string="Tipo de Cálculo de Movimientos en Ejercicio",default='manual',required=True)

	account_ids=fields.Many2many('account.account','finantial_heading_account_rel','account_id','finantial_heading_line_id',string="Cuentas Asociadas al Rubro")
	movements_period = fields.Float(string="Movimientos en Ejercicio o Periodo")


	@api.onchange('is_title')
	def onchange_is_title(self):
		for rec in self:
			if rec.is_title:
				rec.title = rec.name or ''
			else:
				rec.title = ''