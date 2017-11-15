var website = openerp.website;
website.add_template_file('/website_event_participant/static/src/xml/templates.xml');

$(document).ready(function(){

    $("select[name^='ticket-']").on("change", function(){
        var self = $(this);
        openerp.jsonRpc("/render/nbr_partners", "call", {
            'ticket': $(this).attr('name'),
            'tickets': $(this).val(),
        }).done(function(data){
            var tr = $(self.closest("tr[itemscope=itemscope]"));
            //~ console.log(tr.closest("tbody").children());
            //~ self.closest("tbody").find("tr").each(function() {
                //~ if ($(this) == tr) {
                    //~ $(this).nextAll("tr").each(function() {
                        //~ if ($(this).attr("itemscope") != "itemscope")
                            //~ $(this).remove();
                        //~ if ($(this).attr("itemscope") == "itemscope")
                            //~ return false;
                    //~ });
                //~ }
            //~ });
            var row = ''
            $.each(data['rows'], function(key, value) {
                var select_hidden = 'sel fa fa-caret-down fa-2x text-primary';
                var sel = 'form-control';
                var input_hidden = 'form-inline input-group';
                var add = 'add fa fa-plus-circle fa-2x text-success hidden';
                if (data['has_children']) {
                    input_hidden = 'form-inline input-group hidden';
                    add = 'add fa fa-plus-circle fa-2x text-success';
                }
                else {
                    select_hidden = 'sel fa fa-caret-down fa-2x text-primary hidden';
                    sel = 'form-control hidden';
                    input_hidden = 'form-inline input-group hidden';
                    add = 'add fa fa-plus-circle fa-2x text-success';
                }
                var content = openerp.qweb.render('partner_info', {
                    'is_company': data['is_company'],
                    'has_children': data['has_children'],
                    'sel': sel,
                    'select_hidden': select_hidden,
                    'add': add,
                    'input_hidden': input_hidden,
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
    $(this).closest("tr").find("select").addClass("hidden");
    $(this).closest("td").find("div").removeClass("hidden");
});

$(".sel").live('click', function() {
    $(this).addClass("hidden");
    $(this).closest("tr").find(".add").removeClass("hidden");
    $(this).closest("tr").find("div.input-group").addClass("hidden");
    $(this).closest("td").find("select").removeClass("hidden");
});
