# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError , ValidationError
import logging
from itertools import *
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)


class AccountDUAReferencialLine(models.Model):
	_name = 'account.dua.referencial.line'
	_description = "Conceptos Referenciales en Registro de DUA"

	company_id = fields.Many2one('res.company',
		string="Compañia",
		default=lambda self: self.env['res.company']._company_default_get('account.invoice'),
		domain=lambda self: [('id', 'in', [i.id for i in self.env['res.users'].browse(self.env.user.id).company_ids])])

	dua_id = fields.Many2one('account.registro.dua',
		string="Registro de DUA",ondelete="cascade")

	#############################################################################################
	name = fields.Char(string="Concepto")
	amount = fields.Float(string="Monto")