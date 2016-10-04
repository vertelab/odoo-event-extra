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

{
    'name': 'Event Participant',
    'version': '0.1',
    'category': 'Event',
    'summary': 'Handles participants of an event',
    'description': """
Add a participants list in event registration
===================================
""",
    'images': ['static/description/event_participant.jpg'],
    'author': 'Vertel AB',
    'website': 'http://www.vertel.se',
    'depends': ['event', 'report'],
    'data': ['event_participant_view.xml',
            'security/ir.model.access.csv',
            'event_participant_report.xml'
    ],
    'application': False,
    'installable': True,
}
# vim:expandtab:smartindent:tabstop=4s:softtabstop=4:shiftwidth=4:
