import pytz
import calendar
import base64
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta

import logging
_logger=logging.getLogger(__name__)

class SharesParticipationsLine(models.Model):
	_name='shares.participations.line'


	shares_participations_id=fields.Many2one('shares.participations',
		string="id Acciones y Participaciones", ondelete="cascade")
	periodo_incorporacion = fields.Date(string="Fecha Incorporación", required=True)
	accionista = fields.Many2one('res.partner', string="Socio/Accionista", required=True)
	tipo_documento_socio_accionista = fields.Char(string="Tipo Documento Socio/Accionista",
		compute="compute_campo_tipo_documento_socio_accionista", store=True, readonly=True)
	numero_documento_socio_accionista = fields.Char(string="Número Doc Identidad Socio/Accionista",
		compute="compute_campo_numero_documento_socio_accionista", store=True, readonly=True)
	razon_social_socio_accionista = fields.Char(string="Razón Social Socio/Accionista", 
		compute="compute_campo_razon_social_socio_accionista", store=True, readonly=True)

	tipo_accion = fields.Many2one('l10n.pe.catalogs.sunat',string="Código Tipo de Acción/Participación",
		domain="[('associated_table_id.name','=','TABLA 16')]",required=True)

	codigo_tipo_accion = fields.Char(string="Código Tipo de Acción/Participación", 
		compute="compute_campo_codigo_tipo_accion",store=True, readonly=True)

	numero_acciones = fields.Float(string="Número de Acciones/Participaciones", required=True)
	porcentaje_acciones = fields.Float(string="Porcentaje Total de Acciones/Sociales (%)", 
		compute="compute_campo_porcentaje_acciones",store=True, readonly=True)



	@api.depends('accionista')
	def compute_campo_tipo_documento_socio_accionista(self):
		for rec in self:
			if rec.accionista:
				rec.tipo_documento_socio_accionista = rec.accionista.l10n_latam_identification_type_id and rec.accionista.l10n_latam_identification_type_id.l10n_pe_vat_code or ''


	@api.depends('accionista')
	def compute_campo_numero_documento_socio_accionista(self):
		for rec in self:
			if rec.accionista:
				rec.numero_documento_socio_accionista = rec.accionista.vat or ''


	@api.depends('accionista')
	def compute_campo_razon_social_socio_accionista(self):
		for rec in self:
			if rec.accionista:
				rec.razon_social_socio_accionista = rec.accionista.name or ''


	@api.depends('shares_participations_id.shares_participations_line_ids')
	def compute_campo_porcentaje_acciones(self):
		for rec in self:
			if rec.numero_acciones:
				array_acciones=rec.shares_participations_id.shares_participations_line_ids.mapped('numero_acciones')
				if array_acciones:
					rec.porcentaje_acciones = rec.numero_acciones/sum(array_acciones)*100.00
				else:
					rec.porcentaje_acciones = 100.00



	@api.depends('tipo_accion')
	def compute_campo_codigo_tipo_accion(self):
		for rec in self:
			if rec.tipo_accion:
				rec.codigo_tipo_accion = rec.tipo_accion.code or ''