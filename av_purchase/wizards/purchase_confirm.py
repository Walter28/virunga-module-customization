from odoo import models, fields, api, _
from odoo.exceptions import UserError


class PurchaseConfirm(models.TransientModel):
    """
    A wizard model for confirming purchase orders with budget validation.
    
    This wizard provides:
    - Budget validation against project budget
    - Project assignment verification
    - Automatic budget adjustment upon confirmation
    
    Technical Details:
    - Uses TransientModel for temporary wizard records
    - Integrates with project budgeting system
    - Implements budget validation rules
    """
    _name = 'purchase.confirm'
    _description = 'Purchase Order Confirmation'

    purchase_id = fields.Many2one(
        'purchase.order',
        string='Purchase Order',
        required=True,
        help="The purchase order to be confirmed"
    )
    amount_total = fields.Monetary(
        related='purchase_id.amount_total',
        string='Total Amount',
        readonly=True,
        help="Total amount of the purchase order"
    )
    project_amount = fields.Monetary(
        string='Project Budget',
        readonly=True, 
        related='purchase_id.project_id.amount',
        help="Available budget for the related project"
    )
    currency_id = fields.Many2one(
        related='purchase_id.currency_id',
        string='Currency',
        readonly=True,
        help="Currency used for the purchase order"
    )

    def action_confirm(self):
        """
        Confirms the purchase order after validating project and budget constraints.
        
        This method:
        1. Validates project assignment
        2. Checks budget availability
        3. Updates project budget
        4. Confirms the purchase order
        
        Raises:
            UserError: If project is not set or budget is exceeded
            
        Returns:
            Result of the purchase order confirmation action
        """
        self.ensure_one()
        if not self.purchase_id.project_id:
            raise UserError(_('Please set a project before confirming the purchase order.'))
            
        if self.amount_total > self.project_amount:
            raise UserError(_('Purchase order amount exceeds project budget.'))
            
        # Update project amount
        self.purchase_id.project_id.sudo().amount -= self.amount_total
        
        # Confirm purchase order
        return self.purchase_id.button_confirm()
