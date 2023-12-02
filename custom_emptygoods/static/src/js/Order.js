odoo.define('custom_emptygoods.Order', function(require) {
    'use strict';

    var { Order } = require('point_of_sale.models');
    const Registries = require('point_of_sale.Registries');

     const OrderEmptyGoods = (Order) => class OrderEmptyGoods extends Order {

         async add_product(product, options) {
             super.add_product(product, options);

             var emptygoodsProduct = this.pos.db.get_product_by_id(product.emptygoods_product_id[0])
             if (emptygoodsProduct){
                 super.add_product(emptygoodsProduct)
             }
         }
     }

    Registries.Model.extend(Order, OrderEmptyGoods);

});
