/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";
import { TicketScreen } from "@point_of_sale/app/screens/ticket_screen/ticket_screen";
import { useService } from "@web/core/utils/hooks";
import { TextInputPopup } from "@point_of_sale/app/utils/input_popups/text_input_popup";
import { Component } from "@odoo/owl";
import { usePos } from "@point_of_sale/app/store/pos_hook";

export class NoteReasonButton extends Component {
    static template = "l10n_pe_pos_base.NoteReasonButton";

    setup() {
        this.pos = usePos();
        this.popup = useService("popup");
    }

    async click() {
        let { confirmed, payload: reason } = await this.popup.add(TextInputPopup, {
            title: _t("Ingreso un sustento"),
            startingValue: this.props.order.l10n_pe_reason,
            placeholder: _t("Sustento de la nota de crédito"),
        });
        if (confirmed) {
            reason = reason.trim();
            if (reason !== "") {
                this.props.order.set_l10n_pe_reason(reason);
            }
        }
    }
}


patch(TicketScreen, {
    components: { ...TicketScreen.components, NoteReasonButton },
});
