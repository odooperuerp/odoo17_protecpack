
from unittest.mock import patch

from werkzeug.exceptions import Forbidden

from odoo.exceptions import UserError
from odoo.tests import tagged
from odoo.tools import mute_logger

from odoo.addons.payment import utils as payment_utils
from odoo.addons.payment.tests.http_common import PaymentHttpCommon
from odoo.addons.payment_niubiz.models.payment_provider import PaymentProvider
from odoo.addons.payment_niubiz.tests.common import NiubizCommon


@tagged('post_install', '-at_install')
class NiubizTest(NiubizCommon, PaymentHttpCommon):

    @mute_logger('odoo.addons.payment_niubiz.models.payment_provider')
    def test_apis(self):
        token = self.provider._niubiz_generate_token()
        self.assertEqual(token, 'token')