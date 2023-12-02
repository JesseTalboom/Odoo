# -*- coding: utf-8 -*-

from odoo import models, fields, api

class sale_order_inherit(models.Model):
    _inherit = 'sale.order'

    def _compute_amounts(self):
        res = super(sale_order_inherit, self)._compute_amounts()

        self._reset_emptygoods_orderlines()
        self._create_or_update_emptygoods_orderlines()

        self._remove_unused_emptygoods_orderlines()

    def _reset_emptygoods_orderlines(self):
        empty_goods_order_line = self.order_line.filtered(lambda x: x.product_id.product_tmpl_id.emptygoods and x.product_uom_qty >= 0)
        for line in empty_goods_order_line:
            line.product_uom_qty = 0

    def _create_or_update_emptygoods_orderlines(self):
        for line in self.order_line:
            if line.product_id:
                if line.product_id.emptygoods_product_id:
                    empty_goods_product_template = line.product_id.emptygoods_product_id.product_tmpl_id
                    empty_goods_product_product = line.product_id.emptygoods_product_id
                    empty_goods_order_line = self.order_line.filtered(lambda x: x.product_id == empty_goods_product_product and x.product_uom_qty >= 0)

                    # Create
                    if not empty_goods_order_line:
                        if line.product_uom_qty > 0:
                            values = {
                                'order_id': self.id,
                                'product_uom_qty': line.product_uom_qty,
                                'product_uom': empty_goods_product_product.uom_id.id,
                                'product_id': empty_goods_product_product.id,
                                'name': empty_goods_product_template.name,
                                'price_unit': empty_goods_product_template.list_price,
                                'tax_id': [(6, 0, empty_goods_product_template.taxes_id.ids)]
                            }
                            self.env['sale.order.line'].create(values)
                    # Edit
                    else:
                        empty_goods_order_line.product_uom_qty += line.product_uom_qty

    def _remove_unused_emptygoods_orderlines(self):
        unused_empty_goods_order_line = self.order_line.filtered(lambda x: x.product_id.product_tmpl_id.emptygoods and x.product_uom_qty == 0)
        for line in unused_empty_goods_order_line:
            line.unlink()