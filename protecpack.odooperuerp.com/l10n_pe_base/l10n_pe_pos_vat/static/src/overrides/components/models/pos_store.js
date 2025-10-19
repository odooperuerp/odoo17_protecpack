/** @odoo-module */

import { PosStore } from "@point_of_sale/app/store/pos_store";
import { patch } from "@web/core/utils/patch";

patch(PosStore.prototype, {
    async _processData(loadedData) {
        await super._processData(...arguments);
       
        if (this.isPeruvianCompany()) {
            this.l10n_latam_identification_types = loadedData["l10n_latam.identification.type"];
            this.cities = loadedData["res.city"];
            this.districts = loadedData["l10n_pe.res.city.district"];
        } 
    },
    isPeruvianCompany() {
        return this.company.country?.code == "PE";
    },
});

