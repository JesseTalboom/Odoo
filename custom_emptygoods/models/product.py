# -*- coding: utf-8 -*-

from odoo import models, fields, api


class product_template_inherit(models.Model):
    _inherit = 'product.template'

    # usage ex. (detailed_type == 'emptygoods')
    # detailed_type = fields.Selection(selection_add=[
    #     ('emptygoods', 'Empty goods'),
    # ], ondelete={'emptygoods': 'set service'})

    emptygoods = fields.Boolean("Is empty goods")

    emptygoods_product_id = fields.Many2one(
        'product.product', 'Empty goods', check_company=True,
        index=True, ondelete='set null',
        domain=[('product_tmpl_id.emptygoods', '=', 'True')])

    # def _detailed_type_mapping(self):
    #     type_mapping = super()._detailed_type_mapping()
    #     type_mapping['emptygoods'] = 'service'
    #     return type_mapping


