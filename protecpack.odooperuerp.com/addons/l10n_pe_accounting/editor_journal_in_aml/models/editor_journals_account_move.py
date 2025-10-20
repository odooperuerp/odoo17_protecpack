from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
import logging
from itertools import *
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)


class EditorJournalsAccountMove(models.Model):
	_name = 'editor.journals.account.move'
	_description = "Editor de Diarios en Asientos Contables"
	_rec_name = 'name'

	company_id = fields.Many2one('res.company',
		string="Compañia", 
		default=lambda self: self.env['res.company']._company_default_get('account.invoice'),
		domain=lambda self:[('id', 'in',[i.id for i in self.env['res.users'].browse(self.env.user.id).company_ids] )],
		readonly=True)
	########################################################################################################
	name = fields.Char(string="",default='Herramienta de actualización de Diarios en Asientos contables')
	
	state = fields.Selection(selection=[
		('draft','Borrador'),('done','Procesado')],
		readonly=True, string="Estado", default="draft")
	
	editor_journals_account_move_line_ids=fields.One2many('editor.journals.account.move.line',
		'editor_journals_account_move_id',string="Asientos Contables a Editar")

	buffer_account_move_ids = fields.Many2many('account.move','account_move_editor_rel',
		'move_id','editor_id' ,string="Asientos Contables Seleccionados",readonly=False,
		domain="[('state','=','posted')]")
	###### OPERACIONES MASIVAS

	massive_journal_id = fields.Many2one('account.journal',string="Diario")

	def name_get(self):
		result = []
		for rec in self:
			result.append((rec.id,'Herramienta de actualización de Diarios en Asientos contables'))
		return result

	def limpiar_buffer(self):
		for rec in self:
			rec.buffer_account_move_ids=None



	def add_lines(self):

		if self.buffer_account_move_ids:
			registro=[]
			for line in self.buffer_account_move_ids:
				registro.append({'move_id': line.id,'editor_journals_account_move_id':self.id})

			self.editor_journals_account_move_line_ids.create(registro)
			self.limpiar_buffer()
	##########################################################################
	def aplication_massive(self):
		if self.editor_journals_account_move_line_ids and self.massive_journal_id:
			self.editor_journals_account_move_line_ids.write({'new_journal_id':self.massive_journal_id.id or None})


	def update_account_move(self,move_id,journal_id):
		if move_id and journal_id:

			query_account_move_line = ""

			query_account_move_line += """update account_move_line set journal_id=%s"""%(journal_id.id or 'Null')
			query_account_move_line += """ where move_id=%s"""%(move_id.id)

			self.env.cr.execute(query_account_move_line)
			###########################################################################
			
			query_account_move = """update account_move set journal_id=%s"""%(journal_id.id or 'Null')

			query_account_move += """ where id=%s"""%(move_id.id)

			self.env.cr.execute(query_account_move)



	def update_account_move_massive(self):

		if self.state == 'draft':
			if self.editor_journals_account_move_line_ids:

				for line in self.editor_journals_account_move_line_ids:
					self.update_account_move(line.move_id,line.new_journal_id)
			else:
				raise UserError(_('NO SE ESTA PROCESANDO NINGÚN ASIENTO CONTABLE, PROCEDA AGREGANDO LINEAS !!'))

			self.state = 'done'
