from odoo import fields,models,api
from datetime import datetime, timedelta
from odoo.exceptions import UserError , ValidationError
from odoo.tools.float_utils import float_repr
from odoo.tools import groupby
from collections import defaultdict
from markupsafe import Markup, escape
from odoo.tools import frozendict
import json

import logging
_logger = logging.getLogger(__name__)

class AccountBankStatementAutomaticWizard(models.TransientModel):
    _name = 'account.bank.statement.automatic.wizard'
    _description = 'Crear lineas de Extracto Bancario'
    _check_company_auto = True


    move_line_ids = fields.Many2many('account.move.line',string="Movimientos Contables")
    company_id = fields.Many2one('res.company', required=True, readonly=True,string="Compañia")
    company_currency_id = fields.Many2one('res.currency', related='company_id.currency_id')
    total_account_move_line_ids = fields.Integer(string="Total de Movimientos seleccionados",
        compute='_compute_total_account_move_line_ids')
    journal_ids = fields.Many2many('account.journal',required=True,string="Diarios Contables",store=True,
        check_company=True,
        compute="_compute_journal_ids")


    @api.depends('move_line_ids')
    def _compute_journal_ids(self):
        for record in self:
            record.journal_ids = record.move_line_ids.mapped('journal_id.id')


    @api.depends('move_line_ids')
    def _compute_total_account_move_line_ids(self):
        for record in self:
            record.total_account_move_line_ids = len(record.move_line_ids or '')


    @api.constrains('move_line_ids')
    def _check_journal(self):
        for wizard in self:
            if any(aml.journal_id.type not in ['cash','bank'] for aml in wizard.move_line_ids):
                raise ValidationError(_("Solo se pueden generar lineas de extracto para movimientos con Diarios tipo Caja o Banco !"))

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        if not set(fields) & set(['move_line_ids', 'company_id']):
            return res

        if self.env.context.get('active_model') != 'account.move.line' or not self.env.context.get('active_ids'):
            raise UserError(_('Solo puede usarlo en Apuntes Contables !'))

        move_line_ids = self.env['account.move.line'].browse(self.env.context['active_ids'])
        res['move_line_ids'] = [(6, 0, move_line_ids.ids)]

        if any(line.company_id.root_id != move_line_ids[0].company_id.root_id for line in move_line_ids):
            raise UserError(_('No puede utilizar esta herramienta en asientos de diario que pertenecen a diferentes compañias !'))
        res['company_id'] = move_line_ids[0].company_id.root_id.id

        return res



    def create_bank_statement_line_data(self,line):
        values = {
            'journal_id':line.journal_id and line.journal_id.id or False,
            'date':line.date,
            'payment_ref':line.move_id.ref or line.name or '',
            'partner_id':line.partner_id and line.partner_id.id or False,
            'amount':line.amount_currency or 0.00,
            'ref':line.name or '',
            'company_id':line.company_id.id or False,
        }

        if line.payment_id:
            if 'operation_number' in line.payment_id._fields and line.payment_id.operation_number:
                values.update(operation_number = line.payment_id.operation_number or '')
        else:
            if line.operation_number:
                values.update(operation_number = line.operation_number or '')

        return values



    def do_action_generate_account_bank_statement_line(self):
        for aml in self.move_line_ids:
            values = self.create_bank_statement_line_data(aml)
            statement_line = self.env['account.bank.statement.line'].create(values)