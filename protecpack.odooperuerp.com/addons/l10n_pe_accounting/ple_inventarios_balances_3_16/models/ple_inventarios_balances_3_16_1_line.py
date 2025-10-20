import pytz
import calendar
import base64
from io import BytesIO, StringIO
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta
from odoo.addons import ple_base as tools

import logging
_logger=logging.getLogger(__name__)

class PleInventariosBalancesDetalleSaldoCuenta50CapitalLine(models.Model):
	_name='ple.inventarios.balances.3.16.1.line'

	ple_inventarios_balances_3_16_id=fields.Many2one("ple.inventarios.balances.3.16",string="id PLE", ondelete="cascade")
	
	periodo=fields.Char(string="Periodo PLE")
	importe_capital_social_participaciones = fields.Float(string="Importe Capital Social/Participaciones Sociales Periodo")
	valor_nominal_por_accion = fields.Float(string="Valor Nominal por Acción/Participación Social")
	numero_acciones_participaciones_sociales = fields.Float(string="Número Acciones/Participaciones Sociales")
	numero_acciones_participaciones_sociales_pagadas = fields.Float(string="Número Acciones/Participaciones Sociales Pagadas")
	indicador_estado_operacion=fields.Char(string="Estado Operación" , readonly=True, compute="compute_campo_indicador_estado_operacion", store=True)


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
