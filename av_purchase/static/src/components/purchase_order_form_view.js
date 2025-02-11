/** @odoo-module */

// Import required dependencies from Odoo web framework
import { registry } from "@web/core/registry";
import { formView } from "@web/views/form/form_view";
import { FormController } from "@web/views/form/form_controller";
import { useService } from "@web/core/utils/hooks";
import { useEffect } from "@odoo/owl";

/**
 * Custom Form Controller for Purchase Order Form View
 * Extends the base FormController to implement custom behavior for purchase order editing
 * Manages field editability based on order state and user permissions
 */
class PurchaseOrderFormController extends FormController {
    /**
     * Setup function initializes the controller
     * Configures initial state and sets up event listeners
     */
    setup(){
        // Initialize user service for permission checking
        this.user = useService("user")
        console.log("Purchase Order Form View Inherited!");
        console.log(this);
        super.setup();

        // Add effect hook to monitor state changes and update form accordingly
        useEffect(()=>{
            this.disableForm()
        }, ()=>[this.model.root.data.state])

        // Handler for notebook page changes to maintain form state
        this.onNotebookPageChange = (notebookId, page) => {
            this.disableForm()
        };
    }

    /**
     * Controls form field editability based on:
     * - Purchase order state
     * - User permissions (CP user group)
     * - Special states like 'sent', 'purchase', 'done', 'cancel'
     */
    async disableForm(){
        // Select all form elements that need to be controlled
        const inputElts = document.querySelectorAll(".o_form_sheet input, .o_form_sheet select, .o_form_sheet textarea")
        const fieldWidgets = document.querySelectorAll(".o_form_sheet .o_field_widget")
        const projectField = document.querySelector(".o_field_widget[name='project_id']")
        
        // Determine current state and user permissions
        const stateNotInDraft = this.model.root.data.state != "draft"
        const isCpUser = await this.user.hasGroup("av_purchase.group_purchase_cp")
        const isInSentState = this.model.root.data.state === "sent"
        const otherImportantState = ["purchase", "done", "cancel"].includes(this.model.root.data.state)

        // Case 1: Order is in 'sent' state - only allow project_id editing
        if (isInSentState) {
            // Disable all input elements except those in project_id field
            if(inputElts) inputElts.forEach(e => {
                if (!e.closest('.o_field_widget[name="project_id"]')) {
                    e.setAttribute("disabled", 1)
                }
            })
            // Add pointer-events-none to all widgets except project_id
            if(fieldWidgets) fieldWidgets.forEach(e => {
                if (e.getAttribute("name") !== "project_id") {
                    e.classList.add("pe-none")
                }
            })
            // Ensure project field remains interactive
            if(projectField) {
                projectField.classList.remove("pe-none")
                projectField.querySelectorAll("input, select").forEach(e => e.removeAttribute("disabled"))
            }
            this.canEdit = true
        }
        // Case 2: CP users in non-draft state OR order in important states - disable all editing
        else if ((stateNotInDraft && isCpUser) || otherImportantState) {
            if(inputElts) inputElts.forEach(e => e.setAttribute("disabled", 1))
            if(fieldWidgets) fieldWidgets.forEach(e => e.classList.add("pe-none"))
            this.canEdit = false
        } 
        // Case 3: Default case - enable all fields
        else {
            if(inputElts) inputElts.forEach(e => e.removeAttribute("disabled"))
            if(fieldWidgets) fieldWidgets.forEach(e => e.classList.remove("pe-none"))
            this.canEdit = true
        }
    }

    /**
     * Override beforeLeave method to handle form state before navigation
     * Allows leaving without confirmation if purchase order is in draft state
     */
    async beforeLeave() {
        if (this.model.root.data.state == "draft") return
        super.beforeLeave()
    }

    /**
     * Override beforeUnload method to handle browser unload events
     * Allows unloading without confirmation if purchase order is in draft state
     */
    async beforeUnload(ev) {
        if (this.model.root.data.state == "draft") return
        super.beforeUnload(ev)
    }
}

/**
 * Define the custom purchase order form view
 * Extends the base form view with our custom controller
 */
const purchaseOrderFormView = {
    ...formView,
    Controller: PurchaseOrderFormController,
}

// Register the custom form view in Odoo's view registry
registry.category("views").add("purchase_order_form_disable", purchaseOrderFormView);
