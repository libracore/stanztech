# Copyright (c) 2020-2021, libracore and contributors
# For license information, please see license.txt

import frappe
from frappe import _

@frappe.whitelist()
def get_external_details(item_code):
    item = frappe.get_doc("Item", item_code)
    return item.externe_bearbeitung or "-"
