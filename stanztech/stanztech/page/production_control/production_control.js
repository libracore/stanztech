frappe.pages['production_control'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: __('Production Control'),
        single_column: true
    });
    console.log(wrapper);
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
                if (this.value.startsWith("MA-")) {
                    // this is an employee key
                    var employee = document.getElementById("employee");
                    employee.value = this.value;
                    this.value = "";
                    // reload work order if one is open
                    var work_order = document.getElementById("work_order_reference").value;
                    if (work_order) {
                        frappe.production_control.get_work_order(work_order);
                    }
                } else {
                    // open work order
                    frappe.production_control.get_work_order(this.value);
                    this.value = "";
                }
            }
        });
        // check for url parameters
        var url = location.href;
        if (url.indexOf("?work_order=") >= 0) {
            var work_order = url.split('=')[1].split('&')[0];
            document.getElementById("work_order").value = work_order;
            frappe.production_control.get_work_order(work_order);
        }
    },
    get_work_order: function (work_order) {
        document.getElementById("work_order_reference").value = work_order;
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
        var employee = document.getElementById("employee").value;
        for (var s = (work_order.production_steps.length - 1); s >= 0; s--) {
            is_completed = false;
            is_started = false;
            cdn = null;
            // go through logs backwards
            for (var l = (work_order.production_log.length - 1); l >= 0; l--) {
                if (work_order.production_log[l].production_step_type === work_order.production_steps[s].production_step_type) {
                    // this log entry is for the active activity
                    if ((work_order.production_log[l].end) && (work_order.production_log[l].employee === employee)) {
                        // this node has an end from this user
                    } else if ((work_order.production_log[l].start) && (work_order.production_log[l].employee === employee)) {
                        // this node is an open start line
                        is_started = true;
                        cdn = work_order.production_log[l].name;
                    } 
                    if ((work_order.production_log[l].completed === 1) && (!is_completed)) {
                        // this note is completed
                        document.getElementById("tick_complete_" + work_order.production_steps[s].name).style.visibility = "visible";
                        is_completed = true;
                    }
                }
            }
            if (work_order.docstatus < 2) {
                if (is_started) {
                    var btn_stop = document.getElementById("btn_stop_" + work_order.production_steps[s].name);
                    btn_stop.style.visibility = "visible";
                    btn_stop.onclick = frappe.production_control.stop_log.bind(this, work_order.name, cdn, employee)

                    var btn_complete = document.getElementById("btn_complete_" + work_order.production_steps[s].name);
                    btn_complete.style.visibility = "visible";
                    btn_complete.onclick = frappe.production_control.complete_log.bind(this, work_order.name, cdn, employee);

                } else if (!is_completed) {
                    // start button
                    var btn_start = document.getElementById("btn_start_" + work_order.production_steps[s].name);
                    btn_start.style.visibility = "visible";
                    btn_start.onclick = frappe.production_control.start_log.bind(this, work_order.name, work_order.production_steps[s].production_step_type, employee);
                    // checkout button
                    var btn_checkout = document.getElementById("btn_checkout_" + work_order.production_steps[s].name);
                    btn_checkout.style.visibility = "visible";
                    btn_checkout.onclick = frappe.production_control.checkout.bind(this, work_order.name, work_order.production_steps[s].production_step_type, employee);
                }
                var btn_remark = document.getElementById("btn_remark");
                btn_remark.onclick = frappe.production_control.remark.bind(this, work_order.name);
            }
        }
    },
    start_log: function (work_order, production_step_type, employee) {
        frappe.call({
            method: 'stanztech.stanztech.page.production_control.production_control.start_log',
            args: {
                'work_order': work_order,
                'production_step_type': production_step_type,
                'employee': employee
            },
            callback: function(r) {
                frappe.production_control.get_work_order(work_order);
            }
        });
    },
    complete_log: function (work_order, cdn, employee) {
        frappe.call({
            method: 'stanztech.stanztech.page.production_control.production_control.complete_log',
            args: {
                'work_order': work_order,
                'cdn': cdn,
                'employee': employee
            },
            callback: function(r) {
                frappe.production_control.get_work_order(work_order);
            }
        });
    },
    stop_log: function (work_order, cdn, employee) {
        frappe.call({
            method: 'stanztech.stanztech.page.production_control.production_control.end_log',
            args: {
                'work_order': work_order,
                'cdn': cdn,
                'employee': employee
            },
            callback: function(r) {
                frappe.production_control.get_work_order(work_order);
            }
        });
    },
    remark: function (work_order) {
        frappe.prompt([
            {'fieldname': 'remark', 'fieldtype': 'Data', 'label': __('Remark'), 'reqd': 1}  
        ],
        function(values){
            frappe.call({
                method: 'stanztech.stanztech.page.production_control.production_control.remark',
                args: {
                    'work_order': work_order,
                    'remark': values.remark
                },
                callback: function(r) {
                    frappe.show_alert( __("Updated") );
                }
            });
        },
        __('Add remark'),
        'OK'
        );
    },
    checkout: function (work_order, production_step_type, employee) {
        frappe.prompt([
            {'fieldname': 'duration', 'fieldtype': 'Int', 'label': __('Duration'), 'description': __("in minutes"), 'reqd': 1}  
        ],
        function(values){
            frappe.call({
                method: 'stanztech.stanztech.page.production_control.production_control.checkout',
                args: {
                    'work_order': work_order,
                    'duration': values.duration,
                    'production_step_type': production_step_type,
                    'employee': employee
                },
                callback: function(r) {
                    frappe.production_control.get_work_order(work_order);
                }
            });
        },
        __('Checkout'),
        'OK'
        );
    }
}

function clear_qr() {
    document.getElementById("work_order").value = "";
}
