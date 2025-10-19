# -*- coding: utf-8 -*-
# Copyright (c) 2019-2022 Juan Gabriel Fernandez More (kiyoshi.gf@gmail.com)
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

from odoo import api, fields, tools, models, _
import time
#from base64 import encodestring
import base64
from odoo.exceptions import UserError
import re
from io import StringIO, BytesIO
from importlib import reload
import sys
try:
	import qrcode
	qr_mod = True
except:
	qr_mod = False

def encodestring(datos):
	respuesta = datos
	if sys.version_info >= (3, 9):
		respuesta = base64.encode(datos)
	else:
		respuesta = base64.encodestring(datos)

	return respuesta



class Picking(models.Model):
	_inherit = "stock.picking"

	almacen_origen = fields.Many2one('stock.warehouse', 'Almacén Origen', compute="_compute_almacen", store=True)
	almacen_destino = fields.Many2one('stock.warehouse', 'Almacén Destino', compute="_compute_almacen", store=True)

	##########################################################
	pe_unit_quantity = fields.Integer("Cantidad Bultos", copy=False)
	##########################################################

	@api.depends('location_id', 'location_dest_id')
	def _compute_almacen(self):
		for reg in self:
			almacen_origen = False
			almacen_destino = False
			if reg.location_id:
				almacen_origen = self.env['stock.warehouse'].search([('lot_stock_id', '=', reg.location_id.id)], limit=1)

			if reg.location_dest_id:
				almacen_destino = self.env['stock.warehouse'].search([('lot_stock_id', '=', reg.location_dest_id.id)], limit=1)

			reg.almacen_origen = almacen_origen.id if almacen_origen else False
			reg.almacen_destino = almacen_destino.id if almacen_destino else False



	def get_street(self, partner):
		self.ensure_one()
		address = ''
		if partner.street:
			address = "%s" % (partner.street)
		if partner.street2:
			address += ", %s" % (partner.street2)
		reload(sys)
		html_text = str(tools.plaintext2html(address, container_tag=True))
		data = html_text.split('p>')
		if data:
			return data[1][:-2]
		return False


	def get_address_details(self, partner):
		self.ensure_one()
		address = ''
		if partner.l10n_pe_district:
			address = "%s" % (partner.l10n_pe_district.name)
		if partner.city:
			address += ", %s" % (partner.city)
		if partner.state_id.name:
			address += ", %s" % (partner.state_id.name)
		if partner.zip:
			address += "( %s)" % (partner.zip)
		if partner.country_id.name:
			address += ", %s" % (partner.country_id.name)
		reload(sys)
		html_text = str(tools.plaintext2html(address, container_tag=True))
		data = html_text.split('p>')
		if data:
			return data[1][:-2]
		return False