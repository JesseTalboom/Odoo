# -*- coding: utf-8 -*-

from odoo import models, fields, api


class product_template_inherit(models.Model):
    _inherit = 'product.template'

    detailed_type = fields.Selection(selection_add=[
        ('emptygoods', 'Empty goods'),
    ], ondelete={'emptygoods': 'set service'})

    fullgood_product_id = fields.Many2one(
        'product.template', 'Full good', check_company=True,
        index=True, ondelete='set null',
        domain=[('detailed_type', '=', 'product')])

    def _detailed_type_mapping(self):
        type_mapping = super()._detailed_type_mapping()
        type_mapping['emptygoods'] = 'service'
        return type_mapping
