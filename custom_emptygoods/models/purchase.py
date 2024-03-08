# -*- coding: utf-8 -*-

from odoo import models, fields, api

class purchase_order_line_inherit(models.Model):
    _inherit = 'purchase.order.line'

    emptygoods_line_id = fields.Many2one(
        'purchase.order.line', 'Empty goods line', check_company=True,
        index=True, ondelete='cascade')

    fullgoods_line_id = fields.Many2one(
        'purchase.order.line', 'Full goods line', check_company=True,
        index=True, ondelete='cascade')

    emptygoods_line_str = fields.Text('Empty goods line', compute='_compute_emptygoods_line')

    def _compute_emptygoods_line(self):
        for line in self:
            res = ""
            if line.emptygoods_line_id:
                res = line.emptygoods_line_id.product_id.name

            line.emptygoods_line_str = res

class purchase_order_inherit(models.Model):
    _inherit = 'purchase.order'

    amount_emptygoods_min = fields.Monetary(string='Empty goods (-)', store=True, readonly=True,
                                            compute='_amount_emptygoods')
    amount_emptygoods_plus = fields.Monetary(string='Empty goods (+)', store=True, readonly=True,
                                             compute='_amount_emptygoods')
    amount_emptygoods_total = fields.Monetary(string='Total empty goods', store=True, readonly=True,
                                              compute='_amount_emptygoods')

    @api.depends('order_line.price_total')
    def _amount_emptygoods(self):
        for order in self:
            emptygoods_order_lines = order.order_line.filtered(lambda x: x.product_id.emptygoods)
            emptygoods_order_lines_min = emptygoods_order_lines.filtered(lambda x: x.price_subtotal < 0)
            emptygoods_order_lines_plus = emptygoods_order_lines.filtered(lambda x: x.price_subtotal > 0)

            amount_emptygoods_min = sum(emptygoods_order_lines_min.mapped('price_subtotal'))
            amount_emptygoods_plus = sum(emptygoods_order_lines_plus.mapped('price_subtotal'))

            order.amount_emptygoods_min = amount_emptygoods_min
            order.amount_emptygoods_plus = amount_emptygoods_plus
            order.amount_emptygoods_total = order.amount_emptygoods_min + order.amount_emptygoods_plus

    def _amount_all(self):
        res = super(purchase_order_inherit, self)._amount_all()

        self._create_or_update_emptygoods_orderlines()

    def _create_or_update_emptygoods_orderlines(self):
        for line in self.order_line:
            if line.product_id:
                # check if line is a fullgood line
                if line.product_id.emptygoods_product_id:
                    # if empty goods link exists, update
                    if line.emptygoods_line_id:
                        line.emptygoods_line_id.product_uom_qty = line.product_uom_qty

                    # if not, create
                    else:
                        empty_goods_product_template = line.product_id.emptygoods_product_id.product_tmpl_id
                        empty_goods_product_product = line.product_id.emptygoods_product_id

                        if line.product_uom_qty > 0:
                            values = {
                                'order_id': self.id,
                                'product_qty': line.product_qty,
                                'product_uom': empty_goods_product_product.uom_id.id,
                                'product_id': empty_goods_product_product.id,
                                'name': empty_goods_product_template.name,
                                'price_unit': empty_goods_product_template.list_price,
                                'taxes_id': [(6, 0, empty_goods_product_template.taxes_id.ids)],
                                'fullgoods_line_id': line.id
                            }
                            so_emptygoods_line = self.env['purchase.order.line'].create(values)

                            line.emptygoods_line_id = so_emptygoods_line.id

    def action_sort(self):
        seq = 0
        eg_seq = 999
        for line in self.order_line:
            if line.emptygoods_line_id:
                line.sequence = seq
                seq += 1
            else:
                line.sequence = eg_seq
                eg_seq += 1