import calendar
from io import BytesIO, StringIO
from odoo import models, fields, api, _
from datetime import datetime, timedelta
import xlsxwriter
from odoo.exceptions import UserError , ValidationError
import logging
_logger=logging.getLogger(__name__)

class SharesParticipations(models.Model):
	_name='shares.participations'
	_description = "Modulo de Estructura de Acciones y Participaciones"
	_rec_name = "name"


	name = fields.Char(string="Descripción")

	shares_participations_line_ids=fields.One2many('shares.participations.line','shares_participations_id',
		string="Registro de Acciones y Participaciones")

	company_id = fields.Many2one('res.company',string="Compañia",
		default=lambda self: self.env['res.company']._company_default_get('account.invoice'),
		readonly=True,
		domain = lambda self: [('id', 'in',[i.id for i in self.env['res.users'].browse(self.env.user.id).company_ids])])

	total_capital = fields.Float(string="Capital Total", 
		compute="compute_campo_total_capital", store=True,readonly=True)
	valor_nominal_por_accion_participacion = fields.Float(string="Valor Nominal por Acción/Participación Social")



	def name_get(self):
		result = []
		for line in self:
			result.append((line.id, line.company_id.name or 'Nuevo Registro'))
		return result


	@api.model
	def name_search(self, name, args=None, operator='ilike', limit=100):
		args = args or []
		recs = self.search([('company_id', operator, name)] + args, limit=limit)
		return recs.name_get()



	@api.depends(
		'valor_nominal_por_accion_participacion',
		'shares_participations_line_ids.numero_acciones')
	def compute_campo_total_capital(self):
		for rec in self:
			if rec.shares_participations_line_ids:
				rec.total_capital = sum(rec.shares_participations_line_ids.mapped('numero_acciones'))*rec.valor_nominal_por_accion_participacion



	def _convert_object_date(self, date):
		# parametro date que retorna un valor vacio o el foramto 01/01/2100 dia/mes/año
		if date:
			return date.strftime('%d/%m/%Y')
		else:
			return ''


