# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "stanztech"
app_title = "Stanztech"
app_publisher = "libracore"
app_description = "Stanztech ERP Apps"
app_icon = "octicon octicon-cpu"
app_color = "#0b4ea2"
app_email = "info@libracore.com"
app_license = "AGPL"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/stanztech/css/stanztech.css"
# app_include_js = "/assets/stanztech/js/stanztech.js"

# include js, css files in header of web template
# web_include_css = "/assets/stanztech/css/stanztech.css"
# web_include_js = "/assets/stanztech/js/stanztech.js"

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {
    "Work Order" : "public/js/work_order.js",
    "BOM" : "public/js/bom.js"
}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "stanztech.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "stanztech.install.before_install"
# after_install = "stanztech.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "stanztech.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
#	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"stanztech.tasks.all"
# 	],
# 	"daily": [
# 		"stanztech.tasks.daily"
# 	],
# 	"hourly": [
# 		"stanztech.tasks.hourly"
# 	],
# 	"weekly": [
# 		"stanztech.tasks.weekly"
# 	]
# 	"monthly": [
# 		"stanztech.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "stanztech.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "stanztech.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "stanztech.task.get_dashboard_data"
# }

# hook for migrate cleanup tasks
after_migrate = [
    'stanztech.stanztech.updater.cleanup_languages'
]
