odoo.define('custom_emptygoods.EmptyGoodsButton', function(require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const { useListener } = require("@web/core/utils/hooks");
    const Registries = require('point_of_sale.Registries');

    class EmptyGoodsButton extends PosComponent {
        setup() {
            super.setup();
            useListener('click', this.onClick);
        }

        // This method will (re-) calculate total empty goods
        async onClick() {
            const order = this.env.pos.get_order();
            const lines = order.get_orderlines();

            // Init already existing empty goods lines to quantity 0
            const emptyGoodsLines = lines.filter(x => x.product.emptygoods);
            for (let i = 0; i < emptyGoodsLines.length; i++)
            {
                let emptyGoodsLine = emptyGoodsLines[i];
                emptyGoodsLine.set_quantity(0);
            }

            // Update (or create) empty goods line quantities
            const fullGoodsLines = lines.filter(x => !x.product.emptygoods);
            for (let i = 0; i < fullGoodsLines.length; i++){
                let fullGoodsLine = fullGoodsLines[i];
                var emptygoodsProduct = this.env.pos.db.get_product_by_id(fullGoodsLine.product.emptygoods_product_id[0])

                 let emptyGoodLine = lines.filter(x => x.product == emptygoodsProduct)[0] ?? null;
                 // Already existing - Update
                 if (emptyGoodLine)
                 {
                     const oldQuantity = emptyGoodLine.quantity;
                     const newQuantity = oldQuantity + fullGoodsLine.quantity;
                     emptyGoodLine.set_quantity(newQuantity)
                 }
                 // Non-existing - Create
                 else
                 {
                    await order.add_product(emptygoodsProduct)
                    emptyGoodLine = lines.filter(x => x.product == emptygoodsProduct)[0] ?? null;
                    emptyGoodLine.set_quantity(fullGoodsLine.quantity)
                 }
            }

        }

    }

    EmptyGoodsButton.template = 'EmptyGoodsButton';

    ProductScreen.addControlButton({
        component: EmptyGoodsButton,
        condition: function() {
            return true;
        },
    });

    Registries.Component.add(EmptyGoodsButton);

    return EmptyGoodsButton;
});
