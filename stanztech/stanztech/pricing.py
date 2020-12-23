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

@frappe.whitelist()
def fetch_item_pricing(item_code):

    prices = {'buying': [], 'selling': []}
    
    # find buying item price
    sql_query = """SELECT `tabSupplier Quotation Item`.`qty`, 
                          `tabSupplier Quotation Item`.`rate`, 
                          `tabSupplier Quotation Item`.`uom`,
                          `tabSupplier Quotation`.`currency`,
                          `tabSupplier Quotation`.`name`,
                          `tabSupplier Quotation`.`transaction_date` AS `date`
                   FROM `tabSupplier Quotation Item`
                   LEFT JOIN `tabSupplier Quotation` ON `tabSupplier Quotation Item`.`parent` = `tabSupplier Quotation`.`name`
                   WHERE `tabSupplier Quotation Item`.`item_code` = '{item_code}'
                     AND `tabSupplier Quotation`.`docstatus` = 1
                   ORDER BY `tabSupplier Quotation`.`transaction_date` DESC, `tabSupplier Quotation Item`.`qty` ASC
                   LIMIT 5;""".format(item_code=item_code)
    rates = frappe.db.sql(sql_query, as_dict=True)
    if len(rates) > 0:
        for rate in rates:
            prices['buying'].append({
                'qty': rate['qty'],
                'rate': rate['rate'],
                'cdt': 'Supplier Quotation',
                'cdn': rate['name'],
                'date': rate['date'],
                'uom': rate['uom'],
                'currency': rate['currency']
            })
    else:
        # fallback to purchase orders
        sql_query = """SELECT `tabPurchase Order Item`.`qty`, 
                          `tabPurchase Order Item`.`rate`, 
                          `tabPurchase Order Item`.`uom`, 
                          `tabPurchase Order`.`currency`,
                          `tabPurchase Order`.`name`,
                          `tabPurchase Order`.`transaction_date` AS `date`
                   FROM `tabPurchase Order Item`
                   LEFT JOIN `tabPurchase Order` ON `tabPurchase Order Item`.`parent` = `tabPurchase Order`.`name`
                   WHERE `tabPurchase Order Item`.`item_code` = '{item_code}'
                     AND `tabPurchase Order`.`docstatus` = 1
                   ORDER BY `tabPurchase Order`.`transaction_date` DESC, `tabPurchase Order Item`.`qty` ASC
                   LIMIT 5;""".format(item_code=item_code)
        rates = frappe.db.sql(sql_query, as_dict=True)
        if len(rates) > 0:
            for rate in rates:
                prices['buying'].append({
                    'qty': rate['qty'],
                    'rate': rate['rate'],
                    'cdt': 'Purchase Order',
                    'cdn': rate['name'],
                    'date': rate['date'],
                    'uom': rate['uom'],
                    'currency': rate['currency']
                    })
        else:
            # fallback to purchase invoices
            sql_query = """SELECT `tabPurchase Invoice Item`.`qty`, 
                              `tabPurchase Invoice Item`.`rate`, 
                              `tabPurchase Invoice Item`.`uom`, 
                              `tabPurchase Invoice`.`currency`,
                              `tabPurchase Invoice`.`name`,
                              `tabPurchase Invoice`.`posting_date` AS `date`
                       FROM `tabPurchase Invoice Item`
                       LEFT JOIN `tabPurchase Invoice` ON `tabPurchase Invoice Item`.`parent` = `tabPurchase Invoice`.`name`
                       WHERE `tabPurchase Invoice Item`.`item_code` = '{item_code}'
                         AND `tabPurchase Invoice`.`docstatus` = 1
                       ORDER BY `tabPurchase Invoice`.`posting_date` DESC, `tabPurchase Invoice Item`.`qty` ASC
                       LIMIT 5;""".format(item_code=item_code)
            rates = frappe.db.sql(sql_query, as_dict=True)
            if len(rates) > 0:
                for rate in rates:
                    prices['buying'].append({
                        'qty': rate['qty'],
                        'rate': rate['rate'],
                        'cdt': 'Purchase Invoice',
                        'cdn': rate['name'],
                        'date': rate['date'],
                        'uom': rate['uom'],
                        'currency': rate['currency']
                    })
    
    # collect selling prices
    sql_query = """SELECT `tabItem Price`.`min_qty` AS `qty`, 
                          `tabItem Price`.`price_list_rate` AS `rate`, 
                          `tabItem Price`.`name`,
                          IFNULL(`tabItem Price`.`uom`, `tabItem`.`stock_uom`) AS `uom`,
                          `tabItem Price`.`currency`,
                          `tabItem Price`.`valid_from` AS `date`
                       FROM `tabItem Price`
                       LEFT JOIN `tabItem` ON `tabItem`.`name` = `tabItem Price`.`item_code`
                       WHERE `tabItem Price`.`item_code` = '{item_code}'
                         AND `tabItem Price`.`selling` = 1
                       LIMIT 1;""".format(item_code=item_code)
    rates = frappe.db.sql(sql_query, as_dict=True)
    if len(rates) > 0:
        for rate in rates:
            prices['selling'].append({
                'qty': rate['qty'],
                'rate': rate['rate'],
                'cdt': 'Item Price',
                'cdn': rate['name'],
                'date': rate['date'],
                'uom': rate['uom'],
                'currency': rate['currency']
            })
            
    sql_query = """SELECT `tabPricing Rule`.`min_qty` AS `qty`, 
                          `tabPricing Rule`.`rate` AS `rate`, 
                          `tabPricing Rule`.`name`,
                          IFNULL(`tabPricing Rule Item Code`.`uom`, `tabItem`.`stock_uom`) AS `uom`,
                          `tabPricing Rule`.`currency`,
                          `tabPricing Rule`.`valid_from` AS `date`
                       FROM `tabPricing Rule Item Code`
                       LEFT JOIN `tabPricing Rule` ON `tabPricing Rule Item Code`.`parent` = `tabPricing Rule`.`name`
                       LEFT JOIN `tabItem` ON `tabItem`.`name` = `tabPricing Rule Item Code`.`item_code`
                       WHERE `tabPricing Rule Item Code`.`item_code` = '{item_code}'
                         AND `tabPricing Rule`.`selling` = 1
                         AND `tabPricing Rule`.`disable` = 0
                       ORDER BY `tabPricing Rule`.`priority` DESC, `tabPricing Rule`.`min_qty` ASC
                       LIMIT 5;""".format(item_code=item_code)
    rates = frappe.db.sql(sql_query, as_dict=True)
    if len(rates) > 0:
        for rate in rates:
            prices['selling'].append({
                'qty': rate['qty'],
                'rate': rate['rate'],
                'cdt': 'Pricing Rule',
                'cdn': rate['name'],
                'date': rate['date'],
                'uom': rate['uom'],
                'currency': rate['currency']
            })
    
    sql_query = """SELECT `tabSales Order Item`.`qty`, 
                          `tabSales Order Item`.`rate`, 
                          `tabSales Order Item`.`uom`, 
                          `tabSales Order`.`currency`,
                          `tabSales Order`.`name`,
                          `tabSales Order`.`transaction_date` AS `date`
                   FROM `tabSales Order Item`
                   LEFT JOIN `tabSales Order` ON `tabSales Order Item`.`parent` = `tabSales Order`.`name`
                   WHERE `tabSales Order Item`.`item_code` = '{item_code}'
                     AND `tabSales Order`.`docstatus` = 1
                   ORDER BY `tabSales Order`.`transaction_date` DESC, `tabSales Order Item`.`qty` ASC
                   LIMIT 5;""".format(item_code=item_code)
    rates = frappe.db.sql(sql_query, as_dict=True)
    if len(rates) > 0:
        for rate in rates:
            prices['selling'].append({
                'qty': rate['qty'],
                'rate': rate['rate'],
                'cdt': 'Sales Order',
                'cdn': rate['name'],
                'date': rate['date'],
                'uom': rate['uom'],
                'currency': rate['currency']
            })
    return prices
