# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError , ValidationError

class AccountMove(models.Model):
	_inherit = 'account.move'

	declared_ple = fields.Boolean(string="Registro declarado" , copy=False)