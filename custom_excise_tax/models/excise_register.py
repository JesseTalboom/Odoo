# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ExciseRegister(models.Model):
    _name = 'excise.register'
    _description = 'Excise Register'

    date = fields.Datetime("Create Date", default=fields.Datetime.now)

    type = fields.Selection([('in', 'In'), ('out', 'Out')], string="Type")
    type2 = fields.Selection([('ead', 'EAD'), ('ac4', 'AC4')], string="EAD/AC4", readonly=True, compute='_calculate_type2')

    date_ead = fields.Date("Date EAD")
    number_ead = fields.Char("Number EAD")

    amount_ethylalcohol_vol = fields.Integer("Amount Ethylalcohol S200 (% vol)")
    amount_ethylalcohol_real = fields.Integer("Amount Ethylalcohol S200 (real)")
    amount_ethylalcohol_100vol = fields.Integer("Amount Ethylalcohol S200 (100% vol)")

    amount_sparkling_wine = fields.Integer("Amount Sparkling Wine")
    amount_still_wine = fields.Integer("Amount Still Wine")

    amount_intermediate_vol = fields.Integer("Amount Intermediate (% vol)")
    amount_intermediate_real = fields.Integer("Amount Intermediate(real)")
    amount_intermediate_100vol = fields.Integer("Amount Intermediate (100% vol)")

    total = fields.Integer(string='Total', store=True, readonly=True, compute='_calculate_totals')

    sale_order_id = fields.Many2one('sale.order', string="Sale Order", readonly=True)
    purchase_order_id = fields.Many2one('purchase.order', string="Purchase Order", readonly=True)
    stock_move_id = fields.Many2one('stock.move', string="Stock Move", readonly=True)

    @api.depends('type')
    def _calculate_type2(self):
        for s in self:
            if s.type == 'in':
                s.type2 = 'ead'
            else:
                if s.sale_order_id.partner_id.country_id.code != 'BE': #TODO
                    s.type2 = 'ead'
                else:
                    s.type2 = 'ac4'


    @api.depends('amount_ethylalcohol_vol','amount_ethylalcohol_real','amount_ethylalcohol_100vol','amount_sparkling_wine','amount_still_wine','amount_intermediate_vol','amount_intermediate_real','amount_intermediate_100vol')
    def _calculate_totals(self):
        for s in self:
            s.total = s.amount_ethylalcohol_vol + s.amount_ethylalcohol_real #TODO





