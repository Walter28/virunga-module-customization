from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    
    project_id = fields.Many2one('project.project', string='Project')
    department_id = fields.Many2one('hr.department', string='Department', required=True, 
                                  default=lambda self: self.get_current_user_department(), 
                                  help="Department for CP creator for this PO")
    validator = fields.Many2one('res.users', string='Validator', compute='_compute_validator', store=True)
    
    is_user_cp = fields.Boolean(compute="_compute_get_is_user_cp", store=False)
    is_user_hod = fields.Boolean(compute="_compute_get_is_user_hod", store=False)
    hod_department_id = fields.Many2one('hr.department', compute='_compute_hod_department', store=False)
    
    def _compute_get_is_user_cp(self):
        for order in self:
            order.is_user_cp = self.env.user.is_po_cp

    def _compute_get_is_user_hod(self):
        for order in self:
            order.is_user_hod = self.env.user.is_po_hod
    
    def get_current_user_department(self):
        if self.env.user.has_group('av_purchase.group_purchase_cp'):
            employee = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)], limit=1)
            return employee.department_id.id
                
    @api.depends('department_id', 'department_id.manager_id')
    def _compute_validator(self):
        """Compute the validator based on department manager"""
        for order in self:
            if order.department_id and order.department_id.manager_id:
                order.validator = order.department_id.manager_id.user_id
            else:
                order.validator = False

    @api.depends('is_user_hod', 'state')
    def _compute_hod_department(self):
        employee = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)], limit=1)
        for order in self:
            # Default to False
            order.hod_department_id = False
            # Only set department if user is HOD and order is in sent state
            if order.is_user_hod and order.state == 'sent':
                order.hod_department_id = employee.department_id.id if employee else False

    @api.model_create_multi
    def create(self, vals_list):
        if self.env.user.has_group('av_purchase.group_purchase_cp'):
            employee = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)], limit=1)
            if not employee:
                raise UserError(_('CP users must be linked to an employee to create purchase orders.'))
        return super(PurchaseOrder, self).create(vals_list)

    # def button_confirm(self):
    #     self.ensure_one()
    #     if not self.project_id:
    #         raise UserError(_('Please set a project before confirming the purchase order.'))
    #     return super(PurchaseOrder, self).button_confirm()

    def action_confirm_wizard(self):
        """Open confirmation wizard before confirming the purchase order"""
        self.ensure_one()
        return {
            'name': _('Confirm Purchase Order'),
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.confirm',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_purchase_id': self.id,
                'default_amount_total': self.amount_total,
                'default_currency_id': self.currency_id.id,
                'default_project_amount': self.project_id.amount if self.project_id else 0.0,
            }
        }

    def button_cancel(self):
        if self.env.user.has_group('av_purchase.group_purchase_cp') and self.state != 'draft':
            raise UserError(_("You don't have access to cancel this purchase order in its current state."))
        if not self.env.context.get('bypass_reason') and self.state in ['sent', 'to approve', 'purchase']:
            return {
                'name': _('Cancel Purchase Order'),
                'type': 'ir.actions.act_window',
                'res_model': 'purchase.cancel.reason',
                'view_mode': 'form',
                'target': 'new',
                'context': {
                    'default_purchase_id': self.id,
                }
            }
        return super(PurchaseOrder, self).button_cancel()
        
    @api.constrains('state', 'project_id', 'amount_total')
    def _check_project_validation(self):
        for order in self:
            # if order.state not in ('draft', 'sent', 'cancel') and not order.project_id:
            #     raise ValidationError(_('A project must be set for confirmed purchase orders.'))
            
            if order.project_id and order.amount_total:
                # Check if total exceeds project budget
                if order.amount_total > order.project_id.amount:
                    raise ValidationError(_(
                        'Insufficient budget for project "%(project)s"!\n'
                        'Project Budget: %(budget).2f\n'
                        'Total PO Amount : %(total).2f\n'
                        'Remaining Budget: %(remaining).2f'
                    ) % {
                        'project': order.project_id.name,
                        'budget': order.project_id.amount,
                        'total': order.amount_total,
                        'remaining': order.project_id.amount - order.amount_total
                    })

    # @api.constrains('order_line.price_unit', 'order_line.product_qty')
    # def _check_line_values(self):
    #     print("++++++++ Enter _check_line_values")
    #     for order in self:
    #         for line in order.order_line:
    #             if line.price_unit <= 0:
    #                 raise ValidationError(_("Product '%s' must have a price greater than 0.") % line.product_id.name)
    #             if line.product_qty <= 0:
    #                 raise ValidationError(_("Product '%s' must have a quantity greater than 0.") % line.product_id.name)

    @api.constrains('order_line')
    def _check_order_lines(self):
        for order in self:
            if order.state != 'draft':
                if not order.order_line:
                    raise ValidationError(_("You cannot submit an RFQ without any products. Please add at least one product."))
                
            for line in order.order_line:
                if line.price_unit <= 0:
                    raise ValidationError(_("Product '%s' must have a price greater than 0.") % line.product_id.name)
                if line.product_qty <= 0:
                    raise ValidationError(_("Product '%s' must have a quantity greater than 0.") % line.product_id.name)

    # @api.constrains('project_id')
    # def _check_project_budget(self):
    #     for order in self:
    #         if order.state == 'sent' and order.validator and not order.project_id:
    #             raise ValidationError(_("You cannot confirm this RFQ without setting a project. Please select a project first."))

    def action_submit_rfq(self):
        for order in self:
            # Check for products
            if not order.order_line:
                raise ValidationError(_("You cannot submit an RFQ without any products. Please add at least one product."))
            
            # Check for validator
            if not order.validator:
                raise ValidationError(_("This Purchase Order doesn't have any validator. Please add a department responsible for the PO."))
            
            # Create activity for validator
            order.activity_schedule(
                'mail.mail_activity_data_todo',
                summary=_("Review RFQ Submission"),
                note=_("Please review the RFQ submitted by %s") % order.user_id.name,
                user_id=order.validator.id
            )
            
            order.write({'state': 'sent'})
        return True
