# -*- coding: utf-8 -*-

from odoo import models, fields, api

class purchase_order_inherit(models.Model):
    _inherit = 'purchase.order'

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.partner_id and self.partner_id.picking_type_id:
            self.picking_type_id = self.partner_id.picking_type_id.id