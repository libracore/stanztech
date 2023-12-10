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
        {"label": _("Project"), "fieldname": "project", "fieldtype": "Link", "options": "Project", "width": 120},
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
    conditions_wo = ""
    conditions_p = ""
    if 'work_order' in filters and filters['work_order']:
        conditions_wo += """ AND `tabWork Order`.`name` = "{0}" """.format(filters['work_order'])
    if 'employee' in filters and filters['employee']:
        conditions_wo += """ AND `tabProduction Log`.`employee` = "{0}" """.format(filters['employee'])
        conditions_p += """ AND `tabTimesheet`.`employee` = "{0}" """.format(filters['employee'])
    if 'department' in filters and filters['department']:
        c = """ AND `tabEmployee`.`department` = "{0}" """.format(filters['department'])
        conditions_wo += c
        conditions_p += c
    if 'project' in filters and filters['project']:
        conditions_p += """ AND `tabTimesheet Detail`.`project` = "{0}" """.format(filters['project'])
        
    # prepare query
    sql_query = """
        SELECT * 
        FROM (
            SELECT 
                `tabProduction Log`.`start` AS `start`,
                `tabProduction Log`.`end` AS `end`,
                `tabProduction Log`.`duration` AS `duration`,
                `tabProduction Log`.`employee` AS `employee`,
                `tabProduction Log`.`employee_name` AS `employee_name`,
                `tabProduction Log`.`completed` AS `completed`,
                `tabProduction Log`.`production_step_type` AS `production_step_type`,
                `tabWork Order`.`name` AS `work_order`,
                NULL AS `project`,
                `tabEmployee`.`department` AS `department`
            FROM `tabProduction Log`
            LEFT JOIN `tabWork Order` ON `tabProduction Log`.`parent` = `tabWork Order`.`name`
            LEFT JOIN `tabEmployee` ON `tabProduction Log`.`employee` = `tabEmployee`.`name`
            WHERE `tabWork Order`.`docstatus` < 2
              AND DATE(`tabProduction Log`.`start`) >= "{from_date}"
              AND DATE(`tabProduction Log`.`start`) <= "{to_date}"
              {conditions_wo}
            
            UNION SELECT
                `tabTimesheet Detail`.`from_time` AS `start`,
                `tabTimesheet Detail`.`to_time` AS `end`,
                `tabTimesheet Detail`.`hours` AS `duration`,
                `tabTimesheet`.`employee` AS `employee`,
                `tabTimesheet`.`employee_name` AS `employee_name`,
                `tabTimesheet Detail`.`completed` AS `completed`,
                (SELECT `tabTask`.`subject` FROM `tabTask` WHERE `tabTask`.`name` = `tabTimesheet Detail`.`task`) AS `production_step_type`,
                NULL AS `work_order`,
                `tabTimesheet Detail`.`project` AS `project`,
                `tabEmployee`.`department` AS `department`
            FROM `tabTimesheet Detail`
            LEFT JOIN `tabTimesheet` ON `tabTimesheet Detail`.`parent` = `tabTimesheet`.`name`
            LEFT JOIN `tabEmployee` ON `tabTimesheet`.`employee` = `tabEmployee`.`name`
            WHERE `tabTimesheet`.`docstatus` < 2
              AND DATE(`tabTimesheet Detail`.`from_time`) >= "{from_date}"
              AND DATE(`tabTimesheet Detail`.`from_time`) <= "{to_date}"
              {conditions_p}
        ) AS `data` 
        ORDER BY `data`.`start`
        ;
      """.format(from_date=filters['from_date'], to_date=filters['to_date'], 
        conditions_wo=conditions_wo, conditions_p=conditions_p)
    
    data = frappe.db.sql(sql_query, as_dict=True)
        
    return data
