# -*- coding: utf-8 -*-

from odoo import models, fields, api

class product_product_inherit(models.Model):
    _inherit = 'product.product'

    excise_register_id = fields.Many2one('excise.register', string="Excise Register")

class product_template_inherit(models.Model):
    _inherit = 'product.template'

    alcohol_volume = fields.Integer("Alcohol Vol. (%)")
    gn_code = fields.Char("GN Code")
    excise_product_code = fields.Selection(selection='_available_excise_product_codes', string="Product code")
    excise_price = fields.Monetary(string='Excise price', store=True, readonly=True, compute='_calculate_price_taxes')
    eco_tax = fields.Monetary(string='Eco tax', store=True, readonly=True, compute='_calculate_price_taxes')
    cost_price_excise_excl = fields.Monetary(string='Cost price (excise tax excl.)', store=True, readonly=True, compute='_calculate_price_taxes')

    def _available_excise_product_codes(self):
        return [
            ("S200", "Sterke dranken"),
            ("W200", "Stille wijnen"),
            ("W300", "Schuimwijnen"),
        ]

    @api.depends('alcohol_volume','volume','excise_product_code','standard_price')
    def _calculate_price_taxes(self):
        for product in self:
            product.excise_price = product.alcohol_volume * 0.001 #TODO
            product.eco_tax = product.alcohol_volume * 0.002 #TODO

            total_excise_eco_tax = product.excise_price + product.eco_tax

            product.cost_price_excise_excl = product.standard_price - total_excise_eco_tax if product.standard_price > total_excise_eco_tax else 0






