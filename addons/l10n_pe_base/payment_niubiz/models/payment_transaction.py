
import logging
import pprint
import json

from werkzeug.urls import url_encode, url_join

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

from odoo.addons.payment import utils as payment_utils
from odoo.addons.payment_niubiz import const, utils as niubiz_utils
from odoo.addons.payment_niubiz.controllers.main import NiubizController


_logger = logging.getLogger(__name__)


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    niubiz_channel = fields.Char('Niubiz Channel', readonly=True)
    niubiz_response_error_json = fields.Text('Response Error JSON', readonly=True)
    niubiz_response_auth_json = fields.Text('Response Auth JSON', readonly=True)
    niubiz_response_cap_json = fields.Text('Response Capture JSON', readonly=True)
    niubiz_response_void_json = fields.Text('Response Void JSON', readonly=True)
    niubiz_reference = fields.Char('Order number', 
        readonly=True,
        help="Número de Pedido, este valor debe ser creado por el comercio y es único por intento \
            de autorización. Se obtiene desde la referencia de la transacción de Odoo")
    niubiz_signature = fields.Char('Code Unique Signature', 
        readonly=True,
        help="Código único generado por Niubiz \
            al momento de la venta. Ejemplo 2fe2272c-76ec-4526-ac53-f3b2df94d98b")
    niubiz_msg_support_staff = fields.Text('Msg Support Staff')
    niubiz_card_type = fields.Selection([
        ('c', 'Tarjeta de crédito'),
        ('d', 'Tarjeta de débito'),
    ], string='Card Type', readonly=True)

    @api.model_create_multi
    def create(self, values_list):
        """ Para operaciones en Niubiz es necesario que la referencia sea númerica
        Esto aplica a las operaciones hijas de la transacción
            - Se reemplaza R por 9 para las operaciones refund
            - Se reemplaza P por 8 para las operaciones partial capture o void
        """
        txs = super().create(values_list)
        if txs.reference:
            # txs.niubiz_reference = int(txs.reference.replace("S","").replace("-","").replace("R","9").replace("P","8"))
            txs.niubiz_reference = txs.id
        return txs

    def _set_niubiz_msg_support(self, state_message, extra_allowed_states=()):
        """ Update the error message for technical support and notify staff

        :param str state_message: The reason for setting the transactions in the state `error`.
        :param tuple[str] extra_allowed_states: The extra states that should be considered allowed
                                                target states for the source state 'error'.
        : return void
        """
        self.niubiz_msg_support_staff = state_message

    def _get_specific_processing_values(self, processing_values):
        """ Override of payment to return Niubiz-specific processing values.

        Note: self.ensure_one() from `_get_processing_values`

        :param dict processing_values: The generic processing values of the transaction
        :return: The dict of provider-specific processing values
        :rtype: dict
        """
        res = super()._get_specific_processing_values(processing_values)
        if self.provider_code != 'niubiz' or self.operation == 'online_token':
            return res
        
        order = self.env['sale.order'].sudo().browse(self.sale_order_ids.ids).exists()
        # order = self.env['sale.order'].sudo().search([('name', '=', self.reference.split("-")[0])])
        recurring_invoice = self.provider_id._is_order_recurring_invoice(order)
        base_url = self.provider_id.get_base_url()
        return {
            'purchasenumber': self.niubiz_reference,
            'return_url': url_join(
                base_url,
                f'{NiubizController._return_url}?{url_encode({"reference": self.reference})}&{url_encode({"recurring": recurring_invoice})}',
            ),
            'timeout_url': url_join(
                base_url,
                f'{NiubizController._timeout_url}',
            ),
            'close_url': url_join(
                base_url,
                f'{NiubizController._payment_url}',
            ),       
        }
    
    def _send_payment_request(self):
        """ Override of payment to send a payment request to Niubiz with a confirmed api.authorization.

        Note: self.ensure_one()

        :return: None
        :raise: UserError if the transaction is not linked to a token
        """
        super()._send_payment_request()
        if self.provider_code != 'niubiz':
            return
            
        if not self.token_id:
            raise UserError("Niubiz: " + _("The transaction is not linked to a token."))

        notification_data = {'reference': self.reference, 'channel': 'recurrent'}
        # merchant_id = self.provider_id._get_merchant_id(self.currency_id.name)
        merchant_id = self.provider_id.niubiz_merchant_id_recurrent

        authorization_sale = self.provider_id._niubiz_make_request(
            endpoint='/authorization/{}',
            endpoint_param=merchant_id,
            payload=self._niubiz_prepare_authorization_sale_payload(),
            method='POST'
        )
        # _logger.info("\n🆗 authorization_sale:\n%s", json.dumps(authorization_sale, indent=4, sort_keys=True))
        NiubizController._include_authorization_sale_in_notification_data(
            authorization_sale, notification_data
        )
        if authorization_sale.get('dataMap', {}).get('STATUS') == 'Authorized' and self.provider_id.niubiz_confirmation_auto:
            confirmation_sale = self.provider_id._niubiz_make_request(
                endpoint='/confirmation/{}',
                endpoint_param=merchant_id,
                payload=self._niubiz_prepare_confirmation_payload(notification_data),
                method='POST'
            )
            # _logger.info("\n🆗 confirmation_sale:\n%s", json.dumps(confirmation_sale, indent=4, sort_keys=True))
            NiubizController._include_confirmation_in_notification_data(
                confirmation_sale, notification_data
            )
        # Handle the payment request response
        self._handle_notification_data('niubiz', notification_data)

    def _niubiz_prepare_authorization_sale_payload(self):
        """ Prepare the payload for the creation of a api.authorization object in Niubiz format.

        Note: This method serves as a hook for modules that would fully implement Niubiz Tokenización.

        :return: The Niubiz-formatted payload for the api.authorization request.
        :rtype: dict
        """
        return {
            'channel': 'recurrent',
            'captureType': 'manual',
            'countable': self.provider_id.niubiz_liquidation_auto,
            'order': {
                'purchaseNumber': self.niubiz_reference,
                'amount': round(self.amount,2),
                'currency': self.currency_id.name.upper(),
            },
            'card': {
                'tokenId': self.token_id.provider_ref,
                'registerFrequent': False,
                'useFrequent': True
            },
            'cardHolder': {
                'email': self.partner_id.email
            }
        }

    def _send_refund_request(self, amount_to_refund=None):
        """ Override of payment to send a refund request to Niubiz.

        Note: self.ensure_one()

        :param float amount_to_refund: The amount to refund.
        :return: The refund transaction created to process the refund request.
        :rtype: recordset of `payment.transaction`
        """
        refund_tx = super()._send_refund_request(amount_to_refund=amount_to_refund)
        if self.provider_code != 'niubiz':
            return refund_tx
        
        # Make the refund request to Niubiz.
        # _logger.info("\n🆗 _send_refund_request:\n")
        # Make the void request to Niubiz.
        order = self.env['sale.order'].sudo().browse(self.sale_order_ids.ids).exists()
        # order = self.env['sale.order'].sudo().search([('name', '=', self.reference.split("-")[0])])
        recurring_invoice = self.provider_id._is_order_recurring_invoice(order)
        notification_data = {'reference': self.reference, 'channel': self.niubiz_channel}
        merchant_id = self.provider_id._get_merchant_id(self.currency_id.name, recurring_invoice)
        data = self.provider_id._niubiz_make_request(
            endpoint='/refund/{}/{}',
            endpoint_param=(merchant_id, self.provider_reference),
            payload={
                'ruc': self.env.user.company_id.vat,
                'comment': 'Devolución',
                'externalReferenceId': '',
                'amount': round(amount_to_refund, 2)
            },
            method='PUT'
        )
        _logger.info(
            "Refund request response for transaction wih reference %s:\n%s",
            self.reference, json.dumps(data, indent=4, sort_keys=True)
        )
        # Handle the refund request response.
        # _logger.info("\n🆗 _send_refund_request:\n%s", json.dumps(data, indent=4, sort_keys=True))
        NiubizController._include_refund_in_notification_data(data, notification_data)
        refund_tx._handle_notification_data('niubiz', notification_data)

        return refund_tx
    
    def _send_capture_request(self, amount_to_capture=None):
        """ Override of `payment` to send a capture request to Niubiz. """
        child_capture_tx = super()._send_capture_request(amount_to_capture=amount_to_capture)
        if self.provider_code != 'niubiz':
            return child_capture_tx
        # _logger.info("\n🆗 _send_capture_request:\n")

        order = self.env['sale.order'].sudo().browse(self.sale_order_ids.ids).exists()
        # order = self.env['sale.order'].sudo().search([('name', '=', self.reference.split("-")[0])])
        recurring_invoice = self.provider_id._is_order_recurring_invoice(order)
        notification_data = {'reference': self.reference, 'channel': self.niubiz_channel}
        merchant_id = self.provider_id._get_merchant_id(self.currency_id.name, recurring_invoice)

        data = self.provider_id._niubiz_make_request(
            endpoint='/confirmation/{}',
            endpoint_param=merchant_id,
            payload=self._niubiz_prepare_confirmation_payload(notification_data),
            method='POST'
        )
        # _logger.info("\n🆗 _send_capture_request:\n%s", json.dumps(data, indent=4, sort_keys=True))

        # Handle the payment request response
        NiubizController._include_confirmation_in_notification_data(
            data, notification_data
        )
        self._handle_notification_data('niubiz', notification_data)

    def _niubiz_prepare_confirmation_payload(self, data):
        """ Prepare the payload for the creation of a api.confirmation object in Niubiz format.

        Note: This method serves as a hook for modules that would fully implement Niubiz Tokenización.

        :return: The Niubiz-formatted payload for the api.confirmation request.
        :rtype: dict
        """
        return {
            'channel': self.niubiz_channel or data.get('channel'),
            'captureType': 'manual',
            'order': {
                'purchaseNumber': self.niubiz_reference,
                'amount': round(self.amount, 2),
                'currency': self.currency_id.name.upper(),
                'transactionId': self.provider_reference or data.get('auth_sale', {}).get('dataMap', {}).get('TRANSACTION_ID',''),
            }
        }

    def _send_void_request(self, amount_to_void=None):
        """ Override of `payment` to send a void request to Stripe. """
        child_void_tx = super()._send_void_request(amount_to_void=amount_to_void)
        if self.provider_code != 'niubiz':
            return child_void_tx

        # _logger.info("\n🆗 _send_void_request:\n")
        # Make the void request to Niubiz.
        order = self.env['sale.order'].sudo().browse(self.sale_order_ids.ids).exists()
        # order = self.env['sale.order'].sudo().search([('name', '=', self.reference.split("-")[0])])
        recurring_invoice = self.provider_id._is_order_recurring_invoice(order)
        notification_data = {'reference': self.reference, 'channel': self.niubiz_channel}
        merchant_id = self.provider_id._get_merchant_id(self.currency_id.name, recurring_invoice)
        data = self.provider_id._niubiz_make_request(
            endpoint='/void/{}/{}/{}',
            endpoint_param=('ecommerce', merchant_id, self.niubiz_signature),
            payload={
                'annulationReason': 'Anulación completa de la venta'
            },
            method='PUT'
        )
        _logger.info(
            "Void request response for transaction wih reference %s:\n%s",
            self.reference, json.dumps(data, indent=4, sort_keys=True)
        )
        # Handle the refund request response.
        # _logger.info("\n🆗 _send_void_request:\n%s", json.dumps(data, indent=4, sort_keys=True))
        NiubizController._include_void_in_notification_data(data, notification_data)
        child_void_tx._handle_notification_data('niubiz', notification_data)

        return child_void_tx

    def _get_tx_from_notification_data(self, provider_code, notification_data):
        """ Override of payment to find the transaction based on Niubiz data.

        :param str provider_code: The code of the provider that handled the transaction
        :param dict notification_data: The notification data sent by the provider
        :return: The transaction if found
        :rtype: recordset of `payment.transaction`
        :raise: ValidationError if inconsistent data were received
        :raise: ValidationError if the data match no transaction
        """
        tx = super()._get_tx_from_notification_data(provider_code, notification_data)
        if provider_code != 'niubiz' or len(tx) == 1:
            return tx

        reference = notification_data.get('reference')
        if reference:
            tx = self.search([('reference', '=', reference), ('provider_code', '=', 'niubiz')])
        else:
            raise ValidationError("Niubiz: " + _("Received data with missing merchant reference"))

        if not tx:
            raise ValidationError(
                "Niubiz: " + _("No transaction found matching reference %s.", reference)
            )

        return tx

    def _process_notification_data(self, notification_data):
        """ Override of `payment` to process the transaction based on Niubiz data.

        Note: self.ensure_one()

        :param dict notification_data: The notification data build from information passed to the
                                       return route. Depending on the operation of the transaction,
                                       the entries with the keys 'payment_intent', 'setup_intent'
                                       and 'payment_method' can be populated with their
                                       corresponding Niubiz API objects.
        :return: None
        :raise: ValidationError if inconsistent data were received
        """
        super()._process_notification_data(notification_data)
        if self.provider_code != 'niubiz':
            return

        # _logger.info("\n🆗 _process_notification_data:\n%s", json.dumps(notification_data, indent=4, sort_keys=True))

        # Por defecto no tokenizar pagos del servicio pago web de Niubiz
        tokenize_niubiz = False
        # Update the provider reference and the payment state.
        # operation = self.operation
        payment_state = notification_data.get('payment_state')
        self.niubiz_channel = notification_data.get('channel')
        if notification_data.get('errorCode') == 0 and \
            isinstance(notification_data.get('auth_sale'), dict) and \
                notification_data.get('channel') != 'pagoefectivo':
            self.niubiz_response_auth_json = json.dumps(notification_data, indent=4, sort_keys=True)
            self.provider_reference = notification_data['auth_sale']['dataMap']['TRANSACTION_ID']
            self.niubiz_signature = notification_data['auth_sale']['dataMap']['SIGNATURE']
            # tokenize_niubiz = notification_data['auth_sale'].get('token', {}).get('tokenId', '') != ''
            payment_method_code = notification_data['auth_sale']['dataMap']['BRAND']
            if notification_data['auth_sale']['dataMap'].get('YAPE_ID', None):
                payment_method_code = 'yape'
        elif isinstance(notification_data.get('auth_sale'), dict):
            self.niubiz_response_auth_json = json.dumps(notification_data, indent=4, sort_keys=True)
            self.niubiz_signature = notification_data['auth_sale'].get('data', {}).get('SIGNATURE', '')
            payment_method_code = notification_data['auth_sale'].get('data', {}).get('BRAND', '')
        elif notification_data.get('errorCode') == 0 and \
                isinstance(notification_data.get('confirmation'), dict):
            self.niubiz_response_cap_json = json.dumps(notification_data, indent=4, sort_keys=True)
            # self.provider_reference = notification_data['confirmation']['dataMap']['TRANSACTION_ID']
            # self.niubiz_signature = notification_data['confirmation']['dataMap']['SIGNATURE']
            # payment_method_code = notification_data['confirmation']['dataMap']['BRAND']
            payment_method_code = notification_data.get('channel')
        elif notification_data.get('errorCode') == 0 and \
                isinstance(notification_data.get('void'), dict):
            self.niubiz_response_void_json = json.dumps(notification_data, indent=4, sort_keys=True)
            # self.provider_reference = notification_data['void']['dataMap']['TRANSACTION_ID']
            # self.niubiz_signature = notification_data['void']['fulfillment']['signature']
            payment_method_code = notification_data.get('channel')
        else:
            self.niubiz_response_error_json = json.dumps(notification_data, indent=4, sort_keys=True)
            payment_method_code = notification_data.get('channel')

        # Update the payment method.
        payment_method = self.env['payment.method']._get_from_code(
            payment_method_code, mapping=const.PAYMENT_METHODS_MAPPING
        )
        self.payment_method_id = payment_method or self.payment_method_id

        # if self.operation == 'validation':
        #     self.provider_reference = notification_data['order']['id']
        #     payment_state = notification_data['setup_intent']['status']
        # elif self.operation == 'refund':
        #     self.provider_reference = notification_data['refund']['id']
        #     payment_state = notification_data['refund']['status']
        # else:  # 'online_direct', 'online_token', 'offline'
        #     self.provider_reference = notification_data['payment_intent']['id']
        #     payment_state = notification_data['payment_intent']['status']

        if not payment_state:
            raise ValidationError(
                "Niubiz: " + _("Received data with missing payment status.")
            )

        if payment_state in const.STATUS_MAPPING['draft']:
            pass
        elif payment_state in const.STATUS_MAPPING['pending']:
            self._set_pending()
        elif payment_state in const.STATUS_MAPPING['authorized']:
            if self.tokenize or tokenize_niubiz:
                self._niubiz_tokenize_from_notification_data(notification_data)
            if self.provider_id.niubiz_liquidation_auto:
                self._set_done()
            else:
                self._set_authorized()
        elif payment_state in const.STATUS_MAPPING['done']:
            if self.tokenize or tokenize_niubiz:
                self._niubiz_tokenize_from_notification_data(notification_data)
            self._set_done()
        elif payment_state in const.STATUS_MAPPING['cancel']:
            self._set_canceled()
        elif payment_state in const.STATUS_MAPPING['error']:
            if self.operation != 'refund':
                actionCode = notification_data.get('auth_sale',{}).get('data',{}).get('ACTION_CODE','00')
                message = const.ACTION_CODES.get(actionCode)
                self._set_error(message[1] if len(message) else 'Operación Denegada. Contactar con el comercio.')
                self._set_niubiz_msg_support(message[0] if len(message) else 'Review payment process log')
        else:  # Classify unknown intent statuses as `error` tx state
            msg_warning = _("received invalid payment status (%s) for transaction with reference %s", \
                payment_state, self.reference)
            _logger.warning(msg_warning)
            self._set_error(_("Received data with invalid payment status: %s", payment_state))
            self._set_niubiz_msg_support(msg_warning)

    def _niubiz_tokenize_from_notification_data(self, notification_data):
        """ Create a new token based on the notification data.

        :param dict notification_data: The notification data built with Niubiz objects.
                                       See `_process_notification_data`.
        :return: None
        """
        self.ensure_one()
        owner_id = ""
        token_id = notification_data.get('auth_sale',{}).get('token',{}).get('tokenId',None)
        if not token_id:
            token_id = notification_data.get('auth_token',{}).get('token',{}).get('tokenId',None)
            owner_id = notification_data.get('auth_token',{}).get('token',{}).get('ownerId',None)

        if not token_id:
            _logger.warning(
                "🔴 Requested tokenization from notification data with missing payment method"
            )
            return

        # Search token by client email
        domain = [('provider_ref', '=', token_id)]
        if owner_id:
            domain += [('partner_id.email', '=', owner_id)]
        token = self.env['payment.token'].sudo().search(domain)
        if token:
            _logger.warning("🔴 Token registrado N° (%s) del correo %s", token_id, owner_id)
            return

        # Extract the Niubiz objects from the notification data.
        # if self.operation == 'online_direct':
        customer_id = notification_data['transactionToken']
        expireOn = notification_data.get('auth_sale', {}).get('token', {}).get('expireOn', None)
        if not expireOn:
            expireOn = notification_data.get('auth_token', {}).get('token', {}).get('expireOn', None)
        niubiz_expire_on = niubiz_utils.txt_to_datetime(expireOn)
        payment_details = "{cardNumber} \n {expirationMonth}/{expirationYear}".format(
            cardNumber = notification_data['auth_sale']['dataMap']['CARD'],
            expirationMonth = f'{niubiz_expire_on.month:02d}',
            expirationYear = niubiz_expire_on.year
        )
        payment_method_code = notification_data['auth_sale']['dataMap']['BRAND']
        payment_method = self.env['payment.method']._get_from_code(
            payment_method_code, mapping=const.PAYMENT_METHODS_MAPPING
        )
        # Create the token.
        token = self.env['payment.token'].sudo().create({
            'provider_id': self.provider_id.id,
            'payment_method_id': payment_method.id if payment_method else self.payment_method_id.id,
            'payment_details': payment_details,
            'partner_id': self.partner_id.id,
            'provider_ref': token_id,
            'niubiz_transaction_token': customer_id,
            'niubiz_expire_on':  niubiz_expire_on
        })
        self.write({
            'token_id': token,
            'tokenize': False,
        })
        _logger.info(
            "🆗 created token with id %(token_id)s for partner with id %(partner_id)s from "
            "transaction with reference %(ref)s",
            {
                'token_id': token.id,
                'partner_id': self.partner_id.id,
                'ref': self.reference,
            },
        )
    
    def get_niubiz_response_auth_json(self):
        jsonall = {}
        try:
            if self.state in ['done', 'authorized']:
                if self.niubiz_response_auth_json:
                    jsonall = json.loads(self.niubiz_response_auth_json)
                if self.niubiz_response_cap_json:
                    jsonall = json.loads(self.niubiz_response_cap_json)
            elif self.state in ['error']:
                if self.niubiz_response_auth_json:
                    jsonall = json.loads(self.niubiz_response_auth_json)
                elif self.niubiz_response_error_json:
                    jsonall = json.loads(self.niubiz_response_error_json)
            elif self.state in ['cancel']:
                if self.niubiz_response_auth_json:
                    jsonall = json.loads(self.niubiz_response_auth_json)
                elif self.niubiz_response_void_json:
                    jsonall = json.loads(self.niubiz_response_void_json)
            elif self.state in ['refund']:
                if self.niubiz_response_auth_json:
                    jsonall = json.loads(self.niubiz_response_auth_json)
                elif self.niubiz_response_void_json:
                    jsonall = json.loads(self.niubiz_response_void_json)
        except:
            _logger.error("No se pudo cargar el json de niubiz_response_auth_json")

        if self.state in ['done', 'authorized']:
            if isinstance(jsonall.get('auth_sale', {}).get('dataMap'), dict):
                return jsonall.get('auth_sale').get('dataMap')
            if isinstance(jsonall.get('confirmation', {}).get('dataMap'), dict):
                return jsonall.get('confirmation').get('dataMap', {})
            else:
                return {}
        elif self.state in ['error']:
            if isinstance(jsonall.get('auth_sale', {}).get('data'), dict):
                return jsonall.get('auth_sale').get('data')
            elif isinstance(jsonall.get('auth_token', {}).get('data'), dict):
                return jsonall.get('auth_token').get('data')
            elif isinstance(jsonall.get('auth_token', {}).get('order'), dict):
                return jsonall.get('auth_token').get('order')
            elif isinstance(jsonall.get('confirmation', {}).get('data'), dict):
                return jsonall.get('confirmation').get('data')
            elif isinstance(jsonall.get('void', {}).get('data'), dict):
                return jsonall.get('void').get('data')
            else:
                return {}
        else:
            return {}

    def convert_txt_to_datetime(self, txt):
        return niubiz_utils.txt_to_datetime(txt)

    def get_description_eci_or_action(self, json):
        action_code = json.get('ACTION_CODE', '') or json.get('actionCode', '')
        description = const.ACTION_CODES.get(action_code,'')
        description = description[0] if len(description) else description
        if not description:
            description = const.CODE_ECI.get(json.get('ECI',''),'Operación Denegada. Contactar con el comercio.')
        return description
