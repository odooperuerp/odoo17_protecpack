import json
import logging
import requests
import pprint
import uuid

from requests.auth import HTTPBasicAuth

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError, UserError

from odoo.addons.payment import utils as payment_utils
from odoo.addons.payment_niubiz import const, utils as niubiz_utils

_logger = logging.getLogger(__name__)


class PaymentProvider(models.Model):
    _inherit = "payment.provider"

    code = fields.Selection(selection_add=[('niubiz',"Niubiz")],ondelete={"niubiz":'set default'})
    niubiz_user = fields.Char('Correo', required_if_provider="niubiz", groups="base.group_system")
    niubiz_password = fields.Char('Contraseña', required_if_provider="niubiz", groups="base.group_system")
    # Merchant Pago Web
    niubiz_pw_merchant_id_pen = fields.Char('Código de comercio Soles',
        groups="base.group_system", 
        help="Código de Comercio, creado al momento de la afiliación al producto Comercio Electrónico Pago Web")
    niubiz_pw_merchant_id_usd = fields.Char('Código de comercio Dolares', 
        groups="base.group_system", 
        help="Código de Comercio, creado al momento de la afiliación al producto Comercio Electrónico Pago Web")
    # Merchant Tokenización
    niubiz_tk_merchant_id_pen = fields.Char('Código de comercio Soles', 
        groups="base.group_system", 
        help="Código de Comercio, creado al momento de la afiliación al producto Comercio Electrónico Pago Web")
    niubiz_tk_merchant_id_usd = fields.Char('Código de comercio Dolares', 
        groups="base.group_system", 
        help="Código de Comercio, creado al momento de la afiliación al producto Comercio Electrónico Pago Web")
    # Merchant Recurrent
    niubiz_merchant_id_recurrent = fields.Char('Código de comercio recurrente',
        groups="base.group_system", 
        help="Código de Comercio, creado al momento de la afiliación al producto Comercio Electrónico Pago Recurrente")
    
    niubiz_confirmation_auto = fields.Boolean('Confirmación automatica', 
        groups="base.group_system", 
        default=False,
        help='Permitirá realizar la confirmación de una transacción de venta no contable.')
    niubiz_liquidation_auto = fields.Boolean('Liquidación Automatica',
        groups="base.group_system",
        default=True,
        help="Este campo indica si la venta a realizar tendrá liquidación automática o manual."
            "\nAcepta los siguientes valores:"
            "\n• true – Para liquidación automática"
            "\n• false – Para liquidación manual"
            "\nValor por defecto: Según configuración del comercio en BackOffice Niubiz")
    niubiz_state_js = fields.Selection([('test', 'Test'),('sanbox', 'Sanbox')], 
        string='Estado JS', 
        default='test',
        groups="base.group_system",
        help="El estado JS establece con que librerías JS se va a trabajar en el 'Modo de prueba'."
            "\nEn el estado 'Habilitado' se trabaja con las librerias JS de producción.")
    niubiz_show_pen = fields.Boolean(compute='_compute_niubiz_show', string='niubiz_show_pen')
    niubiz_show_usd = fields.Boolean(compute='_compute_niubiz_show', string='niubiz_show_usd')

    @api.depends('available_currency_ids')
    def _compute_niubiz_show(self):
        for payment in self:
            currency_pen = payment.available_currency_ids.filtered(lambda c: c.name == 'PEN')
            currency_usd = payment.available_currency_ids.filtered(lambda c: c.name == 'USD')
            payment.niubiz_show_pen = True if currency_pen else False
            payment.niubiz_show_usd = True if currency_usd else False

    def _check_confirmation_liquidation(self, vals):
        if 'niubiz_confirmation_auto' in vals:
            niubiz_confirmation_auto = vals.get('niubiz_confirmation_auto')
        else:
            niubiz_confirmation_auto = self.niubiz_confirmation_auto
        if 'niubiz_liquidation_auto' in vals:
            niubiz_liquidation_auto = vals.get('niubiz_liquidation_auto')
        else:
            niubiz_liquidation_auto = self.niubiz_liquidation_auto
        if niubiz_liquidation_auto and niubiz_confirmation_auto:
            if 'niubiz_confirmation_auto' in vals:
                vals['niubiz_confirmation_auto'] = not vals['niubiz_confirmation_auto']
            if 'niubiz_liquidation_auto' in vals:
                vals['niubiz_liquidation_auto'] = not vals['niubiz_liquidation_auto']
            raise UserError(_('Cuando la liquidación es automática, no es necesario activar la confirmación automática.'))
    
    #=== CUSTOMIZE MODAL ====#

    niubiz_hidexbutton = fields.Boolean('Ocultar el cerrar (X)', 
        groups="base.group_system", 
        default=True,
        help="Permite ocultar el cerrar (X) en el formulario de pago. Valor por defecto: FALSE. Otros valores:"
            "\n- TRUE \n- FALSE")
    niubiz_expirationminutes = fields.Integer('Minutos de expiración', 
        required_if_provider="niubiz", 
        groups="base.group_system", 
        help='Tiempo de duración de la sesión de pago expresado en minutos.',
        default=20)
    niubiz_merchantname = fields.Char('Nombre de comercio', 
        required_if_provider="niubiz", 
        groups="base.group_system", 
        default="Comercio.pe",
        help="Nombre que se muestra en la cabecera del formulario de pago")
    niubiz_merchantlogo_show = fields.Boolean('Mostrar logo', 
        groups="base.group_system", 
        default=True)
    niubiz_merchantlogo = fields.Char('URL de Logo', 
        groups="base.group_system", 
        default='',
        help="URL del logo del comercio. Altamente recomendable incluir un logo, caso contrario se mostrará el " 
            "nombre del comercio. El tamaño sugerido es 187x40px. Nota: Si no inserta este valor, por no contar " 
            "con una imagen como logo, es obligatorio colocar un texto en el campo “merchantname”")
    niubiz_formbuttoncolor = fields.Char('Color del bóton pagar',
        groups="base.group_system", 
        default='#D80000',
        help="Define el color del botón en el formulario, por default es el color “rojo”.\n"
            "Ingresar valor en hexadecimal")
    niubiz_formbuttontext = fields.Char('Texto del bóton pagar',
        groups="base.group_system", 
        default="",
        help="Define el texto que se mostrará en el botón del formulario, por default es el texto “pagar”")
    niubiz_formbackgroundcolor = fields.Char('Color de fondo',
        groups="base.group_system", 
        default="#FFFFFF",
        help="Define el color de fondo en el formulario, por default es el color “gris”.\n"
            "Ingresar valor en hexadecimal")
    niubiz_formbuttontextcolor = fields.Char('Color del texto del botón,',
        groups="base.group_system", 
        default="#FFFFFF",
        help="Define el color del texto del botón, por default es el color “blanco”.\n"
            "Ingresar valor en hexadecimal")
    niubiz_showamount = fields.Boolean('Mostrar importe', 
        groups="base.group_system",
        default=True,
        help="Indica si se muestra en el botón del formulario algún importe referencial al pago de la transacción" 
            "en caso se ejecute la autorización en ese momento.\nValor por defecto: TRUE.\nOtros valores: \n– TRUE \n– FALSE")
    
    niubiz_url_TyC = fields.Char('URL de Términos y Condiciones', 
        required_if_provider="niubiz", 
        groups="base.group_system", 
        default='/terms')
    
    #=== MODULE ===#
    
    niubiz_module_sale_subscription = fields.Boolean('Module Sale Subscription')

    #=== CRUD METHODS ===#

    def _check_modules_to_install(self):
        # determine modules to install
        expected = [
            fname[7:]           # 'module_account' -> 'account'
            for fname in self._fields
            if fname.startswith('niubiz_module_')
            if any(pay_provider[fname] for pay_provider in self)
        ]
        if expected:
            STATES = ('installed', 'to install', 'to upgrade')
            modules = self.env['ir.module.module'].sudo().search([('name', 'in', expected)])
            modules = modules.filtered(lambda module: module.state not in STATES)
            if modules:
                modules.button_immediate_install()
                # just in case we want to do something if we install a module. (like a refresh ...)
                return True
        return False

    def _check_min_max_expirationminutes(self, vals):
        if 'niubiz_expirationminutes' in vals:
            return 20 >= int(vals['niubiz_expirationminutes']) >= 5
        return True

    def write(self, vals):
        self._check_confirmation_liquidation(vals)
        if self._check_min_max_expirationminutes(vals):
            result = super().write(vals)
            self.sudo()._check_modules_to_install()
            return result
        else:
            raise UserError(_('Los minutos de expiración del modal son de 5 a 20 minutos.'))

    #=== COMPUTE METHODS ===#
    
    def _compute_feature_support_fields(self):
        """ Override of `payment` to enable additional features. """
        super()._compute_feature_support_fields()
        self.filtered(lambda p: p.code == 'niubiz').update({
            'support_manual_capture': 'partial',
            'support_refund': "partial",
            'support_tokenization': True
        })
    
    #=== CHANGE METHODS ===#

    @api.onchange('allow_tokenization')
    def _onchange_allow_tokenization_module_sale_subscription(self):
        if self.allow_tokenization and self.code == 'niubiz':
            self.niubiz_module_sale_subscription = True
        else:
            self.niubiz_module_sale_subscription = False

    #=== GET METHODS ===#

    def _is_order_recurring_invoice(self, order):
        self.ensure_one()
        if self.niubiz_module_sale_subscription:
            return bool(order.sudo().order_line.filtered(lambda l: l.product_id.recurring_invoice))
        return False

    def _get_merchant_id(self, currency, recurring_invoice):
        currency = currency.lower()
        """ Determine which merchant id to use depending on the currency """
        if recurring_invoice:
            merchant_id = self.niubiz_tk_merchant_id_pen if currency == 'pen' else self.niubiz_tk_merchant_id_usd
        else:
            merchant_id = self.niubiz_pw_merchant_id_pen if currency == 'pen' else self.niubiz_pw_merchant_id_usd
        return merchant_id

    def _get_supported_currencies(self):
        """ Override of `payment` to return the supported currencies. """
        supported_currencies = super()._get_supported_currencies()
        if self.code == 'niubiz':
            supported_currencies = supported_currencies.filtered(
                lambda c: c.name in const.SUPPORTED_CURRENCIES
            )
        return supported_currencies

    # === BUSINESS METHODS - PAYMENT FLOW === #

    def _niubiz_make_request(self, endpoint, endpoint_param=None, payload=None, method='POST', security=False, idempotency_key=None):
        """ Make a request to Niubiz API at the specified endpoint.

        Note: self.ensure_one()

        :param str endpoint: The endpoint to be reached by the request
        :param str endpoint_param: A variable required by some endpoints which are interpolated with
                                    it if provided. For example, the provider reference of the source
                                    transaction for the 'api.ecommerce/v2/ecommerce/token/session/{}' endpoint.
        :param dict payload: The payload of the request
        :param str method: The HTTP method of the request
        :param bool security: When creating an access token (Security)
        :param str idempotency_key: The idempotency key to pass in the request.
        :return: The JSON-formatted content of the response
        :rtype: dict
        :raise: ValidationError if an HTTP error occurs
        """
        def _build_url(endpoint_):
            """ Build an API URL by appending the version and endpoint to a base URL.

            The final URL follows this pattern: `<_base>/<_endpoint>`.

            :param str endpoint_: The endpoint of the URL.
            :return: The final URL.
            :rtype: str
            """
            endpoint_ = endpoint_.lstrip('/')  # Remove potential leading slash
            prod_mode = self.state == 'enabled'
            base_ = '/base_prod' if prod_mode else '/base_test' # base_sanbox
            return f'https://{const.API_ENDPOINT[base_]}/{endpoint_}'

        endpoint = const.API_ENDPOINT[endpoint]
        if isinstance(endpoint_param, tuple):
            endpoint = endpoint.format(*endpoint_param)
        if isinstance(endpoint_param, str):
            endpoint = endpoint.format(endpoint_param)
            
        url = _build_url(endpoint)
        try:
            if security:
                response = requests.request(method, url, json=payload, auth=HTTPBasicAuth(self.niubiz_user, self.niubiz_password), timeout=60)
            else:
                headers = {
                    'accept': 'application/json',
                    'Content-Type': 'application/json',
                    'Authorization': self._niubiz_make_request('/security', security=True, method='GET')
                }
                response = requests.request(method, url, json=payload, headers=headers, timeout=60)
            # Niubiz puede enviar 400 errores por errores de pago (no sólo por solicitudes mal formadas).
            # Verifique si hay un código de error presente en el contenido de la respuesta y genere solo si no es así.
            # https://desarrolladores.niubiz.com.pe/docs/bot%C3%B3n-de-pago-1#4%EF%B8%8F%E2%83%A3-solicitar-autorizaci%C3%B3n-de-transacci%C3%B3n
            # Si la solicitud se origina en una operación fuera de línea, no la genere para evitar que el cursor
            # retroceda y devuelva la respuesta tal cual para un manejo específico del flujo.
            if not response.ok and response.status_code != 400:
                try:
                    response.raise_for_status()
                except requests.exceptions.HTTPError:
                    _logger.exception(
                        "\n🔴🔴🔴 invalid API request at %s with data \n%s\n🔴🔴🔴 Motive: \n%s\n", 
                        url, json.dumps(payload, indent=4, sort_keys=True), response.text
                    )
                    # error_msg = response.json().get('error', {}).get('message', '')
                    raise ValidationError(
                        "Niubiz: " + _(
                            "The communication with the API failed.\n"
                            "Niubiz gave us the following info about the problem:\n'%s'", response.text
                        )
                    )
        except requests.exceptions.ConnectionError:
            _logger.exception("\n🔴 unable to reach endpoint at %s", url)
            raise ValidationError("Niubiz: " + _("Could not establish the connection to the API."))
        return response.text if security else response.json()
        
    def _niubiz_make_request_old(self, endpoint, param=None, payload=None, method='POST'):
        def _build_url(endpoint_):
            prod_mode = self.state == 'enabled'
            base_ = 'base_prod' if prod_mode else 'base_test' # base_sanbox
            return f'https://{const.API_ENDPOINT[base_]}/{const.API_ENDPOINT[endpoint_]}'

        url = _build_url(endpoint)
        try:
            headers= {
                'accept': 'application/json',
                'Content-Type': 'application/json',
                'Authorization': param.get('token','') if param else None
            }
            if endpoint == 'security':
                response = requests.request(method, url, json=payload, auth=HTTPBasicAuth(self.niubiz_user, self.niubiz_password), timeout=60)
            elif endpoint == 'session':
                url = f"{url}{param.get('merchant_id','')}"
                response = requests.request(method, url, json=payload, headers=headers, timeout=60)
            elif endpoint == 'authorization_token':
                url = f"{url}{param.get('merchant_id','')}/{param.get('transactionToken','')}"
                response = requests.request(method, url, json=payload, headers=headers, timeout=60)
            elif endpoint == 'authorization_sale':
                url = f"{url}{param.get('merchant_id','')}"
                response = requests.request(method, url, json=payload, headers=headers, timeout=60)
            try:
                response.raise_for_status()
            except requests.exceptions.HTTPError:
                _logger.exception(
                    "invalid API request at %s with data \n%s: \n%s", url, pprint.pformat(payload), response.text
                )
                # msg = response.json().get('errorMessage', '')
                raise ValidationError(
                    "Niubiz: " + _("The communication with the API failed. Details: %s", response.text)
                )
        except requests.exceptions.ConnectionError:
            _logger.exception("unable to reach endpoint at %s", url)
            raise ValidationError("Niubiz: " + _("Could not establish the connection to the API."))
        return response
    
    def _niubiz_prepare_data_session(self, channel, order):
        return {
            'channel': channel if channel else 'web',
            'amount': round(order.amount_total, 2),
            'antifraud': {
                'clientIp': self.get_base_url(),
                'merchantDefineData': {
                    'MDD4': order.partner_id.email,
                    'MDD21': order.partner_id.niubiz_regular_client,
                    'MDD32':  order.partner_id.email,
                    'MDD75':  'Registrado',
                    'MDD77':  order.partner_id.niubiz_days_since_register
                }
            }
        }
        
    def _prepare_data_confirmation(self, auth):
        return {
            'channel': 'web',
            'captureType': 'manual',
            'order': {
                'purchaseNumber': auth['order']['purchaseNumber'],
                'amount': round(auth['order']['amount'], 2),
                'authorizedAmount': round(auth['order']['amount'], 2),
                'currency': auth['order']['currency'],
                'transactionId': auth['order']['transactionId']
            }
        }

    #=== BUSINESS METHODS - GETTERS ===#

    def _niubiz_get_sdk_assets(self, sale_order_id):
        """ Return el endpoint js depending on the order, whether it is a subscription or a single-use product.

        :param int sale_order_id:: The orden of the transaction, as a `sale.order` id.

        :return: The js endpoint for the niubiz payment button
        """
        def _build_url_js(recurring_invoice):
            prod_mode = self.state == 'enabled'
            niubiz_test = self.niubiz_state_js == 'test'
            endpoint_ = 'js_prod' if prod_mode else ('js_test' if niubiz_test else 'js_sanbox')
            endpoint_ += '_token' if recurring_invoice else ''
            return const.API_ENDPOINT[endpoint_]

        order = self.env['sale.order'].sudo().browse(sale_order_id).exists()
        return _build_url_js(self._is_order_recurring_invoice(order))

    def _niubiz_get_inline_form_values(self, amount, currency, partner_id, is_validation, payment_method_sudo=None, **kwargs):
        """ Return a serialized JSON of the required values to render the inline form.

        Note: `self.ensure_one()`

        :param float amount: The amount in major units, to convert in minor units.
        :param res.currency currency: The currency of the transaction.
        :param int partner_id: The partner of the transaction, as a `res.partner` id.
        :param bool is_validation: Whether the operation is a validation.
        :param payment.method payment_method_sudo: The sudoed payment method record to which the
                                                   inline form belongs.
        :return: The JSON serial of the required values to render the inline form.
        :rtype: str
        """
        self.ensure_one()
        partner = self.env['res.partner'].with_context(show_address=1).sudo().browse(partner_id).exists()
        order = self.env['sale.order'].sudo().browse(kwargs.get('sale_order_id')).exists()
        currency = currency or order.currency_id
        amount = amount or order.amount_total
        recurring_invoice = self._is_order_recurring_invoice(order)
        channel = self._get_channel(payment_method_sudo.code, recurring_invoice)
        merchant_id = self._get_merchant_id(currency.name, recurring_invoice)
        session = self._niubiz_make_request(
            endpoint='/session/{}',
            endpoint_param=merchant_id,
            payload=self._niubiz_prepare_data_session(channel, order)
        )

        inline_form_values = {
            'sessiontoken': session['sessionKey'],
            'channel': channel,
            'merchantname': self.niubiz_merchantname,
            'merchantid': merchant_id,
            'amount': round(amount,2),
            'cardholdername': order.partner_id.first_name,
            'cardholderlastname': order.partner_id.last_name,
            'cardholderemail': order.partner_id.email,
            'expirationminutes': self.niubiz_expirationminutes,
            'formbuttoncolor': self.niubiz_formbuttoncolor,
            'formbuttontext': self.niubiz_formbuttontext,
            'showamount': self.niubiz_showamount,
            'hidexbutton': self.niubiz_hidexbutton,
            'formbackgroundcolor': self.niubiz_formbackgroundcolor,
            'formbuttontextcolor': self.niubiz_formbuttontextcolor,
        }
        if recurring_invoice:
            if not partner.niubiz_user_token:
                partner.sudo().write({'niubiz_user_token': uuid.uuid4()})
            # inline_form_values['usertoken'] = partner.niubiz_user_token
        else:
            if not partner.niubiz_user_token_pw:
                partner.sudo().write({'niubiz_user_token_pw': uuid.uuid4()})
            inline_form_values['usertoken'] = partner.niubiz_user_token_pw
            inline_form_values['method'] = 'POST'

        if self.niubiz_merchantlogo_show:
            inline_form_values['merchantlogo'] = self.niubiz_merchantlogo

        # _logger.info("\n🆗 _datos_formulario_pago:\n%s", json.dumps(inline_form_values, indent=4, sort_keys=True))
        return json.dumps(inline_form_values)
 
    def _get_default_payment_method_codes(self):
        """ Override of `payment` to return the default payment method codes. """
        default_codes = super()._get_default_payment_method_codes()
        if self.code != 'niubiz':
            return default_codes
        return const.DEFAULT_PAYMENT_METHODS_CODES

    def _get_channel(self, payment_method_sudo, recurring_invoice):
        if payment_method_sudo == 'card':
            channel = 'paycard' if recurring_invoice else 'web'
        else:
            channel = payment_method_sudo
        return channel
