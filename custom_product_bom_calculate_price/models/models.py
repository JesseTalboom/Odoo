# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api

_logger = logging.getLogger(__name__)

class product_product_inherit(models.Model):
    _inherit = 'product.product'

    @api.onchange('standard_price')
    def calculate_bom_item_price(self):
        print('OLEEEEEEEEEE 2')
        print(self._origin.id)
        bom_line = self.env['mrp.bom.line'].search([('product_id', '=', self._origin.id)])
        print(len(bom_line))
        bom = bom_line.bom_id
        print(bom)
        parent_product_tmpl = bom.product_tmpl_id
        print(parent_product_tmpl)
        parent_product_tmpl.button_bom_cost()
        print('called method')