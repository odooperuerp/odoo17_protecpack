from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
import logging
from itertools import *
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)

class EditorAccountAMLLine(models.Model):
	_name = 'editor.account.aml.line'
	_description = "Editor de cuentas en Apuntes Contables"

	editor_account_aml_id = fields.Many2one("editor.account.aml", string="Editar Apunte Contable", ondelete="cascade")

	move_line_id = fields.Many2one('account.move.line',string="Apunte Contable")

	move_id = fields.Many2one('account.move',string="Asiento Contable",
		related="move_line_id.move_id",readonly=True)
	
	journal_id = fields.Many2one('account.journal',string="Diario",
		related="move_line_id.journal_id",readonly=True)
	
	name = fields.Char(string="Etiqueta",related="move_line_id.name",readonly=True)
	
	date = fields.Date(string="Fecha", compute="compute_campo_date",readonly=True)
	
	old_account_id = fields.Many2one('account.account',string="Cuenta Original del Apunte",
		compute="compute_campo_old_account_id",readonly=True,store=True)
	
	new_account_id = fields.Many2one('account.account', string='Cuenta Nueva del Apunte')


	
	@api.depends('move_line_id')
	def compute_campo_date(self):
		for rec in self:
			rec.date=False
			if rec.move_line_id:
				rec.date=rec.move_line_id.date

	
	@api.depends('move_line_id')
	def compute_campo_old_account_id(self):
		for rec in self:
			rec.old_account_id=False
			if rec.move_line_id:
				rec.old_account_id=rec.move_line_id.account_id