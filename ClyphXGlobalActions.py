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
from consts import *
    
class ClyphXGlobalActions(ControlSurfaceComponent):
    __module__ = __name__
    __doc__ = ' Global actions '    
    
    def __init__(self, parent):
        ControlSurfaceComponent.__init__(self)
        self._parent = parent
	self._last_gqntz = 4
	self._last_rqntz = 5
	if self.song().clip_trigger_quantization != 0:
	    self._last_gqntz = int(self.song().clip_trigger_quantization)
	if self.song().midi_recording_quantization != 0:
	    self._last_rqntz = int(self.song().midi_recording_quantization)
	self._last_scene_index = list(self.song().scenes).index(self.song().view.selected_scene)#---new addition
	self._scenes_to_monitor = []
	self.setup_scene_listeners()
	
	
    def disconnect(self):
	self.remove_scene_listeners()
	self._parent = None
	    
    
    def on_enabled_changed(self):
	pass
        

    def update(self):    
        pass
    
    
    def on_scene_triggered(self, index):
	self._last_scene_index = index
	
	
    def on_scene_list_changed(self):
	self.setup_scene_listeners()
	
	
    def send_midi_message(self, track, xclip, ident, args):
	""" Send formatted note/cc/pc message or raw midi message. """
	status_values = {'NOTE': 144, 'CC': 176, 'PC': 192}
	message_to_send = []
	if args:
	    byte_array = args.split()
	    if len(byte_array) >= 2:
		if len(byte_array) >= 3 and byte_array[0] in status_values:
		    data_bytes = self.convert_strings_to_ints(byte_array[1:])
		    if data_bytes and data_bytes[0] in range(1, 17):
			message_to_send = [status_values[byte_array[0]] + data_bytes[0] - 1]
			for byte in data_bytes[1:]:
			    if byte in range(128):
				message_to_send.append(byte)
			if (byte_array[0] != 'PC' and len(message_to_send) != 3) or (byte_array[0] == 'PC' and len(message_to_send) != 2):
			    return
		else:
		    message_to_send = self.convert_strings_to_ints(byte_array)
		if message_to_send:
		    try: 
			self._parent._send_midi(tuple(message_to_send))
			if byte_array[0] == 'NOTE': #---send matching note off for note messages
			    message_to_send[-1] = 0
			    self._parent._send_midi(tuple(message_to_send))
		    except: pass
		
		    
    def convert_strings_to_ints(self, strings):
	""" Convert list of strings of ints into list of ints. """
	result = []
	try:
	    for string in strings:
		result.append(int(string))
	except: result = []
	return result
	
	
    def set_back_to_arrange(self, track, xclip, ident, value = None):
	""" Triggers back to arrange button """
	self.song().back_to_arranger = 0
	
	
    def set_overdub(self, track, xclip, ident, value = None):
	""" Toggles or turns on/off overdub """
	if value in KEYWORDS:
	    self.song().overdub = KEYWORDS[value]
	else:
	    self.song().overdub = not(self.song().overdub)
	    
	    
    def set_metronome(self, track, xclip, ident, value = None):
	""" Toggles or turns on/off metronome """
	if value in KEYWORDS:
	    self.song().metronome = KEYWORDS[value]
	else:
	    self.song().metronome = not(self.song().metronome)	
	    
	    
    def set_record(self, track, xclip, ident, value = None):
	""" Toggles or turns on/off record """
	if value in KEYWORDS:
	    self.song().record_mode = KEYWORDS[value]
	else:
	    self.song().record_mode = not(self.song().record_mode)	
	    
	    
    def set_punch_in(self, track, xclip, ident, value = None):
	""" Toggles or turns on/off punch in """
	if value in KEYWORDS:
	    self.song().punch_in = KEYWORDS[value]
	else:
	    self.song().punch_in = not(self.song().punch_in)	
	    
	    
    def set_punch_out(self, track, xclip, ident, value = None):
	""" Toggles or turns on/off punch out """
	if value in KEYWORDS:
	    self.song().punch_out = KEYWORDS[value]
	else:
	    self.song().punch_out = not(self.song().punch_out)	

	    
    def restart_transport(self, track, xclip, ident, value = None):
	""" Restarts transport to 0.0 """
	self.song().current_song_time = 0
	
	
    def set_stop_transport(self, track, xclip, ident, value = None):
	""" Stops transport """
	self.song().is_playing = not(self.song().is_playing)
	
	
    def set_stop_all(self, track, xclip, ident, value = None):
	""" Stop all clips """
	self.song().stop_all_clips()
	
	
    def set_tap_tempo(self, track, xclip, ident, value = None):
	""" Tap tempo """
	self.song().tap_tempo()
	
	
    def set_undo(self, track, xclip, ident, value = None):
	""" Triggers Live's undo """
	if self.song().can_undo:
	    self.song().undo()
	    
	    
    def set_redo(self, track, xclip, ident, value = None):
	""" Triggers Live's redo """
	if self.song().can_redo:
	    self.song().redo()
	    
	    
    def move_up(self, track, xclip, ident, value = None):
	""" Scroll up """
	self.application().view.scroll_view(Live.Application.Application.View.NavDirection(0), '', False) 
	    
	
    def move_down(self, track, xclip, ident, value = None):
	""" Scroll down """
	self.application().view.scroll_view(Live.Application.Application.View.NavDirection(1), '', False) 
	
	
    def move_left(self, track, xclip, ident, value = None):
	""" Scroll left """
	self.application().view.scroll_view(Live.Application.Application.View.NavDirection(2), '', False) 
	
	
    def move_right(self, track, xclip, ident, value = None):
	""" Scroll right """
	self.application().view.scroll_view(Live.Application.Application.View.NavDirection(3), '', False)  
	
	
    def move_to_first_device(self, track, xclip, ident, value = None):
	""" Move to the first device on the track and scroll the view """
	self.focus_devices()
	self.song().view.selected_track.view.select_instrument()
	
	
    def move_to_last_device(self, track, xclip, ident, value = None):
	""" Move to the last device on the track and scroll the view """
	self.focus_devices()
	if self.song().view.selected_track.devices:
	    self.song().view.select_device(self.song().view.selected_track.devices[len(self.song().view.selected_track.devices) - 1])
	    self.application().view.scroll_view(Live.Application.Application.View.NavDirection(3), 'Detail/DeviceChain', False)
	    self.application().view.scroll_view(Live.Application.Application.View.NavDirection(2), 'Detail/DeviceChain', False)

      
    def move_to_prev_device(self, track, xclip, ident, value = None):
	""" Move to the previous device on the track """
	self.focus_devices()
	self.application().view.scroll_view(Live.Application.Application.View.NavDirection(2), 'Detail/DeviceChain', False)
	
	
    def move_to_next_device(self, track, xclip, ident, value = None):
	""" Move to the next device on the track """
	self.focus_devices()
	self.application().view.scroll_view(Live.Application.Application.View.NavDirection(3), 'Detail/DeviceChain', False)
	
    
    def focus_devices(self):
	""" Make sure devices are in focus and visible """
	self.application().view.show_view('Detail')
	self.application().view.show_view('Detail/DeviceChain')
		
	
    def show_clip_view(self, track, xclip, ident, value = None):
	""" Show clip view """
	self.application().view.show_view('Detail')
	self.application().view.show_view('Detail/Clip')
	
	
    def show_track_view(self, track, xclip, ident, value = None):
	""" Show track view """
	self.application().view.show_view('Detail')
	self.application().view.show_view('Detail/DeviceChain')
	
	
    def adjust_tempo(self, track, xclip, ident, args):
	""" Adjust/set tempo """
	args = args.strip()
	if args.startswith(('<', '>')):
	    factor = self._parent.get_adjustment_factor(args, True)
	    self.song().tempo = max(20, min(999, (self.song().tempo + factor)))
	elif args.startswith('*'):
	    try: self.song().tempo = max(20, min(999, (self.song().tempo * float(args[1:]))))
	    except: pass
	else:
	    try:
		self.song().tempo = float(args)
	    except: pass
	    
	    
    def adjust_groove(self, track, xclip, ident, args):
	""" Adjust/set global groove """
	args = args.strip()
	if args.startswith(('<', '>')):
	    factor = self._parent.get_adjustment_factor(args, True)
	    self.song().groove_amount = max(0.0, min(1.3125, (self.song().groove_amount + factor * float(1.3125 / 131.0))))
	else:
	    try:
		self.song().groove_amount = int(args) * float(1.3125 / 131.0)
	    except: pass
	    

    def adjust_global_quantize(self, track, xclip, ident, args):
	""" Adjust/set/toggle global quantization """
	args = args.strip()
	if args in GQ_STATES:
	    self.song().clip_trigger_quantization = GQ_STATES[args]
	elif args in ('<', '>'):
	    factor = self._parent.get_adjustment_factor(args)
	    new_gq = self.song().clip_trigger_quantization + factor
	    if new_gq in range (14):
		self.song().clip_trigger_quantization = new_gq
	else:
	    if self.song().clip_trigger_quantization != 0:
		self._last_gqntz = int(self.song().clip_trigger_quantization)
		self.song().clip_trigger_quantization = 0
	    else:
		self.song().clip_trigger_quantization = self._last_gqntz
	    
	    
    def adjust_record_quantize(self, track, xclip, ident, args):
	""" Adjust/set/toggle record quantization """
	args = args.strip()
	if args in RQ_STATES:
	    self.song().midi_recording_quantization = RQ_STATES[args]
	elif args in ('<', '>'):
	    factor = self._parent.get_adjustment_factor(args)
	    new_rq = self.song().midi_recording_quantization + factor
	    if new_rq in range (9):
		self.song().midi_recording_quantization = new_rq
	else:
	    if self.song().midi_recording_quantization != 0:
		self._last_rqntz = int(self.song().midi_recording_quantization)
		self.song().midi_recording_quantization = 0
	    else:
		self.song().midi_recording_quantization = self._last_rqntz
	    
    	    
    def adjust_time_signature(self, track, xclip, ident, args):
	""" Adjust global time signature """
	if '/' in args:
	    name_split = args.split('/')
	    try:
		self.song().signature_numerator = int(name_split[0].strip())
		self.song().signature_denominator = int(name_split[1].strip())
	    except: pass
	    
	    
    def set_jump_all(self, track, xclip, ident, args): 
	""" Jump arrange position forward/backward """
	try: self.song().jump_by(float(args.strip()))
	except: pass
	
	
    def set_unarm_all(self, track, xclip, ident, args):
	""" Unarm all armable tracks """
	for t in self.song().tracks:
	    if t.can_be_armed and t.arm:
		t.arm = 0  
		
		
    def set_unmute_all(self, track, xclip, ident, args):
	""" Unmute all tracks """
	for t in (self.song().tracks + self.song().return_tracks):
	    if t.mute:
		t.mute = 0
		
		
    def set_unsolo_all(self, track, xclip, ident, args):
	""" Unsolo all tracks """
	for t in (self.song().tracks + self.song().return_tracks):
	    if t.solo:
		t.solo = 0
		
		
    def set_fold_all(self, track, xclip, ident, value):
	""" Toggle or turn/on fold for all tracks """
	state_to_set = None
	for t in self.song().tracks:
	    if t.is_foldable:
		if state_to_set == None:
		    state_to_set = not(t.fold_state)
		if value in KEYWORDS:
		    t.fold_state = KEYWORDS[value]
		else:
		    t.fold_state = state_to_set
		    
		    
    def set_scene(self, track, xclip, ident, args):  
	""" Sets scene to play (doesn't launch xclip) """
	scene_to_launch = list(self.song().scenes).index(self.song().view.selected_scene)
	if type(xclip) is Live.Clip.Clip:
	    scene_to_launch = xclip.canonical_parent.canonical_parent.playing_slot_index
	args = args.strip()
	if args != '':
	    if args == 'SEL':
		scene_to_launch = list(self.song().scenes).index(self.song().view.selected_scene)
	    elif args == 'RND' and len(self.song().scenes) > 1:#--Don't allow randomization unless more than 1 scene
		scene_to_launch = Live.Application.get_random_int(0, len(self.song().scenes))
		if scene_to_launch == self._last_scene_index:
		    while scene_to_launch == self._last_scene_index:
			scene_to_launch = Live.Application.get_random_int(0, len(self.song().scenes))
	    elif args.startswith(('<', '>')) and len(self.song().scenes) > 1:#--Don't allow adjustment unless more than 1 scene
		factor = self._parent.get_adjustment_factor(args)
		if factor < len(self.song().scenes):
		    scene_to_launch = self._last_scene_index + factor
		    if scene_to_launch >= len(self.song().scenes):
			scene_to_launch -= len(self.song().scenes)
		    elif scene_to_launch < 0 and abs(scene_to_launch) >= len(self.song().scenes):
			scene_to_launch = -(abs(scene_to_launch) - len(self.song().scenes))
	    else:
		try:
		    if int(args) in range(len(self.song().scenes)):
			scene_to_launch = int(args)-1
		except: pass
	self._last_scene_index = scene_to_launch
	for t in self.song().tracks:
	    if t.is_foldable or (t.clip_slots[scene_to_launch].has_clip and t.clip_slots[scene_to_launch].clip == xclip):
		pass
	    else:
		t.clip_slots[scene_to_launch].fire()
	    		    
		    
    def do_locator_action(self, track, xclip, ident, args):
	""" Jump between locators or to a particular locator """
	args = args.strip()
	if args == '>' and self.song().can_jump_to_next_cue:
	    self.song().jump_to_next_cue()
	elif args == '<' and self.song().can_jump_to_prev_cue:
	    self.song().jump_to_prev_cue()
	else:
	    try:
		for cp in self.song().cue_points:
		    if self._parent.get_name(cp.name) == args:
			cp.jump()
			break
	    except: pass
	    
	    
    def do_loop_action(self, track, xclip, ident, args):
	""" Handle arrange loop actions """
	args = args.strip()
	if args == '' or args in KEYWORDS:
	    self.set_loop_on_off(args)
	else:
	    new_start = self.song().loop_start
	    new_length = self.song().loop_length
	    if args.startswith(('<', '>')):
		self.move_loop_by_factor(args)
		return()
	    elif args == 'RESET':
		new_start = 0
	    elif args.startswith('*'):
		try:
		    new_length = self.song().loop_length * float(args[1:])
		except: pass
	    else:
		try:
		    new_length = float(args) * ((4.0 / self.song().signature_denominator) * self.song().signature_numerator)
		except: pass
	    self.set_new_loop_position(new_start, new_length)
	
	    
    def set_loop_on_off(self, value = None):
	""" Toggles or turns on/off arrange loop """
	if value in KEYWORDS:
	    self.song().loop = KEYWORDS[value]
	else:
	    self.song().loop = not(self.song().loop)
	    
	    
    def move_loop_by_factor(self, args):
	""" Move arrangement loop by its length or by a specified factor """
	factor = self.song().loop_length
	if args == '<':
	    factor = -(factor)
	if len(args) > 1:
	    factor = self._parent.get_adjustment_factor(args, True)
	new_start = self.song().loop_start + factor
	if new_start < 0.0:
	    new_start = 0.0
	self.set_new_loop_position(new_start, self.song().loop_length)
	
	
    def set_new_loop_position(self, new_start, new_length):
	""" For use with other loop actions, ensures that loop settings are within range """
	if new_start >= 0 and new_length >= 0 and new_length <= self.song().song_length:
	    self.song().loop_start = new_start  
	    self.song().loop_length = new_length	
	    
	    
    def setup_scene_listeners(self):
	""" Setup listeners for all scenes in set and check that last index is in current scene range. """
	self.remove_scene_listeners()
	scenes = self.song().scenes
	if not self._last_scene_index in range(len(scenes)):
	    self._last_scene_index = list(self.song().scenes).index(self.song().view.selected_scene)
	for index in range(len(scenes)):
	    self._scenes_to_monitor.append(scenes[index])
	    listener = lambda index = index:self.on_scene_triggered(index)
	    if not scenes[index].is_triggered_has_listener(listener):
		scenes[index].add_is_triggered_listener(listener)
		
	
    def remove_scene_listeners(self):
	if self._scenes_to_monitor:
	    scenes = self._scenes_to_monitor
	    for index in range(len(scenes)):
		if scenes[index]:
		    listener = lambda index = index:self.on_scene_triggered(index)
		    if scenes[index].is_triggered_has_listener(listener):
			scenes[index].remove_is_triggered_listener(listener)
	self._scenes_to_monitor = []     
    