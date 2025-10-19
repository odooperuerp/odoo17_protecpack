from odoo import fields, models, api

class Website(models.Model):
    _inherit = "website"
    
    show_address_in_checkout = fields.Boolean(
        string="Mostar dirección en el checkout",
        default=True
    )

    