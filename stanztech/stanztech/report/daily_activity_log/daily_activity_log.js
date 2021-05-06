// Copyright (c) 2021, libracore and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Daily Activity Log"] = {
    "filters": [
        {
            "fieldname":"from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.get_today(),
            "reqd": 1
        },
        {
            "fieldname":"to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.get_today(),
            "reqd": 1
        },
        {
            "fieldname":"employee",
            "label": __("Employee"),
            "fieldtype": "Link",
            "options": "Employee"
        },
        {
            "fieldname":"department",
            "label": __("Department"),
            "fieldtype": "Link",
            "options": "Department"
        },
        {
            "fieldname":"work_order",
            "label": __("Work Order"),
            "fieldtype": "Link",
            "options": "Work Order"
        }
    ]
};
