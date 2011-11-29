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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.    See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA    02111-1307    USA
#
# For questions regarding this module contact
# Stray <stray411@hotmail.com>
"""

import Live 
import sys
from _Framework.ControlSurface import ControlSurface 
from _Framework.ControlSurfaceComponent import ControlSurfaceComponent
from Macrobat import Macrobat
from ExtraPrefs import ExtraPrefs
from ClyphXTrackActions import ClyphXTrackActions
from ClyphXSnapActions import ClyphXSnapActions
from ClyphXGlobalActions import ClyphXGlobalActions
from ClyphXDeviceActions import ClyphXDeviceActions
from ClyphXClipActions import ClyphXClipActions
from ClyphXControlSurfaceActions import ClyphXControlSurfaceActions
from ClyphXTriggers import ClyphXTrackComponent, ClyphXControlComponent, ClyphXCueComponent
from consts import *

class ClyphX(ControlSurface):
    __module__ = __name__
    __doc__ = " ClyphX Main "
    
    def __init__(self, c_instance):
        ControlSurface.__init__(self, c_instance)
        self.set_suppress_rebuild_requests(True) 
        self._folder_location = '/ClyphX/'
        self._macrobat = Macrobat(self)
        self._extra_prefs = ExtraPrefs(self)
        self._track_actions = ClyphXTrackActions(self)
        self._snap_actions = ClyphXSnapActions(self)
        self._global_actions = ClyphXGlobalActions(self)
        self._device_actions = ClyphXDeviceActions(self)
        self._clip_actions = ClyphXClipActions(self)
        self._control_surface_actions = ClyphXControlSurfaceActions(self)
        self._control_component = ClyphXControlComponent(self)
        ClyphXCueComponent(self)
        self._startup_actions_complete = False
        self._user_variables = {}
        self._play_seq_clips = {}
        self._loop_seq_clips = {}
        self._current_tracks = []
        live = Live.Application.get_application()
        self._can_have_nested_devices = False
        if live.get_major_version() == 8 and live.get_minor_version() >= 2 and live.get_bugfix_version() >= 2:
            self._can_have_nested_devices = True
        self.setup_tracks()
        self.log_message('nativeKONTROL LOG ------- nativeKONTROL ClyphX v2.0.3 for Live 8 ------- Live Version: ' + str(live.get_major_version()) + '.' + str(live.get_minor_version()) + '.' + str(live.get_bugfix_version()) + ' ------- END LOG')
        self.show_message('nativeKONTROL ClyphX v2.0.3 for Live 8')
        self.set_suppress_rebuild_requests(False) 
        
        
    def action_dispatch(self, tracks, xclip, action_name, args, ident):
        """ Main dispatch for calling appropriate class of actions, passes all necessary arguments to class method """
        if tracks:
            if action_name.startswith('SNAP'):
                self._snap_actions.store_track_snapshot(tracks, xclip, ident, action_name, args) 
            elif action_name.startswith('SURFACE'):
                self._control_surface_actions.dispatch_cs_action(tracks[0], xclip, ident, action_name, args)
            elif action_name in GLOBAL_ACTIONS:
                getattr(self._global_actions, GLOBAL_ACTIONS[action_name])(tracks[0], xclip, ident, args)
            for t in tracks:            
                if action_name in TRACK_ACTIONS:
                    getattr(self._track_actions, TRACK_ACTIONS[action_name])(t, xclip, ident, args)
                elif action_name == 'LOOPER': 
                    if args and args.split()[0] in LOOPER_ACTIONS: 
                        getattr(self._device_actions, LOOPER_ACTIONS[args.split()[0]])(t, xclip, ident, args)
                    elif action_name in LOOPER_ACTIONS:
                        getattr(self._device_actions, LOOPER_ACTIONS[action_name])(t, xclip, ident, args)
                elif action_name.startswith('DEV'): 
                    device = self.get_device_to_operate_on(t, action_name)
                    if device:
                        if args and args.split()[0] in DEVICE_ACTIONS: 
                            getattr(self._device_actions, DEVICE_ACTIONS[args.split()[0]])(device, t, xclip, ident, args)
                        elif args and 'CHAIN' in args: 
                            self._device_actions.dispatch_chain_action(device, t, xclip, ident, args)
                        elif action_name.startswith('DEV'):
                            self._device_actions.set_device_on_off(device, t, xclip, ident, args)
                elif action_name.startswith('CLIP') and t in self.song().tracks:
                    clip = self.get_clip_to_operate_on(t, xclip, action_name)
                    if clip:
                        if args and args.split()[0] in CLIP_ACTIONS: 
                            getattr(self._clip_actions, CLIP_ACTIONS[args.split()[0]])(clip, t, xclip, ident, args.replace(args.split()[0], ''))
                        elif args and args.split()[0].startswith('NOTES'):
                            self._clip_actions.do_clip_note_action(clip, t, xclip, ident, args)
                        elif action_name.startswith('CLIP'):
                            self._clip_actions.set_clip_on_off(clip, t, xclip, ident, args)         
                                
    
    def handle_xclip_name(self, track, xclip): 
        """ Directly dispatches snapshot recall, X-Control overrides and Seq X-Clips.    Otherwise, seperates ident from action names, splits up lists of action names and calls action dispatch. """
        name = self.get_name(xclip.name)
        if name:
            if name[0] == '[' and ']' in name and ' || ' in name:
                self._snap_actions.recall_track_snapshot(name, xclip)
                return()
            if '[[' in name and ']]' in name:
                self._control_component.assign_new_actions(name)
                return()
            if name[0] == '[' and name.count('[') == 1 and name.count(']') == 1:
                ident = name[name.index('['):name.index(']')+1].strip() 
                xclip_name = name.replace(ident, '')
                xclip_name = xclip_name.strip()
                is_play_seq = False
                is_loop_seq = False
                if xclip_name == '':
                    return()
                if type(xclip) is Live.Clip.Clip and xclip_name[0] == '(' and '(PSEQ)' in xclip_name: 
                    is_play_seq = True
                    xclip_name = xclip_name.replace('(PSEQ)', '')
                elif type(xclip) is Live.Clip.Clip and xclip_name[0] == '(' and '(LSEQ)' in xclip_name: 
                    is_loop_seq = True
                    xclip_name = xclip_name.replace('(LSEQ)', '')
                action_list = []
                if ';' in xclip_name:
                    for name in xclip_name.split(';'): 
                        action_data = self.format_action_name(track, name.strip())
                        if action_data:
                            action_list.append(action_data)
                else:
                    action_data = self.format_action_name(track, xclip_name.strip())
                    if action_data:
                        action_list.append(action_data)
                if action_list:
                    if is_play_seq: 
                        self.handle_play_seq_action_list(action_list, xclip, ident)
                    elif is_loop_seq:
                        self._loop_seq_clips[xclip.name] = [ident, action_list]
                        self.handle_loop_seq_action_list(xclip, 0)
                    else:
                        for a in action_list:
                            self.action_dispatch(a['track'], xclip, a['action'], a['args'], ident)
                        
                        
    def format_action_name(self, origin_track, origin_name): 
        """ Replaces vars (if any) then splits up track, action name and arguments (if any) and returns dict """
        if '$' in origin_name:
            origin_name = self.handle_user_variables(origin_name)
            if origin_name == None:
                return()
        result_track = [origin_track]
        result_name = origin_name
        if len(origin_name) >= 4 and (('/' in origin_name[:4]) or ('-' in origin_name[:4] and '/' in origin_name[4:]) or (origin_name[0] == '"' and '"/' in origin_name[1:])):
            track_data = self.get_track_to_operate_on(origin_name)
            result_track = track_data[0]
            result_name = track_data[1]
        args = ''
        name = result_name.split()
        if len(name) > 1:
            args = result_name.replace(name[0], '', 1)
            result_name = result_name.replace(args, '')
        return {'track' : result_track, 'action' : result_name.strip(), 'args' : args.strip()}    
    
    
    def handle_loop_seq_action_list(self, xclip, count):
        """ Handles sequenced action lists, triggered by xclip looping """
        if self._loop_seq_clips.has_key(xclip.name):
            if count >= len(self._loop_seq_clips[xclip.name][1]):
                count = count - ((count / len(self._loop_seq_clips[xclip.name][1]))*len(self._loop_seq_clips[xclip.name][1]))
            action = self._loop_seq_clips[xclip.name][1][count]
            self.action_dispatch(action['track'], xclip, action['action'], action['args'], self._loop_seq_clips[xclip.name][0])
                        
                        
    def handle_play_seq_action_list(self, action_list, xclip, ident):
        """ Handles sequenced action lists, triggered by replaying the xclip """
        if self._play_seq_clips.has_key(xclip.name): 
            count = self._play_seq_clips[xclip.name][1] + 1
            if count > len(self._play_seq_clips[xclip.name][2])-1:
                count = 0
            self._play_seq_clips[xclip.name] = [ident, count, action_list]
        else:
            self._play_seq_clips[xclip.name] = [ident, 0, action_list]
        action = self._play_seq_clips[xclip.name][2][self._play_seq_clips[xclip.name][1]]
        self.action_dispatch(action['track'], xclip, action['action'], action['args'], ident)

        
    def do_parameter_adjustment(self, param, value):
        """" Adjust (</>, reset, random, set val) continuous params, also handles quantized param adjustment (should just use +1/-1 for those) """
        if not param.is_enabled:
            return()
        step = (param.max - param.min) / 127
        new_value = param.value
        if value.startswith(('<', '>')):
            factor = self.get_adjustment_factor(value)
            if not param.is_quantized:
                new_value += step * factor
            else:
                new_value += factor
        elif value == 'RESET' and not param.is_quantized:
            new_value = param.default_value
        elif value == 'RND' and not param.is_quantized:
            new_value = (Live.Application.get_random_int(0, 128) * step) + param.min
        else:
            try:
                if int(value) in range (128):
                    try: new_value = (int(value) * step) + param.min
                    except: new_value = param.value
            except: pass
        if new_value >= param.min and new_value <= param.max:
            param.value = new_value
            
            
    def get_adjustment_factor(self, string, as_float = False):
        """ Get factor for use with < > actions """
        factor = 1
        if len(string) > 1:
            if as_float:
                try: factor = float(string[1:])
                except: factor = 1
            else:
                try: factor = int(string[1:])
                except: factor = 1
        if string.startswith('<'): 
            factor = -(factor)
        return factor         
    
    
    def get_track_to_operate_on(self, origin_name):    
        """ Gets track or tracks to operate on """
        result_track = []
        tracks = list(self.song().tracks + self.song().return_tracks + (self.song().master_track,))
        track_range = []
        num = origin_name.split('/')[0]
        if num[0] == '"':
            track_name = num[1:num[1:].index('"') + 1]
            def_name = None
            if ' AUDIO' or ' MIDI' in track_name:
                def_name = track_name.replace(' ', '-')# In Live GUI, default names are 'n Audio' or 'n MIDI', in API it's 'n-Audio' or 'n-MIDI' 
            for track in self.song().tracks:
                name = self.get_name(track.name)
                if name == track_name or name == def_name:
                    result_track = [track]
        elif num == 'SEL':
            result_track = [self.song().view.selected_track]
        elif num == 'MST':
            result_track = [self.song().master_track]
        elif num == 'ALL':
            result_track = tracks
        elif 'GRP' in num:
            """ The form for Group tracks is GRP-"starttrackname"-"endtrackname" """
            self.log_message('GRP')
            start_track = num.split('-')[1].replace('"', '')
            end_track = num.split('-')[2].replace('"', '')
            self.log_message(start_track + ' ' + end_track)
            range_start = 0
            range_end = 0
            for i in range(len(tracks)):
                trackname = self.get_name(tracks[i].name)
                if trackname == start_track:
                    self.log_message(trackname + ' ' + str(i))
                    range_start = i
                if trackname == end_track:
                    self.log_message(trackname + ' ' + str(i))
                    range_end = i
                    break
            for t in range(range_start, range_end + 1):
                self.log_message(tracks[t].name + ' ' + str(t))
                result_track.append(tracks[t])
        elif '-' in num:
            t_range = num.split('-')
            try:
                for t in t_range:
                    t = t.strip()
                    if t == 'MST':
                        t = len(tracks)
                    else:
                        try: t = int(t) - 1
                        except: t = (ord(t.strip(' ')) - 65) + len(self.song().tracks)
                    track_range.append(t)
            except: pass
            if len(track_range) == 2 and track_range[0] >= 0 and track_range[1] > track_range[0]:
                for t in range(track_range[0], track_range[1] + 1):
                    if t < len(tracks):
                        result_track.append(tracks[t])
        
        else:
            try:
                try: track = self.song().tracks[(int(num))-1]
                except: track = self.song().return_tracks[(ord(num))-65]
                if track:
                    result_track = [track]
            except: pass
        result_name = origin_name[origin_name.index('/')+1:].strip()
        return (result_track, result_name)
    
    
    def get_device_to_operate_on(self, track, name):
        """ Get device to operate on """
        device = None
        name_split = name.split()
        if name_split[0] == 'DEV':
            device = track.view.selected_device
            if device == None:
                if track.devices:
                    device = track.devices[0]
        else:
            try:
                dev_num = name_split[0].replace('DEV', '')
                if '.' in dev_num and self._can_have_nested_devices:
                    dev_split = dev_num.split('.')
                    top_level = track.devices[int(dev_split[0]) - 1]
                    if top_level and top_level.can_have_chains:
                        device = top_level.chains[int(dev_split[1]) - 1].devices[0]
                        if len(dev_split) > 2:
                            device = top_level.chains[int(dev_split[1]) - 1].devices[int(dev_split[2]) - 1]
                else:
                    device = track.devices[int(dev_num) - 1]
            except: pass
        return device
    
    
    def get_clip_to_operate_on(self, track, xclip, name):
        """ Get clip to operate on """
        clip = None
        name_split = name.split()
        if name_split[0] == 'CLIP':
            slot = list(self.song().scenes).index(self.song().view.selected_scene)
            if track.playing_slot_index >= 0:
                slot = track.playing_slot_index
            if track.clip_slots[slot].has_clip:
                clip = track.clip_slots[slot].clip
        else:
            try:
                if track.clip_slots[int(name_split[0].replace('CLIP', ''))-1].has_clip:
                    clip = track.clip_slots[int(name_split[0].replace('CLIP', ''))-1].clip
            except: pass
        return clip
                        
    
    def handle_user_variables(self, name):
        """ Add/update entry in user variable dict or retrieves value of variable from dict """
        result = None
        if '=' in name:
            name_split = name.split('=')
            if len(name_split) == 2:
                var_name = name_split[0].replace('$', '')
                self._user_variables[str(var_name.strip())] = str(name_split[1].strip())
        else:
            var_name = name[name.index('$')+1:].split()[0]
            if self._user_variables.has_key(var_name):
                result = name.replace('$'+var_name, self._user_variables[var_name])
        return result
                
                
    def get_user_settings(self, midi_map_handle):
        """ Get user settings (variables, prefs and control settings) from text file and perform startup actions if any """
        list_to_build = None
        ctrl_data = []
        prefs_data = []
        try:
            for line in open(sys.path[1] + self._folder_location + 'UserSettings.txt'): 
                line = self.get_name(line.rstrip('\n'))
                if not line.startswith(('#', '"', 'STARTUP_ACTIONS =', 'INCLUDE_NESTED_DEVICES_IN_SNAPSHOTS =', 'SNAPSHOT_PARAMETER_LIMIT =')) and not line == '':
                    if '[USER CONTROLS]' in line:
                        list_to_build = 'controls'
                    elif '[USER VARIABLES]' in line:
                        list_to_build = 'vars'
                    elif '[EXTRA PREFS]' in line:
                        list_to_build = 'prefs'
                    else:
                        if list_to_build == 'vars' and '=' in line:
                            name_split = line.split('=')
                            if len(name_split) == 2:
                                var_name = name_split[0].replace('$', '')
                                self._user_variables[str(var_name.strip(' '))] = str(name_split[1].strip(' '))
                        elif list_to_build == 'controls' and '=' in line:
                            ctrl_data.append(line)
                        elif list_to_build == 'prefs' and '=' in line:
                            prefs_data.append(line)
                elif line.startswith('INCLUDE_NESTED_DEVICES_IN_SNAPSHOTS ='):
                    include_nested = self.get_name(line[37:].strip())
                    include_nested_devices = False
                    if include_nested.startswith('ON'):
                        include_nested_devices = True
                    self._snap_actions._include_nested_devices = include_nested_devices
                elif line.startswith('SNAPSHOT_PARAMETER_LIMIT ='):
                    try: limit = int(line[26:].strip())
                    except: limit = 500
                    self._snap_actions._parameter_limit = limit
                elif line.startswith('STARTUP_ACTIONS =') and not self._startup_actions_complete:
                    actions = line[17:].strip()
                    if actions != 'OFF':
                        action_list = '[]' + actions
                        self.schedule_message(2, self.perform_startup_actions, action_list)
                        self._startup_actions_complete = True
            if ctrl_data:
                self._control_component.get_user_control_settings(ctrl_data, midi_map_handle)
            if prefs_data:
                self._extra_prefs.get_user_settings(prefs_data)
        except: pass
            
            
    def perform_startup_actions(self, action_list):
        """ Delay startup action so it can perform actions on values that are changed upon set load (like overdub) """
        self.handle_xclip_name(self.song().view.selected_track, StartName(action_list))
            
            
    def setup_tracks(self):    
        """ Setup component tracks on ini and track list changes.    Also call Macrobat's get rack """
        for t in self.song().tracks:
            self._macrobat.setup_tracks(t)
            if (self._current_tracks and t in self._current_tracks):
                pass
            else:
                self._current_tracks.append(t)
                ClyphXTrackComponent(self, t)
        for r in self.song().return_tracks + (self.song().master_track,):
            self._macrobat.setup_tracks(r)
        self._snap_actions.setup_tracks()
            
    
    def get_name(self, name):
        """ Convert name to upper-case string or return blank string if couldn't be converted """
        try: name = str(name).upper()
        except: name = ''
        return name
            
    
    def _on_track_list_changed(self):
        ControlSurface._on_track_list_changed(self)
        self.setup_tracks()
        
        
    def connect_script_instances(self, instanciated_scripts):
        """ Pass connect scripts call to control component """
        self._control_component.connect_script_instances(instanciated_scripts) 
        self._control_surface_actions.connect_script_instances(instanciated_scripts) 
        
            
    def build_midi_map(self, midi_map_handle):
        """ Build user-defined list of midi messages for controlling ClyphX track """
        ControlSurface.build_midi_map(self, midi_map_handle)
        self.get_user_settings(midi_map_handle)
        
        
    def receive_midi(self, midi_bytes):
        """ Receive user-specified messages and send to control script """
        ControlSurface.receive_midi(self, midi_bytes)
        self._control_component.receive_midi(midi_bytes)
        
        
    def handle_sysex(self, midi_bytes):
        """ Handle sysex received from controller """
        pass    
        
    
    def disconnect(self):
        ControlSurface.disconnect(self)
        return None
    
    
class StartName:
    __module__ = __name__
    __doc__ = ' Simple class that allows startup list to have a name '
    
    def __init__(self, name = 'none'):
        self.name = name
                