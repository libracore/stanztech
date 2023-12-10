$('document').ready(function(){
    make();
    run();
});


function make() {
    
}

function run() {
    // get command line parameters
    var arguments = window.location.toString().split("?");
    var key = null;
    if (!arguments[arguments.length - 1].startsWith("http")) {
        var args_raw = arguments[arguments.length - 1].split("&");
        var args = {};
        args_raw.forEach(function (arg) {
            var kv = arg.split("=");
            if (kv.length > 1) {
                args[kv[0]] = kv[1];
            }
        });
        if (args['key']) {
            key = args['key'];
            document.getElementById('key').value = key;
        }
    } else {
        // no arguments provided
        
    }
    // load activities
    if (key) {
        frappe.call({
            'method': 'stanztech.templates.pages.production_activity.get_data',
            'args': {
                'key': key
            },
            'callback': function(r) {
                console.log(r);
                if (r.message.error) {
                    frappe.msgprint(r.message.error);
                } else {
                    for (var i = 0; i < r.message.length; i++) {
                        // Find a table
                        var table = document.getElementById("activity_table");

                        // add new row
                        var row = table.insertRow(-1);

                        // Insert new cells 
                        var cell_employee = row.insertCell(0);
                        cell_employee.innerHTML = r.message[i].employee;
                        var cell_active_element = row.insertCell(1);
                        cell_active_element.innerHTML = r.message[i].dn;
                        var cell_active_element = row.insertCell(2);
                        cell_active_element.innerHTML = r.message[i].detail /* + " (" + r.message[i].start + ")" */;
                        var cell_action = row.insertCell(3);
                        cell_action.innerHTML = r.message[i].customer_name;
                    }
                }
                
                // reload after 60 seconds
                window.setTimeout( function() {
                  window.location.reload();
                }, 60000);

            }
        });
    } else {
        frappe.msgprint( __("Please provide a valid key"), __("Unauthorized") );
    }
}
