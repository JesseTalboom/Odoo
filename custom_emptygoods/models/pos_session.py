
from odoo import fields, models

class pos_session_inherit(models.Model):
    _inherit = 'pos.session'

    def _loader_params_product_product(self):
        result = super()._loader_params_product_product()
        result['search_params']['fields'].append('emptygoods_product_id')
        return result
