/** @odoo-module */

// Import required dependencies from Odoo web framework
import { registry } from "@web/core/registry";
import { formView } from "@web/views/form/form_view";
import { FormController } from "@web/views/form/form_controller";
import { useService } from "@web/core/utils/hooks";
import { useEffect } from "@odoo/owl";

/**
 * Custom Form Controller for Project Form View
 * Extends the base FormController to add custom behavior for project form editing
 */
class EditProjectFormController extends FormController {
    /**
     * Setup function initializes the controller
     * Called when the component is being set up
     */
    setup(){
        // Initialize user service for user-related operations
        this.user = useService("user")
        console.log("Project Form View Inherited!");
        console.log(this);
        super.setup();

        // Add effect hook to monitor stage_id changes and disable form accordingly
        useEffect(()=>{
            this.disableForm()
        }, ()=>[this.model.root.data.stage_id[1]])

        // Handler for notebook page changes to maintain form state
        this.onNotebookPageChange = (notebookId, page) => {
            this.disableForm()
        };
    }

    /**
     * Handles the form field disabling logic based on project stage
     * Makes form fields readonly when project is not in 'To Do' stage
     */
    async disableForm(){
        // Select all form input elements and field widgets
        const inputElts = document.querySelectorAll(".o_form_sheet input, .o_form_sheet select, .o_form_sheet textarea")
        const fieldWidgets = document.querySelectorAll(".o_form_sheet .o_field_widget")
        const stageField = document.querySelector(".o_field_widget[name='stage_id']")
        
        // Check if current stage is not 'To Do'
        const stateNotInToDo = this.model.root.data.stage_id[1] != "To Do"

        // If project is not in 'To Do' stage, disable all fields except stage_id
        if (stateNotInToDo) {
            // Disable all input elements except those in stage_id field
            if(inputElts) inputElts.forEach(e => {
                if (!e.closest('.o_field_widget[name="stage_id"]')) {
                    e.setAttribute("disabled", 1)
                }
            })
            // Add pointer-events-none class to all field widgets except stage_id
            if(fieldWidgets) fieldWidgets.forEach(e => {
                if (e.getAttribute("name") !== "stage_id") {
                    e.classList.add("pe-none")
                }
            })
            // Ensure stage field remains interactive
            if(stageField) {
                stageField.classList.remove("pe-none")
                stageField.querySelectorAll("input, select").forEach(e => e.removeAttribute("disabled"))
            }
            this.canEdit = true
        }
        // If project is in 'To Do' stage, enable all fields
        else {
            if(inputElts) inputElts.forEach(e => e.removeAttribute("disabled"))
            if(fieldWidgets) fieldWidgets.forEach(e => e.classList.remove("pe-none"))
            this.canEdit = true
        }
    }

    /**
     * Override beforeLeave method to handle form state before leaving
     * Allows leaving without confirmation if project is in draft state
     */
    async beforeLeave() {
        if (this.model.root.data.state == "draft") return
        super.beforeLeave()
    }

    /**
     * Override beforeUnload method to handle browser unload events
     * Allows unloading without confirmation if project is in draft state
     */
    async beforeUnload(ev) {
        if (this.model.root.data.state == "draft") return
        super.beforeUnload(ev)
    }
}

/**
 * Define the custom form view by extending the base form view
 * and using our custom controller
 */
const EditProjectFormView = {
    ...formView,
    Controller: EditProjectFormController,
}

// Register the custom form view in Odoo's view registry
registry.category("views").add("edit_project_form_disable", EditProjectFormView);
