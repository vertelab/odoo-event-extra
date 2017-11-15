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
    state = fields.Selection([
            ('draft', 'Unconfirmed'),
            ('cancel', 'Cancelled'),
            ('open', 'Confirmed'),
            ('done', 'Attended'),
        ], string='Status', default='draft', readonly=True, copy=False)
    event_id = fields.Many2one(comodel_name='event.event', related='registration_id.event_id', string='Events')
    registration_id = fields.Many2one(comodel_name='event.registration', string='Registration')
    note = fields.Text(string='Note',help="Good to know information, eg food allergy")

    @api.one
    def do_draft(self):
        self.state = 'draft'

    @api.one
    def registration_open(self):
        """ Open Registration """
        self.state = 'open'

    @api.one
    def button_reg_close(self):
        """ Close Registration """
        today = fields.Datetime.now()
        if self.event_id.date_begin <= today:
            self.state = 'done'
        else:
            raise Warning(_("You must wait for the starting day of the event to do this action."))

    @api.one
    def button_reg_cancel(self):
        self.state = 'cancel'

class event_registration(models.Model):
    _inherit = 'event.registration'

    @api.one
    @api.onchange('participant_ids')
    def _nb_register(self):
        self.nb_register = len(self.participant_ids) or 1

    #~ participant_ids = fields.Many2many(comodel_name='res.partner', relation="event_participant",column2='partner_id',column1='registration_id',string='Participants')
    _participant_ids = fields.One2many(comodel_name='event.participant', inverse_name='registration_id', string='Participants')
    participant_ids = fields.Many2many(comodel_name='res.partner', compute='_get_participant_ids', inverse='_set_participant_ids', string='Participants')

    # get partner ids and store into field participant_ids
    @api.one
    def _get_participant_ids(self):
        self.participant_ids = [(6, 0, [p.partner_id.id for p in self._participant_ids])]

    # remove all partners and create a new list of participants
    @api.one
    def _set_participant_ids(self):
        self._participant_ids.unlink()
        for p in self.participant_ids:
            self.env['event.participant'].create({'registration_id': self.id, 'partner_id': p.id})

    @api.one
    def do_draft(self):
        super(event_registration, self).do_draft()
        for ep in self.mapped('_participant_ids'):
            ep.state = 'draft'

    @api.one
    def confirm_registration(self):
        super(event_registration, self).confirm_registration()
        for ep in self.mapped('_participant_ids'):
            ep.state = 'open'

    @api.one
    def button_reg_close(self):
        super(event_registration, self).button_reg_close()
        for ep in self.mapped('_participant_ids'):
            ep.state = 'done'

    @api.one
    def button_reg_cancel(self):
        super(event_registration, self).button_reg_cancel()
        for ep in self.mapped('_participant_ids'):
            ep.state = 'cancel'

class res_partner(models.Model):
    _inherit = 'res.partner'

    participant_ids = fields.One2many(comodel_name='event.participant', inverse_name='partner_id', string='Participants')
    @api.one
    def _count_participants(self):
        self.count_participants = len(self.participant_ids)
    count_participants = fields.Integer(string='Participants', compute='_count_participants')

    @api.one
    def _event_type_ids(self):
        self.event_type_ids = [(6,0,[e.registration_id.event_id.type.id for e in self.participant_ids if e.state == 'done'])]
    event_type_ids = fields.Many2many(comodel_name='event.type',compute='_event_type_ids',string='Event Types')

    @api.one
    def _my_context(self):
        self.my_context = self._context
    my_context = fields.Text(compute='_my_context')


class event_event(models.Model):
    _inherit = 'event.event'
    @api.one
    def _count_participants(self):
        #~ participants = self.env['event.participant'].search([]).filtered(lambda p: p.registration_id.event_id == self.id)
        self.count_participants = '%s (%s)' %(len(self.registration_ids.mapped('_participant_ids').filtered(lambda p: p.state not in ['cancel'])), len(self.registration_ids.mapped('_participant_ids')))

    count_participants = fields.Char(string='Participants', compute='_count_participants')

    @api.one
    def _participants_ids(self):
        #~ participants = self.env['event.participant'].search([]).filtered(lambda p: p.registration_id.event_id == self.id)
        participants = []
        for r in self.registration_ids:
            for p in r._participant_ids:
                participants.append(p.id)
        #~ participants = [p.id for p in [r.participant_ids for r in self.registration_ids]]
        #~ raise Warning(participants)
        self.participant_ids = [(6,0,participants)]
    participant_ids = fields.One2many(comodel_name='event.participant', compute='_participants_ids', string='Participants')
    course_leader = fields.Many2one(comodel_name="res.partner",string="Course Leader",help="Course Leader or Main Speaker")
