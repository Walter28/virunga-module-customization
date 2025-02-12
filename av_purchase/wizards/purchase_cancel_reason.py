from odoo import models, fields, _

class PurchaseCancelReason(models.TransientModel):
    _name = 'purchase.cancel.reason'
    _description = 'Purchase Order Cancel Reason'

    reason = fields.Text(string='Cancellation Reason', required=True)
    purchase_id = fields.Many2one('purchase.order', string='Purchase Order')

    def action_confirm_cancel(self):
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
