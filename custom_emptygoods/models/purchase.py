# -*- coding: utf-8 -*-

from odoo import models, fields, api

class purchase_order_inherit(models.Model):
    _inherit = 'purchase.order'

    def _amount_all(self):
        res = super(purchase_order_inherit, self)._amount_all()

        self._reset_emptygoods_orderlines()
        self._create_or_update_emptygoods_orderlines()

        self._remove_unused_emptygoods_orderlines()

    def _reset_emptygoods_orderlines(self):
        empty_goods_order_line = self.order_line.filtered(lambda x: x.product_id.product_tmpl_id.emptygoods and x.product_qty >= 0)
        for line in empty_goods_order_line:
            line.product_qty = 0

    def _create_or_update_emptygoods_orderlines(self):
        for line in self.order_line:
            if line.product_id:
                if line.product_id.emptygoods_product_id:
                    empty_goods_product_product = line.product_id.emptygoods_product_id.product_variant_ids[0]
                    empty_goods_order_line = self.order_line.filtered(lambda x: x.product_id == empty_goods_product_product and x.product_qty >= 0)

                    # Create
                    if not empty_goods_order_line:
                        if line.product_qty > 0:
                            values = {
                                'order_id': self.id,
                                'product_qty': line.product_qty,
                                'product_uom': empty_goods_product_product.uom_id.id,
                                'product_id': empty_goods_product_product.id,
                                'name': line.product_id.emptygoods_product_id.name,
                                'price_unit': line.product_id.emptygoods_product_id.list_price,
                                'taxes_id': [(6, 0, line.product_id.emptygoods_product_id.taxes_id.ids)]
                            }
                            self.env['purchase.order.line'].create(values)
                    # Edit
                    else:
                        empty_goods_order_line.product_qty += line.product_qty

    def _remove_unused_emptygoods_orderlines(self):
        unused_empty_goods_order_line = self.order_line.filtered(lambda x: x.product_id.product_tmpl_id.emptygoods and x.product_qty == 0)
        for line in unused_empty_goods_order_line:
            line.unlink()