# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError , ValidationError
import logging
from itertools import *
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)


class TemplateDUAInformacionReferencial(models.Model):
	_name = 'template.dua.informacion.referencial'
	_description = "Registro DUA - Plantilla de Conceptos Referenciales"

	company_id = fields.Many2one('res.company',
		string="Compañia", 
		default=lambda self: self.env['res.company']._company_default_get('account.invoice'),
		domain = lambda self: [('id', 'in',[i.id for i in self.env['res.users'].browse(self.env.user.id).company_ids] )])
	
	name = fields.Char(string="Nombre de Plantilla")

	conceptos_referencial_ids = fields.One2many('template.dua.informacion.referencial.line',
		'informacion_referencial_id',string="Conceptos Referenciales")