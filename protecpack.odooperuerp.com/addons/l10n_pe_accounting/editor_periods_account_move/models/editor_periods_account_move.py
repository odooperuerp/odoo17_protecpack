from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
import logging
from itertools import *
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)

class EditorPeriodsAccountMove(models.Model):
	_name = 'editor.periods.account.move'
	_description = "Editor de Periodos en Asientos Contables"
	

	company_id = fields.Many2one('res.company',
		string="Compañia", 
		default=lambda self: self.env['res.company']._company_default_get('account.invoice'),
		domain = lambda self: [('id', 'in',[i.id for i in self.env['res.users'].browse(self.env.user.id).company_ids] )] , readonly=True)

	state = fields.Selection(selection=[
		('draft','Borrador'),('done','Procesado')],
		readonly=True, string="Estado", default="draft")

	###############################################################################################################################################################
	editor_periods_account_move_line_ids=fields.One2many('editor.periods.account.move.line','editor_periods_account_move_id',string="Asientos Contables a Editar")

	buffer_account_move_ids=fields.Many2many('account.move','account_move_editor_rel',
		'move_id','editor_id' ,string="Asientos Contables Seleccionados", readonly=False)

	###### OPERACIONES MASIVAS ######
	massive_periodo=fields.Selection(selection=[('delete','Eliminar'),('automatic','Cálculo Automático')],string="Periodo")


	def limpiar_buffer(self):
		self.buffer_account_move_ids=False


	def add_lines(self):
		if self.buffer_account_move_ids:
			registro=[]
			for line in self.buffer_account_move_ids:
				registro.append({'move_id': line.id,'editor_periods_account_move_id':self.id})

			self.editor_periods_account_move_line_ids.create(registro)

			self.limpiar_buffer()


	def aplication_massive(self):
		if self.editor_periods_account_move_line_ids:

			for line in self.editor_periods_account_move_line_ids:
				line.onchange_massive_periodo()


	def update_account_move(self,move_id,period_id):
		query_account_move_line = ""
		#if period_id:
		query_account_move_line += """update account_move_line set period_id=%s"""%(period_id.id or 'Null')
		query_account_move_line += """ where move_id=%s"""%(move_id.id)

		self.env.cr.execute(query_account_move_line)
		###########################################################################
		
		query_account_move = """update account_move set period_id=%s"""%(period_id.id or 'Null')

		query_account_move += """ where id=%s"""%(move_id.id)

		self.env.cr.execute(query_account_move)


	def update_account_move_massive(self):
		if self.state == 'draft':
			if self.editor_periods_account_move_line_ids:

				for line in self.editor_periods_account_move_line_ids:
					self.update_account_move(line.move_id,line.period_id)
			else:
				raise UserError(_('NO SE ESTA PROCESANDO NINGÚN ASIENTO CONTABLE, PROCEDA AGREGANDO LINEAS !'))

			self.state = 'done'

