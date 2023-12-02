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

        async onClick() {
            var order = this.env.pos.get_order();
            var lines = order.get_orderlines();
            for (let i = 0; i < lines.length; i++){
                var line = lines[i];
                var emptygoodsProduct = this.env.pos.db.get_product_by_id(line.product.emptygoods_product_id[0])
                if (emptygoodsProduct){
                    order.add_product(emptygoodsProduct)
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
