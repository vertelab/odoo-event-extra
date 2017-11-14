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


from openerp.addons.web import http
from openerp.addons.web.http import request


class website_event_participant(website_event):

    @http.route(['/event/cart/update'], type='http', auth="public", methods=['POST'], website=True)
    def cart_update(self, event_id, **post):
        cr, uid, context = request.cr, request.uid, request.context
        ticket_obj = request.registry.get('event.event.ticket')

        sale = False
        for key, value in post.items():
            quantity = int(value or "0")
            if not quantity:
                continue
            sale = True
            ticket_id = key.split("-")[0] == 'ticket' and int(key.split("-")[1]) or None
            ticket = ticket_obj.browse(cr, SUPERUSER_ID, ticket_id, context=context)
            order = request.website.sale_get_order(force_create=1)
            order.with_context(event_ticket_id=ticket.id)._cart_update(product_id=ticket.product_id.id, add_qty=quantity)

        if not sale:
            return request.redirect("/event/%s" % event_id)
        return request.website.render("website_event_participant.event", {'event': request.env['event.event'].browse(event_id), })


        return request.redirect("/event/participant/update")
        
    @http.route(['/event/participant/update'], type='http', auth="public", website=True)
    #~ @http.route(['/event/participant/update'], type='http', auth="public", methods=['POST'], website=True)
    def participant_update(self, event_id, **post):

        values = {'event': request.env['event.event'].browse(event_id)}
        return request.website.render("website_event_participant.event", values)
        #~ return request.redirect("/event/cart/update")

