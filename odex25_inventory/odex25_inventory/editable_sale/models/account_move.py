from odoo import models, fields, api, _
from datetime import date

from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'

    invoice_date = fields.Date(
        string='Invoice/Bill Date',
        readonly=True,
        index=True,
        copy=False,
        states={'draft': [('readonly', False)]},
        default=lambda self: date.today(),
    )

    def action_post(self):
        for move in self:
            total_debit = sum(move.line_ids.mapped('debit'))
            total_credit = sum(move.line_ids.mapped('credit'))

            if total_debit == 0 or total_credit == 0:
                raise UserError(_(
                    "You cannot post this .\n"
                    "Total Debit and Total Credit must have values and cannot be zero."
                ))

        return super(AccountMove, self).action_post()

