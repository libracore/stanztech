from __future__ import unicode_literals
from frappe import _

def get_data():
    return[
        {
            "label": _("Stammdaten"),
            "icon": "fa fa-money",
            "items": [
                   {
                       "type": "doctype",
                       "name": "Item",
                       "label": _("Item"),
                       "description": _("Item")
                   },
                   {
                       "type": "doctype",
                       "name": "BOM",
                       "label": _("BOM"),
                       "description": _("BOM")
                   },
                   {
                       "type": "doctype",
                       "name": "Production Step Type",
                       "label": _("Production Step Type"),
                       "description": _("Production Step Type")
                   },
                   {
                       "type": "doctype",
                       "name": "Stanztech Settings",
                       "label": _("Stanztech Settings"),
                       "description": _("Stanztech Settings")
                   }
            ]
        },
        {
            "label": _("Auftragsbearbeitung"),
            "icon": "fa fa-bank",
            "items": [
                   {
                       "type": "doctype",
                       "name": "Customer",
                       "label": _("Customer"),
                       "description": _("Customer")                   
                   },
                   {
                       "type": "doctype",
                       "name": "Quotation",
                       "label": _("Quotation"),
                       "description": _("Quotation")                   
                   },
                   {
                       "type": "doctype",
                       "name": "Sales Order",
                       "label": _("Sales Order"),
                       "description": _("Sales Order")                   
                   },
                   {
                       "type": "doctype",
                       "name": "Delivery Note",
                       "label": _("Delivery Note"),
                       "description": _("Delivery Note")                   
                   },
                   {
                       "type": "doctype",
                       "name": "Sales Invoice",
                       "label": _("Sales Invoice"),
                       "description": _("Sales Invoice")                   
                   },
                   {
                       "type": "report",
                       "doctype": "Sales Order",
                       "name": "Delivery Overview",
                       "label": _("Delivery Overview"),
                       "description": _("Delivery Overview"),
                       "is_query_report": True
                   },
                   {
                       "type": "report",
                       "doctype": "Sales Order",
                       "name": "Delivery Positions",
                       "label": _("Delivery Positions"),
                       "description": _("Delivery Positions"),
                       "is_query_report": True
                   }
            ]
        },
        {
            "label": _("Fertigung"),
            "icon": "fa fa-users",
            "items": [
                   {
                       "type": "page",
                       "name": "production_control",
                       "label": _("Production Control"),
                       "description": _("Production Control")
                   },
                   {
                       "type": "doctype",
                       "name": "Work Order",
                       "label": _("Work Order"),
                       "description": _("Work Order")
                   },
                   {
                       "type": "doctype",
                       "name": "Project",
                       "label": _("Project"),
                       "description": _("Project")
                   },
                   {
                       "type": "doctype",
                       "name": "Timesheet",
                       "label": _("Timesheet"),
                       "description": _("Timesheet")
                   }
            ]
        },
        {
            "label": _("Einkauf"),
            "icon": "octicon octicon-file-submodule",
            "items": [
                   {
                       "type": "doctype",
                       "name": "Supplier",
                       "label": _("Supplier"),
                       "description": _("Supplier")                   
                   },
                   {
                       "type": "doctype",
                       "name": "Request for Quotation",
                       "label": _("Request for Quotation"),
                       "description": _("Request for Quotation")                   
                   },
                   {
                       "type": "doctype",
                       "name": "Supplier Quotation",
                       "label": _("Supplier Quotation"),
                       "description": _("Supplier Quotation")                   
                   },
                   {
                       "type": "doctype",
                       "name": "Purchase Order",
                       "label": _("Purchase Order"),
                       "description": _("Purchase Order")                   
                   },
                   {
                       "type": "doctype",
                       "name": "Purchase Receipt",
                       "label": _("Purchase Receipt"),
                       "description": _("Purchase Receipt")                   
                   },
                   {
                       "type": "doctype",
                       "name": "Purchase Invoice",
                       "label": _("Purchase Invoice"),
                       "description": _("Purchase Invoice")                   
                   },
                   {
                       "type": "report",
                       "doctype": "Bin",
                       "name": "Engpassmenge",
                       "label": _("Engpassmenge"),
                       "description": _("Engpassmenge"),
                       "is_query_report": True
                   },
                   {
                       "type": "doctype",
                       "name": "Stock Entry",
                       "label": _("Stock Entry"),
                       "description": _("Stock Entry")                   
                   }             
            ]
        },
        {
            "label": _("Buchhaltung"),
            "icon": "fa fa-bank",
            "items": [
                   {
                       "type": "page",
                       "name": "bank_wizard",
                       "label": _("Bank Wizard"),
                       "description": _("Bank Wizard")
                   },
                   {
                       "type": "doctype",
                       "name": "Payment Proposal",
                       "label": _("Payment Proposal"),
                       "description": _("Payment Proposal")
                   },
                   {
                       "type": "doctype",
                       "name": "Payment Reminder",
                       "label": _("Payment Reminder"),
                       "description": _("Payment Reminder")
                   },
                   {
                        "type": "report",
                        "name": "General Ledger",
                        "label": _("General Ledger"),
                        "doctype": "GL Entry",
                        "is_query_report": True
                    },
                    {
                        "type": "report",
                        "name": "Profit and Loss Statement",
                        "label": _("Profit and Loss Statement"),
                        "doctype": "GL Entry",
                        "is_query_report": True
                    },
                    {
                        "type": "report",
                        "name": "Balance Sheet",
                        "label": _("Balance Sheet"),
                        "doctype": "GL Entry",
                        "is_query_report": True
                    },
                    {
                        "type": "report",
                        "name": "DATEV",
                        "label": _("DATEV"),
                        "doctype": "GL Entry",
                        "is_query_report": True
                    }
            ]
        },
        {
            "label": _("Auswertungen"),
            "icon": "fa fa-users",
            "items": [
                    {
                        "type": "report",
                        "name": "Daily Activity Log",
                        "label": _("Daily Activity Log"),
                        "doctype": "Work Order",
                        "is_query_report": True
                    }
            ]
        }
    ]
