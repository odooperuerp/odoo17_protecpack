/** @odoo-module */
import { patch } from "@web/core/utils/patch";
import {ErrorPopup} from "@point_of_sale/app/errors/popups/error_popup";
import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { Order } from "@point_of_sale/app/store/models";

patch(PaymentScreen.prototype, {
    toggleIsToInvoiceCPE(document_invoice_type) {
        this.currentOrder.document_invoice_type = document_invoice_type
    },
    rucValido: function(ruc) {
        var ex_regular_ruc;
        ex_regular_ruc = /^\d{11}(?:[-\s]\d{4})?$/;
        if (ex_regular_ruc.test(ruc)) {
            return true
        }
        return false;
    },
    dniValido: function(dni) {
        var ex_regular_dni;
        ex_regular_dni = /^\d{8}(?:[-\s]\d{4})?$/;
        if (ex_regular_dni.test(dni)) {
            return true
        }
        return false;
    },
    async validateOrder(isForceValidate) {
        if (this.pos.config.pos_l10n_pe_invoice){
            const order = this.currentOrder;
            order.to_invoice = true
            
            if (order.partner == null) {
                this.popup.add(ErrorPopup, {
                    title: "Error de cliente",
                    body: "Seleccione un cliente antes de validar la venta.",
                });
                return false;
            }

            if (order.document_invoice_type == 3) {
                if (order.get_total_with_tax() > 700) {
                    if (order.partner.anonymous_customer) {
                        this.popup.add(ErrorPopup, {
                            title: "Cliente anónimo",
                            body: "No puede realizar una venta a un cliente anónimo o cliente varios.",
                        });
                        return false;
                    }
                    if (order.partner.vat == "") {
                        this.popup.add(ErrorPopup, {
                            title: "Datos del cliente incorrectos",
                            body: "El número de documento de identidad del cliente es obligatorio.\n Recuerda que para montos mayores a S/. 700.00 el detalle de DNI es obligatorio ",
                        });
                        return false;
                    }
                    if (!this.dniValido(order.partner.vat)) {
                        this.popup.add(ErrorPopup, {
                            title: "Error en número de dni",
                            body: "El DNI del cliente tiene un formato incorrecto.",
                        });
                        return false;
                    }
                }
            }

            if (order.document_invoice_type == 1) {
                if (order.partner.l10n_latam_identification_type_id[1] != 'RUC'){
                    this.popup.add(ErrorPopup, {
                        title: "Error",
                        body: "El cliente debe tener RUC para poder generar una factura.",
                    });
        
                    return false;
                }
                if (!this.rucValido(order.partner.vat)) {
                    this.popup.add(ErrorPopup, {
                        title: "Error",
                        body: "El cliente debe tener un RUC válido para poder generar una factura.",
                    });
        
                    return false;
                }
            }
        }
        
        return await super.validateOrder(...arguments);
    },
});


patch(Order.prototype, {
    setup(_defaultObj, options) {
        super.setup(...arguments);
        var document_invoice_type;
        document_invoice_type = 3;

        this.l10n_pe_edi_refund_reason = ""
        this.l10n_pe_reason = ""

        this.comprobante_origen = ""
        this.fecha_origen = ""

        if (options.json == undefined) {
            this.set_document_invoice_type(document_invoice_type);
        } else {
            this.set_document_invoice_type(options.json.document_invoice_type);
            this.invoice_number = options.json.invoice_number;
            this.comprobante_origen = options.json.comprobante_origen;
            this.fecha_origen = options.json.fecha_origen;
            this.l10n_pe_edi_refund_reason = options.json.l10n_pe_edi_refund_reason
            this.l10n_pe_reason = options.json.l10n_pe_reason
        }

    },
    init_from_JSON(json) {
        super.init_from_JSON(...arguments);
        var document_invoice_type;
        document_invoice_type = 3;
        this.set_document_invoice_type(json.document_invoice_type);
        this.l10n_pe_reason = json.l10n_pe_reason
        this.comprobante_origen = json.comprobante_origen;
        this.fecha_origen = json.fecha_origen;
        this.l10n_pe_edi_refund_reason = json.l10n_pe_edi_refund_reason
        this.l10n_pe_reason = json.l10n_pe_reason
    },
    export_as_JSON() {
        
        const json = super.export_as_JSON(...arguments);

        json.document_invoice_type = this.document_invoice_type;      
        json.l10n_pe_edi_refund_reason = this.l10n_pe_edi_refund_reason
        json.l10n_pe_reason = this.l10n_pe_reason
        json.comprobante_origen = this.comprobante_origen;
        json.fecha_origen = this.fecha_origen;
        return json;
    },
    get_document_invoice_type(){
        return this.document_invoice_type;
    },
    set_document_invoice_type(document_invoice_type){
        this.document_invoice_type = document_invoice_type;
    },
    get_l10n_pe_reason(){
        return this.l10n_pe_reason;
    },
    set_l10n_pe_reason(l10n_pe_reason){
        this.l10n_pe_reason = l10n_pe_reason;
    },
});

