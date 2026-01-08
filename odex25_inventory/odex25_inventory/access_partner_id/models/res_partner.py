from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    company_registration = fields.Char(string='CR')
    sales_person_ids = fields.Many2many(comodel_name='res.users', string='Sales Persons')
