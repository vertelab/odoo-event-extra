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

    registration_id = fields.Many2one(comodel_name='event.registration', string='Registration')
    partner_id = fields.Many2one(comodel_name='res.partner', string='Participant')
    state = fields.Selection([
            ('draft', 'Unconfirmed'),
            ('cancel', 'Cancelled'),
            ('open', 'Confirmed'),
            ('done', 'Attended'),
        ], string='Status', default='draft', readonly=True, copy=False)
    note = fields.Text(string='Note',help="Good to know information, eg food allergy")
    event_id = fields.Many2one(comodel_name='event.event', related='registration_id.event_id', string='Events')
    parent_id = fields.Many2one(comodel_name='res.partner', related='partner_id.parent_id', string='partner')

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

    order_line_id = fields.Many2one(comodel_name="sale.order.line")

    @api.one
    @api.onchange('participant_ids')
    def _nb_register(self):
        self.nb_register = len(self.participant_ids) or 1
        #~ self.order_line_id.product_uom_qty = self.nb_register

    #~ participant_ids = fields.Many2many(comodel_name='res.partner', relation="event_participant",column2='partner_id',column1='registration_id',string='Participants')
    _participant_ids = fields.One2many(comodel_name='event.participant', inverse_name='registration_id', string='Participants')
    participant_ids = fields.Many2many(comodel_name='res.partner', compute='_get_participant_ids', inverse='_set_participant_ids', string='Participants')

    # get partner ids and store into field participant_ids
    @api.one
    def _get_participant_ids(self):
        self.participant_ids = [(6, 0, [p.partner_id.id for p in self._participant_ids])]

    @api.one
    def _set_participant_ids(self):
        # Delete all event.particiant who's partners are no longer in participant_ids
        participants = self.participant_ids
        for participant in self._participant_ids:
            if participant.partner_id not in participants:
                participant.unlink()
        # Add new event.particiants for new partners in participant_ids
        for p in participants:
            if p not in self._participant_ids.mapped('partner_id'):
                self.env['event.participant'].create({
                    'registration_id': self.id,
                    'partner_id': p.id,
                })

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

class sale_order_line(models.Model):
    _inherit = 'sale.order.line'

    event_registration_id = fields.Many2one(comodel_name='event.registration')

    @api.multi
    def button_confirm(self):
        for order_line in self:
            super(sale_order_line, order_line).button_confirm()
            if order_line.event_id and order_line.state != 'cancel':
                registration = self.env['event.registration'].search([('event_id','=', order_line.event_id.id),('event_ticket_id','=',order_line.event_ticket_id and order_line.event_ticket_id.id or None),('origin','=',order_line.order_id.name)])
                if registration:
                    order_line.event_registration_id = registration_id
                    registration.order_line_id = order_line_id.id

    #~ @api.v7
    #~ def button_confirm(self, cr, uid, ids, context=None):
        #~ res = super(sale_order_line, self).button_confirm(cr, uid, ids, context=context)
        #~ env = Environment(cr, uid, context)
