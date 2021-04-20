// Copyright (c) 2021, libracore and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Delivery Overview"] = {
    "filters": [
        {
            "fieldname":"to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.add_days(frappe.datetime.get_today(), +14),
            "width": "60px",
            "reqd": 1
        }
    ],
    "initial_depth": 0
};
