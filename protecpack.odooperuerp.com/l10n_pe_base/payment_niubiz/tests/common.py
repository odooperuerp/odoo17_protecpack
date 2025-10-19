
from odoo.addons.payment.tests.common import PaymentCommon

class NiubizCommon(PaymentCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.niubiz = cls._prepare_provider('niubiz', update_values={
            'niubiz_user': 'integraciones@niubiz.com.pe',
            'niubiz_password': '_7z3@8fF',
            'niubiz_merchant_id_pen': '456879852',
            'niubiz_merchant_id_usd': '456879853',
            'niubiz_client_ip': '127.0.0.1',
        })

        # Override default values
        cls.provider = cls.niubiz
        

        # cls.psp_reference = '0123456789ABCDEF'
        # cls.original_reference = 'FEDCBA9876543210'