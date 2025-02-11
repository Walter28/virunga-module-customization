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
    
    def _compute_get_is_user_cp(self):
        for po in self:
            po.is_user_cp = self.env.user.is_po_cp

    def _compute_get_is_user_hod(self):
        for po in self:
            po.is_user_hod = self.env.user.is_po_hod
    
    def get_current_user_department(self):
        if self.env.user.has_group('av_purchase.group_purchase_cp'):
            employee = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)], limit=1)
            return employee.department_id.id
                
    @api.depends('department_id', 'department_id.manager_id')
    def _compute_validator(self):
        """Compute the validator based on department manager"""
        for record in self:
            if record.department_id and record.department_id.manager_id:
                record.validator = record.department_id.manager_id.user_id
            else:
                record.validator = False

    @api.model_create_multi
    def create(self, vals_list):
        if self.env.user.has_group('av_purchase.group_purchase_cp'):
            employee = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)], limit=1)
            if not employee:
                raise UserError(_('CP users must be linked to an employee to create purchase orders.'))
        return super(PurchaseOrder, self).create(vals_list)

    def button_confirm(self):
        # if self.env.user.has_group('av_purchase.group_purchase_cp'):
        #     raise UserError(_('CP users are not allowed to confirm purchase orders.'))
        if not self.project_id:
            raise UserError(_('Please set a project before confirming the purchase order.'))
        return super(PurchaseOrder, self).button_confirm()

    def button_cancel(self):
        if self.env.user.has_group('av_purchase.group_purchase_cp') and self.state != 'draft':
            raise UserError(_("You don't have access to cancel this purchase order in its current state."))
        return super(PurchaseOrder, self).button_cancel()
        
    @api.constrains('state', 'project_id')
    def _check_project_required(self):
        for order in self:
            if order.state not in ('draft', 'sent', 'cancel') and not order.project_id:
                raise ValidationError(_('A project must be set for confirmed purchase orders.'))

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
        print("++++++++ Enter _check_order_lines")
        for order in self:
            if order.state != 'draft':
                if not order.order_line:
                    raise ValidationError(_("You cannot submit an RFQ without any products. Please add at least one product."))
                
            for line in order.order_line:
                if line.price_unit <= 0:
                    raise ValidationError(_("Product '%s' must have a price greater than 0.") % line.product_id.name)
                if line.product_qty <= 0:
                    raise ValidationError(_("Product '%s' must have a quantity greater than 0.") % line.product_id.name)

    # @api.constrains('project_id', 'state')
    # def _check_project_validation(self):
    #     for record in self:
    #         if record.state == 'sent' and record.validator and not record.project_id:
    #             raise ValidationError(_("You cannot confirm this RFQ without setting a project. Please select a project first."))

    def action_submit_rfq(self):
        for record in self:
            # Check for products
            if not record.order_line:
                raise ValidationError(_("You cannot submit an RFQ without any products. Please add at least one product."))
            
            # Check for validator
            if not record.validator:
                raise ValidationError(_("This Purchase Order doesn't have any validator. Please add a department responsible for the PO."))
            
            # Create activity for validator
            record.activity_schedule(
                'mail.mail_activity_data_todo',
                summary=_("Review RFQ Submission"),
                note=_("Please review the RFQ submitted by %s") % record.user_id.name,
                user_id=record.validator.id
            )
            
            record.write({'state': 'sent'})
        return True
