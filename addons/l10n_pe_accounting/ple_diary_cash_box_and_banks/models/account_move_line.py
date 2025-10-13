# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError , ValidationError

class AccountMoveLine(models.Model):
	_inherit = 'account.move.line'

	declared_ple_0101_0102 = fields.Boolean(string="Registro declarado en PLE's :0101-0102",
		copy=False)