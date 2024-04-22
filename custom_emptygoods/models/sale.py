# -*- coding: utf-8 -*-
from odoo import models, fields, api

LOCKED_FIELD_STATES = {
    state: [('readonly', True)]
    for state in {'done', 'cancel'}
}

class sale_order_line_inherit(models.Model):
    _inherit = 'sale.order.line'

    emptygoods_line_id = fields.Many2one(
        'sale.order.line', 'Empty goods line', check_company=True,
        index=True, ondelete='cascade')

    fullgoods_line_id = fields.Many2one(
        'sale.order.line', 'Full goods line', check_company=True,
        index=True, ondelete='cascade')

    emptygoods_line_str = fields.Text('Empty goods line', compute='_compute_emptygoods_line')

    is_emptygoods_return = fields.Boolean('Empty goods return')

    def _compute_emptygoods_line(self):
        for line in self:
            res = ""
            if line.emptygoods_line_id:
                res = line.emptygoods_line_id.product_id.name

            elif line.fullgoods_line_id:
                res = line.fullgoods_line_id.product_id.name

            line.emptygoods_line_str = res

class sale_order_inherit(models.Model):
    _inherit = 'sale.order'

    amount_emptygoods_min = fields.Monetary(string='Empty goods (-)', store=True, readonly=True, compute='_amount_emptygoods')
    amount_emptygoods_plus = fields.Monetary(string='Empty goods (+)', store=True, readonly=True, compute='_amount_emptygoods')
    amount_emptygoods_total = fields.Monetary(string='Total empty goods', store=True, readonly=True, compute='_amount_emptygoods')
    amount_emptygoods_price_total = fields.Monetary(string='Total emptygoods excl.', store=True, readonly=True, compute='_amount_emptygoods')

    # order_line = fields.One2many(
    #     comodel_name='sale.order.line',
    #     inverse_name='order_id',
    #     string="Order Lines",
    #     states=LOCKED_FIELD_STATES,
    #     copy=True, auto_join=True,
    #     domain=[('fullgoods_line_id', '=', None)]
    # )

    order_line_without_emptygoods = fields.One2many(
        comodel_name='sale.order.line',
        inverse_name='order_id',
        string="Order Lines (without empty goods)",
        states=LOCKED_FIELD_STATES,
        copy=True, auto_join=True,
        domain=[('fullgoods_line_id', '=', None)]
    )

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

            order.amount_emptygoods_price_total = sum(order.order_line.mapped('price_subtotal')) - order.amount_emptygoods_total

    def _compute_amounts(self):
        res = super(sale_order_inherit, self)._compute_amounts()

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
                        if self.id:
                            empty_goods_product_template = line.product_id.emptygoods_product_id.product_tmpl_id
                            empty_goods_product_product = line.product_id.emptygoods_product_id

                            if line.product_uom_qty > 0:
                                values = {
                                        'order_id': self.id,
                                        'product_uom_qty': line.product_uom_qty,
                                        'product_uom': empty_goods_product_product.uom_id.id,
                                        'product_id': empty_goods_product_product.id,
                                        'name': empty_goods_product_template.name,
                                        'price_unit': empty_goods_product_template.list_price,
                                        'tax_id': [(6, 0, empty_goods_product_template.taxes_id.ids)],
                                        'fullgoods_line_id': line.id
                                }
                                so_emptygoods_line = self.env['sale.order.line'].create(values)

                                line.emptygoods_line_id = so_emptygoods_line.id

    def action_sort(self):
        seq_1 = 0
        seq_2 = 999
        seq_3 = 9999
        for line in self.order_line:
            if line.product_id and not line.product_id.emptygoods:
                line.sequence = seq_1
                seq_1 += 1
            else:
                if line.fullgoods_line_id:
                    line.sequence = seq_2
                    seq_2 += 1
                else:
                    line.sequence = seq_3
                    seq_2 += 3

    def create_emptygoods_return(self):
        if self.id:
            for line in self.order_line.filtered(lambda x: x.product_id.emptygoods and x.fullgoods_line_id):
                values = {
                    'order_id': self.id,
                    'product_uom_qty': -line.product_uom_qty,
                    'product_uom': line.product_uom.id,
                    'product_id': line.product_id.id,
                    'name': line.name,
                    'price_unit': line.price_unit,
                    'tax_id': [(6, 0, line.tax_id.ids)],
                    'is_emptygoods_return': True
                }

                emptygoods_return_line = self.env['sale.order.line'].create(values)

    def _get_order_lines_to_report(self):
        order_lines = super(sale_order_inherit, self)._get_order_lines_to_report()
       # return order_lines.filtered(lambda l: l.fullgoods_line_id is None)
        return self.order_line_without_emptygoods
