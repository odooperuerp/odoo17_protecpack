# -*- coding: utf-8 -*-

from odoo import models, fields, api

class l10n_pe_catalogs_sunat(models.Model):
    _name = 'l10n.pe.catalogs.sunat'
    _description = 'Sunat Table Concepts'
    _rec_name = 'display_name'

    associated_table_id = fields.Many2one('l10n.pe.sunat.table',string='Tabla Asociada')

    code = fields.Char(string='Código')
    description = fields.Char(string='Descripción')
    reference = fields.Char(string='Referencia')
    active_concept = fields.Boolean(string='Activo',default=True)
    display_name = fields.Char(string="Nombre a Mostrar",compute="compute_campo_display_name",store=True)

    @api.depends('code','description')
    def compute_campo_display_name(self):
    	for rec in self:
    		rec.display_name = "%s-%s"%(rec.code or '',rec.description or '')