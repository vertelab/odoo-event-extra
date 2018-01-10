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
from openerp import http
from openerp.http import request
from openerp.addons.website_event.controllers.main import website_event
from openerp import tools
import time
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import werkzeug.urls
from werkzeug.exceptions import NotFound

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


class event(models.Model):
    _inherit = 'event.event'

    security_type = fields.Selection([('public','Public'),('private','Private')], string='Security type', default='public', required=True)
    group_ids = fields.Many2many('res.groups', string="Authorized Groups")


class sale_order_line(models.Model):
    _inherit = 'sale.order.line'

    @api.one
    def button_confirm(self):
        res = super(sale_order_line, self).button_confirm()
        self.env['event.registration'].search([('origin', '=', self.order_id.name)]).write({'order_id': self.order_id.id})
        return res


class website_event(website_event):
    @http.route(['/event', '/event/page/<int:page>'], type='http', auth="public", website=True)
    def events(self, page=1, **searches):
        cr, uid, context = request.cr, request.uid, request.context
        event_obj = request.registry['event.event']
        type_obj = request.registry['event.type']
        country_obj = request.registry['res.country']

        searches.setdefault('date', 'all')
        searches.setdefault('type', 'all')
        searches.setdefault('country', 'all')

        domain_search = {}

        def sdn(date):
            return date.strftime('%Y-%m-%d 23:59:59')
        def sd(date):
            return date.strftime(tools.DEFAULT_SERVER_DATETIME_FORMAT)
        today = datetime.today()
        dates = [
            ['all', _('Next Events'), [("date_end", ">", sd(today))], 0],
            ['today', _('Today'), [
                ("date_end", ">", sd(today)),
                ("date_begin", "<", sdn(today))],
                0],
            ['week', _('This Week'), [
                ("date_end", ">=", sd(today + relativedelta(days=-today.weekday()))),
                ("date_begin", "<", sdn(today  + relativedelta(days=6-today.weekday())))],
                0],
            ['nextweek', _('Next Week'), [
                ("date_end", ">=", sd(today + relativedelta(days=7-today.weekday()))),
                ("date_begin", "<", sdn(today  + relativedelta(days=13-today.weekday())))],
                0],
            ['month', _('This month'), [
                ("date_end", ">=", sd(today.replace(day=1))),
                ("date_begin", "<", (today.replace(day=1) + relativedelta(months=1)).strftime('%Y-%m-%d 00:00:00'))],
                0],
            ['nextmonth', _('Next month'), [
                ("date_end", ">=", sd(today.replace(day=1) + relativedelta(months=1))),
                ("date_begin", "<", (today.replace(day=1)  + relativedelta(months=2)).strftime('%Y-%m-%d 00:00:00'))],
                0],
            ['old', _('Old Events'), [
                ("date_end", "<", today.strftime('%Y-%m-%d 00:00:00'))],
                0],
        ]

        # search domains
        current_date = None
        current_type = None
        current_country = None
        for date in dates:
            if searches["date"] == date[0]:
                domain_search["date"] = date[2]
                if date[0] != 'all':
                    current_date = date[1]
        if searches["type"] != 'all':
            current_type = type_obj.browse(cr, uid, int(searches['type']), context=context)
            domain_search["type"] = [("type", "=", int(searches["type"]))]

        if searches["country"] != 'all' and searches["country"] != 'online':
            current_country = country_obj.browse(cr, uid, int(searches['country']), context=context)
            domain_search["country"] = ['|', ("country_id", "=", int(searches["country"])), ("country_id", "=", False)]
        elif searches["country"] == 'online':
            domain_search["country"] = [("country_id", "=", False)]

        def dom_without(without):
            domain = ['&', ('state', "in", ['draft','confirm','done']), '|', ('security_type', '=', 'public'), '&', ('security_type', '=', 'private'), ('group_ids', 'in', request.env.user.groups_id.mapped('id'))]
            for key, search in domain_search.items():
                if key != without:
                    domain += search
            return domain

        # count by domains without self search
        for date in dates:
            if date[0] <> 'old':
                date[3] = event_obj.search(
                    request.cr, request.uid, dom_without('date') + date[2],
                    count=True, context=request.context)

        domain = dom_without('type')
        types = event_obj.read_group(
            request.cr, request.uid, domain, ["id", "type"], groupby="type",
            orderby="type", context=request.context)
        type_count = event_obj.search(request.cr, request.uid, domain,
                                      count=True, context=request.context)
        types.insert(0, {
            'type_count': type_count,
            'type': ("all", _("All Categories"))
        })

        domain = dom_without('country')
        countries = event_obj.read_group(
            request.cr, request.uid, domain, ["id", "country_id"],
            groupby="country_id", orderby="country_id", context=request.context)
        country_id_count = event_obj.search(request.cr, request.uid, domain,
                                            count=True, context=request.context)
        countries.insert(0, {
            'country_id_count': country_id_count,
            'country_id': ("all", _("All Countries"))
        })

        step = 10  # Number of events per page
        event_count = event_obj.search(
            request.cr, request.uid, dom_without("none"), count=True,
            context=request.context)
        pager = request.website.pager(
            url="/event",
            url_args={'date': searches.get('date'), 'type': searches.get('type'), 'country': searches.get('country')},
            total=event_count,
            page=page,
            step=step,
            scope=5)

        order = 'website_published desc, date_begin'
        if searches.get('date','all') == 'old':
            order = 'website_published desc, date_begin desc'
        obj_ids = event_obj.search(
            request.cr, request.uid, dom_without("none"), limit=step,
            offset=pager['offset'], order=order, context=request.context)
        events_ids = event_obj.browse(request.cr, request.uid, obj_ids,
                                      context=request.context)

        values = {
            'current_date': current_date,
            'current_country': current_country,
            'current_type': current_type,
            'event_ids': events_ids,
            'dates': dates,
            'types': types,
            'countries': countries,
            'pager': pager,
            'searches': searches,
            'search_path': "?%s" % werkzeug.url_encode(searches),
        }

        return request.website.render("website_event.index", values)


class event_type(models.Model):
    _inherit = 'event.type'

    category_id = fields.Many2one(comodel_name='res.partner.category', string='Website Competence', help='This competence name shows in website')
    website_published = fields.Boolean(string='Website Publish')


class res_partner(models.Model):
    _inherit = 'res.partner'

    @api.one
    @api.depends('child_competence_ids', 'child_ids', 'child_ids.category_id', 'event_type_ids')
    def _get_child_competence_ids(self):
        if self.is_company:
            event_type_ids = self.env['event.type'].browse([])
            category_ids = self.env['res.partner.category'].browse([])
            for c in self.child_ids:
                for ev in c.event_type_ids:
                    if ev.website_published:
                        event_type_ids |= ev
                for categ in c.category_id:
                    category_ids |= categ
            self.child_competence_ids |= category_ids
            self.child_competence_ids |= event_type_ids.mapped('category_id')
            self.event_type_ids |= event_type_ids
    child_competence_ids = fields.Many2many(comodel_name='res.partner.category', compute='_get_child_competence_ids', string='Child Competences')
