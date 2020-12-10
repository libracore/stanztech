frappe.pages['production_control'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Production Control',
        single_column: true
    });
    
    frappe.production_control.make(page);
    frappe.production_control.run();
    
    // add the application reference
    frappe.breadcrumbs.add("Stanztech");
}

frappe.production_control = {
    start: 0,
    make: function(page) {
        var me = frappe.production_control;
        me.page = page;
        me.body = $('<div></div>').appendTo(me.page.main);
        var data = "";
        $(frappe.render_template('production_control', data)).appendTo(me.body);
        
        /* // attach button handlers
        this.page.main.find(".btn-create-file").on('click', function() {
            frappe.abacus_export.create_transfer_file();
        });
        
        // add menu button
        this.page.add_menu_item(__("Reset export flags"), function() {
            frappe.abacus_export.reset_export_flags();
        }); */

    },
    run: function() {
        /* // set beginning of the year as start and today as current date
        var today = new Date();
        var dd = today.getDate();
        if (dd < 10) { dd = "0" + dd; }
        var mm = today.getMonth() + 1;     //January is 0!
        if (mm < 10) { mm = "0" + mm; }
        var yyyy = today.getFullYear();
        var input_start = document.getElementById("start_date");
        input_start.value = yyyy + "-01-01";
        var input_end = document.getElementById("end_date");
        input_end.value = yyyy + "-" + mm + "-" + dd;
        
        // attach change handlers
        input_start.onchange = function() { frappe.abacus_export.update_preview(); };
        input_end.onchange = function() { frappe.abacus_export.update_preview(); }; */
        
        // add on enter listener to QR code box
        document.getElementById("work_order").addEventListener("keyup", function(event) {
            event.preventDefault();
            if (event.keyCode === 13) {
                frappe.production_control.get_work_order(this.value);
            }
        });
    },
    get_work_order: function (work_order) {
        frappe.call({
            method: 'stanztech.stanztech.page.production_control.production_control.get_work_order',
            args: {'work_order': work_order },
            callback: function(r) {
                var wo = r.message;
                console.log(wo);
                frappe.production_control.display_work_order(wo);
            }
        });
    },
    display_work_order: function (work_order) {
        var html = frappe.render_template('work_order_details', work_order)
        document.getElementById("work_order_view").innerHTML = html;
    }
}

function clear_qr() {
    document.getElementById("work_order").value = "";
}
