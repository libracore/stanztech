# Copyright (c) 2020-2023, libracore and contributors
# For license information, please see license.txt
#

import frappe
from frappe import _

def set_status(self, event):
    # open is coded in validate    
    if self.status == "Open":
        ts = frappe.db.sql("""
            SELECT IFNULL(COUNT(`tabTimesheet Detail`.`name`), 0) AS `count`
            FROM `tabTimesheet Detail`
            WHERE `project` = "{project}"
              AND `docstatus` < 2;
        """.format(project = self.name), as_dict=True)
        if len(ts) > 0 and ts[0]['count'] > 0:
            self.status = "In Progress"
            
    return
    
