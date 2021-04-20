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
    },
    before_update_after_submit(frm) {
        calculate_machine_minutes(frm);
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
    
function calculate_machine_minutes(frm) {
    // calculate total machine minutes
    var machine_minutes = 0;
    if (frm.doc.production_log) {
        for (var i = 0; i < frm.doc.production_log.length; i++) {
            if ((frm.doc.production_log[i].end) && (frm.doc.production_log[i].start)) {
                var duration = (new Date(frm.doc.nutzungen[i].end) - new Date(frm.doc.nutzungen[i].start)) / 60000;
                frappe.model.set_value(frm.doc.nutzungen[i].doctype, frm.doc.nutzungen[i].name, 'duration', duration);
            }
            machine_minutes += frm.doc.nutzungen[i].maschinenstunden;
        }
    }
    cur_frm.set_value('total_time', machine_minutes);
}
