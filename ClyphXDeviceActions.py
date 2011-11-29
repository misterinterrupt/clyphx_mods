"""
# Copyright (C) 2010 Stray <stray411@hotmail.com>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# For questions regarding this module contact
# Stray <stray411@hotmail.com>
"""

import Live 
from _Framework.ControlSurfaceComponent import ControlSurfaceComponent
from _Generic.Devices import *
from consts import *
    
class ClyphXDeviceActions(ControlSurfaceComponent):
    __module__ = __name__
    __doc__ = ' Device and Looper actions '
    
    def __init__(self, parent):
        ControlSurfaceComponent.__init__(self)
        self._parent = parent
	self._looper_data = {}
	
	
    def adjust_best_of_bank_param(self, device, track, xclip, ident, args):
	""" Adjust device best-of-bank parameter """
	param = None
	name_split = args.split()
	try:
	    param_num = int(name_split[0][1])-1
	    if param_num in range (8):
		param = self.get_bob_parameter(device, param_num)
	except: pass
	if param and param.is_enabled and len(name_split) > 1:
	    self._parent.do_parameter_adjustment(param, name_split[-1])
		    
		    
    def adjust_banked_param(self, device, track, xclip, ident, args):
	""" Adjust device banked parameter """
	param = None
	name_split = args.split()
	try:
	    bank_num = int(name_split[0][1])-1		    
	    param_num = int(name_split[1][1])-1
	    if param_num in range (8) and bank_num in range (8):
		param = self.get_banked_parameter(device, bank_num, param_num)
	except: pass
	if param and param.is_enabled and len(name_split) > 1:
	    self._parent.do_parameter_adjustment(param, name_split[-1])
	    
	    
    def adjust_chain_selector(self, device, track, xclip, ident, args):
	""" Adjust device chain selector parameter """
	param = self.get_chain_selector(device)
	name_split = args.split()
	if param and param.is_enabled and len(name_split) > 1:
	    self._parent.do_parameter_adjustment(param, name_split[-1])
	
	
    def randomize_params(self, device, track, xclip, ident, args):
	""" Randomize device parameters """
	name = self._parent.get_name(device.name)
	if not name.startswith(('NK RND', 'NK RST', 'NK CHAIN MIX', 'NK DR', 'NK LEARN', 'NK RECEIVER', 'NK TRACK', 'NK SIDECHAIN')):
	    for p in device.parameters:
		if p and p.is_enabled and not p.is_quantized and p.name != 'Chain Selector':
		    p.value = (((p.max - p.min) / 127) * Live.Application.get_random_int(0, 128)) + p.min   
		
		
    def reset_params(self, device, track, xclip, ident, args):
	""" Reset device parameters """
	name = self._parent.get_name(device.name)
	if not name.startswith(('NK RND', 'NK RST', 'NK CHAIN MIX', 'NK DR', 'NK LEARN', 'NK RECEIVER', 'NK TRACK', 'NK SIDECHAIN')):
	    for p in device.parameters:
		if p and p.is_enabled and not p.is_quantized and p.name != 'Chain Selector':
		    p.value = p.default_value
		
		
    def select_device(self, device, track, xclip, ident, args):
	""" Select device and bring it and the track it's on into view """
	if self.song().view.selected_track != track:
	    self.song().view.selected_track = track
	self.application().view.show_view('Detail')
	self.application().view.show_view('Detail/DeviceChain')
	self.song().view.select_device(device)
			
		
    def set_device_on_off(self, device, track, xclip, ident, value = None):
	""" Toggles or turns device on/off """
	on_off = self.get_device_on_off(device)
	if on_off and on_off.is_enabled:
	    if value in KEYWORDS:
		on_off.value = KEYWORDS[value]
	    else:
		on_off.value = not(on_off.value)
		
		
    def set_looper_on_off(self, track, xclip, ident, value = None):
	""" Toggles or turns looper on/off """
	self.get_looper(track)
	if self._looper_data and self._looper_data['Looper'] and self._looper_data['Device On'].is_enabled:
	    if value in KEYWORDS:
		self._looper_data['Device On'].value = KEYWORDS[value]
	    else:
		self._looper_data['Device On'].value = not(self._looper_data['Device On'].value) 
    
    
    def set_looper_rev(self, track, xclip, ident, value = None):
	""" Toggles or turns looper reverse on/off """
	self.get_looper(track)
	if self._looper_data and self._looper_data['Looper'] and self._looper_data['Reverse'].is_enabled:
	    if value in KEYWORDS:
		self._looper_data['Reverse'].value = KEYWORDS[value]
	    else:
		self._looper_data['Reverse'].value = not(self._looper_data['Reverse'].value) 
    
    
    def set_looper_state(self, track, xclip, ident, value = None):
	""" Sets looper state """
	self.get_looper(track)
	if self._looper_data and self._looper_data['Looper'] and value in LOOPER_STATES and self._looper_data['State'].is_enabled:
	    self._looper_data['State'].value = LOOPER_STATES[value]
	    
	    
    def dispatch_chain_action(self, device, track, xclip, ident, args):
	""" Handle actions related to device chains """
	if self._parent._can_have_nested_devices and device.can_have_chains and device.chains and not device.class_name.startswith('Midi'):
	    arg_list = args.split()
	    try: chain = device.chains[int(arg_list[0].replace('CHAIN', '')) - 1]
	    except: chain = None
	    if chain:
		if len(arg_list) > 1 and arg_list[1] == 'MUTE':
		    if len(arg_list) > 2 and arg_list[2] in KEYWORDS:
			chain.mute = KEYWORDS[arg_list[2]]
		    else:
			chain.mute = not(chain.mute)
		elif len(arg_list) > 1 and arg_list[1] == 'SOLO':
		    if len(arg_list) > 2 and arg_list[2] in KEYWORDS:
			chain.solo = KEYWORDS[arg_list[2]]
		    else:
			chain.solo = not(chain.solo)
		elif len(arg_list) > 2 and arg_list[1] == 'VOL':
		    self._parent.do_parameter_adjustment(chain.mixer_device.volume, arg_list[2].strip())
		elif len(arg_list) > 2 and arg_list[1] == 'PAN':
		    self._parent.do_parameter_adjustment(chain.mixer_device.panning, arg_list[2].strip())
    
    
    def get_device_on_off(self, device):
	""" Get device on/off param """
	result = None
	for parameter in device.parameters:
	    if str(parameter.name).startswith('Device On'):
		result = parameter
		break
	return result
    
    
    def get_chain_selector(self, device):
	""" Get rack chain selector param """
	result = None
	if device.class_name.endswith('GroupDevice'):
	    for parameter in device.parameters:
		if str(parameter.original_name) == 'Chain Selector':
		    result = parameter
		    break
	return result
    
    
    def get_bob_parameter(self, device, param_num):
	""" Get best-of-bank parameter 1-8 for Live's devices """
	result = None
	if (device.class_name in DEVICE_BOB_DICT.keys()):
	    param_bank = DEVICE_BOB_DICT[device.class_name][0]
	    parameter = get_parameter_by_name(device, param_bank[param_num]) 
	    if parameter:
		result = parameter
	return result
    
    
    def get_banked_parameter(self, device, bank_num, param_num):
	""" Get bank 1-8/parameter 1-8 for Live's devices """
	result = None
	if bank_num <= number_of_parameter_banks(device) and device.class_name in DEVICE_DICT.keys():
	    device_bank = DEVICE_DICT[device.class_name]
	    param_bank = device_bank[bank_num]
	    parameter = get_parameter_by_name(device, param_bank[param_num]) 
	    if parameter:
		result = parameter
	return result
    
    
    def get_looper(self, track):
	""" Get first looper device on track and its params """
	self._looper_data = {}
	for d in track.devices:
	    if d.class_name == 'Looper':
		self._looper_data['Looper'] = d
		for p in d.parameters: 
		    if p.name in ('Device On', 'Reverse', 'State'):
			self._looper_data[p.name] = p
		break
	    elif not self._looper_data and self._parent._can_have_nested_devices and d.can_have_chains and d.chains:
		for c in d.chains:
		    self.get_looper(c)
		    
    
    def disconnect(self):
	pass		
	    
    
    def on_enabled_changed(self):
	pass
        

    def update(self):    
        pass
    
    