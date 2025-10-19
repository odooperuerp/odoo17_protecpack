/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { TicketScreen } from "@point_of_sale/app/screens/ticket_screen/ticket_screen";
import { useAutofocus } from "@web/core/utils/hooks";
import { patch } from "@web/core/utils/patch";
import { parseFloat } from "@web/views/fields/parsers";
import { ConfirmPopup } from "@point_of_sale/app/utils/confirm_popup/confirm_popup";
import { Component, useState } from "@odoo/owl";

patch(TicketScreen.prototype, {
    async onDoRefund() {
        if (this.pos.config.pos_l10n_pe_invoice){
            const order = this.getSelectedOrder();
            const partner = order.get_partner();
            const destinationOrder =
                this.props.destinationOrder &&
                partner === this.props.destinationOrder.get_partner() &&
                !this.pos.doNotAllowRefundAndSales()
                    ? this.props.destinationOrder
                    : this._getEmptyOrder(partner);
            
            destinationOrder.document_invoice_type = order.document_invoice_type
            destinationOrder.l10n_pe_edi_refund_reason = order.l10n_pe_edi_refund_reason
            destinationOrder.l10n_pe_reason = order.l10n_pe_reason
        }

        super.onDoRefund(...arguments);
    },
    setRefundReason(value) {
        const order = this.getSelectedOrder();
        order.l10n_pe_edi_refund_reason = value;
    },

});