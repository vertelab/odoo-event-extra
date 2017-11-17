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



class event_event(models.Model):
    _inherit = 'event.event'

    state = fields.Selection(selection_add=[('invoiced', 'Invoiced')])

    @api.multi
    def create_invoice(self):
        self.ensure_one()
        res = self.env['ir.actions.act_window'].for_xml_id('event_invoice_release', 'action_event_invoice')
        res['context'] = {
            'default_event_id': self.id,
        }
        return res


class website(models.Model):
    _inherit = 'website'

    @api.multi
    def Xsale_get_order(self, force_create=False, code=None, update_pricelist=None):
        self.ensure_one()
        sale_order = super(website,self).sale_get_order(force_create,code,update_pricelist)
#        sale_order.invoice_policy = 'manual'
        return sale_order
        
        

class sale_order(models.Model):
    _inherit = "sale.order"

    @api.multi
    def X_cart_update(self, product_id=None, line_id=None, add_qty=0, set_qty=0,**kwargs):
        """ Add or set product quantity, add_qty can be negative """
        _logger.error('_cart update %s' % product_id)
        for order in self:
            if product_id:
               pass
            res = super(sale_order,order)._cart_update(product_id,line_id,add_qty,set_qty,kwargs)
        return {'line_id': res['line_id'], 'quantity': res['quantity']}

    @api.model
    def _prepare_order_line_procurement(self,order, line, group_id=False):
        date_planned = self._get_date_planned(order, line, order.date_order)
        _logger.error('procurement %s %s' % (line.product_id.name,line.event_id.name))
        return {
            'name': line.name,
            'origin': order.name,
            'date_planned': date_planned,
            'product_id': line.product_id.id,
            'product_qty': line.product_uom_qty,
            'product_uom': line.product_uom.id,
            'product_uos_qty': (line.product_uos and line.product_uos_qty) or line.product_uom_qty,
            'product_uos': (line.product_uos and line.product_uos.id) or line.product_uom.id,
            'company_id': order.company_id.id,
            'group_id': group_id,
            'invoice_state': (order.order_policy == 'picking') and '2binvoiced' or 'none',
            'sale_line_id': line.id
        }
        
        
class sale_order_line(models.Model):
    _inherit = 'sale.order.line'

    @api.model
    def _prepare_order_line_invoice_line(self, line, account_id=False):
        _logger.error('prepare order line invoice %s' % line.product_id.name)
        res = super(sale_order_line, self)._prepare_order_line_invoice_line(line, account_id=account_id)
        return res

    @api.multi
    def button_confirm(self):
        for order_line in self:
            if order_line.state == 'cancel':
                continue
            if order_line.event_id:
                order_line.order_id.order_policy = 'manual'
        return super(sale_order_line, self).button_confirm()

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
        for line in self.env['sale.order.line'].search([('event_id','=',self._context['active_ids'][0]),('invoiced','=',False)]):
            if to_invoice.get(line.order_id.partner_id.id):
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
                self.env['account.invoice.line'].create({
                    'invoice_id' : invoice.id,
                    'origin': line.order_id.name,
                    'name': line.name,
                    'account_id': line.product_id.property_account_income.id or line.product_id.categ_id.property_account_income_categ.id,
                    'product_id': line.product_id.id,
                    'uos_id': line.product_uos,
                    'quantity': line.product_uos_qty,
                    'price_unit': line.price_unit,
                    'invoice_line_tax_id': line.tax_id,
                    'discount': line.discount,
                    'account_analytic_id': False,
                })
                line.state = 'done'
            invoice.button_compute(set_total=True)
            invoices.append(invoice)
        for line in self.env['sale.order.line'].search([('event_id','=',self._context['active_ids'][0]),('invoiced','=',False)]):
            line.invoiced = True
            _logger.error('%s'  % line.invoice_lines)
        res = self.env['ir.actions.act_window'].for_xml_id('account', 'action_invoice_tree')
        res['domain'] = [('id','in',[i.id for i in invoices])]
        return res

