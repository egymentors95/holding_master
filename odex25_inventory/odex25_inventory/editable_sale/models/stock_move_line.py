from odoo import api, fields, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"


    unit_price = fields.Float()
    discount = fields.Float()
    tax_id = fields.Many2many(
        "account.tax",
    )
    # analytic_account_id = fields.Many2one(comodel_name='account.analytic.account')
    sale_order_line_id = fields.Many2one(comodel_name='sale.order.line')
    expiration_date = fields.Datetime(string="Expiration Date", related='lot_id.expiration_date', store=True)
    available_quantity = fields.Float(related='lot_id.product_qty', store=True, string='Available Quantity')
