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


class event_registration(models.Model):
    _inherit = 'event.registration'

    order_id = fields.Many2one(comodel_name='sale.order', inverse_name='registration_id', string='Sale Order')
    order_state = fields.Selection(related="order_id.state", string='Order Status')

    @api.multi
    def go_to_order(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': self.env.ref('sale.view_order_form').id,
            'res_id': self.order_id.id,
            'target': 'current',
        }


class sale_order_line(models.Model):
    _inherit = 'sale.order.line'

    @api.one
    def button_confirm(self):
        res = super(sale_order_line, self).button_confirm()
        self.env['event.registration'].search([('origin', '=', self.order_id.name)]).write({'order_id': self.order_id.id})
        return res
