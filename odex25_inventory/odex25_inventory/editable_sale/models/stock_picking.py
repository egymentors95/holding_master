from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"


    def button_validate(self):
        res = super().button_validate()

        if not self._check_backorder() and self.sale_id:
            sale_name = self.origin
            sale = self.env['sale.order'].search([
                ('name', '=', sale_name)
            ], limit=1)

            for rec in self.move_line_ids_without_package:
                qty_done = rec.qty_done
                # if self.location_id.usage == 'customer':
                #     qty_done = -qty_done
                # if qty_done == 0:
                #     continue

                # ➕ CREATE only - no update for non-returns
                self.env['new.order.line'].create({
                    'sale_id': sale.id,
                    'product_id': rec.product_id.id,
                    'qty_done': qty_done,
                    'unit_price': rec.unit_price,
                    # 'analytic_account_id': rec.analytic_account_id.id,
                    'discount': rec.discount,
                    'sale_order_line_id': rec.sale_order_line_id.id,
                    'product_uom_id': rec.product_uom_id.id,
                    'lot_id': rec.lot_id.id,
                    'tax_id': [(6, 0, rec.tax_id.ids)],
                })

        return res
