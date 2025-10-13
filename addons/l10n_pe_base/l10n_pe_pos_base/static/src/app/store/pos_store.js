/** @odoo-module */

import { PosStore } from "@point_of_sale/app/store/pos_store";
import { patch } from "@web/core/utils/patch";


patch(PosStore.prototype, {
    // @Override
    async _flush_orders(orders, options) {
        var self = this;
        var result = await super._flush_orders(...arguments);
        if (Array.isArray(result)) {
            result.forEach((order) => {
                this.get_order().invoice_number = order.invoice_number;
                this.get_order().comprobante_origen = order.comprobante_origen;
                this.get_order().fecha_origen = order.fecha_origen;
                this.get_order().l10n_pe_edi_refund_reason = order.l10n_pe_edi_refund_reason;   
                this.get_order().l10n_pe_reason = order.l10n_pe_reason;
            });
        }
        return result
    },
});