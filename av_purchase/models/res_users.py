from odoo import models, fields, _


class ResUsers(models.Model):
    """
    Extends the res.users model to manage purchase-specific user roles.
    
    This extension provides:
    - Computed fields for purchase role tracking
    - Integration with purchase security groups
    - Dynamic role checking capabilities
    
    Technical Details:
    - Uses computed fields with store=False for real-time role checking
    - Integrates with Odoo's security group system
    - Provides role-based access control for purchase operations
    """
    _inherit = 'res.users'

    is_po_cp = fields.Boolean(
        compute="_compute_is_po_cp",
        store=False,
        help="Indicates if the user is a Confirming Party (CP) for purchase orders"
    )
    is_po_hod = fields.Boolean(
        compute="_compute_is_po_hod",
        store=False,
        help="Indicates if the user is a Head of Department (HOD) for purchase orders"
    )

    def _compute_is_po_cp(self):
        """
        Computes whether the user has Confirming Party (CP) rights.
        
        This method checks if the user belongs to the purchase_cp security group,
        which grants special approval rights for purchase orders.
        """
        for user in self:
            user.is_po_cp = user.has_group(
                'av_purchase.group_purchase_cp'
            )

    def _compute_is_po_hod(self):
        """
        Computes whether the user has Head of Department (HOD) rights.
        
        This method checks if the user belongs to the purchase_hod security group,
        which grants department-level approval rights for purchase orders.
        """
        for user in self:
            user.is_po_hod = user.has_group(
                'av_purchase.group_purchase_hod'
            )
            