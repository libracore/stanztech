# Copyright (c) 2020-2021, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from datetime import datetime
from erpnextswiss.erpnextswiss.doctype.label_printer.label_printer import create_pdf

def get_item_label_data(selected_items):
    sql_query = """SELECT
                       `tabItem`.`item_code` AS `item_code`,
                       `tabItem`.`item_name` AS `item_name`,
                       `tabItem`.`stock_uom` AS `stock_uom`,
                       `tabCustomer`.`customer_name` AS `customer_name`
                    FROM `tabItem`
                    LEFT JOIN `tabCustomer` ON `tabCustomer`.`name` = `tabItem`.`kunde`
                    WHERE `tabItem`.`name` IN ({selected_items});""".format(selected_items=selected_items)

    return frappe.db.sql(sql_query, as_dict=True)

def get_delivery_note_label_data(selected_delivery_notes):
    sql_query = """SELECT
                       `tabDelivery Note`.`customer_name` AS `customer_name`,
                       `tabDelivery Note`.`name` AS `delivery_note`
                    FROM `tabDelivery Note`
                    WHERE `tabDelivery Note`.`name` IN ({selected_delivery_notes});""".format(selected_delivery_notes=selected_delivery_notes)

    return frappe.db.sql(sql_query, as_dict=True)

def get_sales_order_label_data(selected_sales_orders):
    sql_query = """SELECT
                       `tabSales Order`.`customer_name` AS `customer_name`,
                       `tabSales Order`.`name` AS `sales_order`
                    FROM `tabSales Order`
                    WHERE `tabSales Order`.`name` IN ({selected_sales_orders});""".format(selected_sales_orders=selected_sales_orders)

    return frappe.db.sql(sql_query, as_dict=True)
    
@frappe.whitelist()
def get_item_label(selected_items):
    # get label printer
    settings = frappe.get_doc("Stanztech Settings", "Stanztech Settings")
    if not settings.label_printer:
        frappe.throw( _("Please define a label printer under Stanztech Settings.") )
    # get raw data
    data = { 
        'items': get_item_label_data(selected_items),
        'date': datetime.today().strftime('%d.%m.%Y')
    }
    # prepare content
    content = frappe.render_template('stanztech/templates/labels/item_label.html', data)
    label_printer = settings.label_printer
    # create pdf
    printer = frappe.get_doc("Label Printer", label_printer)
    pdf = create_pdf(printer, content)
    # return download
    frappe.local.response.filename = "{name}.pdf".format(name=data['items'][0]['item_code'].replace(" ", "-").replace("/", "-"))
    frappe.local.response.filecontent = pdf
    frappe.local.response.type = "download"

@frappe.whitelist()
def get_delivery_note_label(selected_delivery_notes):
    # get label printer
    settings = frappe.get_doc("Stanztech Settings", "Stanztech Settings")
    if not settings.label_printer:
        frappe.throw( _("Please define a label printer under Stanztech Settings.") )
    label_printer = settings.label_printer
    # get raw data
    data = { 
        'delivery_notes': get_delivery_note_label_data(selected_delivery_notes),
        'date': datetime.today().strftime('%d.%m.%Y'),
        'details': [],
        'detail_count': 0
    }
    # enrich item data
    ref = None
    for dn in data['delivery_notes']:
        dn_doc = frappe.get_doc("Delivery Note", dn['delivery_note'])
        if dn_doc.items[0].against_sales_order:
            so = frappe.get_doc("Sales Order", dn_doc.items[0].against_sales_order)
            ref = so.po_no
        dn_dict = dn_doc.as_dict()
        dn_dict['po_no'] = ref
        data['details'].append(dn_dict)
        for i in dn_doc.items:
            data['detail_count'] += 1
    # prepare content
    content = frappe.render_template('stanztech/templates/labels/delivery_note_label.html', data)
    # create pdf
    printer = frappe.get_doc("Label Printer", label_printer)
    pdf = create_pdf(printer, content)
    # return download
    frappe.local.response.filename = "{name}.pdf".format(name=data['delivery_notes'][0]['delivery_note'].replace(" ", "-").replace("/", "-"))
    frappe.local.response.filecontent = pdf
    frappe.local.response.type = "download"

@frappe.whitelist()
def get_sales_order_label(selected_sales_orders):
    # get label printer
    settings = frappe.get_doc("Stanztech Settings", "Stanztech Settings")
    if not settings.label_printer:
        frappe.throw( _("Please define a label printer under Stanztech Settings.") )
    label_printer = settings.label_printer
    # get raw data
    data = { 
        'delivery_notes': get_sales_order_label_data(selected_sales_orders),
        'date': datetime.today().strftime('%d.%m.%Y'),
        'details': [],
        'detail_count': 0
    }
    # enrich item data
    ref = None
    for dn in data['delivery_notes']:
        dn_doc = frappe.get_doc("Sales Order", dn['sales_order'])
        dn_dict = dn_doc.as_dict()
        data['details'].append(dn_dict)
        for i in dn_doc.items:
            data['detail_count'] += 1
    # prepare content
    content = frappe.render_template('stanztech/templates/labels/delivery_note_label.html', data)
    # create pdf
    printer = frappe.get_doc("Label Printer", label_printer)
    pdf = create_pdf(printer, content)
    # return download
    frappe.local.response.filename = "{name}.pdf".format(name=data['delivery_notes'][0]['sales_order'].replace(" ", "-").replace("/", "-"))
    frappe.local.response.filecontent = pdf
    frappe.local.response.type = "download"
