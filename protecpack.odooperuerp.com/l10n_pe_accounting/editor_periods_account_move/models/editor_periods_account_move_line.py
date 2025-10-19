from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
import logging
from itertools import *
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)

class EditorPeriodsAccountMoveLine(models.TransientModel):
	_name = 'editor.periods.account.move.line'
	_description = "Editor de Periodos en Asientos Contables (Detalles)"

	editor_periods_account_move_id = fields.Many2one("editor.periods.account.move", string="Editar Asiento Contable", ondelete="cascade")

	move_id=fields.Many2one('account.move',string="Asiento Contable")
	date=fields.Date(string="Fecha del Asiento",related="move_id.date",readonly=True)
	ref = fields.Char(string="Referencia",related="move_id.ref",readonly=True)

	original_period_id=fields.Many2one('account.period', string='Periodo Original',
		related="move_id.period_id",store=True)

	period_id = fields.Many2one('account.period', string='Periodo Nuevo')


	def onchange_massive_periodo(self):

		if self.editor_periods_account_move_id.massive_periodo:
			if self.editor_periods_account_move_id.massive_periodo=='delete':
				self.period_id = False
			elif self.editor_periods_account_move_id.massive_periodo=='automatic':

				if self.move_id:

					period_fiscalyear = self.move_id.find_period(self.move_id.date,self.move_id.company_id.id)
					
					if period_fiscalyear:
						self.period_id = period_fiscalyear[0].id
				else:
					self.period_id = False


	