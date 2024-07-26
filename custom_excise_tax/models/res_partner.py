# -*- coding: utf-8 -*-

from odoo import models, fields, api

class res_partner_inherit(models.Model):
    _inherit = 'res.partner'

    picking_type_id = fields.Many2one('stock.picking.type', 'Deliver To')