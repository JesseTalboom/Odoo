# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
import re

class product_template_inherit(models.Model):
    _inherit = 'product.template'

    alcohol_volume = fields.Float("Alcohol Vol. (%)")
    degrees_plato = fields.Float("Degrees Plato (°P)")
    alcohol_100_volume = fields.Float(compute='_calculate_alcohol_100_volume', string="Alcohol Vol. (real)", readonly=True)

    gn_code = fields.Char(string="GN Code")
    excise_category = fields.Char(string="Excise category", compute='_calculate_excise_category', readonly=True, store=True)
    box_33 = fields.Many2one('excise.tax', string="Box 33")

    excise_tax = fields.Float(string='Excise Price (€/HL)', digits=(12, 4), store=True, readonly=True, compute='_calculate_taxes')
    special_excise_tax = fields.Float(string='Special Excise Price (€/HL)', digits=(12, 4), store=True, readonly=True, compute='_calculate_taxes')
    packaging_tax = fields.Float(string='Packaging Tax (€/HL)', digits=(12, 4), store=True, readonly=True, compute='_calculate_taxes')
    total_excise_taxes = fields.Float(string='Total Excise Price (€/HL)', digits=(12, 4), store=True, readonly=True, compute='_calculate_taxes')

    cost_price_excise_taxes_excl = fields.Monetary(string='Cost price (excise taxes excl.)')

    @api.constrains('gn_code')
    def _check_gn_code(self):
        for record in self:
            if record.gn_code and not re.match(r'^\d+$', record.gn_code):
                raise ValidationError('GN Code must contain only digits.')

    def _clean_gn_code(self):
        return re.sub(r'\s+', '', self.gn_code)  # Remove all white spaces

    @api.onchange("gn_code")
    def _onchange_gn_code(self):
        for product in self:
            product.gn_code = product._clean_gn_code()

    def _calculate_alcohol_100_volume(self):
        for product in self:
            product.alcohol_100_volume = product.volume * (product.alcohol_volume / 100)

    @api.depends('gn_code')
    def _calculate_excise_category(self):
        for product in self:
            if isinstance(product.gn_code, str):
                if product.gn_code.startswith("2203"):
                    product.excise_category = "Beer"
                elif product.gn_code.startswith("22042"):
                    product.excise_category = "Still wine (W200)"
                elif product.gn_code.startswith("22041"):
                    product.excise_category = "Sparkling wine (W300)"
                elif product.gn_code.startswith("2208"):
                    product.excise_category = "Spirits (S200)"
                #TODO
                elif product.gn_code.startswith("TODO"):
                    product.excise_category = "Intermediates"
                else:
                    product.excise_category = ""
            else:
                product.excise_category = ""

    def _is_beer(self):
        return self.excise_category == 'Beer'

    def _is_still_wine(self):
        return self.excise_category == 'Still wine (W200)'

    def _is_sparkling_wine(self):
        return self.excise_category == 'Sparkling wine (W300)'

    def _is_ethylalcohol(self):
        return self.excise_category == 'Spirits (S200)'

    def _is_intermediate(self):
        return self.excise_category == 'Intermediates'

    @api.depends('alcohol_volume', 'volume', 'degrees_plato', 'box_33', 'standard_price')
    def _calculate_taxes(self):
        for product in self:
            # Beer
            if product._is_beer():
                product.excise_tax = product.degrees_plato_volume_in_hectoliter() * product._get_excise_tax()
                product.special_excise_tax = product.degrees_plato_volume_in_hectoliter() * product._get_special_excise_tax()
                product.packaging_tax = product.degrees_plato_volume_in_hectoliter() * product._get_packaging_tax()

            # Wine (use Volume)
            elif product._is_still_wine() or product._is_sparkling_wine():
                product.excise_tax = product.volume_in_hectoliter() * product._get_excise_tax()
                product.special_excise_tax = product.volume_in_hectoliter() * product._get_special_excise_tax()
                product.packaging_tax = product.volume_in_hectoliter() * product._get_packaging_tax()

            # Liquer and others (use Alcohol Volume)
            elif product._is_ethylalcohol():
                product.excise_tax = product.alcohol_100_volume_in_hectoliter() * product._get_excise_tax()
                product.special_excise_tax = product.alcohol_100_volume_in_hectoliter() * product._get_special_excise_tax()
                product.packaging_tax = product.alcohol_100_volume_in_hectoliter() * product._get_packaging_tax()

            else:
                product.excise_tax = 0
                product.special_excise_tax = 0
                product.packaging_tax = 0

            product.total_excise_taxes = product.excise_tax + product.special_excise_tax + product.packaging_tax

            product.cost_price_excise_taxes_excl = product.standard_price - product.total_excise_taxes if product.standard_price > product.total_excise_taxes else 0

    def update_standard_price(self):
        for product in self:
            product.standard_price = product.cost_price_excise_taxes_excl + product.total_excise_taxes

    def volume_in_hectoliter(self):
        return self.volume / 100

    def alcohol_100_volume_in_hectoliter(self):
        return self.alcohol_100_volume / 100

    def degrees_plato_volume_in_hectoliter(self):
        return self.volume_in_hectoliter() * self.degrees_plato

    def _get_excise_tax(self):
        return self.box_33.excise_tax if self.box_33 else 0

    def _get_special_excise_tax(self):
        return self.box_33.special_excise_tax if self.box_33 else 0

    def _get_packaging_tax(self):
        return self.box_33.packaging_tax if self.box_33 else 0

class product_product_inherit(models.Model):
    _inherit = 'product.product'

    # Temp set standard_price to cost_price_excise_taxes_excl. After super method is called reset the value back to default
    def _prepare_out_svl_vals(self, quantity, company):
        old_standard_price = self.standard_price

        # Is excise product
        if self.cost_price_excise_taxes_excl > 0 and self.cost_price_excise_taxes_excl != self.standard_price:
            self.standard_price = self.cost_price_excise_taxes_excl

        res = super(product_product_inherit, self)._prepare_out_svl_vals(quantity, company)

        # Reset standard price
        if self.standard_price != old_standard_price:
            self.standard_price = old_standard_price

        return res
