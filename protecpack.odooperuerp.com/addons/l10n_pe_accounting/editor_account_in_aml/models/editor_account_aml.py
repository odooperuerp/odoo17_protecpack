from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
import logging
from itertools import *
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)

class EditorAccountAML(models.Model):
	_name = 'editor.account.aml'
	_inherit = 'mail.thread'
	_description = "Editor de Cuentas en Apuntes Contables"
	_rec_name = 'name'
	
	########################################################################################################
	company_id = fields.Many2one('res.company',
		string="Compañia", 
		default=lambda self: self.env['res.company']._company_default_get('account.invoice'),
		domain=lambda self:[('id', 'in',[i.id for i in self.env['res.users'].browse(self.env.user.id).company_ids] )],
		readonly=True)
	########################################################################################################
	name = fields.Char(string="",default='Herramienta de actualización de Cuentas en Apuntes contables')
	state = fields.Selection(selection=[
		('draft','Borrador'),('done','Procesado')],
		readonly=True, string="Estado", default="draft")


	editor_account_aml_line_ids=fields.One2many('editor.account.aml.line','editor_account_aml_id',
		string="Apuntes Contables a Editar")

	################################################################################################
	buffer_account_move_line_ids=fields.Many2many('account.move.line',
		string="Apuntes Contables Seleccionados", readonly=False,
		domain="[('move_id.state','=','posted')]")

	buffer_account_move_ids=fields.Many2many('account.move',
		string="Apuntes de Asientos Contables Seleccionados", readonly=False,
		domain="[('state','=','posted')]")
	
	###### OPERACIONES MASIVAS #####################################################################
	massive_account_id=fields.Many2one('account.account',string="Cuenta Masiva a Aplicar")

	
	def name_get(self):
		result = []
		for rec in self:
			result.append((rec.id,'Herramienta de actualización de Cuentas en Apuntes contables'))
		return result


	
	def limpiar_buffer(self):
		self.buffer_account_move_line_ids = None
		self.buffer_account_move_ids = None


	
	def add_lines(self):
		if self.buffer_account_move_line_ids:
			registro=[]
			for line in self.buffer_account_move_line_ids:
				registro.append({'move_line_id': line.id,'editor_account_aml_id':self.id})

			self.editor_account_aml_line_ids.create(registro)

		if self.buffer_account_move_ids:
			registro=[]
			for move in self.buffer_account_move_ids:
				for line in move.line_ids:
					registro.append({'move_line_id': line.id,'editor_account_aml_id':self.id})

			self.editor_account_aml_line_ids.create(registro)

		self.limpiar_buffer()


	def aplication_massive(self):
		if self.editor_account_aml_line_ids and self.massive_account_id:
			self.editor_account_aml_line_ids.write({'new_account_id':self.massive_account_id.id or None})


	def update_account_move_line(self,move_line_id,account_id):
		if move_line_id and account_id:
			query_account_move_line = ""
			query_account_move_line += """update account_move_line set account_id = %s"""%(account_id.id or 'Null')
			query_account_move_line += """ where id = %s"""%(move_line_id.id)

			self.env.cr.execute(query_account_move_line)
		###########################################################################

	
	def update_account_move_line_massive(self):
		if self.state == 'draft':
			if self.editor_account_aml_line_ids:

				for line in self.editor_account_aml_line_ids:
					self.update_account_move_line(line.move_line_id,line.new_account_id)
			else:
				raise UserError(_('NO SE ESTA PROCESANDO NINGÚN APUNTE CONTABLE, PROCEDA AGREGANDO LINEAS !'))

			self.state = 'done'
