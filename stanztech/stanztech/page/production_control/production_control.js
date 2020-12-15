frappe.pages['production_control'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: __('Production Control'),
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
    },
    run: function() {       
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
                frappe.production_control.display_work_order(wo);
            }
        });
    },
    display_work_order: function (work_order) {
        var html = frappe.render_template('work_order_details', work_order)
        document.getElementById("work_order_view").innerHTML = html;
        // attach button handlers
        var btn_finish = document.getElementById("btn_finish");
        if (['Not Started', 'In Process'].indexOf(work_order.status) >= 0) {
            btn_finish.style.visibility = "visible";
        }
        btn_finish.onclick = function() {
            frappe.call({
                method: 'erpnext.manufacturing.doctype.work_order.work_order.make_stock_entry',
                args: {
                    'work_order_id': work_order.name,
                    'purpose': "Manufacture",
                    'qty': work_order.qty
                },
                callback: function(r) {
                    var stock_entry = r.message;
                    frappe.model.sync(stock_entry);
                    frappe.set_route('Form', stock_entry.doctype, stock_entry.name);
                }
            });
        };
        // go through steps
        var is_started = false;
        var is_completed = false;
        var cdn = null;
        for (var s = (work_order.production_steps.length - 1); s >= 0; s--) {
            is_completed = false;
            is_started = false;
            cdn = null;
            // go through logs
            for (var l = (work_order.production_log.length - 1); l >= 0; l--) {
                if (work_order.production_log[l].production_step_type === work_order.production_steps[s].production_step_type) {
                    if (work_order.production_log[l].completed === 1) {
                        document.getElementById("tick_complete_" + work_order.production_steps[s].name).style.visibility = "visible";
                        is_completed = true;
                        break;
                    }
                    if (work_order.production_log[l].end) {
                        is_started = false;
                        break;
                    } else if (work_order.production_log[l].start) {
                        is_started = true;
                        cdn = work_order.production_log[l].name;
                        break;
                    }
                }
            }
            if (is_started) {
                var btn_stop = document.getElementById("btn_stop_" + work_order.production_steps[s].name);
                btn_stop.style.visibility = "visible";
                btn_stop.onclick = frappe.production_control.stop_log.bind(this, work_order.name, cdn)

                var btn_complete = document.getElementById("btn_complete_" + work_order.production_steps[s].name);
                btn_complete.style.visibility = "visible";
                btn_complete.onclick = frappe.production_control.complete_log.bind(this, work_order.name, cdn);

            } else if (!is_completed) {
                var btn_start = document.getElementById("btn_start_" + work_order.production_steps[s].name);
                btn_start.style.visibility = "visible";
                btn_start.onclick = frappe.production_control.start_log.bind(this, work_order.name, work_order.production_steps[s].production_step_type);
            }
            var btn_remark = document.getElementById("btn_remark");
            btn_remark.onclick = frappe.production_control.remark.bind(this, work_order.name);

        }
    },
    start_log: function (work_order, production_step_type) {
        frappe.call({
            method: 'stanztech.stanztech.page.production_control.production_control.start_log',
            args: {
                'work_order': work_order,
                'production_step_type': production_step_type
            },
            callback: function(r) {
                frappe.production_control.get_work_order(work_order);
            }
        });
    },
    complete_log: function (work_order, cdn) {
        frappe.call({
            method: 'stanztech.stanztech.page.production_control.production_control.complete_log',
            args: {
                'work_order': work_order,
                'cdn': cdn
            },
            callback: function(r) {
                frappe.production_control.get_work_order(work_order);
            }
        });
    },
    stop_log: function (work_order, cdn) {
        frappe.call({
            method: 'stanztech.stanztech.page.production_control.production_control.end_log',
            args: {
                'work_order': work_order,
                'cdn': cdn
            },
            callback: function(r) {
                frappe.production_control.get_work_order(work_order);
            }
        });
    }
}

function clear_qr() {
    document.getElementById("work_order").value = "";
}
