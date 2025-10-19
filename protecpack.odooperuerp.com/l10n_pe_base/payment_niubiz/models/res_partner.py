
from datetime import datetime
from odoo import _, api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    niubiz_user_token = fields.Char('Niubiz User Token UUID [Tokenización]', 
        help="User Token para el servicio de tokenización de Niubiz")
    niubiz_user_token_pw = fields.Char('Niubiz User Token UUID [Pago Web]',
        help="User Token para el servicio de Pago Web de Niubiz")
    first_name = fields.Char(string = "Name")
    last_name = fields.Char(string = "Last Name")
    niubiz_regular_client = fields.Integer('Niubiz Regular Client',
        help="Es 1 cuando el cliente es frecuente y por defecto es 0 para clientes que realizan pagos por primera vez.")
    niubiz_days_since_register = fields.Integer('Niubiz days since register',
        compute='_compute_niubiz_days_since_register')
    
    @api.depends('create_date')
    def _compute_niubiz_days_since_register(self):
        fecha_actual = datetime.now()
        diferencia_dias = (fecha_actual - self.create_date).days
        self.niubiz_days_since_register = diferencia_dias + 1
