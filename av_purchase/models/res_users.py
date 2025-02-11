from odoo import models, fields, _


class ResUsers(models.Model):
    _inherit = 'res.users'

    is_po_cp = fields.Boolean(compute="_compute_is_po_cp", store=False)
    is_po_hod = fields.Boolean(compute="_compute_is_po_hod", store=False)

    def _compute_is_po_cp(self):
        for user in self:
            user.is_po_cp = user.has_group(
                'av_purchase.group_purchase_cp'
            )

    def _compute_is_po_hod(self):
        for user in self:
            user.is_po_hod = user.has_group(
                'av_purchase.group_purchase_hod'
            )
            