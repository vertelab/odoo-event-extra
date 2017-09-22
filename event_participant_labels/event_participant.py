# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution, third party addon
#    Copyright (C) 2004-2016 Vertel AB (<http://vertel.se>).
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

import logging
_logger = logging.getLogger(__name__)


class event_participant(models.Model):
    _inherit = 'event.participant'

    parent_name = fields.Char(related="partner_id.parent_id.name")
    participant_name = fields.Char(related="partner_id.name")
    event_name = fields.Char(related="event_id.name")
    #~ event_type = fields.Char(related="event_id.event_type.name")
    course_leader = fields.Char(related="event_id.course_leader.name")
    #~ event_date = fields.Datetime(related="event_id.date_start")
