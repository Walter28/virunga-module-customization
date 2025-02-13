"""
This module extends the purchase.order model to add project management functionality.
It allows linking purchase orders to specific projects for better tracking and budget management.
"""

from odoo import models, fields, _


class PurchaseOrder(models.Model):
    """
    Extends the purchase.order model to add project management capabilities.
    
    This extension allows:
    - Linking purchase orders to specific projects
    - Tracking project-specific purchases
    - Managing project budgets through purchase orders
    """
    _inherit = 'purchase.order'
    
    project_id = fields.Many2one(
        'project.project',
        string='Project',
        help="The project associated with this purchase order. Used for budget tracking and project cost management."
    )