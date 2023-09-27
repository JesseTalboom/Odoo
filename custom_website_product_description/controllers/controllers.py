# -*- coding: utf-8 -*-
# from odoo import http


# class Jesse(http.Controller):
#     @http.route('/jesse/jesse', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/jesse/jesse/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('jesse.listing', {
#             'root': '/jesse/jesse',
#             'objects': http.request.env['jesse.jesse'].search([]),
#         })

#     @http.route('/jesse/jesse/objects/<model("jesse.jesse"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('jesse.object', {
#             'object': obj
#         })
