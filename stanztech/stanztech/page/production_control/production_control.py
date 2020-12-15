# -*- coding: utf-8 -*-
# Copyright (c) 2017-2019, libracore and contributors
# License: AGPL v3. See LICENCE
#
# NOTE: this is the old transfer method. 
# It is replaced by the Abacus Transfer File and will be deprecated soon
#

from __future__ import unicode_literals
import frappe
from frappe import throw, _
import hashlib
from datetime import datetime

@frappe.whitelist()
def get_work_order(work_order):
    wo = frappe.get_doc("Work Order", work_order)
    return wo

@frappe.whitelist()
def end_log(work_order, cdn):
    wo = frappe.get_doc("Work Order", work_order)
    for log in wo.production_log:
        frappe.log_error("{0} == {1}".format(log.name, cdn))
        if log.name == cdn:
            log.end = datetime.now()
            break
    wo.save()
    return

@frappe.whitelist()
def complete_log(work_order, cdn):
    wo = frappe.get_doc("Work Order", work_order)
    for log in wo.production_log:
        if log.name == cdn:
            log.completed = 1
            log.end = datetime.now()
            break
    wo.save()
    return

@frappe.whitelist()
def start_log(work_order, production_step_type, employee=None):
    wo = frappe.get_doc("Work Order", work_order)
    row = wo.append('production_log', {
        'production_step_type': production_step_type,
        'start': datetime.now(),
        'employee': employee
    })
    wo.save()
    return
    
@frappe.whitelist()
def remark(work_order, remark):
    wo = frappe.get_doc("Work Order", work_order)
    if wo.remarks:
        wo.remarks += "<br>" + remark
    else:
        wo.remarks = remark
    wo.save()
    return
