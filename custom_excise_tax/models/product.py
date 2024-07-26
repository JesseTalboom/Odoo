# -*- coding: utf-8 -*-

from odoo import models, fields, api

class product_template_inherit(models.Model):
    _inherit = 'product.template'

    alcohol_volume = fields.Float("Alcohol Vol. (%)")
    degrees_plato = fields.Float("Degrees Plato (°P)")
    alcohol_100_volume = fields.Float(compute='_calculate_alcohol_100_volume', string="Alcohol Vol. (real)", readonly=True)
    # gn_code = fields.Selection(selection='_available_gn_codes', string="GN Code")
    gn_code = fields.Char(compute='_calculate_gn_code', string="GN Code", readonly=True)
    box_33 = fields.Selection(selection='_available_box_33_codes', string="Box 33")
    excise_tax = fields.Float(string='Excise Price (€/HL)', digits=(12, 4), store=True, readonly=True, compute='_calculate_taxes')
    special_excise_tax = fields.Float(string='Special Excise Price (€/HL)', digits=(12, 4), store=True, readonly=True, compute='_calculate_taxes')
    packaging_tax = fields.Float(string='Packaging Tax (€/HL)', digits=(12, 4), store=True, readonly=True, compute='_calculate_taxes')
    cost_price_excise_taxes_excl = fields.Monetary(string='Cost price (excise taxes excl.)')

    def _calculate_alcohol_100_volume(self):
        for product in self:
            product.alcohol_100_volume = product.volume * (product.alcohol_volume / 100)

    def _available_gn_codes(self):
        return [
            ("2203", "Beer in reusable/disposable packaging"),
            ("2206", "Beer in disposable packaging - small independent brewery - not exceeding 200000 hl"),
            ("2204 21", "Still wines in disposable packaging"),
            ("2204 10", "Sparkling wines in disposable packaging"),
            ("2204", "Intermediate products (still) in disposable packaging"),
            ("2208", "Spirits, liqueurs and other drinks containing distilled alcohol"),
        ]

    def _calculate_gn_code(self):
        for product in self:
            if product.box_33 == "S001":
                product.gn_code = "2203"
            elif product.box_33 == "S002":
                product.gn_code = "2203"
            elif product.box_33 == "S024":
                product.gn_code = "2206"
            elif product.box_33 == "S101":
                product.gn_code = "2204 21"
            elif product.box_33 == "S109":
                product.gn_code = "2204 10"
            elif product.box_33 == "S125":
                product.gn_code = "2204 10"
            elif product.box_33 == "S301":
                product.gn_code = "2204"
            elif product.box_33 == "S411":
                product.gn_code = "2208"
            else:
                product.gn_code = ""

    def _is_ethylalcohol(self):
        return self.gn_code == '2208'

    def _is_sparkling_wine(self):
        return self.gn_code == '2204 10'

    def _is_still_wine(self):
        return self.gn_code == '2204 21'

    def _is_intermediate(self):
        return self.gn_code == '2204'

    def _is_beer(self):
        return self.gn_code == '2203' or self.gn_code == '2206'

    def _available_box_33_codes(self):
        default = [
            ("S001", "Beer in reusable/disposable packaging"),
            ("S002", "Beer in disposable packaging"),
            ("S024", "Beer in disposable packaging - small independent brewery - not exceeding 200000 hl"),
            ("S101", "Still wines in disposable packaging"),
            ("S109", "Sparkling wines in disposable packaging"),
            ("S125", "Sparkling wines =< 8.5% in disposable packaging"),
            ("S301", "Intermediate products (still) in disposable packaging"),
            ("S411", "Spirits, liqueurs and other drinks containing distilled alcohol"),
        ]

        return default

    @api.depends('alcohol_volume', 'volume', 'degrees_plato', 'box_33', 'standard_price')
    def _calculate_taxes(self):
        for product in self:

            # Beer
            if product.box_33 == 'S001' or product.box_33 == 'S002' or product.box_33 == 'S024':
                product.excise_tax = product.degrees_plato_volume_in_hectoliter() * product._get_excise_tax()
                product.special_excise_tax = product.degrees_plato_volume_in_hectoliter() * product._get_special_excise_tax()
                product.packaging_tax = product.degrees_plato_volume_in_hectoliter() * product._get_packaging_tax()

            # Wine (use Volume)
            if product.box_33 == 'S101' or product.box_33 == 'S109' or product.box_33 == 'S125':
                product.excise_tax = product.volume_in_hectoliter() * product._get_excise_tax()
                product.special_excise_tax = product.volume_in_hectoliter() * product._get_special_excise_tax()
                product.packaging_tax = product.volume_in_hectoliter() * product._get_packaging_tax()

            # Liquer and others (use Alcohol Volume)
            if product.box_33 == 'S301' or product.box_33 == 'S411':
                product.excise_tax = product.alcohol_100_volume_in_hectoliter() * product._get_excise_tax()
                product.special_excise_tax = product.alcohol_100_volume_in_hectoliter() * product._get_special_excise_tax()
                product.packaging_tax = product.alcohol_100_volume_in_hectoliter() * product._get_packaging_tax()

            total_taxes = product.excise_tax + product.special_excise_tax + product.packaging_tax

            product.cost_price_excise_taxes_excl = product.standard_price - total_taxes if product.standard_price > total_taxes else 0

    def update_standard_price(self):
        for product in self:
            total_taxes = product.excise_tax + product.special_excise_tax + product.packaging_tax

            product.standard_price = product.cost_price_excise_taxes_excl + total_taxes

    def volume_in_hectoliter(self):
        return self.volume / 100

    def alcohol_100_volume_in_hectoliter(self):
        return self.alcohol_100_volume / 100

    def degrees_plato_volume_in_hectoliter(self):
        return self.volume_in_hectoliter() * self.degrees_plato

    # price per HL
    def _get_excise_tax(self):
        if self.box_33 == "S001":
            return 0.7933
        if self.box_33 == "S002":
            return 0.7933
        if self.box_33 == "S024":
            return 0.4462
        if self.box_33 == "S101":
            return 0
        if self.box_33 == "S109":
            return 0
        if self.box_33 == "S125":
            return 0
        if self.box_33 == "S301":
            return 66.9313
        if self.box_33 == "S411":
            return 223.1042

    # price per HL
    def _get_special_excise_tax(self):
        if self.box_33 == "S001":
            return 1.2110
        if self.box_33 == "S002":
            return 1.2110
        if self.box_33 == "S024":
            return 1.5292
        if self.box_33 == "S101":
            return 74.9086
        if self.box_33 == "S109":
            return 256.3223
        if self.box_33 == "S125":
            return 23.9119
        if self.box_33 == "S301":
            return 90.8479
        if self.box_33 == "S411":
            return 2769.6886

    # price per HL
    def _get_packaging_tax(self):
        if self.box_33 == "S001":
            return 1.4100
        if self.box_33 == "S002":
            return 9.8600
        if self.box_33 == "S024":
            return 9.8600
        if self.box_33 == "S101":
            return 9.8600
        if self.box_33 == "S109":
            return 9.8600
        if self.box_33 == "S125":
            return 9.8600
        if self.box_33 == "S301":
            return 9.8600
        if self.box_33 == "S411":
            return 9.8600
