# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Enterprise Management Solution, third party addon
#    Copyright (C) 2004-2017 Vertel AB (<http://vertel.se>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import json
import datetime

from openerp.addons.web import http
from openerp.addons.web.http import request

from openerp import SUPERUSER_ID
from openerp.addons.web import http
from openerp.addons.web.http import request
from openerp.addons.website_event_sale.controllers.main import website_event
from openerp.tools.translate import _
from openerp.addons.website_sale.controllers.main import get_pricelist

from openerp.addons.web import http
from openerp.addons.web.http import request

import logging
_logger = logging.getLogger(__name__)


class website_event_participant(website_event):

    @http.route(['/event/cart/update'], type='http', auth="public", methods=['POST'], website=True)
    def cart_update(self, event_id, **post):
        cr, uid, context = request.cr, request.uid, request.context
        ticket_obj = request.registry.get('event.event.ticket')

        sale = False
        for key, value in post.items():
            if key.split('-')[0] == 'ticket':
                ticket_id = int(key.split('-')[1]) or None
                quantity = int(value or "0")
                if not quantity:
                    continue
                sale = True
                ticket = ticket_obj.browse(cr, SUPERUSER_ID, ticket_id, context=context)
                order = request.website.sale_get_order(force_create=1)
                line_dict = order.with_context(event_ticket_id=ticket.id)._cart_update(product_id=ticket.product_id.id, add_qty=quantity)

                if ticket_id and order and line_dict:
                    for key, value in post.items():
                        if key.split('-')[0] == 'sel_ticket' and post.get(key) != '' and int(key.split('-')[1]) == ticket_id:
                            # if there's a partner has been chosen, then create a participant of this partner
                            request.env['sale.order.line.participant'].create({
                                'partner_id': int(post.get(key)),
                                'comment': post.get(key.replace('sel_ticket', 'com_ticket')),
                                'sale_order_line_id': line_dict.get('line_id'),
                            })
                        elif key.split('-')[0] == 'fname_ticket' and post.get(key) != '' and int(key.split('-')[1]) == ticket_id and post.get(key.replace('fname_ticket', 'sel_ticket')) == '':
                            # if first name is not empty and select option is empty, then create a new partner and new participant of this partner
                            partner = request.env['res.partner'].create({
                                'name': post.get(key) + '%s' %((' ' + post.get(key.replace('fname_ticket', 'lname_ticket'))) if post.get(key.replace('fname_ticket', 'lname_ticket')) != '' else ''),
                                'parent_id': request.env.user.commercial_partner_id.partner_id.id,
                            })
                            if partner:
                                request.env['sale.order.line.participant'].create({
                                    'partner_id': partner.id,
                                    'comment': post.get(key.replace('fname_ticket', 'com_ticket')),
                                    'sale_order_line_id': line_dict.get('line_id'),
                                })

        if not sale:
            return request.redirect("/event/%s" % event_id)
        return request.redirect("/shop/checkout")

    @http.route(['/event/participant/update'], type='http', auth="public", website=True)
    #~ @http.route(['/event/participant/update'], type='http', auth="public", methods=['POST'], website=True)
    def participant_update(self, event_id, **post):

        values = {'event': request.env['event.event'].browse(event_id)}
        return request.website.render("website_event_participant.event", values)
        #~ return request.redirect("/event/cart/update")

    @http.route(['/render/nbr_partners'], type='json', auth="public", website=True)
    def render_nbr_partners(self, ticket, tickets=0, **kw):
        rows = []
        select = ''
        options = ''
        comment = ''
        if len(request.env.user.partner_id.commercial_partner_id.child_ids) > 0:
            for partner in request.env.user.partner_id.commercial_partner_id.child_ids:
                options += '<option value="%s"><p>%s</p></option>' %(partner.id, partner.name)
        for i in range(0, int(tickets)):
            rows.append({
                'select': 'sel_%s-%s' %(ticket, str(i)),
                'option': options,
                'firstname': 'fname_%s-%s' %(ticket, str(i)),
                'lastname': 'lname_%s-%s' %(ticket, str(i)),
                'comment': 'com_%s-%s' %(ticket, str(i)),
            })
        return {
            'has_children': True if len(request.env.user.partner_id.commercial_partner_id.child_ids) > 0 else False,
            'rows': rows,
        }
