# -*- coding: utf-8 -*-

from odoo import models, fields, api

class l10n_pe_sunat_table(models.Model):
    _name = 'l10n.pe.sunat.table'
    _description = 'Sunat Table'
    _rec_name = 'name'

    name = fields.Char(string='Name')
    description = fields.Char(string='Descripción')

    line_ids = fields.One2many('l10n.pe.catalogs.sunat','associated_table_id',string="Conceptos")