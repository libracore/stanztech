# Copyright (c) 2020-2023, libracore and contributors
# For license information, please see license.txt
#
# Get part transactions with 
# frappe.call({ 'method': 'stanztech.stanztech.utils.get_part_transactions', 'args': {'part': '2512173'}, 'callback': function(r) { console.log(r); }});
#

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
                   WHERE `tabSales Order`.`po_no` IN ('{refs}') AND `tabSales Order`.`docstatus` = 1;""".format(refs="', '".join(references))
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

@frappe.whitelist()
def get_part_transactions(part):
    sql_query = """
        SELECT
            `tabPurchase Order`.`transaction_date` AS `po_date`,
            `tabPurchase Order Item`.`parent` AS `purchase_order`,
            `tabPurchase Receipt Item`.`parent` AS `purchase_receipt`
        FROM `tabPurchase Order Item`
        LEFT JOIN `tabPurchase Receipt Item` ON 
            `tabPurchase Receipt Item`.`purchase_order` = `tabPurchase Order Item`.`parent`
            AND `tabPurchase Receipt Item`.`part` = `tabPurchase Order Item`.`part`
            AND `tabPurchase Receipt Item`.`docstatus` < 2
        LEFT JOIN `tabPurchase Order` ON `tabPurchase Order`.`name` = `tabPurchase Order Item`.`parent`
        WHERE 
            `tabPurchase Order Item`.`part` = "{part}"
            AND `tabPurchase Order Item`.`docstatus` < 2;
    """.format(part=part)
    
    transactions = frappe.db.sql(sql_query, as_dict=True)
    
    return transactions

def set_work_order_in_process(work_order):
    wo = frappe.get_doc("Work Order", work_order)
    if wo.production_log and len(wo.production_log) > 0 and wo.status == "Not Started":
        frappe.db.sql("""
            UPDATE `tabWork Order` 
            SET `status` = "In Process" 
            WHERE `name` = "{work_order}"; """.format(work_order=work_order))
        frappe.db.commit()
    return
