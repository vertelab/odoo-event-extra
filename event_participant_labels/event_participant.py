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
from openerp.addons.web.http import Controller, route, request

import unicodecsv
import os
import tempfile

import logging
_logger = logging.getLogger(__name__)

class event_participant(models.Model):
    _inherit = 'event.participant'

    @api.multi
    def print_labels(self):
        temp = tempfile.NamedTemporaryFile(mode='w+t',suffix='.csv')
        outfile = tempfile.NamedTemporaryFile(mode='w+b',suffix='.pdf')
        labelwriter = unicodecsv.writer(temp,delimiter=',',encoding='utf-8')
        for p in self:
            labelwriter.writerow([p.partner_id.name,p.partner_id.parent_id.name])
        temp.seek(0)
        #~ temp.close()
        res = os.system("glabels-3-batch -o %s -s 25   -c 21  -i %s %s" % (outfile.name,temp.name,os.path.join(get_module_path('event_participant_labels'), 'static', 'labels.glables')))
        outfile.seek(0)
        #~ pdf = report_obj.get_pdf(cr, uid, docids, reportname, data=options_data, context=context)
        pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', len(outfile.read()))]
        return request.make_response(outfile.read(), headers=pdfhttpheaders)
        raise Warning(res,outfile.name,temp.name)        
        
        temp.close()
        
        
        
