/** @odoo-module **/
import publicWidget from "@web/legacy/js/public/public_widget";
import wSale from "@website_sale/js/website_sale";

const ID_RUC = 4;
const ID_DNI = 5;
const ID_CE = 3;
const ID_PASSPORT = 2;

//const patron_ruc = /^[12]\d{10}$/
const patron_dni = /^\d{8}$/
const patron_ce = /^\d{9,11}$/


wSale.WebsiteSale = wSale.WebsiteSale.include({
    _changeCountry:function(){
        return
    }
})


publicWidget.registry.WebsiteSaleCustom = publicWidget.Widget.extend({
    selector:".oe_website_sale form",
    events:{
        'change input[name="vat"]':'change_vat',
        'change input[name="contact_vat"]':'change_contact_vat',
        'change select[name="contact_l10n_latam_identification_type_id"]': 'change_contact_vat',
        'change select[name="country_id"]':'change_country',
        'change select[name="state_id"]':'change_state',
        'change select[name="city_id"]':'change_city',
        'change input[name="require_invoice"]':'change_require_invoice',
    },
    start: function  () {
        this.rpc = this.bindService("rpc");
        //this.country_id = parseInt(this.$el.find('select[name="country_id"]').val())
        this.state_id = parseInt(this.$el.find('select[name="state_id"]').val())
        this.city_id =  parseInt(this.$el.find('select[name="city_id"]').val())
        this.l10n_pe_district = parseInt(this.$el.find('select[name="l10n_pe_district"]').val())
        this.vat = this.$el.find("input[name='vat']").val()
        this.l10n_latam_identification_type_id = parseInt(this.$el.find("input[name='l10n_latam_identification_type_id']:checked").val())
    },
    change_require_invoice: function(ev){
        var field_required = 'phone,name'

        if($(ev.currentTarget).val() == "1"){
            this.$el.find("#section_invoice").removeClass("d-none")
            this.$el.find('input[name="field_required"]').val(field_required+',vat,company_name')
            this.$el.find('input[name="l10n_latam_identification_type_id"]').val(ID_RUC)
            this.$el.find('input[name="vat"]').val("")
        }else{
            this.$el.find("#section_invoice").addClass("d-none")
            this.$el.find('input[name="field_required"]').val(field_required)
            this.$el.find('input[name="l10n_latam_identification_type_id"]').val(this.contact_l10n_latam_identification_type_id)
            this.$el.find('input[name="vat"]').val(this.contact_vat)
            this.$el.find('input[name="company_name"]').val("")
        }
    },
    change_contact_vat: function(ev){
        this.contact_vat = this.$el.find("input[name='contact_vat']").val()
        this.contact_l10n_latam_identification_type_id = this.$el.find("select[name='contact_l10n_latam_identification_type_id']").val()
        this.$el.find('input[name="require_invoice"]:checked').trigger("change")
    },
    change_vat:async function(ev){
        var name = "";
        var street = "";

        //this.l10n_latam_identification_type_id = parseInt(this.$el.find("input[name='l10n_latam_identification_type_id']:checked").val())
        this.vat = this.$el.find("input[name='vat']").val()

        if(this._validate_vat(ID_RUC,this.vat)){
            var data = await this._request_data_by_vat(ID_RUC,this.vat);
            name = data["name"];
            street = data["street"];
            this.city_id = data["city_id"];
            this.state_id = data["state_id"];
            this.l10n_pe_district = data["l10n_pe_district"];
        }

        this.$el.find('input[name="company_name"]').val(name)
        this.$el.find('input[name="street"]').val(street)
        
        this.$el.find('select[name="state_id"]').val(this.state_id)
        this.$el.find('select[name="state_id"]').trigger("change")
        this.$el.find('select[name="city_id"]').val(this.city_id)
        this.$el.find('select[name="l10n_pe_district"]').val(this.l10n_pe_district)
    },
    _request_data_by_vat: function(l10n_latam_identification_type_id,vat){
        return new Promise((resolve, reject) => {
            this.rpc("/request/vat/json",
                {
                    l10n_latam_identification_type_id:parseInt(l10n_latam_identification_type_id),
                    vat:vat
                }
            ).then(function(data){
                resolve(data);
            });
        });
    },
    _validate_vat:function(l10n_latam_identification_type_id,vat){
        var is_valid = false;
        if(l10n_latam_identification_type_id == ID_RUC ){
            is_valid = this._validate_ruc(vat);
        }else if(l10n_latam_identification_type_id == ID_DNI){
            is_valid =  patron_dni.test(vat)?true:false;
        }else if(l10n_latam_identification_type_id == ID_CE){
            is_valid = patron_ce.test(vat)?true:false;
        }else{
            is_valid = true;
        }
        if(is_valid){
            this.$el.find('input[name="vat"]').removeClass('is-invalid');
        }else{
            this.$el.find('input[name="vat"]').addClass('is-invalid');
        }
        return is_valid
    },
    _validate_ruc: function(ruc){
        if (ruc.length != 11) return false
        var f = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]
        var g = ruc.toString().slice(0,-1);
        var sum = 0
        for (var i = 0; i < 10; i++) {
            sum += f[i] * parseInt(g[i])
        }
        var res = (11 - sum % 11).toString().slice(-1)
        return res == ruc.slice(-1)
    },
    change_country: async function(ev){
        var self = this
        var country_id = this.$el.find("select[name='country_id']").val()
        this.state_id = await parseInt(this.$el.find("select[name='state_id']").val())
        if( country_id == "0") return;

        var $select_states = this.$el.find("select[name='state_id']")
        this.rpc('/list-states-by-country', {country_id})
            .then(function (data) {
                $select_states.empty()
                $select_states.append($('<option selected="" disabled=""/>').val("").text("Departamentos ..."));
                for (let i = 0; i < data.length; i++) {
                    if(self.state_id != data[i].id){
                        $select_states.append($('<option />').val(data[i].id).text(data[i].name));
                    }else{
                        $select_states.append($('<option selected="1"/>').val(data[i].id).text(data[i].name));
                    }
                    if(i == data.length-1){
                        $select_states.trigger("change");
                    }
                }
            })
        
    },
    change_state: function(ev){
        var self = this
        let state_id = this.$el.find("select[name='state_id']").val()
        if( state_id == "0") return;

        var $select_city = this.$el.find('select[id="city_id"]')
        
        this.rpc('/list-cities-by-state', {state_id})
            .then(function (data) {
                $select_city.empty()
                $select_city.append($('<option selected="" disabled="">Provincias ...</option>'))
                for (let i = 0; i < data.length; i++) {
                    if(self.city_id != data[i].id){
                            $select_city.append($('<option />').val(data[i].id).text(data[i].name));
                    }else{
                            $select_city.append($('<option selected="1"/>').val(data[i].id).text(data[i].name));
                    }
                    if(i == data.length-1){
                        $select_city.trigger("change");
                    }
                }
            })
        
    },
    change_city:function(ev){
        var self = this
        var city_id = this.$el.find("select[name='city_id']").val()
        if( city_id == "0") return;

        var $select_districts = this.$el.find("select[name='l10n_pe_district']")
        //this.l10n_pe_district = $select_districts.val()

        this.rpc('/list-districts-by-city', {city_id})
            .then(function (data) {
                $select_districts.empty()
                $select_districts.append($('<option selected="" disabled="">Seleccionar</option>'))
                for (let i = 0; i < data.length; i++) {
                    if(self.l10n_pe_district != data[i].id){
                        $select_districts.append($('<option />').val(data[i].id).text(data[i].name));
                    }else{
                        $select_districts.append($('<option selected="1"/>').val(data[i].id).text(data[i].name));
                    }
                }
            }) 
    },
    change_company_vat: async function(ev){
        var company_vat = $(ev.currentTarget).val()
        var company_name = ""
        var company_street = ""
        if(this._validate_ruc(company_vat)){
            var data = await this._request_data_by_vat(ID_RUC,company_vat);
            company_name = data["name"];
            company_street = data["street"];
        }
        this.$el.find('input[name="company_name"]').val(company_name)
        this.$el.find('input[name="company_street"]').val(company_street)
    }
})
