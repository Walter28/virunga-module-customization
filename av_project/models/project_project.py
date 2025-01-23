from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ProjectProject(models.Model):
    _inherit = 'project.project'

    department_id = fields.Many2one('hr.department', string='Department')
    department_manager_id = fields.Many2one('hr.employee', string='Department Manager', compute='_compute_department_manager', store=True)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
        default=lambda self: self.env.company.currency_id.id)
    amount = fields.Monetary(string='Amount', default=0.0, currency_field='currency_id')
    date_start = fields.Date(required=True)
    date = fields.Date(required=True)
    purchase_order_ids = fields.One2many('purchase.order', 'project_id', string='Purchase Orders')
    purchase_order_count = fields.Integer(compute='_compute_purchase_order_count', string='Purchase Order Count')

    @api.depends('department_id')
    def _compute_department_manager(self):
        for project in self:
            project.department_manager_id = project.department_id.manager_id.id if project.department_id else False

    @api.depends('purchase_order_ids')
    def _compute_purchase_order_count(self):
        for project in self:
            project.purchase_order_count = len(project.purchase_order_ids)

    @api.constrains('amount')
    def _check_amount(self):
        for project in self:
            if project.amount < 0:
                raise ValidationError(
                    _("Project amount cannot be negative.")
                )

    @api.constrains('date_start', 'date')
    def _check_date_start(self):
        for project in self:
            if not project.date_start or not project.date:
                raise ValidationError(
                    _("Both start date and end date are required.")
                )
                
            if project.date_start > project.date:
                raise ValidationError(
                    _("Project start date must be before end date.")
                )

            today = fields.Date.context_today(self)
            if not (project.date_start <= today <= project.date):
                raise ValidationError(
                    _("Current date must be within project date range (between start and end date).")
                )
