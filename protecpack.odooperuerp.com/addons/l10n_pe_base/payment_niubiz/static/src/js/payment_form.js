/** @odoo-module **/
/* NiubizCheckout */
import paymentForm from '@payment/js/payment_form';
import { jsonrpc } from "@web/core/network/rpc_service";
import { _t } from '@web/core/l10n/translation';

paymentForm.include({

    /**
     * Displays `message` in an alert box at the top of the page if it's a
     * non-empty string.
     *
     * @param {string | null} message
     */
    showWarning(message) {
        // debugger;
        if (!message) {
            return;
        }
        var $page = $('.oe_website_payment');
        var cart_alert = $page.children('#data_warning');
        if (!cart_alert.length) {
            cart_alert = $(
                '<div class="alert alert-danger alert-dismissible" role="alert" id="data_warning">' +
                    '<button type="button" class="btn-close" data-bs-dismiss="alert"></button> ' +
                    '<span></span>' +
                '</div>').prependTo($page);
        }
        cart_alert.children('span:last-child').text(message);
        cart_alert.removeClass("d-none");
    },

    /**
     * Update the payment context with the selected payment option and initiate its payment flow.
     *
     * @private
     * @param {Event} ev
     * @return {void}
     */

    /**
     * @override
     */
    async _submitForm(ev) {
        // debugger;
        const radio = document.querySelector('input[name="o_payment_radio"]:checked');
        const code = radio.getAttribute('data-provider-code');
        if (code != 'niubiz') {
            this._super(...arguments);
            return;
        }
        const check_terms_and_conditions = document.querySelector('input[name="check_terms_and_conditions"]:checked');
        if (check_terms_and_conditions){
            this._super(...arguments);
            return;
        }
        this.showWarning(_t("Aceptar los términos y condiciones antes de pagar."));
    },

    // #=== DOM MANIPULATION ===#

    /**
     * Prepare the inline form of Niubiz for direct payment.
     *
     * @override method from @payment/js/payment_form
     * @private
     * @param {number} providerId - The id of the selected payment option's provider.
     * @param {string} providerCode - The code of the selected payment option's provider.
     * @param {number} paymentOptionId - The id of the selected payment option
     * @param {string} paymentMethodCode - The code of the selected payment method, if any.
     * @param {string} flow - The online payment flow of the selected payment option
     * @return {void}
     */

    /**
     * @override
     */

    async _prepareInlineForm(providerId, providerCode, paymentOptionId, paymentMethodCode, flow) {
        if (providerCode !== 'niubiz') {
            this._super(...arguments);

            $(".js_terms_and_conditions").addClass("d-none");
            $('button[name="o_payment_submit_button"]').toggleClass('disabled', false);
            
            return;
        }

        // console.log(" 🔴🔴🔴 _prepareInlineForm");
        // console.log('providerCode: ', providerCode);
        // console.log('paymentOptionId: ', paymentOptionId);
        // console.log('paymentMethodCode: ', paymentMethodCode);
        // console.log('flow: ', flow);

        // debugger;

        // Check if instantiation of the element is needed.
        this.niubizElements ??= {}; // Store the element of each instantiated payment method.

        // Mostrar términos y condiciones
        // debugger;
        // const check_terms_and_conditions = $('input[name="check_terms_and_conditions"]').prop('checked')
        $(".js_terms_and_conditions").removeClass("d-none");
        // $('button[name="o_payment_submit_button"]').toggleClass('disabled', !check_terms_and_conditions);
        // $('button[name="o_payment_submit_button"]').toggleClass('disabled', false);
        jsonrpc('/payment/niubiz/url_tyc', { providerCode })
            .then((terms_and_conditions_url) => {
                $(".js_a_terms_and_conditions").attr('href', terms_and_conditions_url);
            });

        // Check if instantiation of the element is needed.
        if (flow === 'token') {
            return; // No elements for tokens.
        } else if (this.niubizElements[paymentOptionId]) {
            this._setPaymentFlow('direct'); // Overwrite the flow even if no re-instantiation.
            return; // Don't re-instantiate if already done for this provider.
        }

        // Overwrite the flow of the select payment option.
        this._setPaymentFlow('direct');

        // Extract and deserialize the inline form values.
        
        const radio = document.querySelector('input[name="o_payment_radio"]:checked');
        const inlineForm = this._getInlineForm(radio);
        const niubizInlineForm = inlineForm.querySelector('[name="o_niubiz_element_container"]');
        this.niubizInlineFormValues = JSON.parse(
            niubizInlineForm.dataset['niubizInlineFormValues']
        );
    },

    // #=== PAYMENT FLOW ===#
    /**
     * Trigger the payment processing by submitting the elements.
     *
     * @override method from @payment/js/payment_form
     * @private
     * @param {string} providerCode - The code of the selected payment option's provider.
     * @param {number} paymentOptionId - The id of the selected payment option.
     * @param {string} paymentMethodCode - The code of the selected payment method, if any.
     * @param {string} flow - The payment flow of the selected payment option.
     * @return {void}
     */
    async _initiatePaymentFlow(providerCode, paymentOptionId, paymentMethodCode, flow) {
        if (providerCode !== 'niubiz' || flow === 'token') {
            this._super(...arguments); // Tokens are handled by the generic flow
            return;
        }

        // Trigger form validation and wallet collection.
        const _super = this._super.bind(this);
        return await _super(...arguments);
    },

    /**
     * Process Niubiz implementation of the direct payment flow.
     *
     * @override method from payment.payment_form
     * @private
     * @param {string} providerCode - The code of the selected payment option's provider.
     * @param {number} paymentOptionId - The id of the selected payment option.
     * @param {string} paymentMethodCode - The code of the selected payment method, if any.
     * @param {object} processingValues - The processing values of the transaction.
     * @return {void}
     */
    async _processDirectFlow(providerCode, paymentOptionId, paymentMethodCode, processingValues) {
        if (providerCode !== 'niubiz') {
            await this._super(...arguments);
            return;
        }

        await this._openNiubiz(processingValues);
    },

    /**
     * Handle the open event of the component and open the payment.
     *
     * @private
     * @param {object} processingValues - The processing values of the transaction.
     * @return {void}
     */
    async _openNiubiz(processingValues) {
        const configure = {
            ...this.niubizInlineFormValues,
            'action': processingValues['return_url'],
            'timeouturl': processingValues['timeout_url'],
            'purchasenumber': processingValues['purchasenumber'],
            complete: function (params) {
                alert(JSON.stringify(params));
            },
            cancel: function () {
                // window.location.href = processingValues['close_url'];
                window.location.reload()
            },
        }
        // console.log(" 🔴🔴🔴 configure \n", configure);
        VisanetCheckout.configure(configure);
        VisanetCheckout.open()
    },
});