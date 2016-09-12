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
import base64
from openerp.exceptions import except_orm, Warning, RedirectWarning
from openerp.modules import get_module_path
from pyPdf import PdfFileWriter, PdfFileReader

import os
import tempfile

import logging
_logger = logging.getLogger(__name__)

class event_diploma_wizard(models.TransientModel):
    _name = 'event.diploma.wizard'
    _description = 'Diploma Wizard'

    data = fields.Binary('File')
    state =  fields.Selection([('choose', 'choose'), ('get', 'get')],default="choose") 
    name = fields.Char(default='diploma.sla')
   
    @api.multi
    def print_diploma(self,):
        diploma = self[0]
        #_logger.warning('data %s b64 %s ' % (account.data,base64.decodestring(account.data)))
        
        temp_obj = self.env.ref('event_participant_diploma.sla_template_diploma')

        files = []
        for p in self.env['event.participant'].browse(self._context.get('active_ids', [])):
            #~ raise Warning(temp_obj.render_template(temp_obj.body_html, 'event.participant', p.id))
            temp = tempfile.NamedTemporaryFile(mode='w+t',suffix='.sla')
            temp.write(temp_obj.render_template(temp_obj.body_html, 'event.participant', p.id).lstrip().encode('utf-8'))
            temp.seek(0)
            #outfile = tempfile.NamedTemporaryFile(mode='w+b',suffix='.pdf')
            #files.append(outfile.name)
            #scribus = "/usr/bin/scribus-ng -ns -g -py %s -pa -o %s -pa -t %s > /tmp/foo 2> /tmp/foo2" % (os.path.join(get_module_path('event_participant_diploma'),'scribus.py'),outfile.name,temp.name)
            #res = os.system(scribus)
            #_logger.info('command %s (%s)' % (scribus,res))
            #outfile.seek(0)
            
        #~ for f in files:  # concatenate files
            #~ input = PdfFileReader(open(f,"rb"))
            #~ [output.addPage(f.getPage(page_num)) for page_num in range(input.numPages)]
        #~ outfile = tempfile.NamedTemporaryFile(mode='w+b',suffix='.pdf')
        #~ output.write(PdfFileWriter(outfile.name))
        diploma.write({'state': 'get','data': base64.b64encode(temp.read()) })
#            raise Warning(scribus,outfile.read(),)
            
            
        #~ temp.close()
        #~ raise Warning("glabels-3-batch -o %s -s 25   -c 21  -i %s %s" % (outfile.name,temp.name,os.path.join(get_module_path('event_participant_labels'), 'static', 'label.glabels')))
#        res = os.system("glabels-3-batch -o %s -l -C -i %s %s" % (outfile.name,temp.name,os.path.join(get_module_path('event_participant_labels'), 'static', 'label.glabels')))
#        outfile.seek(0)
        #temp.close()
#        diploma.write({'state': 'get','data': base64.b64encode(outfile.read()) })
        #~ _logger.warn(res,temp.read(),temp.name,outfile.name,outfile.read())
        temp.close()
        #outfile.close()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'event.diploma.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': diploma.id,
            'views': [(False, 'form')],
            'target': 'new',
        }

