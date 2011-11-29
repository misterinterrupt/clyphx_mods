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

class ClyphXControlComponent(ControlSurfaceComponent):
    __module__ = __name__
    __doc__ = ' Control component for ClyphX '
    
    def __init__(self, parent):
        ControlSurfaceComponent.__init__(self)
        self._parent = parent
	self._control_list = {}
	self._xt_scripts = []
	
	
    def connect_script_instances(self, instanciated_scripts):
	""" Try to connect to ClyphX_XT instances """
	ClyphX_XT = None
	for i in range (5):
	    try:
		if i == 0:
		    from ClyphX_XTA.ClyphX_XT import ClyphX_XT
		elif i == 1:
		    from ClyphX_XTB.ClyphX_XT import ClyphX_XT
		elif i == 2:
		    from ClyphX_XTC.ClyphX_XT import ClyphX_XT
		elif i == 3:
		    from ClyphX_XTD.ClyphX_XT import ClyphX_XT
		elif i == 4:
		    from ClyphX_XTE.ClyphX_XT import ClyphX_XT
	    except: pass
	    if ClyphX_XT:
		for i in instanciated_scripts:
		    if isinstance(i, ClyphX_XT) and not i in self._xt_scripts:
			self._xt_scripts.append(i)
			break
		
	
    def assign_new_actions(self, string):
	""" Assign new actions to controls via xclips """
	if self._xt_scripts:
	    for x in self._xt_scripts:
		x.assign_new_actions(string)
 	ident = string[string.index('[')+2:string.index(']')].strip()
	actions = string[string.index(']')+2:].strip()
	for c, v in self._control_list.items():
	    if ident == v['ident']:
		new_actions = actions.split(',')
		on_action = '[' + ident + '] ' + new_actions[0]
		off_action = None
		if on_action and len(new_actions) > 1:
		    if new_actions[1].strip() == '*':
			off_action = on_action
		    else:
			off_action = '[' + ident + '] ' + new_actions[1]
		if on_action:
		    v['on_action'] = on_action    
		    v['off_action'] = off_action
		break
		
	    
    def receive_midi(self, bytes):
	""" Receive user-defined midi messages """
	if self._control_list:
	    ctrl_data = None
	    if bytes[2] == 0 or bytes[0] < 144:
		if (bytes[0], bytes[1]) in self._control_list.keys() and self._control_list[(bytes[0], bytes[1])]['off_action']:
		    ctrl_data = self._control_list[(bytes[0], bytes[1])]
		elif (bytes[0] + 16, bytes[1]) in self._control_list.keys() and self._control_list[(bytes[0] + 16, bytes[1])]['off_action']:
		    ctrl_data = self._control_list[(bytes[0] + 16, bytes[1])]
		if ctrl_data:
		    ctrl_data['name'].name = ctrl_data['off_action']	
	    elif bytes[2] != 0 and (bytes[0], bytes[1]) in self._control_list.keys():
		ctrl_data = self._control_list[(bytes[0], bytes[1])]
		ctrl_data['name'].name = ctrl_data['on_action']
	    if ctrl_data:
		self._parent.handle_xclip_name(self.song().view.selected_track, ctrl_data['name'])
	    
		
    def get_user_control_settings(self, data, midi_map_handle):
	""" Receives control data from user settings file and builds control dictionary """
	self._control_list = {}
	for d in data:
	    status_byte = None
	    channel = None
	    ctrl_num = None
	    on_action = None
	    off_action = None
	    d = d.split('=')
	    ctrl_name = d[0].strip()
	    new_ctrl_data = d[1].split(',')
	    try:
		if new_ctrl_data[0].strip() == 'NOTE':
		    status_byte = 144
		elif new_ctrl_data[0].strip() == 'CC':
		    status_byte = 176
		if int(new_ctrl_data[1].strip()) in range(1,17):
		    channel = int(new_ctrl_data[1].strip()) - 1
		if int(new_ctrl_data[2].strip()) in range(128):
		    ctrl_num = int(new_ctrl_data[2].strip())
		on_action = '[' + ctrl_name + '] ' + new_ctrl_data[3]
		if on_action and len(new_ctrl_data) > 4:
		    if new_ctrl_data[4].strip() == '*':
			off_action = on_action
		    else:
			off_action = '[' + ctrl_name + '] ' + new_ctrl_data[4]
	    except: pass
	    if status_byte and channel != None and ctrl_num != None and on_action:
		self._control_list[(status_byte + channel, ctrl_num)] = {'ident' : ctrl_name, 'on_action' : on_action, 'off_action' : off_action, 'name' : NamedControl(on_action)}
		if status_byte == 144:
		    Live.MidiMap.forward_midi_note(self._parent._c_instance.handle(), midi_map_handle, channel, ctrl_num)
		else:
		    Live.MidiMap.forward_midi_cc(self._parent._c_instance.handle(), midi_map_handle, channel, ctrl_num)

		    
    def disconnect(self):
	pass

	    
    def on_enabled_changed(self):
        pass
        

    def update(self):    
        pass
    
    
class NamedControl:
    __module__ = __name__
    __doc__ = ' Simple class that allows controls to have names '
    
    def __init__(self, name = 'none'):
	self.name = name
	

class ClyphXTrackComponent(ControlSurfaceComponent):
    __module__ = __name__
    __doc__ = ' Track component that monitors play slot index and calls main script on changes '
    
    def __init__(self, parent, track):
        ControlSurfaceComponent.__init__(self)
        self._parent = parent
	self._track = track
	self._clip = None
	self._last_playing_pos = -1
	self._loop_count = 0
	self._track.add_playing_slot_index_listener(self.play_slot_index_changed)
	self._register_timer_callback(self.on_timer)
	self._do_action_list = False
	
	
    def play_slot_index_changed(self):
	""" Called on track play slot index changes, checks if clip has ident and adds status listener if so """
	self.remove_playing_status_listener()
	if self._track.playing_slot_index >= 0:	    
	    clip_name = self._parent.get_name(self._track.clip_slots[self._track.playing_slot_index].clip.name)
	    if len(clip_name) > 2 and clip_name[0] == '[' and ']' in clip_name:
		self._clip = self._track.clip_slots[self._track.playing_slot_index].clip
		if not self._clip.playing_status_has_listener(self.playing_status_changed):
		    self._clip.add_playing_status_listener(self.playing_status_changed)
		    self.playing_status_changed()
		
		
    def playing_status_changed(self):
	""" Called on play status changes to set do action list to true """
	self._do_action_list = False
	if self._clip and self._clip.is_playing and not self._clip.is_triggered and not self._clip.is_recording:
	    self._do_action_list = True
	    self._last_playing_pos = -1
	    self._loop_count = 0
	    
		
    def on_timer(self):
	""" Continuous timer, calls main script if do action is true and also on loop changes for LSEQ """
	if self._do_action_list and self._track and self._clip:
	    self._parent.handle_xclip_name(self._track, self._clip)
	    self._do_action_list = False
	if self._clip and self._clip.looping and self._clip.is_playing and not self._clip.is_triggered and not self._clip.is_recording:
	    if self._clip.playing_position < self._last_playing_pos and self._clip.playing_position >= 0:
		self._loop_count += 1
		self._parent.handle_loop_seq_action_list(self._clip, self._loop_count)
	    self._last_playing_pos = self._clip.playing_position
	    
	    
    def remove_playing_status_listener(self):
	if self._clip and self._clip.playing_status_has_listener(self.playing_status_changed):
	    self._clip.remove_playing_status_listener(self.playing_status_changed)
	self._clip = None
		    
	    
    def disconnect(self):
	self.remove_playing_status_listener()
	self._unregister_timer_callback(self.on_timer)
	if self._track and self._track.playing_slot_index_has_listener(self.play_slot_index_changed):
	    self._track.remove_playing_slot_index_listener(self.play_slot_index_changed)
	self._track = None
	
	
    def on_enabled_changed(self):
	pass
        

    def update(self):    
        pass
    
    
class ClyphXCueComponent(ControlSurfaceComponent):
    __module__ = __name__
    __doc__ = ' Cue component that monitors cue points and calls main script on changes '
    
    def __init__(self, parent):
        ControlSurfaceComponent.__init__(self)
        self._parent = parent
	self.song().add_current_song_time_listener(self.arrange_time_changed)
	self.song().add_is_playing_listener(self.arrange_time_changed)
	self.song().add_cue_points_listener(self.cue_points_changed)
	self._x_points = {}
	self._x_point_time_to_watch_for = -1
	self._last_arrange_position = -1
	self.cue_points_changed()
    	
	    
    def cue_points_changed(self):
	""" Called on cue point changes to set up points to watch, cue points can't be named via the API so cue points can't perform any actions requiring naming """
	self.remove_cue_point_listeners()
	for cp in self.song().cue_points:
	    if not cp.time_has_listener(self.cue_points_changed):
		cp.add_time_listener(self.cue_points_changed)
	    if not cp.name_has_listener(self.cue_points_changed):
		cp.add_name_listener(self.cue_points_changed)
	    name = self._parent.get_name(cp.name)
	    if len(name) > 2 and name[0] == '[' and name.count('[') == 1 and name.count(']') == 1:
		cue_name = name.replace(name[name.index('['):name.index(']')+1].strip(), '')
		self._x_points[cp.time] = cp
	self.set_x_point_time_to_watch()

	
    def arrange_time_changed(self):
	""" Called on arrange time changed and schedules actions where necessary """
	if self._x_point_time_to_watch_for != -1 and self.song().is_playing:
	    if self.song().current_song_time >= self._x_point_time_to_watch_for and self._x_point_time_to_watch_for < self._last_arrange_position:
		self._parent.schedule_message(1, self.schedule_x_point_action_list, self._x_point_time_to_watch_for)
		self._x_point_time_to_watch_for = -1
	    self._last_arrange_position = self.song().current_song_time
	else:
	    self.set_x_point_time_to_watch()
	    
	    
    def set_x_point_time_to_watch(self):
	""" Determine which cue point time to watch for next """
	if self._x_points:
	    times = sorted(self._x_points.keys())
	    if self.song().is_playing:
		for t in times:
		    if t >= self.song().current_song_time:
			self._x_point_time_to_watch_for = t
			break
	    else:
		self._x_point_time_to_watch_for = -1
		
		
    def schedule_x_point_action_list(self, point):
	self._parent.handle_xclip_name(self.song().view.selected_track, self._x_points[point])
	    
    
    def remove_cue_point_listeners(self):
	for cp in self.song().cue_points:
	    if cp.time_has_listener(self.cue_points_changed):
		cp.remove_time_listener(self.cue_points_changed)
	    if cp.name_has_listener(self.cue_points_changed):
		cp.remove_name_listener(self.cue_points_changed)
	self._x_points = {}
	self._x_point_time_to_watch_for = -1
	
	
    def disconnect(self):
	self.remove_cue_point_listeners()
	self.song().remove_current_song_time_listener(self.arrange_time_changed)
	self.song().remove_is_playing_listener(self.arrange_time_changed)
	self.song().remove_cue_points_listener(self.cue_points_changed)
	
    
    def on_enabled_changed(self):
	pass
        

    def update(self):    
        pass
    