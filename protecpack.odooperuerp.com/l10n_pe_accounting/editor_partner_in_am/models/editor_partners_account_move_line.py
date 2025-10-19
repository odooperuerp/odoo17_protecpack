from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
import logging
from itertools import *
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)


class EditorPartnersAccountMoveLine(models.Model):
	_name = 'editor.partners.account.move.line'
	_description = "Editor de Auxiliares en Asientos Contables (Detalles)"

	editor_partners_account_move_id = fields.Many2one("editor.partners.account.move",
		string="Editar Asiento Contable", ondelete="cascade")


	move_id=fields.Many2one('account.move',string="Asiento Contable")

	ref = fields.Char(string="Referencia",related="move_id.ref",readonly=True)	

	date=fields.Date(string="Fecha del Asiento",related="move_id.date",readonly=True)

	original_partner_id=fields.Many2one('res.partner', string='Auxiliar Original',
		related="move_id.partner_id",store=True)

	new_partner_id = fields.Many2one('res.partner', string='Auxiliar Nuevo')