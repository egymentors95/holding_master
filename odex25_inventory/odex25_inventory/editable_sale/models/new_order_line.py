from odoo import api, fields, models


class NewOrderLine(models.Model):
    _name = "new.order.line"
    _description = 'New Order Line'

    sale_id = fields.Many2one(comodel_name='sale.order')
    unit_price = fields.Float()
    discount = fields.Float()
    tax_id = fields.Many2many(
        "account.tax",
    )
    product_id = fields.Many2one(comodel_name='product.product')
    lot_id = fields.Many2one(
        'stock.production.lot',
        string='Lot/Serial Number',
    )
    qty_done = fields.Float(string='Quantity')
    company_id = fields.Many2one(comodel_name='res.company', related='sale_id.company_id', store=True)
    product_uom_id = fields.Many2one(comodel_name='uom.uom')
    sale_order_line_id = fields.Many2one(comodel_name='sale.order.line')
    user_id = fields.Many2one(comodel_name='res.users', string='User', default=lambda self: self.env.user, copy=False)
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account',
        index=True, compute="_compute_analytic_account_id", store=True, readonly=False, check_company=True, copy=False)



    @api.depends('product_id', 'user_id')
    def _compute_analytic_account_id(self):
        for record in self:
            if record.user_id and record.user_id.analytic_account_id:
                record.analytic_account_id = record.user_id.analytic_account_id.id
            else:
                record.analytic_account_id = False
