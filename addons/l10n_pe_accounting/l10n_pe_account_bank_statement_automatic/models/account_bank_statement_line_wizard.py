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

class AccountBankStatementLineWizard(models.TransientModel):
    _name = 'account.bank.statement.line.wizard'
    _description = 'Crear lineas de Extracto Bancario'
    _check_company_auto = True


    move_line_ids = fields.Many2many('account.move.line',string="Movimientos Contables")
    company_id = fields.Many2one('res.company', required=True, readonly=True,string="Compañia")
    company_currency_id = fields.Many2one('res.currency', related='company_id.currency_id')
    total_account_move_line_ids = fields.Integer(string="Total de Movimientos seleccionados",
        compute='_compute_total_account_move_line_ids')
    journal_id = fields.Many2one('account.journal',required=True,string="Diario Contable",check_company=True)

    statement_id = fields.Many2one('account.bank.statement',string="Estado de Cuenta",check_company=True)

    only_diary_cash_bank = fields.Boolean(string="Solo Diarios de Caja/Banco",default=True)

    @api.depends('move_line_ids')
    def _compute_total_account_move_line_ids(self):
        for record in self:
            record.total_account_move_line_ids = len(record.move_line_ids or '')


    @api.constrains('move_line_ids','only_diary_cash_bank')
    def _check_journal(self):
        for wizard in self:
            if wizard.only_diary_cash_bank:
                if any(aml.journal_id.type not in ['cash','bank'] for aml in wizard.move_line_ids):
                    raise ValidationError("Solo se pueden generar lineas de extracto para movimientos con Diarios tipo Caja o Banco !")

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)

        _logger.info('\n\nCONTENIDO DEL CONTEXT\n\n')
        _logger.info(self.env.context)

        if not set(fields) & set(['journal_id', 'company_id']):
            return res

        if self.env.context.get('active_model') not in ['account.bank.statement','account.bank.statement.line'] or not self.env.context.get('active_ids'):
            raise UserError('Solo puede usarlo en Estados de Cuenta y Transacciones de Caja/Banco !')

        journal_id = self.env['account.journal'].browse(self.env.context['default_journal_id'])
        res['journal_id'] = journal_id.id

        res['company_id'] = journal_id.company_id.root_id.id

        return res


    ############################################################################################
    
    """@api.onchange('journal_id')
    def set_domain_for_provision_payment_id(self):
        if self.journal_id:
            records = []
            records = self.env['account.move.line'].search([
                ('move_id.state','=','posted'),
                ('account_id.reconcile','=',True),
                ('journal_id','=',self.journal_id.id)])

            res = {}
            res['domain'] = {'move_line_ids': [('id', 'in', [i.id for i in records])]}
            return res"""



    def create_bank_statement_line_data(self,line):
        values = {
            'statement_id':self.statement_id and self.statement_id.id or False,
            'journal_id':self.journal_id and self.journal_id.id or False,
            'date':line.date,
            'payment_ref':line.move_id.ref or line.name or line.ref or '',
            'partner_id':line.partner_id and line.partner_id.id or False,
            #'amount':line.amount_currency or 0.00,
            'ref':line.name or line.ref or '',
            'company_id':line.company_id.id or False,
        }

        if self.journal_id and self.journal_id.currency_id and self.journal_id.currency_id != self.company_currency_id:
            values['amount'] = line.amount_currency or 0.00
        else:
            values['amount'] = line.balance or 0.00


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