// Copyright (c) 2022, libracore and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Delivery Positions"] = {
    "filters": [
        {
            "fieldname":"from_date",
            "label": __("From Date"),
            "fieldtype": "Date"
        },
        {
            "fieldname":"to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.add_days(frappe.datetime.get_today(), +14),
            "reqd": 1
        },
        {
            "fieldname":"order_type",
            "label": __("Typ"),
            "fieldtype": "Select",
            "options": "\nexterne\ninterne"
        }
    ],
    "onload": (report) => {
        if (!locals.double_click_handler) {
            locals.double_click_handler = true;
            
            // add event listener for double clicks
            cur_page.container.addEventListener("dblclick", function(event) {
                console.log(event);
                var row = event.delegatedTarget.getAttribute("data-row-index");
                var column = event.delegatedTarget.getAttribute("data-col-index");
                frappe.prompt([
                        {
                            'fieldname': 'information', 
                            'fieldtype': 'Data', 
                            'label': __('Information'), 
                            'default': frappe.query_report.data[row].information,
                            'reqd': 1
                        }  
                    ],
                    function(values){
                        frappe.call({
                            'method': 'frappe.client.set_value',
                            'args': {
                                'doctype': 'Sales Order',
                                'name': frappe.query_report.data[row].sales_order,
                                'fieldname': 'information',
                                'value': values.information
                            },
                            'callback': function() {
                                frappe.query_report.refresh();
                            }
                        });

                    },
                    'Information',
                    'OK'
                );
            });
        }
    }
};
