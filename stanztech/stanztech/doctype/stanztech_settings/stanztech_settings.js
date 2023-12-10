// Copyright (c) 2021-2023, libracore and contributors
// For license information, please see license.txt

frappe.ui.form.on('Stanztech Settings', {
    refresh: function(frm) {
        frm.add_custom_button(__("Production Activity"), function() {
            window.open("/production_activity?key=" + frm.doc.access_key, "_blank");
        });
    }
});
