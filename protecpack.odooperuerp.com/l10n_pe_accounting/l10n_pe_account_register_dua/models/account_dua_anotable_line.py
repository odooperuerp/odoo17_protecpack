# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError , ValidationError
import logging
from itertools import *
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)


class AccountDUAAnotableLine(models.Model):
	_name = 'account.dua.anotable.line'
	_description = "Conceptos Anotables en Registro de DUA"

	company_id = fields.Many2one('res.company',
		string="Compañia",
		default=lambda self: self.env['res.company']._company_default_get('account.invoice'),
		domain=lambda self: [('id', 'in', [i.id for i in self.env['res.users'].browse(self.env.user.id).company_ids])])

	dua_id = fields.Many2one('account.registro.dua',string="Registro de DUA",ondelete="cascade")

	#########################################################################

	product_id = fields.Many2one('product.product',string="Concepto")
	account_id = fields.Many2one('account.account',string="Cuenta Contable")
	tax_id = fields.Many2one('account.tax',string="Impuesto")
	type_concepto = fields.Selection(selection=[('gasto','Gasto'),('impuesto','Impuesto')],
		string="Tipo de Concepto",default='impuesto')

	#########################################################################
	amount = fields.Float(string="Monto")

