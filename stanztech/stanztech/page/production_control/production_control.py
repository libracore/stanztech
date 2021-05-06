# -*- coding: utf-8 -*-
# Copyright (c) 2017-2021, libracore and contributors
# License: AGPL v3. See LICENCE
#

from __future__ import unicode_literals
import frappe
from frappe import throw, _
import hashlib
from datetime import datetime, timedelta

@frappe.whitelist()
def get_work_order(work_order):
    wo = frappe.get_doc("Work Order", work_order)
    return wo

@frappe.whitelist()
def end_log(work_order, cdn, employee, completed=0):
    wo = frappe.get_doc("Work Order", work_order)
    total_duration = 0
    for log in wo.production_log:
        frappe.log_error("{0} == {1}".format(log.name, cdn))
        if log.name == cdn:
            log.end = datetime.now()
            log.completed = completed
            log.duration = float((log.end - log.start).total_seconds() / 60)
            break
        total_duration += log.duration
    wo.total_time = total_duration
    wo.save()
    return

@frappe.whitelist()
def complete_log(work_order, cdn, employee):
    end_log(work_order, cdn, employee, completed=1)
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

@frappe.whitelist()
def checkout(work_order, duration, production_step_type, employee=None):
    wo = frappe.get_doc("Work Order", work_order)
    duration = int(duration)
    row = wo.append('production_log', {
        'production_step_type': production_step_type,
        'start': datetime.now(),
        'employee': employee,
        'duration': duration,
        'completed': 1,
        'end': datetime.now() + timedelta(minutes = duration)
    })
    wo.total_time = wo.total_time + duration
    wo.save()
    return
