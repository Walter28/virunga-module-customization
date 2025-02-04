from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ProjectProject(models.Model):
    """
    Extends the project.project model to add department management, financial tracking,
    and purchase order integration capabilities.

    This extension adds fields for department assignment, project budget tracking,
    date management, and related purchase orders.
    """
    _inherit = 'project.project'

    department_id = fields.Many2one('hr.department', string='Department',
                                  help="Department responsible for this project")
    department_manager_id = fields.Many2one('hr.employee', string='Department Manager',
                                          compute='_compute_department_manager',
                                          store=True,
                                          help="Manager of the assigned department")
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                 default=lambda self: self.env.company.currency_id.id,
                                 help="Currency used for project financial calculations")
    amount = fields.Monetary(string='Amount', default=0.0,
                           currency_field='currency_id',
                           help="Total budget allocated for this project")
    date_start = fields.Date(help="Project start date")
    date = fields.Date(help="Project end date")

    @api.depends('department_id')
    def _compute_department_manager(self):
        """
        Compute method to automatically set the department manager based on the selected department.
        Updates the department_manager_id field whenever the department_id changes.
        """
        for project in self:
            project.department_manager_id = project.department_id.manager_id.id if project.department_id else False
            

    @api.constrains('amount')
    def _check_amount(self):
        """
        Validation method to ensure project amount is not negative.
        
        Raises:
            ValidationError: If the project amount is less than 0.
        """
        for project in self:
            if project.amount <= 0:
                raise ValidationError(
                    _("Project amount cannot be negative or null.")
                )

    @api.constrains('date_start', 'date')
    def _check_date_start(self):
        """
        Validation method to ensure project dates are properly set and logical.
        
        Validates:
            1. Both start and end dates are set
            2. Current date must be within project date range (between start and end date)
               OR project start date must be in the future
        
        Raises:
            ValidationError: If any of the date validations fail
        """
        for project in self:
            if not project.date_start or not project.date:
                raise ValidationError(
                    _("Both start date and end date are required.")
                )

            today = fields.Date.context_today(self)
            if not (project.date_start <= today <= project.date or project.date_start > today):
                raise ValidationError(
                    _("Current date must be within project date range (between start and end date) or project must start in the future")
                )
