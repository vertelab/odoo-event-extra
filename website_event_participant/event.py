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

from openerp import models, fields, api, _
from datetime import datetime, timedelta
from dateutil import relativedelta
from openerp import http
from openerp.http import request

import logging
_logger = logging.getLogger(__name__)


class event_type(models.Model):
    _inherit = 'event.type'

    address_id = fields.Many2one(comodel_name='res.partner', string='Location')
    orginazer_id = fields.Many2one(comodel_name='res.partner', string='Organizer')
    user_id = fields.Many2one(comodel_name='res.users', string='Responsible User')
    description = fields.Html(string='Description')


class event_create_wizard(models.TransientModel):
    _name = 'event.create.wizard'
    _description = 'Event Create Wizard'

    name = fields.Char(string='Name', required=True)
    date_begin = fields.Datetime(string='Event Start', required=True)
    date_end = fields.Datetime(string='Event End', required=True)
    date_until = fields.Datetime(string='Until Date', required=True)
    type_id = fields.Many2one(comodel_name='event.type', string='Type of Event', required=True)
    interval = fields.Integer(string='Repeat Every', default=1, required=True)
    rrule_type = fields.Selection([('daily', 'Day(s)'), ('weekly', 'Week(s)'), ('monthly', 'Month(s)'), ('yearly', 'Year(s)')], default=('weekly', 'Week(s)'), required=True)
    weekday_mon = fields.Boolean(string='Monday')
    weekday_tue = fields.Boolean(string='Tuesday')
    weekday_wed = fields.Boolean(string='Wednesday')
    weekday_thu = fields.Boolean(string='Thursday')
    weekday_fri = fields.Boolean(string='Friday')
    weekday_sat = fields.Boolean(string='Staturday')
    weekday_sun = fields.Boolean(string='Sunday')

    @api.multi
    def create_events(self):
        wizard = self[0]
        events = []
        for date in self.get_dates(fields.Datetime.from_string(self.date_until), self.interval, self.rrule_type):
            events.append(self.env['event.event'].create({
                'name': self.name,
                'date_begin': date[0],
                'date_end': date[1],
                'type': self.type_id.id,
                'description': self.type_id.description,
                'user_id': self.type_id.user_id.id,
                'address_id': self.type_id.address_id.id,
                'orginazer_id': self.type_id.orginazer_id.id,
                'seats_min': self.type_id.default_registration_min,
                'seats_max': self.type_id.default_registration_max,
                'replay_to': self.type_id.default_reply_to,
                'email_confirmation_id': self.type_id.default_email_event.id if self.type_id.default_email_event else None,
                'email_registration_id': self.type_id.default_email_registration.id if self.type_id.default_email_registration else None,
            }))
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'event.event',
            'view_mode': 'kanban',
            'view_type': 'form',
            'view_id': self.env.ref('event.view_event_kanban').id,
            'context': {'search_default_name': self.name},
            #~ 'target': 'current',
        }

    #return dates from given period
    def get_dates(self, end, interval, rrule_type):
        dates = []
        b = fields.Datetime.from_string(self.date_begin)
        e = fields.Datetime.from_string(self.date_end)
        weekdays = []
        if self.weekday_mon:
            weekdays.append(0)
        if self.weekday_tue:
            weekdays.append(1)
        if self.weekday_wed:
            weekdays.append(2)
        if self.weekday_thu:
            weekdays.append(3)
        if self.weekday_fri:
            weekdays.append(4)
        if self.weekday_sat:
            weekdays.append(5)
        if self.weekday_sun:
            weekdays.append(6)
        _logger.warn(weekdays)
        if rrule_type == 'daily':
            while (e <= fields.Datetime.from_string(self.date_until)):
                b += timedelta(days=interval)
                e += timedelta(days=interval)
                dates.append((b, e))
            return dates
        if rrule_type == 'weekly':
            while (e <= fields.Datetime.from_string(self.date_until)):
                if b.weekday() in weekdays:
                    dates.append((b, e))
                b += timedelta(days=1)
                e += timedelta(days=1)
            return dates
        if rrule_type == 'monthly':
            while (e <= fields.Datetime.from_string(self.date_until)):
                b = b + relativedelta.relativedelta(months=interval)
                e = e + relativedelta.relativedelta(months=interval)
                dates.append((b, e))
            return dates
        if rrule_type == 'yearly':
            while (e <= fields.Datetime.from_string(self.date_until)):
                b = b + relativedelta.relativedelta(years=interval)
                e = e + relativedelta.relativedelta(years=interval)
                dates.append((b, e))
            return dates
        return [(b, e)]
