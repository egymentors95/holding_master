from odoo import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    landed_cost_count = fields.Integer(
        string="Landed Costs",
        compute="_compute_landed_cost_count"
    )

    def _compute_landed_cost_count(self):
        LandedCost = self.env['stock.landed.cost']
        for order in self:
            order.landed_cost_count = LandedCost.search_count([
                ('purchase_order_id', '=', order.id)
            ])

    def action_view_landed_costs(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Landed Costs',
            'res_model': 'stock.landed.cost',
            'view_mode': 'tree,form',
            'domain': [('purchase_order_id', '=', self.id)],
            'context': {
                'default_purchase_order_id': self.id,
            }
        }



    def _create_picking(self):
        res = super(PurchaseOrder, self)._create_picking()

        for order in self:
            pickings = self.env['stock.picking'].search([
                ('origin', '=', order.name),
                ('purchase_order_id', '=', False),
            ])
            pickings.write({
                'purchase_order_id': order.id
            })

        return res

    def action_create_invoice(self):
        res = super().action_create_invoice()

        if isinstance(res, dict) and res.get('res_id'):
            move = self.env['account.move'].browse(res['res_id'])
            if move and len(self) == 1:
                move.purchase_order = self.id

        return res

    def button_confirm(self):
        res = super(PurchaseOrder, self).button_confirm()

        for order in self:
            pickings = self.env['stock.picking'].search([
                ('origin', '=', order.name)
            ])

            for picking in pickings:
                for move in picking.move_ids_without_package:
                    line = move.purchase_line_id
                    if not line or not line.lot_name:
                        continue

                    self.env['stock.move.line'].create({
                        'move_id': move.id,
                        'product_id': move.product_id.id,
                        'lot_name': line.lot_name,
                        'qty_done': move.product_uom_qty,
                        'product_uom_id': move.product_uom.id,
                        'location_id': move.location_id.id,
                        'location_dest_id': move.location_dest_id.id,
                        'picking_id': picking.id,
                    })

        return res



