# -*- coding: utf-8 -*-
# from odoo import http


# class SaleReportImports(http.Controller):
#     @http.route('/sale_report_imports/sale_report_imports', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sale_report_imports/sale_report_imports/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('sale_report_imports.listing', {
#             'root': '/sale_report_imports/sale_report_imports',
#             'objects': http.request.env['sale_report_imports.sale_report_imports'].search([]),
#         })

#     @http.route('/sale_report_imports/sale_report_imports/objects/<model("sale_report_imports.sale_report_imports"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sale_report_imports.object', {
#             'object': obj
#         })

