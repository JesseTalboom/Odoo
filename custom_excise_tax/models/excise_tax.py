# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ExciseTax(models.Model):
    _name = 'excise.tax'
    _description = 'Excise Tax'

    name = fields.Char("Box 33", required=True)

    excise_tax = fields.Float(string='Excise Price (€/HL)', digits=(12, 4), required=True)
    special_excise_tax = fields.Float(string='Special Excise Price (€/HL)', digits=(12, 4), required=True)
    packaging_tax = fields.Float(string='Packaging Tax (€/HL)', digits=(12, 4), required=True)

