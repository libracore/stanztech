# Copyright (c) 2021-2022, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
import ast
#from datetime import datetime, timedelta, combine
import datetime
from frappe.utils import cint, get_url_to_form

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"label": _("SO Item Date"), "fieldname": "so_item_date", "fieldtype": "Date", "width": 80},
        {"label": _("Item"), "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 130},
        {"label": _("Description"), "fieldname": "description", "fieldtype": "Text Editor", "width": 200},
        #{"label": _("Sales Order"), "fieldname": "sales_order", "fieldtype": "Link", "options": "Sales Order", "width": 120},
        #{"label": _("Customer"), "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 40},        
        {"label": _("Customer name"), "fieldname": "customer_name", "fieldtype": "Data", "width": 200},
        #{"label": _("SO Date"), "fieldname": "so_date", "fieldtype": "Date", "width": 80},
        #{"label": _("SO Delivery"), "fieldname": "so_delivery", "fieldtype": "Date", "width": 80},
        {"label": _("Reference"), "fieldname": "reference", "fieldtype": "Data", "width": 100},
        #{"label": _("Purchase"), "fieldname": "is_purchase_item", "fieldtype": "Check", "width": 20},
        {"label": _(""), "fieldname": "indicator_purchase", "fieldtype": "Data", "width": 20},
        #{"label": _("Purchase Order"), "fieldname": "purchase_order", "fieldtype": "Link", "options": "Purchase Order", "width": 130},
        {"label": _("Purchase Receipt"), "fieldname": "purchase_receipt", "fieldtype": "Link", "options": "Purchase Receipt", "width": 130},
        {"label": _("Order Confirmation No"), "fieldname": "order_confirmation_no", "fieldtype": "Data", "width": 150},
        {"label": _(""), "fieldname": "indicator_delivery", "fieldtype": "Data", "width": 20},
        {"label": _("Reqd By Date"), "fieldname": "po_item_date", "fieldtype": "Date", "width": 80},
        {"label": _("Qty"), "fieldname": "qty", "fieldtype": "Float", "width": 80},
        {"label": _("Qty delivered"), "fieldname": "qty_delivered", "fieldtype": "Float",  "width": 80},
        #{"label": _("Done"), "fieldname": "done", "fieldtype": "Check",  "width": 30},
        {"label": _("Status"), "fieldname": "status", "fieldtype": "Data",  "width": 120},
        {"label": _("Information"), "fieldname": "information", "fieldtype": "Data",  "width": 450}
    ]

def get_data(filters):
    if type(filters) is str:
        filters = ast.literal_eval(filters)
    else:
        filters = dict(filters)
    
    conditions = ""
    if 'from_date' in filters:
        conditions += " AND `tabSales Order`.`delivery_date` >= '{from_date}' ".format(from_date=filters['from_date'])
    
    if 'order_type' in filters:
        if filters.get('order_type') == "externe":
            conditions += " AND `tabPurchase Order`.`order_confirmation_no` IS NOT NULL "
        elif filters.get('order_type') == "interne":
            conditions += " AND `tabPurchase Order`.`order_confirmation_no` IS NULL "
            
    # prepare query
    sql_query = """SELECT
          `tabSales Order`.`name` AS `sales_order`,
          `tabSales Order`.`customer` AS `customer`,
          `tabSales Order`.`customer_name` AS `customer_name`,
          `tabSales Order`.`po_no` AS `reference`,
          `tabSales Order`.`transaction_date` AS `so_date`,
          `tabSales Order`.`delivery_date` AS `so_delivery`,
          `tabItem`.`is_purchase_item` AS `is_purchase_item`,
          `tabItem`.`description` AS `description`,
          `tabSales Order Item`.`item_code` AS `item_code`,
          `tabPurchase Order Item`.`parent` AS `purchase_order`,
          (SELECT `tabPurchase Receipt Item`.`parent`
           FROM `tabPurchase Receipt Item`
           WHERE `tabPurchase Receipt Item`.`purchase_order` = `tabPurchase Order Item`.`parent`
           LIMIT 1) AS `purchase_receipt`,
          `tabSales Order Item`.`delivery_date` AS `so_item_date`,
          `tabPurchase Order Item`.`schedule_date` AS `po_item_date`,
          `tabSales Order Item`.`qty` AS `qty`,
          `tabSales Order Item`.`delivered_qty` AS `qty_delivered`,
          `tabSales Order`.`information` AS `information`,
          `tabPurchase Order`.`order_confirmation_no` AS `order_confirmation_no`,
          (SELECT `tabWork Order`.`status`
           FROM `tabWork Order`
           WHERE `tabWork Order`.`sales_order` = `tabSales Order`.`name`
             AND `tabWork Order`.`production_item` = `tabSales Order Item`.`item_code`
             AND `tabWork Order`.`docstatus` < 2
           LIMIT 1) AS `work_order_status`,
          (SELECT `tabProject`.`status`
           FROM `tabProject`
           WHERE tabProject.`sales_order` = `tabSales Order`.`name`
           LIMIT 1) AS `project_status`
        FROM `tabSales Order Item`
        LEFT JOIN `tabSales Order` ON `tabSales Order`.`name` = `tabSales Order Item`.`parent`
        LEFT JOIN `tabItem` ON `tabItem`.`item_code` = `tabSales Order Item`.`item_code` 
        LEFT JOIN `tabPurchase Order Item` ON `tabPurchase Order Item`.`sales_order_item` = `tabSales Order Item`.`name`
        LEFT JOIN `tabPurchase Order` ON `tabPurchase Order`.`name` = `tabPurchase Order Item`.`parent`
        WHERE `tabSales Order Item`.`delivery_date` <= '{to_date}'
          AND `tabSales Order`.`docstatus` = 1
          AND `tabSales Order`.`delivery_status` IN ("Not Delivered", "Partly Delivered")
          AND `tabSales Order`.`status` NOT IN ("Closed", "Completed")
          AND (`tabSales Order Item`.`qty` - `tabSales Order Item`.`delivered_qty`) > 0
          {conditions}
        ORDER BY `tabSales Order Item`.`delivery_date` ASC, `tabSales Order`.`name` ASC;
      """.format(to_date=filters['to_date'], conditions=conditions)
    
    data = frappe.db.sql(sql_query, as_dict=True)
    
    now_ts = get_timestamp(datetime.datetime.now().date())
    for d in data:
        # purchase indicator
        if not d['purchase_order']:
            d['indicator_purchase'] = "<span style=\"color: silver; \">&#x2b24;</span>"
        elif d['purchase_order'] and d['purchase_receipt']:
            d['indicator_purchase'] = "<span style=\"color: green; \">&#x2b24;</span>"
        else:
            d['indicator_purchase'] = "<span style=\"color: red; \">&#x2b24;</span>"
        
        # delivery indicator
        if d['so_item_date']:
            ts = get_timestamp(d['so_item_date'])
            if (ts - now_ts) > (3 * 24 * 60 * 60):
                d['indicator_delivery'] = "<span style=\"color: green; \">&#x2b24;</span>"
            elif ts > now_ts:
                d['indicator_delivery'] = "<span style=\"color: yellow; \">&#x2b24;</span>"
            else:
                d['indicator_delivery'] = "<span style=\"color: red; \">&#x2b24;</span>"
        else:
            d['indicator_delivery'] = "<span style=\"color: silver; \">&#x2b24;</span>"
            
        # rewrite reference as link to sales order
        if d['sales_order']:
            d['reference'] = "<a href=\"{0}\">{1}</a>".format(get_url_to_form("Sales Order", d['sales_order']), d['reference'])
        
        # rewrite order confirmation number to purchase order
        if d['purchase_order']:
            d['order_confirmation_no'] = "<a href=\"{0}\">{1}</a>".format(get_url_to_form("Purchase Order", d['purchase_order']), d['order_confirmation_no'])
        
        # consolidate status
        d['status'] = d['work_order_status'] or d['project_status']
        if d['status'] in ["Completed", "Closed"]:
            d['status'] = "<span style=\"color: green; \">&#x2b24;</span> {0}".format(d['status'])
        elif d['status'] in ["Not Started", "In Process", "Open"]:
            d['status'] = "<span style=\"color: yellow; \">&#x2b24;</span> {0}".format(d['status'])
        else:
            d['status'] = "<span style=\"color: silver; \">&#x2b24;</span> {0}".format(d['status'] or "")
            
    return data

def get_timestamp(d):
    if type(d) == str:
        d = datetime.datetme.strptime(date, "%Y-%m-%d")
    elif type(d) == datetime.date:
        d = datetime.datetime.combine(d, datetime.time(0))
        
    return datetime.datetime.timestamp(d)
