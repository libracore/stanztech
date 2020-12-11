frappe.ui.form.on('Work Order', {
    bom_no(frm) {
        // fetch production steps
        if (frm.doc.docstatus === 0) {
            update_production_steps(frm)
        }
    },
    before_save(frm) {
        // fetch production steps
        if ((frm.doc.docstatus === 0) && (frm.doc.production_steps-length === 0)) {
            update_production_steps(frm)
        }
    }
});

function update_production_steps(frm) {
    frappe.call({
        "method": "frappe.client.get",
        "args": {
            "doctype": "BOM",
            "name": frm.doc.bom_no
        },
        "async": false,
        "callback": function(response) {
            var bom = response.message;

            if (bom) {
                // remove all rows
                var tbl = frm.doc.production_steps || [];
                var i = tbl.length;
                while (i--) {
                    cur_frm.get_field("production_steps").grid.grid_rows[i].remove();
                }
                cur_frm.refresh();
                // add rows
                bom.production_steps.forEach(function (step) {
                    var child = cur_frm.add_child('production_steps');
                    frappe.model.set_value(child.doctype, child.name, 'production_step_type', step.production_step_type);
                    frappe.model.set_value(child.doctype, child.name, 'remarks', step.remarks);
                });
                cur_frm.refresh_field('production_steps');
                // update item_name if missing
                if (!frm.doc.item_name) {
                    cur_frm.set_value("item_name", bom.item_name);
                }
            } else {
                frappe.msgprint("BOM not found");
            }
        }
    });
}
    
