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
    _name = 'event.participant'

    partner_id = fields.Many2one(comodel_name='res.partner', string='Participant')
    parent_id = fields.Many2one(comodel_name='res.partner', related='partner_id.parent_id', string='partner')
    state = fields.Selection(related='registration_id.state', string='State')
    event_id = fields.Many2one(comodel_name='event.event', related='registration_id.event_id', string='Events',store=True)
    registration_id = fields.Many2one(comodel_name='event.registration', string='Registration')
    note = fields.Text(string='Note',help="Good to know information, eg food allergy")


class event_registration(models.Model):
    _inherit = 'event.registration'

    participant_ids = fields.Many2many(comodel_name='res.partner', relation="event_participant",column2='partner_id',column1='registration_id',string='Participants')


class res_partner(models.Model):
    _inherit = 'res.partner'

    participant_ids = fields.One2many(comodel_name='event.participant', inverse_name='partner_id', string='Participants')
    @api.one
    def _count_participants(self):
        participants = self.env['event.participant'].search([('partner_id', '=', self.id)])
        self.count_participants = len(participants)
    count_participants = fields.Integer(string='Participants', compute='_count_participants')

    @api.one
    def _event_type_ids(self):
        self.event_type_ids = [(6,0,[e.registration_id.event_id.type.id for e in self.participant_ids if e.state == 'done'])]
    event_type_ids = fields.Many2many(comodel_name='event.type',compute='_event_type_ids',string='Event Types')


class event_event(models.Model):
    _inherit = 'event.event'
    @api.one
    def _count_participants(self):
        participants = self.env['event.participant'].search([('event_id', '=', self.id)])
        self.count_participants = len(participants)
    count_participants = fields.Integer(string='Participants', compute='_count_participants')
    participant_ids = fields.One2many(comodel_name='event.participant', inverse_name='event_id', string='Participants')
    course_leader = fields.Many2one(comodel_name="res.partner",string="Course Leader",help="Course Leader or Main Speaker")

