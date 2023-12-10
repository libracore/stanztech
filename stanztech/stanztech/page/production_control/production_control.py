# -*- coding: utf-8 -*-
# Copyright (c) 2017-2023, libracore and contributors
# License: AGPL v3. See LICENCE
#

from __future__ import unicode_literals
import frappe
from frappe import throw, _
from frappe.utils import cint
import hashlib
from datetime import datetime, timedelta, date
from stanztech.stanztech.utils import set_work_order_in_process

@frappe.whitelist()
def get_work_order(work_order):
    wo = frappe.get_doc("Work Order", work_order)
    return wo

@frappe.whitelist()
def get_project(project):
    project_data = frappe.get_doc("Project", project).as_dict()
    # add tasks
    tasks = frappe.get_all("Task", 
        filters=[['status', '!=', 'Closed'], ['project', '=', project]],
        fields=['name', 'subject', 'progress']
    )
    project_data['tasks'] = tasks
    return project_data

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
    frappe.db.commit()
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
    frappe.db.commit()
    set_work_order_in_process(wo.name)
    return
    
@frappe.whitelist()
def remark(work_order, remark):
    wo = frappe.get_doc("Work Order", work_order)
    if wo.remarks:
        wo.remarks += "<br>" + remark
    else:
        wo.remarks = remark
    wo.save()
    frappe.db.commit()
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
    frappe.db.commit()
    set_work_order_in_process(wo.name)
    return

"""
Checks if the employee is working in a project

Returns None if there is no open timesheet, or a list with the projects and their tasks that are not completed
"""
@frappe.whitelist()
def check_employee_project(employee):
    ts = frappe.db.sql("""
        SELECT `name`
        FROM `tabTimesheet`
        WHERE 
            `docstatus` = 0
            AND `employee` = "{employee}"
            AND `start_date` = CURDATE();""".format(employee=employee), as_dict=True)
    if len(ts) == 0:
        # no active timesheets
        return None
    else:
        # find open projects
        projects = {}
        timesheet = frappe.get_doc("Timesheet", ts[0]['name'])
        for t in timesheet.time_logs:
            if not t.completed:
                if t.project not in projects:
                    projects[t.project] = {
                        'timesheet': ts[0]['name'],
                        'tasks': []
                    }
                
                projects[t.project]['tasks'].append(t.task)
        return projects

"""
This will start a new task and close all open tasks
"""
@frappe.whitelist()
def start_project_time(employee, project, task):
    # close any previous (and pull existing timesheet)
    timesheet = close_project_time(employee=employee, submit=0)
    # load timesheet
    if timesheet:
        # add entry
        ts = frappe.get_doc("Timesheet", timesheet)
    else:
        # create a new timesheet
        ts = frappe.get_doc({
            'doctype': "Timesheet",
            'employee': employee
        })
    # extend project row
    ts.append('time_logs', {
        'activity_type': frappe.get_value("Stanztech Settings", "Stanztech Settings", "default_activity"),
        'from_time': datetime.now(),
        'project': project,
        'task': task,
        'completed': 0,
        'hours': 0.0,
        'to_time': datetime.now()
    })
    # insert or save
    if not timesheet:
        ts.insert(ignore_permissions=True)
    else:
        ts.save(ignore_permissions=True)
    frappe.db.commit()
    return ts.name
    
@frappe.whitelist()
def close_project_time(employee, submit=0):
    projects = check_employee_project(employee)
    timesheet = None
    if projects and len(projects) > 0:
        # fetch timesheet from projects
        for k, v in projects.items():
            timesheet = v['timesheet']
        ts = frappe.get_doc("Timesheet", timesheet)
        # set unfinished logs to current time and close (should only always be one!)
        for log in ts.time_logs:
            if not log.completed:
                log.to_time = datetime.now()
                diff = log.to_time - log.from_time
                log.hours = diff.total_seconds() / 3600
                log.completed = 1
        ts.save(ignore_permissions=True)
        if submit:
            ts.submit()
        frappe.db.commit()
    return timesheet
            
"""
This will update a task progress value
"""
@frappe.whitelist()
def set_task_progress(task, progress):
    if type(progress) != int:
        progress = cint(progress)
        
    task_doc = frappe.get_doc("Task", task)
    task_doc.progress = progress if progress <= 100 else 100
    task_doc.save()
    frappe.db.commit()
    return
    
