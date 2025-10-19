# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError , ValidationError
import logging
from itertools import *
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)


class TemplateDUAInformacionReferencialLine(models.Model):
	_name = 'template.dua.informacion.referencial.line'
	_description = "Registro DUA - Plantilla de Conceptos Referenciales - Conceptos"

	informacion_referencial_id = fields.Many2one('template.dua.informacion.referencial',
		string="Plantilla de Conceptos Referenciales",ondelete="cascade")

	name = fields.Char(string="Concepto")