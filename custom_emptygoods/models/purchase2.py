# -*- coding: utf-8 -*-

from odoo import models, fields, api

class purchase_order_line_inherit(models.Model):
    _inherit = 'purchase.order.line'

    emptygoods_total = fields.Float(
        string="Empty goods",
        compute='_compute_emptygoods',
        digits='Product Price',
        store=True, readonly=False, required=True, precompute=True)

    # Calculate emptygoods_total
    @api.depends('product_id', 'product_uom', 'product_uom_qty')
    def _compute_emptygoods(self):
        for line in self:
            # check if there is already invoiced amount. if so, the price shouldn't change as it might have been
            # manually edited
            if line.qty_invoiced > 0:
                continue
            if not line.product_id:
                line.emptygoods_total = 0.0
            else:
                line.emptygoods_total = line.product_id.emptygoods_product_id.list_price * line.product_uom_qty

    # Re-calculate price_subtotal (trial and error since it happened that saving te form reset value to orignal calculation)
    @api.depends('product_qty', 'price_unit', 'taxes_id', 'emptygoods_total')
    def _compute_amount(self):
        res = super(purchase_order_line_inherit, self)._compute_amount()
        for line in self:
            price_subtotal = (line.product_qty * line.price_unit) + line.emptygoods_total
            line.update({
                'price_subtotal': price_subtotal,
                'price_total': price_subtotal + line.price_tax,
            })

        return res

    def _convert_to_tax_base_line_dict(self):
        self.ensure_one()
        vals = super(purchase_order_line_inherit, self)._convert_to_tax_base_line_dict()
        vals.update({"emptygoods": self.emptygoods_total})
        return vals

class purchase_order_inherit(models.Model):
    _inherit = 'purchase.order'

    def _compute_tax_totals(self):
        res = super(purchase_order_inherit, self)._compute_tax_totals()

class account_tax_inherit(models.Model):
    _inherit = 'account.tax'

    def _prepare_tax_totals(self, base_lines, currency, tax_lines=None):
        print("TAXXX")
        print(base_lines)
        res = super(account_tax_inherit, self)._prepare_tax_totals(base_lines, currency, tax_lines)
        print(res)
        return res
