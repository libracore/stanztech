# Copyright (c) 2019-2020, libracore and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from ast import literal_eval

""" This function will add a pricing rule """
@frappe.whitelist()
def add_pricing_rule(item, qty, rate):
    # check if this exists already
    sql_query = """SELECT DISTINCT(`tabPricing Rule`.`name`) AS `name`
                   FROM `tabPricing Rule Item Code` 
                   LEFT JOIN `tabPricing Rule` ON `tabPricing Rule`.`name` = `tabPricing Rule Item Code`.`parent`
                   WHERE `item_code` = '{item_code}' AND `min_qty` = {qty}
                   ORDER BY `tabPricing Rule`.`min_qty` ASC;""".format(item_code=item, qty=qty)
    matches = frappe.db.sql(sql_query, as_dict=True)
    if len(matches) > 0:
        frappe.throw( _("This pricing rule already exists: {0}").format(matches[0]['name']))
    # create pricing rule
    pr = frappe.get_doc({
        'doctype': 'Pricing Rule',
        'price_or_product_discount': 'Price',
        'apply_on': 'Item Code',
        'selling': 1,
        'min_qty': qty,
        'rate_or_discount': 'Rate',
        'rate': rate,
        'title': "Staffelpreis {qty} Stk ({item})".format(item=item, qty=qty)
    })
    pr.append('items', {
            'item_code': item
        })
    pr.insert()
    # set correct priorities for volume discounts
    sort_priorities(item)
    return pr

""" This function sets priorities to reflect qty (volume pricing) """
def sort_priorities(item):
    sql_query = """SELECT DISTINCT(`tabPricing Rule`.`name`) AS `name`
                   FROM `tabPricing Rule Item Code` 
                   LEFT JOIN `tabPricing Rule` ON `tabPricing Rule`.`name` = `tabPricing Rule Item Code`.`parent`
                   WHERE `item_code` = '{item_code}'
                   ORDER BY `tabPricing Rule`.`min_qty` ASC;""".format(item_code=item)
    matches = frappe.db.sql(sql_query, as_dict=True)
    
    priority = 1
    for match in matches:
        pr = frappe.get_doc("Pricing Rule", match['name'])
        pr.priority = "{0}".format(priority)
        pr.save()
        if priority < 20:
            priority += 1
    frappe.db.commit()
    return

""" This function fetches former prices used in sales orders """
@frappe.whitelist()
def fetch_former_prices(customer, items):
    if type(items) == str:
        items = literal_eval(items)
    former_prices = []
    for item in items:
        # check if item has been ordered before
        sql_query = """SELECT 
                         `tabSales Order Item`.`item_code` AS `item_code`, 
                         `tabSales Order Item`.`rate` AS `rate`, 
                         `tabSales Order Item`.`qty` AS `qty`,
                         `tabSales Order`.`transaction_date` AS `date`
                       FROM `tabSales Order Item` 
                       LEFT JOIN `tabSales Order` ON `tabSales Order`.`name` = `tabSales Order Item`.`parent`
                       WHERE `tabSales Order`.`docstatus` = 1
                         AND `tabSales Order Item`.`item_code` = '{item}'
                       ORDER BY `tabSales Order`.`transaction_date` DESC
                       LIMIT 1;""".format(item=item)
        former_info = frappe.db.sql(sql_query, as_dict=True)
        if len(former_info) > 0:
            former_prices.append({
                'item_code': item,
                'qty': former_info[0]['qty'],
                'rate': former_info[0]['rate'],
                'date': former_info[0]['date']
            })
    return former_prices
