# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError , ValidationError

class AccountMoveLine(models.Model):
	_inherit = 'account.move.line'

	declared_ple_0301 = fields.Boolean(string="Registro declarado en PLE-0301",copy=False)
