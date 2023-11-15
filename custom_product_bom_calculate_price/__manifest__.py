# -*- coding: utf-8 -*-
{
    'name': "custom_product_bom_calculate_price",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Corbital",
    'website': "https://www.corbital.be",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Customizations',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['product','mrp'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
    ],
}
