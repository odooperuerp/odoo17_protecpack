# -*- coding: utf-8 -*-

from odoo import models, fields, api

class product(models.Model):
	_inherit = 'product.template'
	n_porc_utilidad = fields.Float(string="Porc.utilidad")
	marca = fields.Char(string="Marca")
	descripcion = fields.Text(string="")
	cod_interno = fields.Text(string="Código interno")
	modelo = fields.Char(string="Modelo")
	#description_sale = fields.Html(string="Sales Description")
    
	#mz = fields.Char(string="Manzana")
	#lte = fields.Integer(string="Lote")
	#area = fields.Float(string="Area")
	#estado = fields.Selection([('Disponible','DISPONIBLE'),('Vendido','VENDIDO')],string="Estado")


	@api.onchange('n_porc_utilidad')
	def _n_porc_utilidad(self):
			self.list_price = self.standard_price*(1+self.n_porc_utilidad/100)

class partner(models.Model):
	_inherit = 'res.partner'
	#abc = fields.Selection([('a','A'),('b','B'),('c','C')],string="Clasificación ABC")
	#type_legal = fields.Selection([('Natural','Natural'),('Jurídica','Jurídica')],string="Estado legal")
	#conyugue = fields.Many2one('res.partner', string='Conyugue') 
   
   
class SaleOrder(models.Model):

	_inherit = 'sale.order'
#	id_partner_id = fields.Integer(related='partner_id.id', string='Atencion contact')
#	contact_parent_name = fields.Many2one('res.partner', string='Seleccionar contacto')
#	atencion = fields.Char(string="Atencion") 

	#@api.onchange('contact_parent_name')
	#def atencion_(self):
	#	self.atencion = self.contact_parent_name.name

class company(models.Model):
	_inherit = 'res.company'
#	logo2 = fields.Binary(string="Logo alternativo")
#	tradename = fields.Char(string="Nombre Comercial") 
 
#class AccountMove2(models.Model):
#	_inherit = "account.move"
#   is_retention=fields.Boolean(string="Documento sujeto a Retención",compute="_compute_retention",default=False)
#	money_ = fields.Char(related='currency_id.name', string='Moneda')
#	nro_guia_remision = fields.Char(related ='guia_remision_ids.numero', string="numero guía")
 

#class SaleOrderLine(models.Model):
#	_inherit = 'sale.order.line'
#	marca = fields.Char(related='product_id.marca', readonly=True)
#	product_image = fields.Binary(related='product_id.image_1920', string="Product Image")
    

#class Crmlead(models.Model):

 #   _inherit = 'crm.lead'
  #  begin_date = fields.Date(string="Fecha de inicio:")
   # finish_date = fields.Date(string="Fecha de finalización:")

#class Proyecttask(models.Model):
#	_inherit = "project.task"
#	buy_id = fields.Many2one("purchase.order", string="Pedido de compra")
#	begin_date = fields.Date(string="Fecha de inicio:")
#	finish_date = fields.Date(string="Fecha de finalización:")

#class product_uom(models.Model):
#	_inherit = 'product.uom'
#	code2 = fields.Char(string="Nombre corto reportes:")

#class mrp_production(models.Model):
#	_inherit = 'mrp.production'
#	_sale_order_id = fields.Many2one("sale.order")
	