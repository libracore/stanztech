frappe.ui.form.on('BOM', {
    button_insert_steps(frm) {
        insert_steps(frm);
    }
});

function insert_steps(frm) {
    // fetch available production steps
    frappe.call({
        'method': "frappe.client.get_list",
        'args': {
            'doctype': "Production Step Type",
            'fields': ["title"],
            'limit_page_length': 100
        },
        'callback': function(response) {
            var values = response.message;
            var fields = [];
            for (var i = 0; i < values.length; i++) {
                fields.push({'fieldname': 'c' + i, 'fieldtype': 'Check', 'label': values[i].title});
                if (i === 15) {
                    fields.push({'fieldname': 'column_' + i, 'fieldtype': 'Column Break'});
                }
            }
            frappe.prompt(
                fields,
                function(v){
                    // insert production steps
                    for (var j = 0; j < values.length; j++) {
                        if (v[('c' + j)] === 1) {
                            var child = cur_frm.add_child('production_steps');
                            frappe.model.set_value(child.doctype, child.name, 'production_step_type', values[j].title);
                        }
                    }
                    cur_frm.refresh_field('production_steps');
                },
                __('Insert Steps'),
                'OK'
            );
        }
    });
}
