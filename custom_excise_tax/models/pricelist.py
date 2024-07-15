# -*- coding: utf-8 -*-

from odoo import models, fields, api

class product_pricelist_item_inherit(models.Model):
    _inherit = 'product.pricelist.item'

    base = fields.Selection(
        selection=[
            ('list_price', 'Sales Price'),
            ('standard_price', 'Cost'),
            ('cost_price_excise_taxes_excl', 'Cost (excise taxes excl.)'),
            ('pricelist', 'Other Pricelist'),
        ],
        string="Based on",
        default='list_price',
        required=True,
        help="Base price for computation.\n"
             "Sales Price: The base price will be the Sales Price.\n"
             "Cost Price : The base price will be the cost price.\n"
             "Other Pricelist : Computation of the base price based on another Pricelist.")

    def _compute_base_price(self, product, quantity, uom, date, target_currency):

        if self.base == 'cost_price_excise_taxes_excl':
            src_currency = product.currency_id
            price = product.product_tmpl_id.cost_price_excise_taxes_excl

            if src_currency != target_currency:
                price = src_currency._convert(price, target_currency, self.env.company, date, round=False)

        else:
            price = super(product_pricelist_item_inherit, self)._compute_base_price(product, quantity, uom, date,target_currency)

        return price