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

class PleDiaryLine(models.Model):
	_name='ple.diary.line'

	ple_diary_id=fields.Many2one("ple.diary",string="id PLE", ondelete="cascade" )
	

	move_id=fields.Many2one("account.move",string="Asiento contable",readonly=True)
	move_line_id=fields.Many2one("account.move.line",string="Apuntes Contables",readonly=True)
	
	periodo_apunte=fields.Char(string="Periodo del apunte contable",readonly=True)
	asiento_contable=fields.Char(string="Nombre del asiento contable",readonly=True)
	m_correlativo_asiento_contable=fields.Char(string="M-correlativo asiento contable",readonly=True)
	#	compute="_compute_campo_m_correlativo_asiento_contable",store=True)# 
	
	codigo_cuenta_desagregado_id=fields.Many2one('account.account',
		string="Código cuenta contable desagregado",readonly=True)

	journal_id=fields.Many2one('account.journal',string="Diario",readonly=True)
	codigo_cuenta_desagregado=fields.Char(string="Código cuenta contable desagregado",readonly=True)
	codigo_unidad_operacion=fields.Char(string="Código unidad operación",default="")
	codigo_centro_costos=fields.Char(string="Código centro de costos",default="")
	tipo_moneda_origen= fields.Char(string="Tipo de Moneda de origen",readonly=True)
	tipo_doc_iden_emisor = fields.Char(string="Tipo Documento Identidad Emisor",readonly=True)
	num_doc_iden_emisor= fields.Char(string="Número Documento Identidad Emisor",readonly=True)
	tipo_comprobante_pago= fields.Char(string="Tipo de Comprobante Pago",readonly = True)

	num_serie_comprobante_pago= fields.Char(string="Número serie Comprobante Pago")
	num_comprobante_pago= fields.Char(string="Número Comprobante de Pago")

	fecha_contable= fields.Date(string="Fecha Contable",readonly = True)
	fecha_vencimiento = fields.Date(string="Fecha de vencimiento")
	fecha_operacion = fields.Date(string="Fecha de la operación o emisión",readonly = True)
	glosa = fields.Char(string="Glosa o descripción naturaleza de operación")
	glosa_referencial = fields.Char(string="Glosa referencial" , default="")
	movimientos_debe = fields.Float(string="Movimientos del Debe",readonly = True)
	movimientos_haber = fields.Float(string="Movimientos del Haber",readonly = True)
	dato_estructurado= fields.Char(string="Dato estructurado")
	indicador_estado_operacion= fields.Char(string="Dato estado operación")


	#@api.depends('move_line_id','move_id')
	#def _compute_campo_m_correlativo_asiento_contable(self):
	# Esta función asigna correlativos m1 ,m2 , m3..a los elementos de un asiento , teniendo en cuenta
	# que los apuntes contables estan ordenados por codigo cuenta
	#	for rec in self:
	#		if rec.move_id.line_ids:
	#			indice= sorted([(line.account_id.code or '',line.id) for line in rec.move_id.line_ids]).index((rec.move_line_id.account_id.code or '',rec.move_line_id.id))
	#			rec.m_correlativo_asiento_contable='M' + str(indice+1)