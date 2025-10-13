# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError , ValidationError
import logging
from itertools import *
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)


class TemplateDUAInformacionAnotable(models.Model):
	_name = 'template.dua.informacion.anotable'
	_description = "Registro DUA - Plantilla de información Anotable"

	company_id = fields.Many2one('res.company',
		string="Compañia", 
		default=lambda self: self.env['res.company']._company_default_get('account.invoice'),
		domain = lambda self: [('id', 'in',[i.id for i in self.env['res.users'].browse(self.env.user.id).company_ids] )])
	
	name = fields.Char(string="Nombre de Plantilla")

	conceptos_anotable_ids = fields.One2many('template.dua.informacion.anotable.line',
		'informacion_anotable_id',string="Conceptos Anotables")