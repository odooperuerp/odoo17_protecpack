/** @odoo-module **/
import publicWidget from "@web/legacy/js/public/public_widget";
import { _t } from "@web/core/l10n/translation";

publicWidget.registry.WebsitePaymentNiubiz = publicWidget.Widget.extend({
    selector: ".o_wsale_accordion",
    events: {
        'change input[name="check_terms_and_conditions"]': '_onChangeTermsConditions',
    },
    start: function () {
        // debugger;
        // let $check_terms_and_conditions = this.$el.find('input[name="check_terms_and_conditions"]')
        // if ($check_terms_and_conditions) {
        //     $check_terms_and_conditions.trigger("change");
        // }
    },
    _onChangeTermsConditions: function (ev) {
        // debugger;
        // let $payment_submit = this.$el.find('button[name="o_payment_submit_button"]');
        // $payment_submit.toggleClass('disabled', !$(ev.currentTarget).prop('checked'));
        var $page = $('.oe_website_payment');
        var cart_alert = $page.children('#data_warning');
        cart_alert.addClass("d-none");
    }
});

// publicWidget.registry.WebsiteSaleNiubiz = publicWidget.Widget.extend({
//     selector: ".o_payment_form",
//     events: {
//         'change input[name="check_terms_and_conditions"]': '_onChangeTermsConditions',
//     },
//     start: function () {
//         debugger;
//         let $check_terms_and_conditions = this.$el.find('input[name="check_terms_and_conditions"]')
//         if ($check_terms_and_conditions) {
//             $check_terms_and_conditions.trigger("change");
//         }
//     },
//     _onChangeTermsConditions: function (ev) {
//         debugger;
//         let $payment_submit = this.$el.find('button[name="o_payment_submit_button"]');
//         $payment_submit.toggleClass('disabled', !$(ev.currentTarget).prop('checked'));
//     }
// });