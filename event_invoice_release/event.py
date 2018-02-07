# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution, third party addon
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
from openerp.exceptions import Warning

import logging
_logger = logging.getLogger(__name__)


class event_registration(models.Model):
    _inherit = 'event.registration'
    line_id = fields.Many2one(comodel_name='sale.order.line')

class event_event(models.Model):
    _inherit = 'event.event'

    invoice = fields.Boolean(string="Released for invoice")

    @api.multi
    def create_invoice(self):
        self.ensure_one()
        res = self.env['ir.actions.act_window'].for_xml_id('event_invoice_release', 'action_event_invoice')
        res['context'] = {
            'default_event_id': self.id,
        }
        return res


class event_invoice(models.TransientModel):
    _name = "event.invoice"

    journal_id = fields.Many2one(comodel_name='account.journal',string='Destination Journal',required=True)
    event_id = fields.Many2one(comodel_name='event.event',string='Event',required=True)
    invoice_date = fields.Date(string="Invoice Date")

    @api.model
    def view_init(self,fields_list):
        res = super(event_invoice, self).view_init(fields_list)
        if len(self.env['sale.order.line'].search([('event_id','=',self.event_id.id),('invoiced','=',False)])) == 0:
            raise Warning(_('None of these registrations require invoicing.'))
        return res

    @api.multi
    def create_invoice(self):
        self.ensure_one()
        to_invoice = {}
        order_info = {}
        self.event_id.invoice = True
        for line in self.env['sale.order.line'].search([('event_id', '=', self.event_id.id), ('invoiced', '=', False), ('order_id.state', '!=', 'draft')]):
            if line.event_registration_id.state in ['cancel']:
                line.state = 'exception'
            elif to_invoice.get(line.order_id.partner_id.id):
                to_invoice[line.order_id.partner_id.id].append(line)
            else:
                to_invoice[line.order_id.partner_id.id] = [line]
                order_info[line.order_id.partner_id.id] = line.order_id
        invoices = []
        for partner_id in to_invoice.keys():
            invoice = self.env['account.invoice'].create({ # TODO merge to an open invoice
                'origin': order_info[partner_id].name,
                'date_invoice': self.invoice_date,
                'user_id': order_info[partner_id].user_id.id,
                'partner_id': partner_id,
                'account_id': order_info[partner_id].partner_id.property_account_receivable.id,
                'payment_term': order_info[partner_id].partner_id.property_payment_term.id or False,
                'type': 'out_invoice',
                'fiscal_position': order_info[partner_id].fiscal_position.id,
                'company_id': order_info[partner_id].company_id.id,
                'currency_id': order_info[partner_id].currency_id.id,
                'journal_id': self.journal_id.id,
            })
            for line in to_invoice[partner_id]:
                line.invoice_lines |= self.env['account.invoice.line'].create({
                    'invoice_id' : invoice.id,
                    'origin': line.order_id.name,
                    'name': line.name,
                    'account_id': line.product_id.property_account_income.id or line.product_id.categ_id.property_account_income_categ.id,
                    'product_id': line.product_id.id,
                    'uos_id': line.product_uos,
                    'quantity': line.event_registration_id.nb_register,
                    'price_unit': line.price_unit,
                    'invoice_line_tax_id': [(4, t.id, 0) for t in line.tax_id],
                    
                    'discount': line.discount,
                    'account_analytic_id': False,
                })
                line.state = 'done'

            invoice.button_compute(set_total=True)
            invoices.append(invoice)
        res = self.env['ir.actions.act_window'].for_xml_id('account', 'action_invoice_tree')
        res['domain'] = [('id','in',[i.id for i in invoices])]
        return res

class sale_order_line(models.Model):
    _inherit = 'sale.order.line'

    event_registration_id = fields.Many2one(comodel_name='event.registration')

    @api.model
    def _prepare_order_line_invoice_line(self, line, account_id=False):  # Prevent non released event-lines to be invoiced
        if line.event_id and line.event_id.invoice == False:
            return None
        if line.event_registration_id and line.event_registration_id.state == 'cancel':
            return None
        return super(sale_order_line, self)._prepare_order_line_invoice_line(line, account_id=account_id)

    @api.multi
    def button_confirm(self):
        res = super(sale_order_line, self).button_confirm()
        for order_line in self: # connect registration to order line
            if order_line.event_id:
                registration = self.env['event.registration'].search([('event_ticket_id', '=', order_line.event_ticket_id.id), ('partner_id', '=', order_line.order_id.partner_id.id),('line_id', '=', None)], order='create_date desc',limit=1)
                if not registration:
                    raise Warning(_("Couldn't find %s's registration to the %s event!" % (order_line.order_id.partner_id.name, order_line.event_id.name)))
                registration.line_id = order_line.id
                order_line.event_registration_id = registration.id
        return res

    #~ @api.v7
    #~ def button_confirm(self, cr, uid, ids, context=None):
        #~ res = super(sale_order_line, self).button_confirm(cr, uid, ids, context=context)
        #~ env = Environment(cr, uid, context)
        #~ for order_line in env['sale.order.line'].browse(ids): # connect registration to order line
            #~ if order_line.event_id:
                #~ registration = env['event.registration'].search([('event_ticket_id', '=', order_line.event_ticket_id.id), ('partner_id', '=', order_line.order_id.partner_id.id),('line_id', '=', None)], order='create_date desc',limit=1)
                #~ if not registration:
                    #~ raise Warning(_("Couldn't find %s's registration to the %s event!" % (order_line.order_id.partner_id.name, order_line.event_id.name)))
                #~ registration.line_id = order_line.id
                #~ order_line.event_registration_id = registration.id
        #~ return res
