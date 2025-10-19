from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
import logging
from itertools import *
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)


class EditorJournalsAccountMoveLine(models.Model):
	_name = 'editor.journals.account.move.line'
	_description = "Editor de Diarios en Asientos Contables (Detalles)"

	editor_journals_account_move_id = fields.Many2one("editor.journals.account.move", string="Editar Asiento Contable", ondelete="cascade")


	move_id=fields.Many2one('account.move',string="Asiento Contable")

	ref = fields.Char(string="Referencia",related="move_id.ref",readonly=True)	

	date=fields.Date(string="Fecha del Asiento",related="move_id.date",readonly=True)

	original_journal_id=fields.Many2one('account.journal', string='Diario Original',
		related="move_id.journal_id",store=True)

	new_journal_id = fields.Many2one('account.journal', string='Diario Nuevo')