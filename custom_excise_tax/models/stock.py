# -*- coding: utf-8 -*-

from odoo import models, fields, api

class stock_quant_inherit(models.Model):
    _inherit = 'stock.quant'

    # Fields needed to show in Tree
    product_volume = fields.Float(related='product_id.product_tmpl_id.volume', store=True, readonly=True, string="Volume (L)")
    product_alcohol_volume = fields.Float(related='product_id.product_tmpl_id.alcohol_volume', store=True, readonly=True, string="Alcohol Vol. (%) / °P")
    product_alcohol_100_volume = fields.Float(related='product_id.product_tmpl_id.alcohol_100_volume', store=True, readonly=True, string="Alcohol Vol. (real)")

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
                    excise_register = self.env['excise.register'].create({
                        'type': 'in',
                        'stock_picking_id': picking.id,
                        'purchase_order_id': picking.purchase_id.id if picking.purchase_id else None,
                        'stock_move_ids': [(6, 0, [move.id for move in moves_in])],
                    })

                    excise_register._calculate_amounts()

                elif any(moves_out):
                    excise_register = self.env['excise.register'].create({
                        'type': 'out',
                        'stock_picking_id': picking.id,
                        'sale_order_id': picking.sale_id.id if picking.sale_id else None,
                        'stock_move_ids': [(6, 0, [move.id for move in moves_out])],
                    })

                    excise_register._calculate_amounts()

        return res
