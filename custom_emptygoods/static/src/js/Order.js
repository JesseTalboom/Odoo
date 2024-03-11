odoo.define('custom_emptygoods.Order', function(require) {
    'use strict';

    var { Order } = require('point_of_sale.models');
    const Registries = require('point_of_sale.Registries');

     const OrderEmptyGoods = (Order) => class OrderEmptyGoods extends Order {

         // Inherits add_product method, if product is fullgoods add the emtpygoods as seperate line
         async add_product(product, options) {
             // Check if product already exists, if so emptygoods line added can be merged, if not do not merge emptygoods
             const lines = this.get_orderlines();
             const productExists = lines.filter(x => x.product.id == product.id)[0] ?? null;

             // If an emptygoods product is added, this may never be merged

             if (product.emptygoods){
                 options.merge = false;
             }

             // SUPER
             var res = super.add_product(product, options);

             // Find emptygoods product
             var emptygoodsProduct = this.pos.db.get_product_by_id(product.emptygoods_product_id[0])
             if (emptygoodsProduct){
                 // MERGE *OLD CODE*
                 // const lines = this.get_orderlines();
                 // const emptyGoodLine = lines.filter(x => x.product == emptygoodsProduct)[0] ?? null;
                 // // Already existing - Update
                 // if (emptyGoodLine)
                 // {
                 //     const oldQuantity = emptyGoodLine.quantity;
                 //     const newQuantity = oldQuantity + 1;
                 //     emptyGoodLine.set_quantity(newQuantity)
                 // }
                 // // Non-existing - Create
                 // else
                 // {
                 //    super.add_product(emptygoodsProduct)
                 // }

                 let opt = {};

                 const fullgoods_line = super.get_selected_orderline();
                 opt.fullgoods_line_id = fullgoods_line.id;
                 opt.description = fullgoods_line.product.display_name;

                 if (!productExists){
                     opt.merge = false;
                 }

                 super.add_product(emptygoodsProduct, opt)

                 const emptygoods_line = super.get_selected_orderline();
                 fullgoods_line.emptygoods_line_id = emptygoods_line.id;
             }

             return res;
         }

         set_orderline_options(orderline, options) {
             var res = super.set_orderline_options(orderline, options);
             if (options.fullgoods_line_id){
                orderline.fullgoods_line_id = options.fullgoods_line_id;
             }
             return res;
         }
     }

    Registries.Model.extend(Order, OrderEmptyGoods);

});
