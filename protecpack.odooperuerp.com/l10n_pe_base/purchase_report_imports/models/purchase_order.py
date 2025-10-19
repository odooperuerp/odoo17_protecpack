# -*- coding: utf-8 -*-
import babel.dates

from odoo import api, fields, models, SUPERUSER_ID, _

# PURCHASE_ORDER_TYPE = [
#     ('po', 'Purchase order'),
#     ('so', 'Service order'),
#     ('io', 'Import order')
# ]

PURCHASE_ORDER_TYPE = [
    ('po', 'Orden de Compra'),
    ('so', 'Orden de Servicio'),
    ('io', 'Orden de Importación')
]

def get_purchase_order_type_name(key):
    for item in PURCHASE_ORDER_TYPE:
        if item[0] == key:
            return item[1]
    return None


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    
    purchase_type = fields.Selection(
        selection=PURCHASE_ORDER_TYPE,
        string='Type of purchase',
        tracking=3,
        default='po')

    supplier_contact_id = fields.Many2one('res.partner',string="Contacto de Proveedor")

    name_currency = fields.Char(string="Nombre de Moneda",compute="compute_campo_name_currency")

    """
    @api.depends('currency_id','partner_id','partner_id.lang')
    def compute_campo_name_currency(self):
        for rec in self:
            if rec.currency_id and rec.currency_id.name=='USD' and rec.partner_id and rec.partner_id.lang=='es_PE':
                rec.name_currency = "Dólares Americanos"
            else:
                rec.name_currency = rec.currency_id and rec.currency_id.currency_unit_label or ''
    """

    @api.onchange('partner_id')
    def onchange_domain_partner_id(self):
        for rec in self:
            if rec.partner_id:
                res = {}
                records = []
                records = self.env['res.partner'].search(
                    [('parent_id.id','=',rec.partner_id.id),('type','=','contact'),('active','=',True)])

                res['domain'] = {'supplier_contact_id': [('id', 'in', [i.id for i in records])]}
                return res
            else:
                return {'domain': {'supplier_contact_id':[]}}


    def _compute_display_document_type(self):
        super(PurchaseOrder, self)._compute_display_document_type()
        for record in self:
            purchase_type = get_purchase_order_type_name(self.purchase_type) \
                            or _('Purchase Order')
            if self.partner_id.lang == 'en_US' and self.purchase_type == 'po':
                purchase_type = 'Purchase Order'
            if self.partner_id.lang == 'en_US' and self.purchase_type == 'so':
                purchase_type = 'Service Order'
            if self.partner_id.lang == 'en_US' and self.purchase_type == 'io':
                purchase_type = 'Import Order'
            STATES = {
                "draft": _("Request for Purchase Quotation"),
                "sent": _("Request for Purchase Quotation"),
                "to approve": _("Request for Purchase Quotation"),
                "purchase": purchase_type,
                "done": purchase_type,
                "cancel": _(f"{purchase_type} cancelled"),
            }
            record.display_document_type = STATES[record.state]

    def get_formatted_date(self, date, locale='es_ES'):
        if not date:
            return ''
        month_name = babel.dates.format_date(date, format='MMMM', locale=locale)
        day = date.day
        year = date.year
        suffix = self._get_day_suffix(day)
        return f"{month_name} {day}{suffix} {year}"

    def _get_day_suffix(self, day):
        if 10 <= day % 100 <= 20:
            suffix = 'th'
        else:
            suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')
        return suffix

    