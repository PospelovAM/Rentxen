"""
Override the behavior of the sale.py file
"""
from odoo import api, fields, models


class InheritedSaleOrder(models.Model):
    """
    Extension for the sale.order model

    new field:
        * partner_marginality - reference to the res.partner model marginality field for easier use inside the view file

    new features:
        * Override onchange_partner_id method to update Order Lines according to the new partner marginality
    """
    _inherit = 'sale.order'

    partner_marginality = fields.Integer(compute="_compute_marginality")

    @api.depends('partner_id')
    def _compute_marginality(self):
        """
        Sets the value from partner_id.marginality field when the partner is changed
        """
        for order in self:
            order.partner_marginality = order.partner_id.marginality

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        """
        Update the following fields when the partner is changed:
        - Pricelist
        - Payment terms
        - Invoice address
        - Delivery address
        - Sales Team
        - Order Lines
        """

        super().onchange_partner_id()

        lines_to_update = []
        for line in self.order_line.filtered(lambda line: not line.display_type):
            product = line.product_id.with_context(
                partner=self.partner_id,
                quantity=line.product_uom_qty,
                date=self.date_order,
                pricelist=self.pricelist_id.id,
                uom=line.product_uom.id
            )
            price_unit = self.env['account.tax']._fix_tax_included_price_company(
                line._get_display_price(product),
                line.product_id.taxes_id,
                line.tax_id,
                line.company_id) \
                * (1 + (self.partner_id.marginality or 0.0) / 100.0)
            if self.pricelist_id.discount_policy == 'without_discount' and price_unit:
                discount = max(0, (price_unit - product.price) * 100 / price_unit)
            else:
                discount = 0
            lines_to_update.append((1, line.id, {'price_unit': price_unit, 'discount': discount}))
        self.update({'order_line': lines_to_update})


class InheritedSaleOrderLine(models.Model):
    """
    Extension for the sale.order.line model

    new features:
        * Override product_id_change and product_uom_change methods to use partner marginality
    """

    _inherit = 'sale.order.line'

    @api.onchange('product_id')
    def product_id_change(self):
        """
        Updates order line values according to the changed product
        """
        super().product_id_change()
        self.update({'price_unit': self.price_unit * (1 + self.order_partner_id.marginality / 100.0)})

    @api.onchange('product_uom', 'product_uom_qty')
    def product_uom_change(self):
        """
        Updates order line values according to added product or updated quantity field
        """
        super().product_uom_change()
        self.update({'price_unit': self.price_unit * (1 + self.order_partner_id.marginality / 100.0)})
