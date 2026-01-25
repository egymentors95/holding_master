from odoo import models, fields, api


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    lot_id = fields.Many2one(
        'stock.production.lot',
        string='Lot/Serial Number',
        domain="[('product_id', '=', product_id)]"
    )
    new_order_line_id = fields.Many2one(
        'new.order.line',
        string='New Order Line'
    )
    sale_id = fields.Many2one(comodel_name='sale.order', string='Sale Order', related='move_id.sale_id', store=True)