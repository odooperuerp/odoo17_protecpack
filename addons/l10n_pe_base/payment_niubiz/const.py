# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _

API_ENDPOINT = {
    '/base_sanbox': 'apisandbox.vnforappstest.com',
    '/base_test': 'apitestenv.vnforapps.com',
    '/base_prod': 'apiprod.vnforapps.com',
    '/security': 'api.security/v1/security', # 1. Crear un token de acceso (Seguridad)
    '/session/{}': 'api.ecommerce/v2/ecommerce/token/session/{}', # 2. Crear un token de sesión
    '/token_card/{}/{}': 'api.ecommerce/v2/ecommerce/token/card/{}/{}', # 4. Solicitar autorización de transacción [Tokenizacion]
    '/yape/{}': 'api.yape/v2/yape/transaction/{}', # Pago con Yape Integrado
    '/authorization/{}': 'api.authorization/v3/authorization/ecommerce/{}', # 5. Esta API permitirá realizar una operación de venta con una tarjeta o token.
    '/confirmation/{}': 'api.confirmation/v1/confirmation/ecommerce/{}', # API de Confirmación
    '/void/{}/{}/{}': 'api.authorization/v3/void/{}/{}/{}', # Anular una venta del día
    '/reverse/{}/{}': 'api.authorization/v3/reverse/{}/{}', # API de reversa o extorno una venta
    '/refund/{}/{}': 'api.refund/v1/refund/{}/{}', # API Registro de Devolución Individual
    'js_sanbox': 'https://static-content-qas.vnforapps.com/env/sandbox/js/checkout.js', # 3. Configurar el botón de pago web
    'js_test': 'https://static-content-qas.vnforapps.com/v2/js/checkout.js?qa=true', # 3. Configurar el botón de pago web
    'js_prod': 'https://static-content.vnforapps.com/v2/js/checkout.js', # 3. Configurar el botón de pago web
    'js_sanbox_token': 'https://static-content-qas.vnforapps.com/vTokenSandbox/js/checkout.js', # 3.  Configurar el botón de tokenización web
    'js_test_token': 'https://static-content-qas.vnforapps.com/vToken/js/checkout.js', # 3.  Configurar el botón de tokenización web
    'js_prod_token': 'https://static-content.vnforapps.com/vToken/js/checkout.js', # 3.  Configurar el botón de tokenización web
}

# Currency codes of the currencies supported by Niubiz in ISO 4217 format.
# See https://api.mercadopago.com/currencies. Last seen online: 24 November 2022.
SUPPORTED_CURRENCIES = [
    'PEN',  # Sol
    'USD',  # US Dollars
]

# The codes of the payment methods to activate when Niubiz is activated.
DEFAULT_PAYMENT_METHODS_CODES = [
    # Primary payment methods.
    'card',
    # 'pagoefectivo',
    # Brand payment methods.
    'visa',
    'mastercard',
    'amex',
    'diners',
    'unionpay',
    'yape',
    'tunki',
    # 'pagoefectivo_brand',
]

# Mapping of payment method codes to Niubiz codes.
# odoo -> provider
PAYMENT_METHODS_MAPPING = {
    'amex': 'amex',
    'diners': 'dinersclub',
    'unionpay': 'unionpay',
    'visa': 'visa',
    'mastercard': 'mastercard',
    'yape': 'yape'
}

# Mapping of transaction states to Niubiz payment statuses.
# See https://www.mercadopago.com.mx/developers/en/reference/payments/_payments_id/get.
STATUS_MAPPING = {
    'draft': (''),
    'pending': ('Verified', 'Review'),
    'authorized': ('Authorized', 'pagoefectivo'),
    'done': ('Confirmed'),
    'cancel': ('Voided', 'Reject', 'null', None),
    'error': ('Not Authorized', 'Not Confirmed', 'Not Verified', 'Not Voided','400','401','500'),
}
# The countries supported by Niubiz. See https://stripe.com/global page.
SUPPORTED_COUNTRIES = {
    'PE'
}


# Mapping of error action codes denials to Niubiz
# https://www.niubiz.com.pe/wp-content/uploads/2020/11/Documento-de-Integracio%CC%81n-Pago-Web.pdf
CODE_ECI = {
    '05': _('Transacción autenticada'),
    '06': _('Comercio intentó autenticación pero tarjetahabiente no está participando'),
    '07': _('Transacción no autenticada pero enviada en canal seguro'),
    '10': _('Entidad emisora no disponible para autenticación'),
    '11': _('Clave secreta del tarjetahabiente incorrecta'),
    '12': _('Tarjeta Vencida'),
}

ACTION_CODES = {
    '000': [_('Aprobado y completado con exito'),_('Aprobado y completado con exito')],
    '00': [_('Operación Denegada. Revisar registros log.'),_('Operación Denegada. Contactar con el comercio.')],
    '101': [_('Operación Denegada. Tarjeta Vencida.'),_('Operación Denegada. Tarjeta Vencida. Verifique los datos en su tarjeta e ingréselos correctamente.')],
    '102': [_('Operación Denegada. Contactar con la entidad emisora.'),_('Operación Denegada. Contactar con entidad emisora de su tarjeta.')],
    '104': [_('Operación Denegada. Operación no permitida para esta tarjeta.'),_('Operación Denegada. Operación no permitida para esta tarjeta. Contactar con la entidad emisora de su tarjeta.')],
    '106': [_('Operación Denegada. Exceso de intentos de ingreso de clave secreta.'),_('Operación Denegada. Intentos de clave secreta excedidos. Contactar con la entidad emisora de su tarjeta.')],
    '107': [_('Operación Denegada. Contactar con la entidad emisora.'),_('Operación Denegada. Contactar con la entidad emisora de su tarjeta.')],
    '108': [_('Operación Denegada. Exceso de actividad.'),_('Operación Denegada. Contactar con la entidad emisora de su tarjeta.')],
    '109': [_('Operación Denegada. Identificación inválida de establecimiento.'),_('Operación Denegada. Contactar con el comercio.')],
    '110': [_('Operación Denegada. Operación no permitida para esta tarjeta.'),_('Operación Denegada. Operación no permitida para esta tarjeta. Contactar con la entidad emisora de su tarjeta')],
    '111': [_('Operación Denegada. El monto de la transacción supera el valor máximo permitido para operaciones virtuales.'),_('Operación Denegada. Contactar con el comercio.')],
    '112': [_('Operación Denegada. Se requiere clave secreta.'),_('Operación Denegada. Se requiere clave secreta.')],
    '113': [_('Operación Denegada. Monto no permitido'),_('Operación Denegada. Monto no permitido')],
    '116': [_('Operación Denegada. Fondos insuficientes.'),_('Operación Denegada. Fondos insuficientes. Contactar con entidad emisora de su tarjeta.')],
    '117': [_('Operación Denegada. Clave secreta incorrecta.'),_('Operación Denegada. Clave secreta incorrecta.')],
    '118': [_('Operación Denegada. Tarjeta inválida.'),_('Operación Denegada. Tarjeta Inválida. Contactar con entidad emisora de su tarjeta.')],
    '119': [_('Operación Denegada. Exceso de intentos de ingreso de clave secreta.'),_('Operación Denegada. Intentos de clave secreta excedidos. Contactar con entidad emisora de su tarjeta.')],
    '121': [_('Operación Denegada.'),_('Operación Denegada.')],
    '126': [_('Operación Denegada. Clave secreta inválida.'),_('Operación Denegada. Clave secreta inválida.')],
    '129': [_('Operación Denegada. Tarjeta no operativa.'),_('Operación Denegada. Código de seguridad invalido. Contactar con entidad emisora de su tarjeta')],
    '180': [_('Operación Denegada. Tarjeta inválida.'),_('Operación Denegada. Tarjeta Inválida. Contactar con entidad emisora de su tarjeta.')],
    '181': [_('Operación Denegada. Tarjeta con restricciones de Débito.'),_('Operación Denegada. Tarjeta con restricciones de débito. Contactar con entidad emisora de su tarjeta.')],
    '182': [_('Operación Denegada. Tarjeta con restricciones de Crédito.'),_('Operación Denegada. Tarjeta con restricciones de crédito. Contactar con entidad emisora de su tarjeta.')],
    '183': [_('Operación Denegada. Error de sistema.'),_('Operación Denegada. Problemas de comunicación. Intente más tarde.')],
    '190': [_('Operación Denegada. Contactar con entidad emisora.'),_('Operación Denegada. Contactar con entidad emisora de su tarjeta.')],
    '191': [_('Operación Denegada. Contactar con entidad emisora.'),_('Operación Denegada. Contactar con entidad emisora de su tarjeta.')],
    '192': [_('Operación Denegada. Contactar con entidad emisora.'),_('Operación Denegada. Contactar con entidad emisora de su tarjeta.')],
    '199': [_('Operación Denegada.'),_('Operación Denegada.')],
    '201': [_('Operación Denegada. Tarjeta vencida.'),_('Operación Denegada. Tarjeta vencida. Contactar con entidad emisora de su tarjeta.')],
    '202': [_('Operación Denegada. Contactar con entidad emisora.'),_('Operación Denegada. Contactar con entidad emisora de su tarjeta.')],
    '204': [_('Operación Denegada. Operación no permitida para esta tarjeta.'),_('Operación Denegada. Operación no permitida para esta tarjeta. Contactar con entidad emisora de su tarjeta.')],
    '206': [_('Operación Denegada. Exceso de intentos de ingreso de clave secreta.'),_('Operación Denegada. Intentos de clave secreta excedidos. Contactar con la entidad emisora de su tarjeta.')],
    '207': [_('Operación Denegada. Contactar con entidad emisora.'),_('Operación Denegada. Contactar con entidad emisora de su tarjeta.')],
    '208': [_('Operación Denegada. Tarjeta perdida.'),_('Operación Denegada. Contactar con entidad emisora de su tarjeta.')],
    '209': [_('Operación Denegada. Tarjeta robada.'),_('Operación Denegada. Contactar con entidad emisora de su tarjeta.')],
    '263': [_('Operación Denegada. Error en el envío de parámetros.'),_('Operación Denegada. Contactar con el comercio.')],
    '264': [_('Operación Denegada. Entidad emisora no está disponible para realizar la autenticación.'),_('Operación Denegada. Entidad emisora de la tarjeta no está disponible para realizar la autenticación')],
    '265': [_('Operación Denegada. Clave secreta del tarjetahabiente incorrecta.'),_('Operación Denegada. Clave secreta del tarjetahabiente incorrecta. Contactar con entidad emisora de su tarjeta.')],
    '266': [_('Operación Denegada. Tarjeta vencida.'),_('Operación Denegada. Tarjeta Vencida. Contactar con entidad emisora de su tarjeta.')],
    '280': [_('Operación Denegada. Clave errónea.'),_('Operación Denegada. Clave secreta errónea. Contactar con entidad emisora de su tarjeta.')],
    '290': [_('Operación Denegada. Contactar con entidad emisora.'),_('Operación Denegada. Contactar con entidad emisora de su tarjeta.')],
    '300': [_('Operación Denegada. Número de pedido del comercio duplicado. Favor no atender.'),_('Operación Denegada. Número de pedido del comercio duplicado. Favor no atender.')],
    '306': [_('Operación Denegada. Contactar con entidad emisora.'),_('Operación Denegada. Contactar con entidad emisora de su tarjeta.')],
    '401': [_('Operación Denegada. Tienda inhabilitada.'),_('Operación Denegada. Contactar con el comercio.')],
    '402': [_('Operación Denegada.'),_('Operación Denegada.')],
    '403': [_('Operación Denegada. Tarjeta no autenticada.'),_('Operación Denegada. Tarjeta no autenticada.')],
    '404': [_('Operación Denegada. El monto de la transacción supera el valor máximo permitido.'),_('Operación Denegada. Contactar con el comercio.')],
    '405': [_('Operación Denegada. La tarjeta ha superado la cantidad máxima de transacciones en el día.'),_('Operación Denegada. Contactar con el comercio.')],
    '406': [_('Operación Denegada. La tienda ha superado la cantidad máxima de transacciones en el día.'),_('Operación Denegada. Contactar con el comercio.')],
    '407': [_('Operación Denegada. El monto de la transacción no llega al mínimo permitido.'),_('Operación Denegada. Contactar con el comercio.')],
    '408': [_('Operación Denegada. CVV2 no coincide.'),_('Operación Denegada. Código de seguridad no coincide. Contactar con entidad emisora de su tarjeta.')],
    '409': [_('Operación Denegada. CVV2 no procesado por entidad emisora.'),_('Operación Denegada. Código de seguridad no procesado por la entidad emisora de la tarjeta.')],
    '410': [_('Operación Denegada. CVV2 no procesado por no ingresado.'),_('Operación Denegada. Código de seguridad no ingresado.')],
    '411': [_('Operación Denegada. CVV2 no procesado por entidad emisora.'),_('Operación Denegada. Código de seguridad no procesado por la entidad emisora de la tarjeta.')],
    '412': [_('Operación Denegada. CVV2 no reconocido por entidad emisora.'),_('Operación Denegada. Código de seguridad no reconocido por la entidad emisora de la tarjeta.')],
    '413': [_('Operación Denegada. Contactar con entidad emisora.'),_('Operación Denegada. Contactar con entidad emisora de su tarjeta.')],
    '414': [_('Operación Denegada.'),_('Operación Denegada.')],
    '415': [_('Operación Denegada.'),_('Operación Denegada.')],
    '416': [_('Operación Denegada.'),_('Operación Denegada.')],
    '417': [_('Operación Denegada.'),_('Operación Denegada.')],
    '418': [_('Operación Denegada.'),_('Operación Denegada.')],
    '419': [_('Operación Denegada.'),_('Operación Denegada.')],
    '420': [_('Operación Denegada. Tarjeta no es VISA.'),_('Operación Denegada. Tarjeta no es VISA.')],
    '421': [_('Operación Denegada. Contactar con entidad emisora.'),_('Operación Denegada. Contactar con entidad emisora de su tarjeta.')],
    '422': [_('Operación Denegada. El comercio no está configurado para usar este medio de pago.'),_('Operación Denegada. El comercio no está configurado para usar este medio de pago. Contactar con el comercio.')],
    '423': [_('Operación Denegada. Se canceló el proceso de pago.'),_('Operación Denegada. Se canceló el proceso de pago.')],
    '424': [_('Operación Denegada. Contactar con entidad emisora.'),_('Operación Denegada.')],
    '476': [_('Operación Denegada. La operación ya se encuentra en un depósito.'),_('Operación Denegada. Contactar con el comercio.')],
    '479': [_('Operación Denegada. Código de comercio no existe o es inválido'),_('Operación Denegada. Contactar con el comercio.')],
    '499': [_('Operacion Denegada. Bóveda no asignada al establecimiento'),_('Operación Denegada. Contactar con el comercio.')],
    '666': [_('Operación Denegada. Problemas de comunicación. Intente más tarde.'),_('Operación Denegada. Problemas de comunicación. Intente más tarde.')],
    '667': [_('Operación Denegada. Transacción sin autenticación. Inicio del Proceso de Pago.'),_('Operación Denegada. Transacción sin respuesta de Verified by Visa.')],
    '668': [_('Operación Denegada.'),_('Operación Denegada. Contactar con el comercio.')],
    '669': [_('Operación Denegada.'),_('Operación Denegada. Contactar con el comercio')],
    '670': [_('Operación Denegada. Módulo antifraude.'),_('Operación Denegada. Contactar con el comercio.')],
    '672': [_('Operación Denegada. Transacción sin respuesta de Antifraude.'),_('Operación Denegada. Contactar con el comercio.')],
    '673': [_('Operación Denegada. Transacción sin respuesta del Autorizador.'),_('Operación Denegada. Contactar con el comercio.')],
    '674': [_('Operación Denegada. Sesión no válida.'),_('Operación Denegada. Contactar con el comercio.')],
    '675': [_('Inicialización de transacción.'),_('Inicialización de transacción.')],
    '676': [_('Operación Denegada. No activa la opción Revisar Enviar al Autorizador.'),_('Operación Denegada. Contactar con el comercio.')],
    '677': [_('Operación Denegada. Respuesta Antifraude con parámetros nos válidos.'),_('Operación Denegada. Contactar con el comercio.')],
    '678': [_('Operación Denegada. Valor ECI no válido.'),_('Operación Denegada. Contactar con el comercio.')],
    '682': [_('Operación Denegada. Intento de Pago fuera del tiempo permitido.'),_('Operación Denegada. Operación Denegada.')],
    '683': [_('Operación Denegada. Registro incorrecto de sesión.'),_('Operación Denegada. Registro incorrecto de sesión.')],
    '684': [_('Operación Denegada. Registro Incorrecto Antifraude.'),_('Operación Denegada Registro Incorrecto Antifraude.')],
    '685': [_('Operación Denegada. Registro Incorrecto Autorizador.'),_('Operación Denegada Registro Incorrecto Autorizador.')],
    '754': [_('Operación Denegada. Comercio no válido.'),_('Operación Denegada. Contactar con el comercio.')],
    '904': [_('Operación Denegada. Formato de mensaje erróneo.'),_('Operación Denegada.')],
    '909': [_('Operación Denegada. Error de sistema.'),_('Operación Denegada. Problemas de comunicación. Intente más tarde.')],
    '910': [_('Operación Denegada. Error de sistema.'),_('Operación Denegada.')],
    '912': [_('Operación Denegada. Entidad emisora no disponible.'),_('Operación Denegada. Entidad emisora de la tarjeta no disponible.')],
    '913': [_('Operación Denegada. Transmisión duplicada.'),_('Operación Denegada.')],
    '916': [_('Operación Denegada. Contactar con entidad emisora.'),_('Operación Denegada.')],
    '928': [_('Operación Denegada. Contactar con entidad emisora.'),_('Operación Denegada.')],
    '940': [_('Operación Denegada. Transacción anulada previamente.'),_('Operación Denegada.')],
    '941': [_('Operación Denegada. Transacción ya anulada previamente.'),_('Operación Denegada.')],
    '942': [_('Operación Denegada.'),_('Operación Denegada.')],
    '943': [_('Operación Denegada. Datos originales distintos.'),_('Operación Denegada.')],
    '945': [_('Operación Denegada. Referencia repetida.'),_('Operación Denegada.')],
    '946': [_('Operación Denegada. Operación de anulación en proceso.'),_('Operación Denegada. Operación de anulación en proceso.')],
    '947': [_('Operación Denegada. Comunicación duplicada.'),_('Operación Denegada. Problemas de comunicación. Intente más tarde.')],
    '948': [_('Operación Denegada. Contactar con entidad emisora.'),_('Operación Denegada.')],
    '949': [_('Operación Denegada. Contactar con entidad emisora.'),_('Operación Denegada.')],
    '965': [_('Operación Denegada. Contactar con entidad emisora.'),_('Operación Denegada.')],
}
