odoo.define('custom_emptygoods.OrderReceipt', function(require) {
    'use strict';

    const OrderReceipt = require('point_of_sale.OrderReceipt');
    const Registries = require('point_of_sale.Registries');

    const OrderReceiptEmptyGoods = OrderReceipt => class extends OrderReceipt {

        get receiptEnv () {
            let receipt_render_env = super.receiptEnv;
            let order = this.env.pos.get_order();

            const amount_emptygoods_min = order.orderlines.reduce((total, orderline) => {
              if (orderline.quantity < 0 && orderline.product != null && orderline.product.emptygoods) {
                return total + (orderline.price * orderline.quantity * (1 - orderline.discount));
              }
              return total;
            }, 0);

            const amount_emptygoods_plus = order.orderlines.reduce((total, orderline) => {
              if (orderline.quantity > 0 && orderline.product != null && orderline.product.emptygoods) {
                return total + (orderline.price * orderline.quantity * (1 - orderline.discount));
              }
              return total;
            }, 0);

            const amount_emptygoods_total = amount_emptygoods_min + amount_emptygoods_plus;

            receipt_render_env.receipt.amount_emptygoods_min = amount_emptygoods_min;
            receipt_render_env.receipt.amount_emptygoods_plus = amount_emptygoods_plus;
            receipt_render_env.receipt.amount_emptygoods_total = amount_emptygoods_total;

            return receipt_render_env;
        }
    }

    Registries.Component.extend(OrderReceipt, OrderReceiptEmptyGoods);

    return OrderReceipt;
});
