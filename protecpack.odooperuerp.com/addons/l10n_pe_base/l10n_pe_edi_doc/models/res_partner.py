from odoo import models, fields, api
from odoo.osv import expression

class ResPartner(models.Model):
    _inherit = "res.partner"
    
    l10n_pe_edi_address_type_code = fields.Char(string='Anexo', help='Código para establecimiento anexo')
    
    l10n_pe_nombre_comercial = fields.Char(string='Nombre Comercial', help='Nombre comercial')
    
    """
    @api.model
    def _name_search(self, name, domain=None, operator='ilike', limit=100,  order=None):
        domain = domain or []
        domain = ['|', ('l10n_pe_nombre_comercial', '=ilike', name + '%'), ('name', operator, name)]
        return self._search(domain, limit=limit,  order=order)
    """
    
    @api.model
    def _name_search(self, name, domain=None, operator='ilike', limit=100, order=None):
        domain = domain or []
        if name:
            name_domain = ['|','|', ('l10n_pe_nombre_comercial', operator, name + '%'), ('name', operator, name + '%'),('vat', operator, name + '%')]
            if operator in expression.NEGATIVE_TERM_OPERATORS:
                name_domain = ['&', '!'] + name_domain[1:]
            domain = domain + name_domain
        return self._search(domain, limit=limit, order=order)


    @api.depends('complete_name', 'email', 'vat', 'state_id', 'country_id', 'commercial_company_name','l10n_pe_nombre_comercial')
    @api.depends_context('show_address', 'partner_show_db_id', 'address_inline', 'show_email', 'show_vat', 'lang')
    def _compute_display_name(self):
        for partner in self:
            super(ResPartner, partner)._compute_display_name()
            if partner.l10n_pe_nombre_comercial:
                name = f"[{partner.l10n_pe_nombre_comercial}] {partner.display_name}"
                partner.display_name = name.strip()
    
    @api.model
    def get_official_distributors(self):
        distributors = self.search([('is_company', '=', True)], order='name asc')
        return distributors