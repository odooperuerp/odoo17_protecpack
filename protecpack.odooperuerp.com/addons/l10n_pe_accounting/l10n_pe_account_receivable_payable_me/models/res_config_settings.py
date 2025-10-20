from odoo import _, api, fields, models

import logging
_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"


    property_account_payable_fees_id=fields.Many2one('account.account',
        string="Cuenta Recibo Honorarios por Pagar",
        domain="[('account_type', '=', 'liability_payable'),('deprecated','=', False)]",
        related='company_id.property_account_payable_fees_id',
        readonly=False
        )


    property_account_receivable_me_id=fields.Many2one('account.account',
        string="Cuenta por cobrar ME",
        implied_group='base.group_multi_currency',
        domain="[('account_type','=','asset_receivable'),('deprecated','=',False)]",
        related='company_id.property_account_receivable_me_id',
        readonly=False
        )

    property_account_payable_me_id=fields.Many2one('account.account',
        string="Cuenta por pagar ME",
        implied_group='base.group_multi_currency',
        domain="[('account_type','=','liability_payable'),('deprecated','=',False)]",
        related='company_id.property_account_payable_me_id',
        readonly=False
        )


    property_account_payable_me_fees_id=fields.Many2one('account.account',
        string="Cuenta Recibo Honorarios por Pagar ME",
        implied_group='base.group_multi_currency',
        domain="[('account_type','=','liability_payable'),('deprecated','=',False)]",
        related='company_id.property_account_payable_me_fees_id',
        readonly=False
        )


    ##################################################################################################

    def sync_account_me_partners(self):
        
        self.with_context(force_company=self.company_id.id)
        partner_ids = self.env['res.partner'].sudo().search([('active','=',True),
            ('massive_update_account_me','=',True),('parent_id','in',[False,None,''])])
        
        for partner_id in partner_ids:

            partner_id.sudo().write({'property_account_receivable_me_id':self.property_account_receivable_me_id.id})
            partner_id.sudo().write({'property_account_payable_me_id':self.property_account_payable_me_id.id})
    

    def sync_account_fees_partners(self):
        self.with_context(force_company=self.company_id.id)
        partner_ids = self.env['res.partner'].sudo().search([('active','=',True),
            ('parent_id','in',[False,None,'']),('massive_update_account_fees','=',True)])
        
        for partner_id in partner_ids:
            partner_id.sudo().write({
                'property_account_payable_fees_id':self.property_account_payable_fees_id and self.property_account_payable_fees_id.id or False,
                'property_account_payable_me_fees_id':self.property_account_payable_me_fees_id and self.property_account_payable_me_fees_id.id or False})