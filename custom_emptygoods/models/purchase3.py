# -*- coding: utf-8 -*-

from odoo import models, fields, api

class purchase_order_line_inherit(models.Model):
    _inherit = 'purchase.order.line'

    emptygoods_order_line_id = fields.Many2one('purchase.order.line', 'Empty goods', ondelete='set null')

    # @api.onchange('product_id', 'product_qty')
    # def _compute_emptygoods(self):
    #     for line in self:
    #         if line.emptygoods_order_line_id:
    #             if line.product_id:
    #                 if line.product_id.emptygoods_product_id:
    #                     print("IF")
    #                     line.emptygoods_order_line_id.product_id = line.product_id.id
    #                     line.emptygoods_order_line_id.name = line.product_id.name
    #                     line.emptygoods_order_line_id.price_unit = line.product_id.list_price
    #                     line.emptygoods_order_line_id.product_qty = line.product_qty
    #                 else:
    #                     #TODO unlink
    #                     print("UNLINK")
    #                     line.emptygoods_order_line_id.unlink()

    @api.model
    def write(self, vals):
        print("write")
        result = super(purchase_order_line_inherit, self).write(vals)

        if 'product_id' in vals or 'product_qty' in vals:
            for line in self:
                if line.emptygoods_order_line_id:
                    if line.product_id:
                        if line.product_id.emptygoods_product_id:
                            line.emptygoods_order_line_id.product_id = line.product_id.id
                            line.emptygoods_order_line_id.name = line.product_id.name
                            line.emptygoods_order_line_id.price_unit = line.product_id.list_price
                            line.emptygoods_order_line_id.product_qty = line.product_qty
                        else:
                            # TODO unlink
                            print("UNLINK ME")
                            #line.emptygoods_order_line_id.unlink()
            return result

    @api.model
    def create(self, values):
        original_line = super(purchase_order_line_inherit, self).create(values)

        product_id = values.get('product_id', False)
        product_tmpl_id = self.env['product.product'].sudo().search([('id', '=', product_id)]).product_tmpl_id

        if product_tmpl_id.emptygoods_product_id:
            emptygoods_product_id = product_tmpl_id.emptygoods_product_id

            duplicate_values = {
                'order_id': values.get('order_id', False),
                'product_qty': values.get('product_qty', False),
                'product_uom': values.get('product_uom', False),
                'product_id': emptygoods_product_id.product_variant_ids[0].id,
                'name': emptygoods_product_id.name,
                'price_unit': emptygoods_product_id.list_price,
                'taxes_id': []
            }

            duplicate_line = super(purchase_order_line_inherit, self).create(duplicate_values)

            original_line.emptygoods_order_line_id = duplicate_line.id
            print(original_line.emptygoods_order_line_id)

        return original_line

    @api.model
    def unlink(self):
        if self.emptygoods_order_line_id:
            self.emptygoods_order_line_id.unlink()
        return super(purchase_order_line_inherit, self).unlink()

