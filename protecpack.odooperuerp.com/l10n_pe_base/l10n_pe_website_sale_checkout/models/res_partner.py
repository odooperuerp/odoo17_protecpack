from odoo import api, fields, models, tools, SUPERUSER_ID, _, Command

class ResPartner(models.Model):
    _inherit = "res.partner"

    require_invoice = fields.Boolean(string="Requiere Factura", default=False) 
    contact_vat = fields.Char("Documento de Identidad del contacto")
    contact_l10n_latam_identification_type_id = fields.Many2one("l10n_latam.identification.type",string="Tipo de documento de identidad del contacto")


    def create_company(self):
        self.ensure_one()
        if self.company_name:
            # Create parent company
            values = dict(name=self.company_name, is_company=True, vat=self.vat, l10n_latam_identification_type_id = self.l10n_latam_identification_type_id.id)
            values.update(self._update_fields_values(self._address_fields()))
            new_company = self.create(values)
            # Set new company as my parent
            self.write({
                'parent_id': new_company.id,
                'child_ids': [Command.update(partner_id, dict(parent_id=new_company.id)) for partner_id in self.child_ids.ids]
            })
        return True

    def check_vat_pe(self, vat):
        if self.l10n_latam_identification_type_id.l10n_pe_vat_code == "6":
            if len(vat) != 11 or not vat.isdigit():
                return False
            dig_check = 11 - (sum([int('5432765432'[f]) * int(vat[f]) for f in range(0, 10)]) % 11)
            if dig_check == 10:
                dig_check = 0
            elif dig_check == 11:
                dig_check = 1
            return int(vat[10]) == dig_check
            
        return True