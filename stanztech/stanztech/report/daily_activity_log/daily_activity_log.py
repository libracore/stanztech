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
        {"label": _("Start"), "fieldname": "start", "fieldtype": "Date", "width": 140},     
        {"label": _("End"), "fieldname": "end", "fieldtype": "Date", "width": 140},
        {"label": _("Duration"), "fieldname": "duration", "fieldtype": "Float", "precision": 2, "width": 80},
        {"label": _("Work Order"), "fieldname": "work_order", "fieldtype": "Link", "options": "Work Order", "width": 120},
        {"label": _("Production Step"), "fieldname": "production_step_type", "fieldtype": "Link", "options": "Production Step Type", "width": 120},
        {"label": _("Employee"), "fieldname": "employee", "fieldtype": "Link", "options": "Employee", "width": 80},
        {"label": _("Employee Name"), "fieldname": "employee_name", "fieldtype": "Data", "width": 120},
        {"label": _("Department"), "fieldname": "department", "fieldtype": "Link", "options": "Department", "width": 120},
        {"label": _("Completed"), "fieldname": "completed", "fieldtype": "Check", "width": 50}
    ]

def get_data(filters):
    if type(filters) is str:
        filters = ast.literal_eval(filters)
    else:
        filters = dict(filters)
    # get additional conditions
    conditions = ""
    if 'work_order' in filters and filters['work_order']:
        conditions += """ AND `tabWork Order`.`name` = "{0}" """.format(filters['work_order'])
    if 'employee' in filters and filters['employee']:
        conditions += """ AND `tabProduction Log`.`employee` = "{0}" """.format(filters['employee'])
    if 'department' in filters and filters['department']:
        conditions += """ AND `tabEmployee`.`department` = "{0}" """.format(filters['department'])
        
    # prepare query
    sql_query = """SELECT 
            `tabProduction Log`.`start` AS `start`,
            `tabProduction Log`.`end` AS `end`,
            `tabProduction Log`.`duration` AS `duration`,
            `tabProduction Log`.`employee` AS `employee`,
            `tabProduction Log`.`employee_name` AS `employee_name`,
            `tabProduction Log`.`completed` AS `completed`,
            `tabProduction Log`.`production_step_type` AS `production_step_type`,
            `tabWork Order`.`name` AS `work_order`,
            `tabEmployee`.`department` AS `department`
        FROM `tabProduction Log`
        LEFT JOIN `tabWork Order` ON `tabProduction Log`.`parent` = `tabWork Order`.`name`
        LEFT JOIN `tabEmployee` ON `tabProduction Log`.`employee` = `tabEmployee`.`name`
        WHERE `tabWork Order`.`docstatus` < 2
          AND DATE(`tabProduction Log`.`start`) >= "{from_date}"
          AND DATE(`tabProduction Log`.`start`) <= "{to_date}"
          {conditions}
        ORDER BY `tabProduction Log`.`start` ASC;
      """.format(from_date=filters['from_date'], to_date=filters['to_date'], conditions=conditions)
    
    data = frappe.db.sql(sql_query, as_dict=True)
        
    return data
