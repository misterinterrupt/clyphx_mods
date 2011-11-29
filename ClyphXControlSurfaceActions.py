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
from _Framework.ControlSurface import ControlSurface
from _Framework.SessionComponent import SessionComponent 
from _Framework.MixerComponent import MixerComponent
from _Framework.DeviceComponent import DeviceComponent
    
class ClyphXControlSurfaceActions(ControlSurfaceComponent):
    __module__ = __name__
    __doc__ = ' Actions related to control surfaces '
    
    def __init__(self, parent):
        ControlSurfaceComponent.__init__(self)
        self._parent = parent
	self._scripts = {}
	
	
    def connect_script_instances(self, instanciated_scripts):
	""" Build dict of connected scripts and their components, doesn't work with non-Framework scripts, but does work with User Remote Scripts """
	self._scripts = {}
	for index in range (len(instanciated_scripts)):
	    self._scripts[index] = {'mixer' : None, 'device' : None, 'session' : None, 'color' : False}
	    if isinstance (instanciated_scripts[index], ControlSurface):
		script_name = instanciated_scripts[index].__class__.__name__  
		if not script_name.startswith('ClyphX') and instanciated_scripts[index].components:
		    for c in instanciated_scripts[index].components:
			if isinstance (c, SessionComponent):
			    self._scripts[index]['session'] = c
			    if script_name.startswith('APC'):
				self._scripts[index]['color'] = {'GREEN' : (1, 2), 'RED' : (3, 4), 'AMBER' : (5, 6)}
				self._scripts[index]['metro'] = {'controls' : c._stop_track_clip_buttons, 'component' : None, 'override' : None}
			    if script_name == 'Launchpad':
				self._scripts[index]['color'] = {'GREEN' : (52, 56), 'RED' : (7, 11), 'AMBER' : (55, 59)}
				self._scripts[index]['metro'] = {'controls' : instanciated_scripts[index]._selector._side_buttons, 'component' : None, 'override' : instanciated_scripts[index]._selector}
			if isinstance (c, MixerComponent):
			    self._scripts[index]['mixer'] = c
			if isinstance (c, DeviceComponent):
			    self._scripts[index]['device'] = c
			        
			    
    def dispatch_cs_action(self, track, xclip, ident, action, args):  
	""" Dispatch appropriate control surface actions """
	try: 
	    script = int(action.strip('SURFACE')) - 1
	    if not self._scripts.has_key(script): 
		return()
	except: return()
	if 'METRO ' in args and self._scripts[script].has_key('metro'):
	    self.handle_visual_metro(self._scripts[script], args)
	elif 'RING ' in args and self._scripts[script]['session']:
            self.handle_session_offset(self._scripts[script]['session'], args[5:]) 
	elif 'COLORS ' in args and self._scripts[script]['session'] and self._scripts[script]['color']:
	    self.handle_session_colors(self._scripts[script]['session'], self._scripts[script]['color'], args[7:])
	elif 'DEV LOCK' in args and self._scripts[script]['device']:
	    self._scripts[script]['device'].canonical_parent.toggle_lock()
	elif 'BANK ' in args and self._scripts[script]['mixer']:
	    self.handle_track_bank(self._scripts[script]['mixer'], self._scripts[script]['session'], args[5:])
	else:
	    if self._scripts[script]['mixer'] and '/' in args[:4]:
		self.handle_track_action(self._scripts[script]['mixer'], xclip, ident, args)
		
		
    def handle_track_action(self, mixer, xclip, ident, args):  
	""" Get control surface track(s) to operate on and call main action dispatch """
	track_start = None
	track_end = None
	track_range = args.split('/')[0]
	actions = str(args[args.index('/')+1:].strip()).split()
	new_action = actions[0]
	new_args = ''
	if len(actions) > 1:
	    new_args = ' '.join(actions[1:])
	if 'ALL' in track_range:
	    track_start = 0
	    track_end = len(mixer._channel_strips)
	elif '-' in track_range:
	    track_range = track_range.split('-')
	    try:
		track_start = int(track_range[0]) - 1
		track_end = int(track_range[1])
	    except: 
		track_start = None
		track_end = None
	else:
	    try: 
		track_start = int(track_range) - 1
		track_end = track_start + 1
	    except:
		track_start = None
		track_end = None
	if track_start != None and track_end != None:
	    if track_start in range (len(mixer._channel_strips) + 1) and track_end in range (len(mixer._channel_strips) + 1) and track_start < track_end:
		track_list = []
		for index in range (track_start, track_end):
		    if index + mixer._track_offset in range (len(mixer.tracks_to_use())):
			track_list.append(mixer.tracks_to_use()[index + mixer._track_offset])
		if track_list:
		    self._parent.action_dispatch(track_list, xclip, new_action, new_args, ident)  
   	
    
    def handle_track_bank(self, mixer, session, args):
	""" Move track bank (or session bank) and select first track in bank...this works even with controllers without banks like User Remote Scripts """
	new_offset = None
	if args == 'FIRST':
	    new_offset = 0
	elif args == 'LAST':
	    new_offset = len(mixer.tracks_to_use()) - len(mixer._channel_strips)
	else:
	    try: 
		offset = int(args)
		if offset + mixer._track_offset in range (len(mixer._channel_strips)):
		    new_offset = offset + mixer._track_offset
	    except: new_offset = None
	if new_offset >= 0:
	    if session:
		session.set_offsets(new_offset, session._scene_offset)
	    else:
		mixer.set_track_offset(new_offset)
		self.handle_track_action(mixer, 'SEL', 1) 
		
    
    def handle_session_offset(self, session, args):
	""" Handle moving session offset """
	try:
	    new_track = session._track_offset
	    new_scene = session._scene_offset
	    args = args.split()
	    for a in args:
		if 'T' in a:
		    new_track = int(a.strip('T')) - 1
		if 'S' in a:
		    new_scene = int(a.strip('S')) - 1
	    session.set_offsets(new_track, new_scene)
	except: pass
	
	
    def handle_session_colors(self, session, colors, args):
	""" Handle changing clip launch LED colors """
	args = args.split()
	if len(args) == 3:
	    for a in args:
		if not a in colors:
		    return
	    for scene_index in range(session.height()):
		scene = session.scene(scene_index)
		for track_index in range(session.width()):
		    clip_slot = scene.clip_slot(track_index)
		    clip_slot.set_started_value(colors[args[0]][0])
		    clip_slot.set_triggered_to_play_value(colors[args[0]][1])
		    clip_slot.set_recording_value(colors[args[1]][0])
		    clip_slot.set_triggered_to_record_value(colors[args[1]][1])
		    clip_slot.set_stopped_value(colors[args[2]][0])
	    session.canonical_parent.refresh_state()
	    
	    
    def handle_visual_metro(self, script, args):
	""" Handle visual metro for APC and Launchpad (should work with APC20, but untested here) """
	if 'ON' in args and not script['metro']['component']:
	    m = VisualMetro(self._parent, script['metro']['controls'], script['metro']['override']) 
	    script['metro']['component'] = m
	elif 'OFF' in args and script['metro']['component']:
	    script['metro']['component'].disconnect()
	    script['metro']['component'] = None
  

    def disconnect(self):
	pass		
	    
    
    def on_enabled_changed(self):
	pass
        

    def update(self):    
        pass    
    
    
class VisualMetro(ControlSurfaceComponent):
    __module__ = __name__
    __doc__ = ' Visual metro for APCs and Launchpad '
    
    def __init__(self, parent, controls, override):
        ControlSurfaceComponent.__init__(self)
	self._parent = parent
        self._controls = controls
	self._override = override
	self._last_beat = -1
	self.song().add_current_song_time_listener(self.on_time_changed)
	self.song().add_is_playing_listener(self.on_time_changed)
	
	
    def on_time_changed(self):
	""" Show visual metronome via control LEDs upon beat changes (will not be shown if in Launchpad User 1) """
	if self.song().is_playing and (not self._override or (self._override and self._override._mode_index != 1)):
	    time = str(self.song().get_current_beats_song_time()).split('.')
	    if self._last_beat != int(time[1])-1:
		self._last_beat = int(time[1])-1
		self.clear()
		if self._last_beat < len(self._controls):
		    self._controls[self._last_beat].turn_on()
		else:
		    self._controls[len(self._controls)-1].turn_on()
	else:
	    self.clear()
		
		
    def clear(self):
	""" Clear all control LEDs """
	for c in self._controls:
	    c.turn_off()
	
	
    def disconnect(self):
	if self._controls:
	    self.clear()
	    self.song().remove_current_song_time_listener(self.on_time_changed)	
	    self.song().remove_is_playing_listener(self.on_time_changed)
	    self._controls = None
	    
    
    def on_enabled_changed(self):
	pass
        

    def update(self):    
        pass    
    