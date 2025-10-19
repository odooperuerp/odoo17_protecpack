# -*- coding: utf-8 -*-
from odoo import http

# class PoModelModule(http.Controller):
#     @http.route('/po_model_module/po_model_module/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/po_model_module/po_model_module/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('po_model_module.listing', {
#             'root': '/po_model_module/po_model_module',
#             'objects': http.request.env['po_model_module.po_model_module'].search([]),
#         })

#     @http.route('/po_model_module/po_model_module/objects/<model("po_model_module.po_model_module"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('po_model_module.object', {
#             'object': obj
#         })