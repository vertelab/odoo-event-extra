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

import unicodecsv
import os
import tempfile

import logging
_logger = logging.getLogger(__name__)

class event_labels_wizard(models.TransientModel):
    _name = 'event.labels.wizard'
    _description = 'Labels Wizard'

    data = fields.Binary('File')
    state =  fields.Selection([('choose', 'choose'), ('get', 'get')],default="choose") 
    name = fields.Char(default='label.pdf')


   
    @api.multi
    def print_labels(self,):
        label = self[0]
        #_logger.warning('data %s b64 %s ' % (account.data,base64.decodestring(account.data)))
        
        temp = tempfile.NamedTemporaryFile(mode='w+t',suffix='.csv')
        outfile = tempfile.NamedTemporaryFile(mode='w+b',suffix='.pdf')
        labelwriter = unicodecsv.writer(temp,delimiter=',',encoding='utf-8')
        for p in self.env['event.participant'].browse(self._context.get('active_ids', [])):
            labelwriter.writerow([p.partner_id.name,p.partner_id.parent_id.name])
        temp.seek(0)
        #~ temp.close()
        #~ raise Warning("glabels-3-batch -o %s -s 25   -c 21  -i %s %s" % (outfile.name,temp.name,os.path.join(get_module_path('event_participant_labels'), 'static', 'label.glabels')))
        res = os.system("glabels-3-batch -o %s -l -C -i %s %s" % (outfile.name,temp.name,os.path.join(get_module_path('event_participant_labels'), 'static', 'label.glabels')))
        outfile.seek(0)
        #temp.close()
        label.write({'state': 'get','data': base64.b64encode(outfile.read()) })
        #~ _logger.warn(res,temp.read(),temp.name,outfile.name,outfile.read())
        temp.close()
        outfile.close()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'event.labels.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': label.id,
            'views': [(False, 'form')],
            'target': 'new',
        }

