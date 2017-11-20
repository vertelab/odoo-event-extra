//~ addEventListener(document, "touchstart", function(e) {
    //~ console.log(e.defaultPrevented);  // will be false
    //~ e.preventDefault();   // does nothing since the listener is passive
    //~ console.log(e.defaultPrevented);  // still false
//~ }, Modernizr.passiveeventlisteners ? {passive: true} : false);

var website = openerp.website;
website.add_template_file('/website_event_participant/static/src/xml/templates.xml');

$(document).ready(function(){

    $("select[name^='ticket-']").on("change", function(){
        var self = $(this);
        var parent_tr = self.closest("tr[itemscope=itemscope]");
        openerp.jsonRpc("/render/nbr_partners", "call", {
            'ticket': $(this).attr('name'),
            'tickets': $(this).val(),
        }).done(function(data){
            $(self.closest("tbody")).find(parent_tr).nextAll().each(function() {
                if($(this).attr("itemscope") == 'itemscope')
                    return false;
                else
                    $(this).remove();
            });
            var row = ''
            $.each(data['rows'], function(key, value) {
                var sel = 'sel fa fa-caret-down fa-2x text-primary hidden';
                var selection = 'form-control';
                var add = 'add fa fa-plus-circle fa-2x text-success';
                var input = 'form-inline input-group hidden';
                if (data['input']) {
                    selection = 'form-control hidden';
                    add = 'add fa fa-plus-circle fa-2x text-success hidden';
                    input = 'form-inline input-group';
                }
                var content = openerp.qweb.render('partner_info', {
                    'multi': data['multi'],
                    'sel': sel,
                    'selection': selection,
                    'add': add,
                    'input': input,
                    'select': data['rows'][key]['select'],
                    'option': data['rows'][key]['option'],
                    'firstname': data['rows'][key]['firstname'],
                    'lastname': data['rows'][key]['lastname'],
                    'comment': data['rows'][key]['comment'],
                });
                row += content;
            });
            self.closest("tr").after(row);
        });

    });
});

$(".add").live('click', function() {
    $(this).addClass("hidden");
    $(this).closest("tr").find(".sel").removeClass("hidden");
    $(this).closest("tr").find("select").attr("value", "");
    $(this).closest("tr").find("select").addClass("hidden");
    $(this).closest("td").find("div").removeClass("hidden");
});

$(".sel").live('click', function() {
    $(this).addClass("hidden");
    $(this).closest("tr").find(".add").removeClass("hidden");
    $(this).closest("tr").find("div.input-group").addClass("hidden");
    $(this).closest("td").find("select").removeClass("hidden");
});
