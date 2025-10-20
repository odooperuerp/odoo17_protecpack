# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError , ValidationError
import logging
from itertools import *
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)


class TemplateDUAInformacionAnotableLine(models.Model):
	_name = 'template.dua.informacion.anotable.line'
	_description = "Registro DUA - Plantilla de información Anotable - Conceptos"

	informacion_anotable_id = fields.Many2one('template.dua.informacion.anotable',
		string="Plantilla de Conceptos Anotables",ondelete="cascade")

	#########################################################################
	product_id = fields.Many2one('product.product',string="Concepto")
	account_id = fields.Many2one('account.account',string="Cuenta Contable")
	tax_id = fields.Many2one('account.tax',string="Impuesto")
	type_calculo = fields.Selection(selection=[('porcentaje','Porcentaje'),('monto','Monto Fijo')],
		string="Tipo Cálculo",default='porcentaje')
	amount_porcentaje_monto = fields.Float(string="Porcentaje/Monto")
	type_concepto = fields.Selection(selection=[('gasto','Gasto'),('impuesto','Impuesto')],
		string="Tipo de Concepto",default='impuesto')

	#########################################################################

	@api.onchange('product_id')
	def onchange_account_id(self):
		for rec in self:
			if rec.product_id:
				rec.account_id = rec.product_id.property_account_expense_id or \
					(rec.product_id.categ_id and rec.product_id.categ_id.property_account_expense_categ_id) or False

	
	@api.onchange('product_id')
	def onchange_tax_id(self):
		for rec in self:
			if rec.product_id:
				rec.tax_id = rec.product_id.supplier_taxes_id and rec.product_id.supplier_taxes_id[0] or False

				
