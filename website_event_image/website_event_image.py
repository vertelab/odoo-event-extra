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
from openerp.exceptions import except_orm, Warning, RedirectWarning
from openerp import http
from openerp.http import request
from openerp import SUPERUSER_ID
from datetime import datetime
import werkzeug



import logging
_logger = logging.getLogger(__name__)


class website_event_image(http.Controller):


class website(models.Model):
    _inherit = 'website'

    def event_image_url(self, record, recipe):
        """Returns a local url that points to the image field of a given browse record."""
        if record.image:
            return self.imagemagick_url(record, 'image', recipe)
        if record.author_avatar:
            return self.imagemagick_url(record, 'author_avatar', recipe)
        return '/imageurl/%s/ref/%s' % (os.path.join('web', 'static', 'src', 'img', 'stock_person.png'), recipe)

    #~ @http.route([
                #~ '/eventimage/<model("event.event"):event>',
                #~ ],
                #~ type='http', auth="public", website=True)
    #~ def view_simple_event(self, event=None, simple_blog_post=None, **post):
        #~ return request.website.render("website_event_image.simple_view", {'event': event, })


class event(models.Model):
    _inherit = "event.event"

    image = fields.Binary(string="Image")
