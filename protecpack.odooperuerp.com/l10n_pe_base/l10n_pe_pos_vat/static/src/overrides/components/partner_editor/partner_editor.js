/** @odoo-module */

import { PartnerDetailsEdit } from "@point_of_sale/app/screens/partner_list/partner_editor/partner_editor";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";
import { _t } from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { jsonrpc } from "@web/core/network/rpc_service";

patch(PartnerDetailsEdit.prototype, {
    setup(){
        super.setup(...arguments);
        this.rpc = useService("rpc");
       
        if (this.pos.isPeruvianCompany()) {
            this.intFields.push("l10n_latam_identification_type_id");
            this.intFields.push("city_id");
            this.intFields.push("l10n_pe_district");
            this.changes.anonymous_customer = this.props.partner.anonymous_customer || false;
            this.changes.l10n_latam_identification_type_id =
                this.props.partner.l10n_latam_identification_type_id &&
                this.props.partner.l10n_latam_identification_type_id[0];
            
            this.change_identification_type()
        }
         
    },
    change_identification_type(ev){
        this.l10n_pe_vat_code = "1";
        this.changes.company_type = "person"
        var l10n_latam_identification_type_id = this.pos.l10n_latam_identification_types.find((el)=> el.id == this.changes.l10n_latam_identification_type_id)
        if (l10n_latam_identification_type_id){
            this.l10n_pe_vat_code = l10n_latam_identification_type_id.l10n_pe_vat_code
            if(this.l10n_pe_vat_code == "6"){
                this.changes.company_type = "company"
            }
        }
    },
    async autocomplete_client(ev){
        var self = this;
        self.changes.vat = (self.changes.vat || "").replace(/\s/g, '').toString()
        var partner=  await this.pos.partners.find((el)=> (el.vat || "").replace(/\s/g, '') == self.changes.vat)


        if(partner == undefined){
            await jsonrpc(`/web/dataset/call_kw/res.partner/api_search_partner_by_vat`, {
                model: "res.partner",
                method: "api_search_partner_by_vat",
                args: [self.l10n_pe_vat_code,self.changes.vat],
                kwargs: {},
            }).then((result) => {
                this.changes.name = result.name
                this.changes.street = result.street
                this.changes.country_id = result.country_id || this.pos.company.country?.id
                this.changes.state_id = result.state_id
                this.changes.city_id = result.city_id
                this.changes.l10n_pe_district = result.l10n_pe_district
            });
        }else if(partner.id != this.pos.selectedOrder.partner?.id){
            this.props.onClickPartner(partner)
        }else{
            this.props.onClickBack(true)
        }
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
    saveChanges() {
        const processedChanges = {};
        for (const [key, value] of Object.entries(this.changes)) {
            if (this.intFields.includes(key)) {
                processedChanges[key] = parseInt(value) || false;
            } else {
                processedChanges[key] = value;
            }
        }
        if (
            processedChanges.state_id &&
            this.pos.states.find((state) => state.id === processedChanges.state_id)
                .country_id[0] !== processedChanges.country_id
        ) {
            processedChanges.state_id = false;
        }

        if ((!this.props.partner.name && !processedChanges.name) || processedChanges.name === "") {
            return this.popup.add(ErrorPopup, {
                title: _t("A Customer Name Is Required"),
            });
        }

        
        if (this.l10n_pe_vat_code == "6") {
            if (!this.rucValido(processedChanges.vat)) {
                return this.popup.add(ErrorPopup, {
                    title: _t("Error"),
                    body: _t("Se requiere de un número de RUC válido."),
                });

            }
        }
        if (this.l10n_pe_vat_code == "1") {
            console.log()
            if (!this.dniValido(processedChanges.vat)) {
                return this.popup.add(ErrorPopup, {
                    title: _t("Error"),
                    body: _t("Se requiere de un número de DNI válido."),
                });
            }
        }
        
        processedChanges.id = this.props.partner.id || false;
        this.props.saveChanges(processedChanges);
    }
});
