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

class WebsiteEventCalendar(http.Controller):

    #TODO: Is <datetime:start> implemented by Odoo?
    @http.route(['/event_calendar/get_events/<int:start>/<int:end>'], type='http', auth='public', website=True)
    def get_events(self, start, end, **post):
        cr, uid, context = request.cr, request.uid, request.context

        #Get events
        calendar_event_obj = request.registry['calendar.event']
        calendar_event_ids = calendar_event_obj.search(cr, uid, [('start', '<', unicode(datetime.datetime.fromtimestamp(end))), ('stop', '>', unicode(datetime.datetime.fromtimestamp(start)))], context=context)
        calendar_events = calendar_event_obj.browse(cr, uid, calendar_event_ids, context = context)

        contacts = []
        if request.website.user_id.id != uid:
            calendar_contact_obj = request.registry['calendar.contacts']
            calendar_contact_ids = calendar_contact_obj.search(cr, uid, [('user_id', '=', uid)], context=context)
            calendar_contacts = calendar_contact_obj.browse(cr, uid, calendar_contact_ids, context = context)

            #Create response (Cannot serialize object)
            contacts.append(request.env.user.partner_id.id)
            for contact in calendar_contacts:
                contacts.append(contact.partner_id.id)

        #Events
        events = []
        #~ for event in request.env['event.event'].search( [('state','in',['cancel','confirm']),('date_begin', '<', unicode(datetime.datetime.fromtimestamp(end))), ('date_end', '>', unicode(datetime.datetime.fromtimestamp(start)))]):
        for event in request.env['event.event'].search( [('state','in',['cancel','confirm'])]):
            #Fetch attendees
            attandees = []
            #~ for attandee_id in calendar_event.attendee_ids:
                #~ attandees.append({ 'id': attandee_id.partner_id.id, 'name': attandee_id.partner_id.name })

            events.append({
                           'id': event.id,
                           'start': event.date_begin,
                           'end': event.date_end,
                           'title': event.name,
                           'description': event.description,
                           'type': event.type.name,
                           #'allDay': event.allday,
                           #'color': event.color_partner_id,
                           'attendees': attandees,
                           'url': '/event/%s' % event.id,
                           'seats_available': event.seats_max - event.seats_used,
                           'state': event.state,
                           })

        return json.dumps({ 'events': events, 'contacts': contacts })


    @http.route([
        '/event/<model("event.type"):type>/type',
    ], type='http', auth="user", website=True)
    def event_type(self, type=None, **post):
        return request.website.render("website_event_category.type_editor", {'type': type})
