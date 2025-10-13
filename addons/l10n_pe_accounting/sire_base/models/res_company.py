from odoo import models, fields, api, _

import logging
_logger = logging.getLogger(__name__)


class ResCompany(models.Model):
	_inherit = "res.company"

	client_id_portal_sunat = fields.Char(string="Client ID")
	client_secret_portal_sunat = fields.Char(string="Client secret")
	usuario_portal_sunat = fields.Char(string="Usuario SUNAT")
	clavesol_portal_sunat = fields.Char(string="Clave SOL")