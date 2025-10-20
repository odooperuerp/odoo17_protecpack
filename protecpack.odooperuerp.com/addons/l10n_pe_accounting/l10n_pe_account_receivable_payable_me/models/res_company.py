from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class ResCompany(models.Model):
    _inherit = "res.company"


    property_account_payable_fees_id=fields.Many2one('account.account',
        string="Cuenta Recibo Honorarios por Pagar",
        domain="[('account_type', '=', 'liability_payable'), ('deprecated', '=', False)]")

    ###############################################################
    property_account_receivable_me_id=fields.Many2one('account.account',
        string="Cuenta por cobrar en ME",
        domain="[('account_type', '=', 'asset_receivable'), ('deprecated', '=', False)]",
        implied_group='base.group_multi_currency')

    property_account_payable_me_id=fields.Many2one('account.account',
        string="Cuenta por pagar en ME",
        domain="[('account_type', '=', 'liability_payable'), ('deprecated', '=', False)]",
        implied_group='base.group_multi_currency')


    property_account_payable_me_fees_id=fields.Many2one('account.account',
        string="Cuenta Recibo Honorarios por Pagar en ME",
        domain="[('account_type', '=', 'liability_payable'), ('deprecated', '=', False)]",
        implied_group='base.group_multi_currency')