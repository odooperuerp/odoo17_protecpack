from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import re

class ResPartner(models.Model):
    _inherit = "res.partner"


    massive_update_account_fees = fields.Boolean(
        string="Sujeto a actualización Masiva de cuentas de Recibo Honorario",
        default=True)


    property_account_payable_fees_id=fields.Many2one('account.account',
        string="Cuenta Recibo Honorarios por Pagar",
        domain="[('account_type', '=', 'liability_payable'), ('deprecated', '=', False)]",
        company_dependent=True)

    ######################################################
    massive_update_account_me = fields.Boolean(string="Sujeto a actualización Masiva de cuentas en ME",
        default=True)
    
    property_account_receivable_me_id=fields.Many2one('account.account',
        string="Cuenta por cobrar ME",
        implied_group='base.group_multi_currency',
        domain="[('account_type', '=', 'asset_receivable'), ('deprecated', '=', False)]",
        company_dependent=True)

    property_account_payable_me_id=fields.Many2one('account.account',
        string="Cuenta por pagar ME",
        implied_group='base.group_multi_currency',
        domain="[('account_type', '=', 'liability_payable'), ('deprecated', '=', False)]",
        company_dependent=True)


    massive_update_account_fees_me = fields.Boolean(string="Sujeto a actualización Masiva de cuentas de Recibo Honorario en ME",
        default=True)

    property_account_payable_me_fees_id=fields.Many2one('account.account',
        string="Cuenta Recibo Honorarios por Pagar ME",
        implied_group='base.group_multi_currency',readonly=False,
        domain="[('account_type', '=', 'liability_payable'), ('deprecated', '=', False)]",
        company_dependent=True)


    @api.model
    def _commercial_fields(self):
        return super(ResPartner, self)._commercial_fields() + \
            ['property_account_receivable_me_id', 'property_account_payable_me_id',
                'property_account_payable_fees_id','property_account_payable_me_fees_id']
