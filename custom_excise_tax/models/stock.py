# -*- coding: utf-8 -*-

from odoo import models, fields, api

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
                moves_in = picking.move_ids.filtered(lambda m: m.product_id and m.product_id.excise_product_code and not m.location_id.is_excise_depot and m.location_dest_id.is_excise_depot)
                moves_out = picking.move_ids.filtered(lambda m: m.product_id and m.product_id.excise_product_code and m.location_id.is_excise_depot and not m.location_dest_id.is_excise_depot)
            
                if any(moves_in):
                    self.env['excise.register'].create({
                        'type': 'in',
                        'stock_picking_id': picking.id,
                        'purchase_order_id': picking.purchase_id.id if picking.purchase_id else None,
                        'product_ids': [(6, 0, [move.product_id.id for move in moves_in])],
                        #TODO quantities
                        'amount_ethylalcohol_vol': sum(move.product_id.alcohol_volume * move.product_qty for move in moves_in.filtered(lambda m: m.product_id.excise_product_code == 'S200')),
                        'amount_ethylalcohol_real': sum(move.product_id.alcohol_volume * move.product_qty for move in moves_in.filtered(lambda m: m.product_id.excise_product_code == 'S200')),
                        'amount_ethylalcohol_100vol': sum(move.product_id.alcohol_volume * move.product_qty for move in moves_in.filtered(lambda m: m.product_id.excise_product_code == 'S200')),
                        'amount_sparkling_wine': sum(move.product_id.alcohol_volume * move.product_qty for move in moves_in.filtered(lambda m: m.product_id.excise_product_code == 'W300')),
                        'amount_still_wine': sum(move.product_id.alcohol_volume * move.product_qty for move in moves_in.filtered(lambda m: m.product_id.excise_product_code == 'W200')),
                        'amount_intermediate_vol': sum(move.product_id.alcohol_volume * move.product_qty for move in moves_in.filtered(lambda m: m.product_id.excise_product_code == '1234')),
                        'amount_intermediate_real': sum(move.product_id.alcohol_volume * move.product_qty for move in moves_in.filtered(lambda m: m.product_id.excise_product_code == '1234')),
                        'amount_intermediate_100vol': sum(move.product_id.alcohol_volume * move.product_qty for move in moves_in.filtered(lambda m: m.product_id.excise_product_code == '1234')),
                    })

                elif any(moves_out):
                    self.env['excise.register'].create({
                        'type': 'out',
                        'stock_picking_id': picking.id,
                        'sale_order_id': picking.sale_id.id if picking.sale_id else None,
                        'product_ids': [(6, 0, [move.product_id.id for move in moves_out])],
                        #TODO quantities
                        'amount_ethylalcohol_vol': sum(move.product_id.alcohol_volume * move.product_qty for move in moves_out.filtered(lambda m: m.product_id.excise_product_code == 'S200')),
                        'amount_ethylalcohol_real': sum(move.product_id.alcohol_volume * move.product_qty for move in moves_out.filtered(lambda m: m.product_id.excise_product_code == 'S200')),
                        'amount_ethylalcohol_100vol': sum(move.product_id.alcohol_volume * move.product_qty for move in moves_out.filtered(lambda m: m.product_id.excise_product_code == 'S200')),
                        'amount_sparkling_wine': sum(move.product_id.alcohol_volume * move.product_qty for move in moves_out.filtered(lambda m: m.product_id.excise_product_code == 'W300')),
                        'amount_still_wine': sum(move.product_id.alcohol_volume * move.product_qty for move in moves_out.filtered(lambda m: m.product_id.excise_product_code == 'W200')),
                        'amount_intermediate_vol': sum(move.product_id.alcohol_volume * move.product_qty for move in moves_out.filtered(lambda m: m.product_id.excise_product_code == '1234')),
                        'amount_intermediate_real': sum(move.product_id.alcohol_volume * move.product_qty for move in moves_out.filtered(lambda m: m.product_id.excise_product_code == '1234')),
                        'amount_intermediate_100vol': sum(move.product_id.alcohol_volume * move.product_qty for move in moves_out.filtered(lambda m: m.product_id.excise_product_code == '1234')),
                    })

        return res
