from odoo import models, fields, api, _
from odoo.exceptions import UserError

class PurchaseConfirm(models.TransientModel):
    _name = 'purchase.confirm'
    _description = 'Purchase Order Confirmation'

    purchase_id = fields.Many2one('purchase.order', string='Purchase Order', required=True)
    amount_total = fields.Monetary(related='purchase_id.amount_total', string='Total Amount', readonly=True)
    project_amount = fields.Monetary(related='purchase_id.project_id.amount', string='Project Budget', readonly=True)
    currency_id = fields.Many2one(related='purchase_id.currency_id', string='Currency', readonly=True)

    def action_confirm(self):
        self.ensure_one()
        if not self.purchase_id.project_id:
            raise UserError(_('Please set a project before confirming the purchase order.'))
            
        if self.amount_total > self.project_amount:
            raise UserError(_('Purchase order amount exceeds project budget.'))
            
        # Update project amount
        self.purchase_id.project_id.sudo().amount -= self.amount_total
        
        # Confirm purchase order
        return self.purchase_id.button_confirm()
