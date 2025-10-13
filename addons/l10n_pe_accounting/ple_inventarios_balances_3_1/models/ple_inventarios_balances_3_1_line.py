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


class PleInventariosBalancesEstadoSituacionFinancieraLine(models.Model):
	_name='ple.inventarios.balances.3.1.line'

	ple_inventarios_balances_3_1_id=fields.Many2one("ple.inventarios.balances.3.1",
		string="id PLE", ondelete="cascade" ,readonly=True)
	
	periodo=fields.Char(string="Periodo PLE",readonly=True)

	codigo_catalogo_id=fields.Many2one("financial.statement.heading" , string="Catálogo",readonly=True)
	codigo_catalogo=fields.Char(string="Código Catálogo",readonly=True)
	rubro_estado_financiero = fields.Many2one('financial.statement.heading.line',
		string="Rubro Estado Financiero", readonly=True)
	codigo_rubro_estado_financiero = fields.Char(string="Código Rubro EEFF",
		readonly=True)
	grupo_del_rubro_id=fields.Many2one('group.heading.financial.statement', string="Grupo de Rubro")
	saldo_rubro_contable = fields.Float(string="Saldo",readonly=True)
	indicador_estado_operacion=fields.Char(string="Estado Operación",readonly=True)



	def _convert_object_date(self, date):
		if date:
			return date.strftime('%d/%m/%Y')
		else:
			return ''