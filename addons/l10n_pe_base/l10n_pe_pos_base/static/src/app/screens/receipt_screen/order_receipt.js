/** @odoo-module */

import { Order } from "@point_of_sale/app/store/models";
import { patch } from "@web/core/utils/patch";

const nc_type = {
        "01":"Anulación",
        "02":"Error en el RUC",
        "04":"Descuento global",
        "05":"Descuento por item",
        "06":"Devolución total",
        "07":"Devolución por item",
        "10":"Otros conceptos"
}

patch(Order.prototype, {
    export_for_printing() {
        const result = super.export_for_printing(...arguments);
        if (this.get_partner()) {
            result.partner = this.get_partner();
        }
        if (this.pos.config.pos_l10n_pe_invoice){
            result['l10n_pe_invoice'] = true;
        }
        if(this.invoice_number){
            result.document_invoice_type = this.document_invoice_type;
            result['headerData']['invoice_number'] = this.invoice_number;
        }
        if(this.l10n_pe_edi_refund_reason){
            result['l10n_pe_edi_refund_reason'] = nc_type[this.l10n_pe_edi_refund_reason]
            
        }
        if(this.l10n_pe_reason){
            result['l10n_pe_reason'] = this.l10n_pe_reason;
        }
        if(this.comprobante_origen){
            result['comprobante_origen'] = this.comprobante_origen;
        }
        if(this.fecha_origen){
            result['fecha_origen'] = this.fecha_origen;
        }
        result['headerData']['pos_l10n_pe_display_option'] = this.pos.config.pos_l10n_pe_display_option;
        console.log(this)
        console.log(result)
        return result;
    },

});
