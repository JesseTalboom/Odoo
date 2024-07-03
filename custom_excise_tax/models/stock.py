# -*- coding: utf-8 -*-

from odoo import models, fields, api

class stock_location_inherit(models.Model):
    _inherit = 'stock.location'

    is_excise_depot = fields.Boolean("Is excise depot")
    bonded_warehouse_number = fields.Char("Bonded warehouse number")

class stock_move_inherit(models.Model):
    _inherit = 'stock.move'

    def _action_done(self, cancel_backorder=False):
        res = super(stock_move_inherit, self)._action_done(cancel_backorder)

        for move in self:
            if move.state == 'done' and move.product_id:
                if not move.location_id.is_excise_depot and move.location_dest_id.is_excise_depot:

                    self.env['excise.register'].create({
                        'type': 'in',
                        'stock_move_id': move.id,
                        'purchase_order_id': move.picking_id.purchase_id.id if move.picking_id.purchase_id else None,
                        #TODO quantities
                        'amount_ethylalcohol_vol': move.product_id.alcohol_volume * move.product_qty if move.product_id.excise_product_code == 'S200' else 0,
                        'amount_ethylalcohol_real': move.product_id.alcohol_volume * move.product_qty if move.product_id.excise_product_code == 'S200' else 0,
                        'amount_ethylalcohol_100vol': move.product_id.alcohol_volume * move.product_qty if move.product_id.excise_product_code == 'S200' else 0,
                        'amount_sparkling_wine': move.product_id.alcohol_volume * move.product_qty if move.product_id.excise_product_code == 'W300' else 0,
                        'amount_still_wine': move.product_id.alcohol_volume * move.product_qty if move.product_id.excise_product_code == 'W200' else 0,
                        'amount_intermediate_vol': move.product_id.alcohol_volume * move.product_qty if move.product_id.excise_product_code == '9999' else 0,
                        'amount_intermediate_real': move.product_id.alcohol_volume * move.product_qty if move.product_id.excise_product_code == '9999' else 0,
                        'amount_intermediate_100vol': move.product_id.alcohol_volume * move.product_qty if move.product_id.excise_product_code == '9999' else 0,
                    })

                elif move.location_id.is_excise_depot and not move.location_dest_id.is_excise_depot:

                    self.env['excise.register'].create({
                        'type': 'out',
                        'stock_move_id': move,
                        'sale_order_id': move.picking_id.sale_id.id if move.picking_id.sale_id else None,
                        #TODO quantities
                        'amount_ethylalcohol_vol': move.product_id.alcohol_volume * move.product_qty if move.product_id.excise_product_code == 'S200' else 0,
                        'amount_ethylalcohol_real': move.product_id.alcohol_volume * move.product_qty if move.product_id.excise_product_code == 'S200' else 0,
                        'amount_ethylalcohol_100vol': move.product_id.alcohol_volume * move.product_qty if move.product_id.excise_product_code == 'S200' else 0,
                        'amount_sparkling_wine': move.product_id.alcohol_volume * move.product_qty if move.product_id.excise_product_code == 'W300' else 0,
                        'amount_still_wine': move.product_id.alcohol_volume * move.product_qty if move.product_id.excise_product_code == 'W200' else 0,
                        'amount_intermediate_vol': move.product_id.alcohol_volume * move.product_qty if move.product_id.excise_product_code == '9999' else 0,
                        'amount_intermediate_real': move.product_id.alcohol_volume * move.product_qty if move.product_id.excise_product_code == '9999' else 0,
                        'amount_intermediate_100vol': move.product_id.alcohol_volume * move.product_qty if move.product_id.excise_product_code == '9999' else 0,
                    })

        return res