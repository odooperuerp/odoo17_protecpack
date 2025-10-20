from odoo import models,fields,api


class AccountMove(models.Model):
    _inherit = "account.move"
    
    def _get_invoiced_lot_values(self):
        self.ensure_one()

        lot_values = super(AccountMove, self)._get_invoiced_lot_values()
        for lot in lot_values:
            lot_id = lot.get('pos_lot_id',False)
            if lot_id:
                stock_lot_id = self.env["pos.pack.operation.lot"].browse(lot_id)
                lot.update({
                    "product_id": stock_lot_id.product_id.id
                })
        
        """
        if self.state == 'draft':
            return lot_values

        # user may not have access to POS orders, but it's ok if they have
        # access to the invoice
        for order in self.sudo().pos_order_ids:
            for line in order.lines:
                lots = line.pack_lot_ids or False
                if lots:
                    for lot in lots:
                        lot_values.append({
                            'product_id': lot.product_id.id,
                            'product_name': lot.product_id.name,
                            'quantity': line.qty if lot.product_id.tracking == 'lot' else 1.0,
                            'uom_name': line.product_uom_id.name,
                            'lot_name': lot.lot_name,
                            'pos_lot_id': lot.id,
                        })
        """
        return lot_values