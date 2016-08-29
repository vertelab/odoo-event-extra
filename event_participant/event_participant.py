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

    participant_ids = fields.Many2many(comodel_name='res.partner', string='Participants')


class event_participant(models.Model):
    _name = 'event.participant'

    @api.one
    def _name_(self):
        self.name = self.partner_id.name

    name = fields.Char(string='Name', compute='_name_')
    partner_id = fields.Many2one(comodel_name='res.partner', string='Participant')
    registration_id = fields.Many2one(comodel_name='event.registration', string='Registration')


class res_partner(models.Model):
    _inherit = "res.partner"

    participant_ids = fields.One2many(comodel_name='event.participant', inverse_name='partner_id', string='Participants')
