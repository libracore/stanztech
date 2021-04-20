# Copyright (c) 2021, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
import ast
from datetime import datetime, timedelta
from frappe.utils import cint

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"label": _("Sales Order"), "fieldname": "sales_order", "fieldtype": "Link", "options": "Sales Order", "width": 120},
        {"label": _("Customer"), "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 40},        
        {"label": _("Customer name"), "fieldname": "customer_name", "fieldtype": "Data", "width": 150},
        {"label": _("SO Date"), "fieldname": "so_date", "fieldtype": "Date", "width": 80},
        {"label": _("SO Delivery"), "fieldname": "so_delivery", "fieldtype": "Date", "width": 80},
        {"label": _("Reference"), "fieldname": "reference", "fieldtype": "Data", "width": 60},
        {"label": _("Purchase"), "fieldname": "is_purchase_item", "fieldtype": "Check", "width": 20},
        {"label": _("Item"), "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 80},
        {"label": _("Purchase Order"), "fieldname": "purchase_order", "fieldtype": "Link", "options": "Purchase Order", "width": 80},
        {"label": _("SO Item Date"), "fieldname": "so_item_date", "fieldtype": "Date", "width": 80},
        {"label": _("PO Item Date"), "fieldname": "po_item_date", "fieldtype": "Date", "width": 80},
        {"label": _("Qty"), "fieldname": "qty", "fieldtype": "Float", "width": 80},
        {"label": _("Qty delivered"), "fieldname": "qty_delivered", "fieldtype": "Float",  "width": 80},
        {"label": _("Done"), "fieldname": "done", "fieldtype": "Check",  "width": 30}
    ]

def get_data(filters):
    if type(filters) is str:
        filters = ast.literal_eval(filters)
    else:
        filters = dict(filters)
    
    # prepare query
    sql_query = """SELECT
          `tabSales Order`.`name` AS `sales_order`,
          `tabSales Order`.`customer` AS `customer`,
          `tabSales Order`.`customer_name` AS `customer_name`,
          `tabSales Order`.`po_no` AS `reference`,
          `tabSales Order`.`transaction_date` AS `so_date`,
          `tabSales Order`.`delivery_date` AS `so_delivery`,
          `tabItem`.`is_purchase_item` AS `is_purchase_item`,
          `tabSales Order Item`.`item_code` AS `item_code`,
          `tabPurchase Order Item`.`parent` AS `purchase_order`,
          `tabSales Order Item`.`delivery_date` AS `so_item_date`,
          `tabPurchase Order Item`.`schedule_date` AS `po_item_date`,
          `tabSales Order Item`.`qty` AS `qty`,
          `tabSales Order Item`.`delivered_qty` AS `qty_delivered`,
          IF ((`tabSales Order Item`.`qty` - `tabSales Order Item`.`delivered_qty`) <= 0, 1, 0) AS `done`
        FROM `tabSales Order Item`
        LEFT JOIN `tabSales Order` ON `tabSales Order`.`name` = `tabSales Order Item`.`parent`
        LEFT JOIN `tabItem` ON `tabItem`.`item_code` = `tabSales Order Item`.`item_code` 
        LEFT JOIN `tabPurchase Order Item` ON `tabPurchase Order Item`.`sales_order_item` = `tabSales Order Item`.`name`
        WHERE `tabSales Order`.`delivery_date` <= '{to_date}'
        ORDER BY `tabSales Order`.`delivery_date` ASC, `tabSales Order`.`name` ASC;
      """.format(to_date=filters['to_date'])
    
    data = frappe.db.sql(sql_query, as_dict=True)

    # compute indent
    previous_so = None
    row_idx = 0
    header_row_idx = 0
    for row in data:
        if row['sales_order'] == previous_so:
            row['indent'] = 1
        else:
            row['indent'] = 0
            header_row_idx = row_idx
        previous_so = row['sales_order']
        row_idx += 1
        
    return data
