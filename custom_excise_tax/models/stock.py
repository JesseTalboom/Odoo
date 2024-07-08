# -*- coding: utf-8 -*-

from odoo import models, fields, api

class stock_move_inherit(models.Model):
    _inherit = 'stock.move'

    excise_register_id = fields.Many2one('excise.register', string="Excise Register")

    # Fields needed to show in Excise Register Form
    product_default_code = fields.Char(related='product_id.default_code', store=True, readonly=True, string="Product Code")
    product_name = fields.Char(related='product_id.name', store=True, readonly=True, string="Product Name")
    product_gn_code = fields.Char(related='product_id.product_tmpl_id.gn_code', store=True, readonly=True, string="GN Code")
    product_volume = fields.Float(related='product_id.product_tmpl_id.volume', store=True, readonly=True, string="Volume (L)")
    product_alcohol_volume = fields.Float(related='product_id.product_tmpl_id.alcohol_volume', store=True, readonly=True, string="Alcohol Vol. (%)")

class stock_location_inherit(models.Model):
    _inherit = 'stock.location'

    is_excise_depot = fields.Boolean("Is excise depot")
    bonded_warehouse_number = fields.Char("Bonded warehouse number")

class stock_picking_inherit(models.Model):
    _inherit = 'stock.picking'

    def _action_done(self):
        res = super(stock_picking_inherit, self)._action_done()

        for picking in self:
            if picking.state == 'done':
                moves_in = picking.move_ids.filtered(lambda m: m.product_id and m.product_id.gn_code and not m.location_id.is_excise_depot and m.location_dest_id.is_excise_depot)
                moves_out = picking.move_ids.filtered(lambda m: m.product_id and m.product_id.gn_code and m.location_id.is_excise_depot and not m.location_dest_id.is_excise_depot)
            
                if any(moves_in):
                    ethylalcohol_vol = {move.product_id.alcohol_volume for move in moves_in.filtered(lambda m: m.product_id.gn_code == '2208')}

                    self.env['excise.register'].create({
                        'type': 'in',
                        'stock_picking_id': picking.id,
                        'purchase_order_id': picking.purchase_id.id if picking.purchase_id else None,
                        'stock_move_ids': [(6, 0, [move.id for move in moves_in])],
                        'amount_ethylalcohol_vol': ethylalcohol_vol.pop() if len(ethylalcohol_vol) == 1 else "div.",
                        'amount_ethylalcohol_real': sum(move.product_id.volume * move.product_qty for move in moves_in.filtered(lambda m: m.product_id.gn_code == '2208')),
                        'amount_ethylalcohol_100vol': sum(move.product_id.volume * (move.product_id.alcohol_volume/100) * move.product_qty for move in moves_in.filtered(lambda m: m.product_id.gn_code == '2208')),
                        'amount_sparkling_wine': sum(move.product_id.volume * move.product_qty for move in moves_in.filtered(lambda m: m.product_id.gn_code == '2204 10')),
                        'amount_still_wine': sum(move.product_id.volume * move.product_qty for move in moves_in.filtered(lambda m: m.product_id.gn_code == '2204 21')),
                        'amount_intermediate_vol': sum(move.product_id.alcohol_volume * move.product_qty for move in moves_in.filtered(lambda m: m.product_id.gn_code == '2204')),
                        'amount_intermediate_real': sum(move.product_id.volume * move.product_qty for move in moves_in.filtered(lambda m: m.product_id.gn_code == '2204')),
                        'amount_intermediate_100vol': sum(move.product_id.volume * (move.product_id.alcohol_volume/100) * move.product_qty for move in moves_in.filtered(lambda m: m.product_id.gn_code == '2204')),
                    })

                elif any(moves_out):
                    ethylalcohol_vol = {move.product_id.alcohol_volume for move in moves_out.filtered(lambda m: m.product_id.gn_code == '2208')}
                    self.env['excise.register'].create({
                        'type': 'out',
                        'stock_picking_id': picking.id,
                        'sale_order_id': picking.sale_id.id if picking.sale_id else None,
                        'stock_move_ids': [(6, 0, [move.id for move in moves_out])],
                        'amount_ethylalcohol_vol': ethylalcohol_vol.pop() if len(ethylalcohol_vol) == 1 else "div.",
                        'amount_ethylalcohol_real': sum(move.product_id.volume * move.product_qty for move in moves_out.filtered(lambda m: m.product_id.gn_code == '2208')),
                        'amount_ethylalcohol_100vol': sum(move.product_id.volume * (move.product_id.alcohol_volume/100) * move.product_qty for move in moves_out.filtered(lambda m: m.product_id.gn_code == '2208')),
                        'amount_sparkling_wine': sum(move.product_id.volume * move.product_qty for move in moves_out.filtered(lambda m: m.product_id.gn_code == '2204 10')),
                        'amount_still_wine': sum(move.product_id.volume * move.product_qty for move in moves_out.filtered(lambda m: m.product_id.gn_code == '2204 21')),
                        'amount_intermediate_vol': sum(move.product_id.alcohol_volume * move.product_qty for move in moves_out.filtered(lambda m: m.product_id.gn_code == '2204')),
                        'amount_intermediate_real': sum(move.product_id.volume * move.product_qty for move in moves_out.filtered(lambda m: m.product_id.gn_code == '2204')),
                        'amount_intermediate_100vol': sum(move.product_id.volume * (move.product_id.alcohol_volume/100) * move.product_qty for move in moves_out.filtered(lambda m: m.product_id.gn_code == '2204')),
                    })

        return res
