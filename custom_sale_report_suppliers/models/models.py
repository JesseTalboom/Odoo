# -*- coding: utf-8 -*-

from odoo import models, fields, api

class sale_report_inherit(models.Model):
    _inherit = 'sale.report'

    seller_id = fields.Many2one(
        related='product_tmpl_id.seller_ids.partner_id',
        domain=[('supplier', '=', True)],
    )