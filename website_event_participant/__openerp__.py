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

{
    'name': 'Event Category',
    'category': 'website',
    'summary': 'Using Category as template for event on website.',
    'version': '1.0',
    'description': """
Event Category
==============

* Extends category to work as template for new events
""",
    'author': "Vertel AB",
    'website': "http://vertel.se",
    'depends': ['website_event'],
    'data': [
        'website_event.xml',
    ],
    'demo': [],
    'qweb': ['static/src/xml/templates.xml'],
    'installable': True,
    'auto_install': False,
    'application': False,
}
