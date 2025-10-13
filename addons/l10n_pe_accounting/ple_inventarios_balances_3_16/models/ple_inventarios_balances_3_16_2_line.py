import pytz
import calendar
import base64
from io import BytesIO, StringIO
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta
from odoo.addons import ple_base as tools

class PleInventariosBalancesEstructuraParticipacionLine(models.Model):
	_name='ple.inventarios.balances.3.16.2.line'

	ple_inventarios_balances_3_16_id=fields.Many2one("ple.inventarios.balances.3.16",string="id PLE", ondelete="cascade")
	
	periodo=fields.Char(string="Periodo PLE")
	tipo_documento_socio_accionista = fields.Char(string="Tipo Doc Identidad Socio/Accionista")
	numero_documento_socio_accionista = fields.Char(string="Número Doc Identidad Socio/Accionista")
	tipo_accion = fields.Char(string="Tipo Acción")
	codigo_tipo_accion = fields.Char(string="Código Tipo de Acción/participación")
	razon_social_socio_accionista = fields.Char(string="Razón Social Socio/Accionista")
	numero_acciones = fields.Float(string="Número de Acciones/Participaciones")
	porcentaje_total_participaciones = fields.Float(string="Porcentaje Total Acciones/Participaciones Sociales", compute="compute_campo_porcentaje_total_participaciones")
	indicador_estado_operacion=fields.Char(string="Estado Operación" , readonly=True, compute="compute_campo_indicador_estado_operacion", store=True)


	@api.depends('ple_inventarios_balances_3_16_id','numero_acciones')
	def compute_campo_porcentaje_total_participaciones(self):
		for rec in self:
			if rec.ple_inventarios_balances_3_16_id and rec.numero_acciones:
				array_acciones=rec.ple_inventarios_balances_3_16_id.ple_inventarios_balances_3_16_2_line_ids.mapped('numero_acciones')
				if array_acciones:
					rec.porcentaje_total_participaciones = rec.numero_acciones/sum(array_acciones)*100.00
				else:
					rec.porcentaje_total_participaciones = 100.00



	@api.depends('ple_inventarios_balances_3_16_id')
	def compute_campo_indicador_estado_operacion(self):
		for rec in self:
			if rec.ple_inventarios_balances_3_16_id:
				rec.indicador_estado_operacion ='1'


	def _convert_object_date(self, date):
		if date:
			return date.strftime('%d/%m/%Y')
		else:
			return ''