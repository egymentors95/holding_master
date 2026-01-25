from odoo import models, api, fields
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    new_order_line_ids = fields.One2many(comodel_name='new.order.line', inverse_name='sale_id', copy=False)

    def action_create_invoice_direct(self):
        """يستدعي الـ wizard sale.advance.payment.inv وينفذ إنشاء الفاتورة"""
        for order in self:
    #         wizard = self.env['sale.advance.payment.inv'].create({
    #             'advance_payment_method': 'delivered',  # أو 'all' لو عايز لكل الطلب
    #         })
    #
    #         # تمرير الـ sale.order الحالي في الـ context
    #         ctx = {
    #             'active_model': 'sale.order',
    #             'active_ids': [order.id],
    #             'active_id': order.id,
    #             'open_invoices': False,  # لو عايز تفتح الفاتورة بعد الإنشاء خليها True
    #         }
    #
    #         # استدعاء دالة الإنشاء من الـ wizard
    #         wizard.with_context(ctx).create_invoices()
    #
    #         # 🔹 استرجاع الفواتير اللي اتعملت
    #         invoices = self.env['account.move'].search([
    #             ('invoice_origin', '=', order.name),
    #             ('state', '!=', 'cancel')
    #         ])
    #
    #         # 🔹 إضافة sale_id
    #         invoices.write({'sale_id': order.id})

            # 🔹 مزامنة new_order_lines
            order.sudo().sync_new_order_lines_to_invoice()

        return True

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for order in self:
            for l in order.order_line:
                stock_moves = self.env['stock.move.line'].search([('picking_id.origin', '=', order.name)])
                for move in stock_moves:
                    if move.product_id == l.product_id:
                        move.write({
                            'unit_price': l.price_unit,
                            'sale_order_line_id': l.id,
                            'discount': l.discount,
                            'product_uom_id': l.product_uom.id,
                            'tax_id': [(6, 0, l.tax_id.ids)],
                        })

        return res

    def sync_new_order_lines_to_invoice(self):
        for sale in self:
            lines = []
            for nol in sale.new_order_line_ids:
                account = nol.product_id.property_account_income_id or \
                          nol.product_id.categ_id.property_account_income_categ_id
                if not account:
                    raise UserError(f"No income account defined for product {nol.product_id.name}")

                lines.append((0, 0, {
                    'product_id': nol.product_id.id,
                    'quantity': nol.qty_done,
                    'price_unit': nol.unit_price,
                    'discount': nol.discount,
                    'tax_ids': [(6, 0, nol.tax_id.ids)],
                    'new_order_line_id': nol.id,
                    'name': nol.product_id.name,
                    'account_id': account.id,
                    'sale_line_ids': [(6, 0, [nol.sale_order_line_id.id])] if nol.sale_order_line_id else [],
                    'lot_id': nol.lot_id.id if nol.lot_id else False,

                    'product_uom_id': nol.product_uom_id.id,
                    # 'sale_line_ids': [(6, 0, [nol.id])],
                    # 'analytic_tag_ids': [(6, 0, nol.analytic_tag_ids.ids)],
                    'analytic_account_id': nol.analytic_account_id.id if nol.analytic_account_id.id else False,

                }))

            # الفاتورة الآن تحتوي على lines عند الإنشاء
            invoice_vals = {
                'move_type': 'out_invoice',
                'invoice_origin': sale.name,
                'partner_id': sale.partner_invoice_id.id,
                'currency_id': sale.pricelist_id.currency_id.id,
                'invoice_payment_term_id': sale.payment_term_id.id,
                'team_id': sale.team_id.id,
                'sale_id': sale.id,
                'ref': sale.client_order_ref,
                'invoice_user_id': sale.user_id.id,
                'narration': sale.note,
                'fiscal_position_id': (sale.fiscal_position_id or sale.fiscal_position_id.get_fiscal_position(
                    sale.partner_id.id)).id,
                'partner_shipping_id': sale.partner_shipping_id.id,
                'payment_reference': sale.reference,
                'partner_bank_id': sale.company_id.partner_id.bank_ids[:1].id,
                'campaign_id': sale.campaign_id.id,
                'medium_id': sale.medium_id.id,
                'source_id': sale.source_id.id,

                'invoice_line_ids': lines,
            }
            invoice = self.env['account.move'].sudo().create(invoice_vals)

            # recompute taxes للتأكد من التوازن
            invoice.sudo()._recompute_dynamic_lines(recompute_all_taxes=True)
            invoice.sudo()._check_balanced()
            invoice.sudo()._onchange_partner_id()

