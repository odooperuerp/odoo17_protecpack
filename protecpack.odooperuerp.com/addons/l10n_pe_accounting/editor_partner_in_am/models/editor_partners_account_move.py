from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
import logging
from itertools import *
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)


class EditorPartnersAccountMove(models.Model):
	_name = 'editor.partners.account.move'
	_description = "Editor de Auxiliares en Asientos Contables"
	_rec_name = 'name'

	company_id = fields.Many2one('res.company',
		string="Compañia", 
		default=lambda self: self.env['res.company']._company_default_get('account.invoice'),
		domain=lambda self:[('id', 'in',[i.id for i in self.env['res.users'].browse(self.env.user.id).company_ids] )],
		readonly=True)
	########################################################################################################
	name = fields.Char(string="",default='Herramienta de actualización de Auxiliares en Asientos contables')
	
	state = fields.Selection(selection=[
		('draft','Borrador'),('done','Procesado')],
		readonly=True, string="Estado", default="draft")
	
	editor_partners_account_move_line_ids=fields.One2many('editor.partners.account.move.line',
		'editor_partners_account_move_id',string="Asientos Contables a Editar")

	buffer_account_move_ids = fields.Many2many('account.move','editor_partner_account_move_rel',
		'move_id','editor_id' ,string="Asientos Contables Seleccionados",readonly=False,
		domain="[('state','=','posted')]")
	###### OPERACIONES MASIVAS

	massive_partner_id = fields.Many2one('res.partner',string="Auxiliar")

	def name_get(self):
		result = []
		for rec in self:
			result.append((rec.id,'Herramienta de actualización de Auxiliares en Asientos contables'))
		return result


	def limpiar_buffer(self):
		for rec in self:
			rec.buffer_account_move_ids=None


	def add_lines(self):

		if self.buffer_account_move_ids:
			registro=[]
			for line in self.buffer_account_move_ids:
				registro.append({'move_id': line.id,'editor_partners_account_move_id':self.id})

			self.editor_partners_account_move_line_ids.create(registro)
			self.limpiar_buffer()

	##########################################################################

	def aplication_massive(self):
		if self.editor_partners_account_move_line_ids and self.massive_partner_id:
			self.editor_partners_account_move_line_ids.write({'new_partner_id':self.massive_partner_id.id or None})


	def update_account_move(self,move_id,partner_id):
		if move_id and partner_id:

			query_account_move_line = ""

			query_account_move_line += """update account_move_line set partner_id=%s"""%(partner_id.id or 'Null')
			query_account_move_line += """ where move_id=%s"""%(move_id.id)

			self.env.cr.execute(query_account_move_line)
			###########################################################################
			
			query_account_move = """update account_move set partner_id=%s"""%(partner_id.id or 'Null')

			query_account_move += """ where id=%s"""%(move_id.id)

			self.env.cr.execute(query_account_move)



	def update_account_move_massive(self):

		if self.state == 'draft':
			if self.editor_partners_account_move_line_ids:

				for line in self.editor_partners_account_move_line_ids:
					self.update_account_move(line.move_id,line.new_partner_id)
			else:
				raise UserError(_('NO SE ESTA PROCESANDO NINGÚN ASIENTO CONTABLE, PROCEDA AGREGANDO LINEAS !!'))

			self.state = 'done'
