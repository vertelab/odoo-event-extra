# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution, third party addon
#    Copyright (C) 2004-2015 Vertel AB (<http://vertel.se>).
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


class event_registration(models.Model):
    _inherit = 'event.registration'

    participant_ids = fields.Many2many(comodel_name='res.partner', relation="event_participant",column2='partner_id',column1='registration_id',string='Participants')


class event_participant(models.Model):
    _name = 'event.participant'

    partner_id = fields.Many2one(comodel_name='res.partner', string='Participant')
    registration_id = fields.Many2one(comodel_name='event.registration', string='Registration')


class res_partner(models.Model):
    _inherit = "res.partner"

    participant_ids = fields.One2many(comodel_name='event.participant', inverse_name='partner_id', string='Participants')
    
    @api.one
    def _event_type_ids(self):
        raise Warning(self.participant_ids,[e.event_id.type.name for e in self.participant_ids])
        self.event_type_ids = [(6,0,[e.event_id.type.name for e in self.participant_ids])]
    event_type_ids = fields.One2many(comodel_name='event.type',compute='_event_type_ids',string='Event Types')
