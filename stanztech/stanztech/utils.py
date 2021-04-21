# Copyright (c) 2020-2021, libracore and contributors
# For license information, please see license.txt

import frappe
from frappe import _
import json

@frappe.whitelist()
def get_external_details(item_code):
    item = frappe.get_doc("Item", item_code)
    return item.externe_bearbeitung or "-"

@frappe.whitelist()
def get_so_items_by_reference(reference_str):
    references = reference_str.split(",")
    sql_query = """SELECT `tabSales Order`.`name` AS `sales_order`,
                    `tabSales Order Item`.`item_code` AS `item_code`, 
                    `tabSales Order Item`.`name` AS `so_detail`
                   FROM `tabSales Order Item`
                   LEFT JOIN `tabSales Order` ON `tabSales Order`.`name` = `tabSales Order Item`.`parent`
                   WHERE `tabSales Order`.`po_no` IN ('{refs}');""".format(refs="', '".join(references))
    so_items = frappe.db.sql(sql_query, as_dict=True)
    return so_items

@frappe.whitelist()
def bulk_create_items(quickentry, item_group):
    if type(quickentry) is str:
        quickentry = json.loads(quickentry)
    else:
        quickentry = dict(quickentry)
        
    for i in quickentry:
        if not frappe.db.exists("Item", i['item_code']):
            new_item = frappe.get_doc({
                "doctype": "Item",
                "item_code": i['item_code'],
                "item_group": item_group
            })
            new_item.insert()
    frappe.db.commit()
    return
