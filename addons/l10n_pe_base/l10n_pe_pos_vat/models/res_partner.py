from odoo import models,fields,api
from odoo.exceptions import UserError
import re

patron_ruc = re.compile('[12]\d{10}$')
patron_dni = re.compile('\d{8}$')

class ResPartner(models.Model):
    _inherit = "res.partner"

    anonymous_customer = fields.Boolean(string="Cliente Varios",default=False)
    
    def write(self, values):
        for record in self:
            if record.anonymous_customer and not self.env.user.has_group('l10n_pe_pos_vat.group_base_allow_edit_anonymous_customer'):
                raise UserError("No se puede modificar un cliente varios")
        return super(ResPartner, self).write(values)

    def unlink(self):
        for record in self:
            if record.anonymous_customer and not self.env.user.has_group('l10n_pe_pos_vat.group_base_allow_edit_anonymous_customer'):
                raise UserError("El cliente varios no puede ser eliminado, sólo puede ser archivado")
        return super(ResPartner, self).unlink()
    



    @api.model
    def create_from_ui(self, partner):
        if partner.get('image_1920'):
            partner['image_1920'] = partner['image_1920'].split(',')[1]
        partner_id = partner.pop('id', False)
        
        if partner_id:  # Modifying existing partner
            self.browse(partner_id).write(partner)
        else:
            partner_vat = partner.get("vat")

            if patron_ruc.match(partner_vat) or patron_dni.match(partner_vat):
                partner_result = self.search([('vat', '=', partner_vat), ("vat", "!=", False)], limit=1)
                if partner_result.exists():
                    partner_result.write(partner)
                    partner_id = partner_result.id
                else:
                    partner_id = self.create(partner).id
            else:
                partner_id = self.create(partner).id
        
        return partner_id