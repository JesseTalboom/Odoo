odoo.define('custom_emptygoods.Orderline', function(require) {
    'use strict';

    var { Orderline } = require('point_of_sale.models');
    const Registries = require('point_of_sale.Registries');

     const OrderlineEmptyGoods = (Orderline) => class OrderlineEmptyGoods extends Orderline {

         // Update quantity of empty goods line
         set_quantity(quantity, keep_price) {
             const oldQuantity = this.quantity ?? 0;
             // Check if oldQuantity is not 0, because if 0 then this method is called from constructor and empty good may not be added since this is already added from Order.add_product.
             if (oldQuantity > 0)
             {
                 // If fullgoods line is edited, update emptygoods line aswell
                 if (this.emptygoods_line_id){
                     const emptygoods_line = this.order.get_orderline(this.emptygoods_line_id);
                     emptygoods_line.set_quantity(quantity);
                 }

                 // const quantityDiff = quantity - oldQuantity;
                 // const emptygoodProduct = this.pos.db.get_product_by_id(this.product.emptygoods_product_id[0])
                 // if (emptygoodProduct)
                 // {
                 //     const lines = this.order.get_orderlines();
                 //     const emptyGoodLine = lines.filter(x => x.product == emptygoodProduct)[0] ?? null;
                 //     if (emptyGoodLine)
                 //     {
                 //         //const newQuantity = Math.max(emptyGoodLine.quantity + quantityDiff, 0);
                 //         const oldQuantity = emptyGoodLine.quantity;
                 //         const newQuantity = oldQuantity + quantityDiff;
                 //         emptyGoodLine.set_quantity(newQuantity)
                 //     }
                 // }
             }

             return super.set_quantity(quantity, keep_price);
         }

         // Inherit merge and call super set_quantity instead of inherit method. Since empty good may not be added since this is already added from order.add_product
         merge(orderline){
            this.order.assert_editable();
            super.set_quantity(this.get_quantity() + orderline.get_quantity());
        }
     }

    Registries.Model.extend(Orderline, OrderlineEmptyGoods);

});
