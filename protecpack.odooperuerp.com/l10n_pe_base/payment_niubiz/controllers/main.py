# -*- coding: utf-8 -*-
import logging
import pprint
import json

from werkzeug.urls import url_encode, url_join

from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale

_logger = logging.getLogger(__name__)


class NiubizController(http.Controller):
    _return_url = '/payment/niubiz/return'
    _timeout_url = '/payment/niubiz/timeout'
    _payment_url = '/shop/payment'

    @http.route(_return_url, type='http', auth='public', csrf=False, save_session=False)
    def niubiz_return_from_checkout(self, **data):
        """ Process the notification data sent by Niubiz after redirection from payment.

        Customers go through this route regardless of whether the payment was direct or with
        redirection to Niubiz or to an external service (e.g., for strong authentication).

        :param dict data: The notification data, including the reference appended to the URL in
                          `_get_specific_processing_values`.
        """

        # _logger.info("\n🆗 niubiz_return_from_checkout:\n%s", json.dumps(data, indent=4, sort_keys=True))

        # Retrieve the transaction based on the reference included in the return url.
        tx_sudo = request.env['payment.transaction'].sudo()._get_tx_from_notification_data(
            'niubiz', data
        )
        reference = data.get('reference', '')
        order = request.env['sale.order'].sudo().search([('name', '=', reference.split("-")[0])])
        recurring_invoice = tx_sudo.provider_id._is_order_recurring_invoice(order)
        # Si el canal es 'paycard' invocar "Solicitar autorización de transacción" (api.ecommerce/v2/ecommerce/token/card/)
        merchant_id = tx_sudo.provider_id._get_merchant_id(tx_sudo.currency_id.name, recurring_invoice)
        authorization_token = {}
        authorization_sale = {}
        # La persona de integración de Niubiz indico que el channel la primera vez es web
        # cambiar el canal a web involucra buscar otra manera de ejecutar el api de token_card

        # order = request.env['sale.order'].sudo().search([('name', '=', tx_sudo.reference.split("-")[0])])
        # recurring_invoice = tx_sudo.provider_id._is_order_recurring_invoice(order)

        if data.get('channel') == 'paycard':
            authorization_token = tx_sudo.provider_id._niubiz_make_request(
                endpoint='/token_card/{}/{}',
                endpoint_param=(merchant_id, data.get('transactionToken')),
                method='GET'
            )
            # _logger.info("\n🆗 authorization_token:\n%s", json.dumps(authorization_token, indent=4, sort_keys=True))
            self._include_authorization_token_in_notification_data(authorization_token, data)

            if authorization_token.get('order', {}).get('status', '') == 'Verified':
                authorization_sale = tx_sudo.provider_id._niubiz_make_request(
                    endpoint='/authorization/{}',
                    endpoint_param=merchant_id,
                    payload=self._niubiz_prepare_authorization_sale_payload(data, tx_sudo),
                    method='POST'
                )
                # _logger.info("\n🆗 authorization_sale:\n%s", json.dumps(authorization_sale, indent=4, sort_keys=True))
                self._include_authorization_sale_in_notification_data(authorization_sale, data)

        if data.get('channel') == 'web':
            authorization_sale = tx_sudo.provider_id._niubiz_make_request(
                endpoint='/authorization/{}',
                endpoint_param=merchant_id,
                payload=self._niubiz_prepare_authorization_sale_payload(data, tx_sudo),
                method='POST'
            )
            # _logger.info("\n🆗 authorization_sale:\n%s", json.dumps(authorization_sale, indent=4, sort_keys=True))
            self._include_authorization_sale_in_notification_data(authorization_sale, data)

        if authorization_sale.get('dataMap', {}).get('STATUS') == 'Authorized' and tx_sudo.provider_id.niubiz_confirmation_auto:
            confirmation_sale = tx_sudo.provider_id._niubiz_make_request(
                endpoint='/confirmation/{}',
                endpoint_param=merchant_id,
                payload=self._niubiz_prepare_confirmation_payload(data, tx_sudo),
                method='POST'
            )
            # _logger.info("\n🆗 confirmation_sale:\n%s", json.dumps(confirmation_sale, indent=4, sort_keys=True))
            self._include_confirmation_in_notification_data(confirmation_sale, data)
        
        # else:
        #     if data.get('transactionToken'):
        #         data.update({'errorCode': 0,'payment_state': data.get('channel')})

        # Handle the notification data crafted with Niubiz API's objects.
        tx_sudo._handle_notification_data('niubiz', data)
        return request.redirect('/payment/status')
        # return request.redirect(url_join('/payment/status',f''))

    @staticmethod
    def _niubiz_prepare_confirmation_payload(data, tx_sudo):
        """ Prepare the payload for the creation of a api.confirmation object in Niubiz format.

        Note: This method serves as a hook for modules that would fully implement Niubiz Tokenización.

        :return: The Niubiz-formatted payload for the api.confirmation request.
        :rtype: dict
        """
        return {
            'channel': data.get('channel'),
            'captureType': 'manual',
            'order': {
                'purchaseNumber': tx_sudo.niubiz_reference,
                'amount': round(tx_sudo.amount, 2),
                'currency': tx_sudo.currency_id.name.upper(),
                'transactionId': data.get('auth_sale', {}).get('dataMap', {}).get('TRANSACTION_ID',''),
            }
        }

    @staticmethod
    def _niubiz_prepare_authorization_sale_payload(data, tx_sudo):
        """ Prepare the payload for the creation of a api.authorization object in Niubiz format.

        Note: This method serves as a hook for modules that would fully implement Niubiz Tokenización.

        :return: The Niubiz-formatted payload for the api.authorization request.
        :rtype: dict
        """
        payload = {
            'channel': 'web',
            'captureType': 'manual',
            'countable': tx_sudo.provider_id.niubiz_liquidation_auto,
            'order': {
                'purchaseNumber': tx_sudo.niubiz_reference,
                'amount': round(tx_sudo.amount,2),
                'currency': tx_sudo.currency_id.name.upper(),
            }
        }
        if data.get('recurring','False') == 'True':
            payload.update({
                'card': {
                    'tokenId': data.get('auth_token', {}).get('token', {}).get('tokenId'),
                    'registerFrequent': True,
                    'useFrequent': False
                },
                'cardHolder': {
                    'email': tx_sudo.partner_id.email
                }
            })
        else:
            payload.update({
                'order': {**payload.get('order'),
                    'tokenId': data.get('transactionToken')
                }
            })
        # _logger.info("\n🆗 _niubiz_prepare_authorization_sale_payload:\n%s", json.dumps(payload, indent=4, sort_keys=True))
        return payload

    @staticmethod
    def _include_authorization_token_in_notification_data(auth_token, notification_data):
        notification_data.update({
            'auth_token': auth_token,
            'errorCode': auth_token.get('errorCode', 0),
            'payment_state': auth_token.get('order', {}).get('status', '401')
        })
    
    @staticmethod
    def _include_authorization_sale_in_notification_data(auth_sale, notification_data):
        payment_state = auth_sale.get('dataMap', {}).get('STATUS', '401')
        notification_data.update({
            'auth_sale': auth_sale,
            'errorCode': 401 if payment_state == '401' else auth_sale.get('errorCode', 0),
            'payment_state': payment_state
        })
    
    @staticmethod
    def _include_confirmation_in_notification_data(confirmation, notification_data):
        payment_state = confirmation.get('dataMap', {}).get('STATUS', '401')
        notification_data.update({
            'confirmation': confirmation,
            'errorCode': 401 if payment_state == '401' else confirmation.get('errorCode', 0),
            'payment_state': payment_state
        })

    @staticmethod
    def _include_void_in_notification_data(void, notification_data):
        notification_data.update({
            'void': void,
            'errorCode': void.get('errorCode', 0),
            'payment_state': void.get('dataMap', {}).get('STATUS', '401')
        })
    
    @staticmethod
    def _include_refund_in_notification_data(refund, notification_data):
        notification_data.update({
            'refund': refund,
            'errorCode': refund.get('errorCode', 0),
            'payment_state': refund.get('data', {}).get('DSCERROR', '401')
        })

    @http.route(_timeout_url, type='http', auth='public')
    def niubiz_timeout_from_checkout(self, **data):
        """ Process the notification data sent by Niubiz after timeout from payment.

        Customers go through this route regardless of whether the payment was direct or with
        redirection to Niubiz or to an external service (e.g., for strong authentication).

        :param dict data: The notification data, including the reference appended to the URL in
                          `_get_specific_processing_values`.
        """

        # Retrieve the transaction based on the reference included in the timeout url.
        # tx_sudo = request.env['payment.transaction'].sudo()._get_tx_from_notification_data(
        #     'niubiz', data
        # )
        # _logger.info(f'\n◀️ niubiz_timeout_from_checkout (data):\n {data} \n')
        return request.redirect('/shop/payment')

    @http.route(['/payment/niubiz/url_tyc'], type='json', auth="public", website=True)
    def terms_and_conditions_url(self, **kw):
        # return request.env['payment.provider'].sudo().search([('code', '=', provider_code)]).mapped(lambda r: {'url': r.niubiz_url_TyC})
        provider = request.env['payment.provider'].sudo().search([('code', '=', kw.get('providerCode'))], limit=1)
        base_url = provider.get_base_url()
        return url_join(base_url, provider.niubiz_url_TyC) or '/terms'


# class WebsiteSaleExtend(WebsiteSale):

#     def _get_shop_payment_values(self, order, **kwargs):
#         values = super(WebsiteSaleExtend,self)._get_shop_payment_values(order=order, **kwargs)

#         config_setting = {
#             'terms_and_conditions_route': request.website.terms_and_conditions_route if request.website.terms_and_conditions_show else None
#         }
#         values = {**values,**config_setting}
#         return values
