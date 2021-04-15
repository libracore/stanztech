from __future__ import unicode_literals
from frappe import _

def get_data():
    return[
        {
            "label": _("Fertigung"),
            "icon": "fa fa-users",
            "items": [
                   {
                       "type": "page",
                       "name": "production_control",
                       "label": _("Production Control"),
                       "description": _("Production Control")
                   }
            ]
        }
    ]
