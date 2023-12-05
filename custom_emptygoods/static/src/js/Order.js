odoo.define('custom_emptygoods.Order', function(require) {
    'use strict';

    var { Order } = require('point_of_sale.models');
    const Registries = require('point_of_sale.Registries');

     const OrderEmptyGoods = (Order) => class OrderEmptyGoods extends Order {

         // Inherits add_product method, if product has an emptygoods product linked this will add it as new line, if this line is already existing quantity is updated
         async add_product(product, options) {
             var res = super.add_product(product, options);

             var emptygoodsProduct = this.pos.db.get_product_by_id(product.emptygoods_product_id[0])
             if (emptygoodsProduct){
                 const lines = this.get_orderlines();
                 const emptyGoodLine = lines.filter(x => x.product == emptygoodsProduct)[0] ?? null;
                 // Already existing - Update
                 if (emptyGoodLine)
                 {
                     const oldQuantity = emptyGoodLine.quantity;
                     const newQuantity = oldQuantity + 1;
                     emptyGoodLine.set_quantity(newQuantity)
                 }
                 // Non-existing - Create
                 else
                 {
                    super.add_product(emptygoodsProduct)
                 }
             }

             return res;
         }
     }

    Registries.Model.extend(Order, OrderEmptyGoods);

});
