# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ExciseRegister(models.Model):
    _name = 'excise.register'
    _description = 'Excise Register'

    date = fields.Datetime("Create Date", default=fields.Datetime.now, readonly=True)

    type = fields.Selection([('in', 'In'), ('out', 'Out')], string="Type")
    type2 = fields.Selection([('ead', 'EAD'), ('ac4', 'AC4')], string="EAD/AC4", readonly=True, compute='_calculate_type2')

    date_ead = fields.Date("Date EAD")
    number_ead = fields.Char("Number EAD")

    amount_ethylalcohol_vol = fields.Char("Amount Ethylalcohol S200 (% vol)")
    amount_ethylalcohol_real = fields.Float("Amount Ethylalcohol S200 (real)")
    amount_ethylalcohol_100vol = fields.Float("Amount Ethylalcohol S200 (100% vol)")

    amount_sparkling_wine = fields.Float("Amount Sparkling Wine")
    amount_still_wine = fields.Float("Amount Still Wine")

    amount_intermediate_vol = fields.Char("Amount Intermediate (% vol)")
    amount_intermediate_real = fields.Float("Amount Intermediate (real)")
    amount_intermediate_100vol = fields.Float("Amount Intermediate (100% vol)")

    amount_beer_vol = fields.Char("Amount Beer (°P)")
    amount_beer_real = fields.Float("Amount Beer (real)")
    amount_beer_100vol = fields.Float("Amount Beer (°P vol)")

    # total_ethylalcohol_real = fields.Integer(string='Total Ethylalcohol (real)', store=True, readonly=True, compute='_calculate_totals')
    # total_ethylalcohol_100vol = fields.Integer(string='Total Ethylalcohol (100% vol)', store=True, readonly=True, compute='_calculate_totals')
    # total_sparkling_wine_real = fields.Integer(string='Total Sparkling Wine', store=True, readonly=True, compute='_calculate_totals')
    # total_still_wine = fields.Integer(string='Total Still Wine', store=True, readonly=True, compute='_calculate_totals')
    # total_intermediate_real = fields.Integer(string='Total Intermediate (real)', store=True, readonly=True, compute='_calculate_totals')
    # total_intermediate_100vol = fields.Integer(string='Total Intermediate (100% vol)', store=True, readonly=True, compute='_calculate_totals')

    sale_order_id = fields.Many2one('sale.order', string="Sale Order", readonly=True)
    purchase_order_id = fields.Many2one('purchase.order', string="Purchase Order", readonly=True)
    stock_picking_id = fields.Many2one('stock.picking', string="Stock Picking", readonly=True)
    stock_move_ids = fields.One2many('stock.move', 'excise_register_id', string="Stock Moves", readonly=True)

    @api.depends('type')
    def _calculate_type2(self):
        for s in self:
            if s.type == 'in':
                s.type2 = 'ead'
            else:
                if s.sale_order_id and s.sale_order_id.partner_id.country_id.code != 'BE':
                    s.type2 = 'ead'
                else:
                    s.type2 = 'ac4'

    def _calculate_amounts(self):
        for s in self:
            ethylalcohol_vol = {move.product_id.alcohol_volume for move in s.stock_move_ids.filtered(lambda m: m.product_id.product_tmpl_id._is_ethylalcohol())}
            intermediate_vol = {move.product_id.alcohol_volume for move in s.stock_move_ids.filtered(lambda m: m.product_id.product_tmpl_id._is_intermediate())}
            beer_vol = {move.product_id.degrees_plato for move in s.stock_move_ids.filtered(lambda m: m.product_id.product_tmpl_id._is_beer())}

            s.amount_ethylalcohol_vol = ethylalcohol_vol.pop() if len(ethylalcohol_vol) == 1 else ("" if len(ethylalcohol_vol) == 0 else "div.")
            s.amount_ethylalcohol_real = sum(move.product_id.volume * move.product_qty for move in s.stock_move_ids.filtered(lambda m: m.product_id.product_tmpl_id._is_ethylalcohol()))
            s.amount_ethylalcohol_100vol = sum(move.product_id.volume * (move.product_id.alcohol_volume / 100) * move.product_qty for move in s.stock_move_ids.filtered(lambda m: m.product_id.product_tmpl_id._is_ethylalcohol()))
            s.amount_sparkling_wine = sum(move.product_id.volume * move.product_qty for move in s.stock_move_ids.filtered(lambda m: m.product_id.product_tmpl_id._is_sparkling_wine()))
            s.amount_still_wine = sum(move.product_id.volume * move.product_qty for move in s.stock_move_ids.filtered(lambda m: m.product_id.product_tmpl_id._is_still_wine()))
            s.amount_intermediate_vol = intermediate_vol.pop() if len(intermediate_vol) == 1 else ("" if len(intermediate_vol) == 0 else "div.")
            s.amount_intermediate_real = sum(move.product_id.volume * move.product_qty for move in s.stock_move_ids.filtered(lambda m: m.product_id.product_tmpl_id._is_intermediate()))
            s.amount_intermediate_100vol = sum(move.product_id.volume * (move.product_id.alcohol_volume / 100) * move.product_qty for move in s.stock_move_ids.filtered(lambda m: m.product_id.product_tmpl_id._is_intermediate()))
            s.amount_beer_vol = beer_vol.pop() if len(beer_vol) == 1 else ("" if len(beer_vol) == 0 else "div.")
            s.amount_beer_real = sum(move.product_id.volume * move.product_qty for move in s.stock_move_ids.filtered(lambda m: m.product_id.product_tmpl_id._is_beer()))
            s.amount_beer_100vol = sum(move.product_id.volume * (move.product_id.degrees_plato) * move.product_qty for move in s.stock_move_ids.filtered(lambda m: m.product_id.product_tmpl_id._is_beer()))




