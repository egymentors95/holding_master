from odoo import models, fields, api


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'


    lot_name = fields.Char(string='Lot', help="Lot number for the product")
    expiration_date = fields.Datetime()
