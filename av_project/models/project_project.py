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
    project_stage_name = fields.Char(related='stage_id.name', string='Project Stage', store=True)
    
    @api.depends('department_id')
    def _compute_department_manager(self):
        """
        Compute method to automatically set the department manager based on the selected department.
        Updates the department_manager_id field whenever the department_id changes.
        """
        for project in self:
            project.department_manager_id = project.department_id.manager_id.id if project.department_id else False
            
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'amount' in vals:
                if vals.get('amount') <= 0:
                    raise ValidationError(_("Project amount cannot be negative or null."))
        return super(ProjectProject, self).create(vals_list)

    @api.constrains('date_start', 'date')
    def _check_date_start(self):
        """
        Validates:
            Project start date must be in the future or today
        
        Raises:
            ValidationError: If the project start date is not in the future or today
        """
        for project in self:
            if project.date_start:
                today = fields.Date.context_today(self)
                if project.date_start < today:
                    raise ValidationError(
                        _("Project must start in the future or today")
                    )

    def write(self, vals):
        if 'stage_id' in vals:
            stage = self.env['project.task.type'].browse(vals['stage_id'])
            if stage.name in ['In Progress', 'Done']:
                for project in self:
                    # Check required fields before allowing stage change
                    if not all([project.department_id, project.date_start, project.date, project.amount]):
                        missing_fields = []
                        if not project.department_id:
                            missing_fields.append(_("Department"))
                        if not project.date_start:
                            missing_fields.append(_("Start Date"))
                        if not project.date:
                            missing_fields.append(_("End Date"))
                        if not project.amount:
                            missing_fields.append(_("Amount"))
                        
                        raise ValidationError(
                            _("Cannot change project stage to %s.\n\nThe following fields are required :\n   ★ %s") % 
                            (stage.name, ", ".join(missing_fields))
                        )
        return super(ProjectProject, self).write(vals)
