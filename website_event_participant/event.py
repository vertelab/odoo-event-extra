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


class sale_order_line_participant(models.Model):
    _name = 'sale.order.line.participant'

    parnter_id = fields.Many2one(comodel_name='res.partner', string='Partner')
    comment = fields.Text(string='Comment')
    sale_order_line_id = fields.Many2one(comodel_name='sale.order.line', string='Sale Order Line')


class sale_order_line(models.Model):
    _inherit = 'sale.order.line'

    participant_ids = fields.One2many(comodel_name='sale.order.line.participant', inverse_name='sale_order_line_id', string='Participants')
