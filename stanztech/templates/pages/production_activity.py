# -*- coding: utf-8 -*-
# Copyright (c) 2022, libracore and contributors
# License: AGPL v3. See LICENCE

from __future__ import unicode_literals
import frappe
from frappe import _

@frappe.whitelist(allow_guest=True)
def get_data(key):
    if validate_credentials(key):
        # fetch active employees
        # find work order production logs with no end and timesheet details that are not complete
        sql_query = """
            SELECT *
            FROM
                (
                    SELECT 
                        `tabProduction Log`.`employee` AS `employee`,
                        `tabProduction Log`.`start` AS `start`,
                        "Work Order" AS `dt`,
                        `tabProduction Log`.`parent` AS `dn`,
                        `tabProduction Log`.`production_step_type` AS `detail`
                    FROM `tabProduction Log`
                    WHERE 
                        `tabProduction Log`.`start` >= CURDATE()
                        AND `tabProduction Log`.`end` IS NULL
                    UNION SELECT 
                        `tabTimesheet`.`employee` AS `employee`,
                        `tabTimesheet Detail`.`from_time` AS `start`,
                        "Project" AS `dt`,
                        `tabTimesheet Detail`.`project` AS `dn`,
                        `tabTimesheet Detail`.`task` AS `detail`
                    FROM `tabTimesheet Detail`
                    LEFT JOIN `tabTimesheet` ON `tabTimesheet Detail`.`parent` = `tabTimesheet`.`name`
                    WHERE
                        `tabTimesheet`.`docstatus` = 0
                        AND `start_date` = CURDATE()
                ) AS `raw`
            ORDER BY `raw`.`employee` ASC, `raw`.`start` DESC;
        """
        
        data = frappe.db.sql(sql_query, as_dict=True)
        
        return data
    else:
        return {'error': 'Not allowed'}
        
def validate_credentials(key):
    stanztech_key = frappe.get_value("Stanztech Settings", "Stanztech Settings", "access_key")
    if key == stanztech_key:
        return True
    else:
        return False
