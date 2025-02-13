from odoo import models, fields, _


class PurchaseCancelReason(models.TransientModel):
    """
    A wizard model for capturing and storing purchase order cancellation reasons.
    
    This wizard:
    - Prompts users to provide a reason when cancelling a purchase order
    - Records the cancellation reason in the chatter
    - Maintains an audit trail of who cancelled the order and why
    
    Technical Details:
    - Uses TransientModel to create temporary records
    - Integrates with the purchase order's messaging system
    - Provides a clean UI for cancellation reason input
    """
    _name = 'purchase.cancel.reason'
    _description = 'Purchase Order Cancel Reason'

    reason = fields.Text(
        string='Cancellation Reason',
        required=True,
        help="Detailed explanation of why the purchase order is being cancelled"
    )
    purchase_id = fields.Many2one(
        'purchase.order',
        string='Purchase Order',
        help="The purchase order being cancelled"
    )

    def action_confirm_cancel(self):
        """
        Executes the cancellation process with the provided reason.
        
        This method:
        1. Validates the presence of required data
        2. Creates a formatted message for the chatter
        3. Posts the cancellation reason to the purchase order's chatter
        4. Triggers the actual cancellation of the purchase order
        
        Returns:
            The result of the purchase order cancellation action
        """
        self.ensure_one()
        if self.purchase_id and self.reason:
            # Create a styled message for the chatter
            message = f"""
                <b>🚫 PURCHASE ORDER CANCELLED</b>
                ------------------------
                <b>Cancelled by:</b> {self.env.user.name}
                <b>Cancellation Reason:</b>
                {self.reason}
            """
            
            self.purchase_id.message_post(body=message)
            return self.purchase_id.with_context(bypass_reason=True).button_cancel()
