# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import re
import base64
from lxml import etree
from num2words import num2words

from odoo import api, fields, models, tools, _
from odoo.tools.float_utils import float_repr, float_round
from odoo.exceptions import UserError

class ResCurrency(models.Model):
    _inherit = 'res.currency'

    currency_unit_label = fields.Char(translate=True)
    currency_subunit_label = fields.Char(translate=True)

    def amount_to_text(self, amount):
        #res = super(ResCurrency, self).amount_to_text(amount)
        #return res.upper()

        self.ensure_one()
        amount_i, amount_d = divmod(amount, 1)
        amount_d = int(round(amount_d * 100, 2))

        lang = tools.get_lang(self.env)

        words = num2words(amount_i, lang=lang.iso_code)

        result = _('%(words)s Y %(amount_d)02d/100 %(currency_name)s') % {
            'words': words,
            'amount_d': amount_d,
            'currency_name': self.currency_unit_label,
        }
        return result.upper()