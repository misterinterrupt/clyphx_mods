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

class ClyphXTrackActions(ControlSurfaceComponent):
    __module__ = __name__
    __doc__ = ' Track-related actions '    

    def __init__(self, parent):
        ControlSurfaceComponent.__init__(self)
        self._parent = parent

    def set_toggle_devices_enabled(self, track, xclip, ident, value = None):
        """ disable devices on a given track """
        for device in track.devices:
            if(hasattr(device, 'parameters')):
                self._parent._device_actions.set_device_on_off(device, track, xclip, ident);
        
        
    def set_name(self, track, xclip, ident, args): 
        """ Set track's name """
        if track in self.song().tracks + self.song().return_tracks:
            args = args.strip()
            if args:
                track.name = args
        
        
    def set_mute(self, track, xclip, ident, value = None):
        """ Toggles or turns on/off track mute """
        if track in self.song().tracks + self.song().return_tracks:
            if value in KEYWORDS:
                track.mute = KEYWORDS[value]
            else:
                track.mute = not(track.mute)
                
                
    def set_solo(self, track, xclip, ident, value = None):
        """ Toggles or turns on/off track solo """
        if track in self.song().tracks + self.song().return_tracks:
            if value in KEYWORDS:
                track.solo = KEYWORDS[value]
            else:
                track.solo = not(track.solo)

                                
    def set_arm(self, track, xclip, ident, value = None):
        """ Toggles or turns on/off track arm """
        if track in self.song().tracks and track.can_be_armed:
            if value in KEYWORDS:
                track.arm = KEYWORDS[value]
            else:
                track.arm = not(track.arm)
                
                
    def set_fold(self, track, xclip, ident, value = None):
        """ Toggles or turns on/off track fold """
        if track.is_foldable:
            if value in KEYWORDS:
                track.fold_state = KEYWORDS[value]
            else:
                track.fold_state = not(track.fold_state)
                   
    
    def set_monitor(self, track, xclip, ident, args):
        """ Toggles or sets monitor state """
        if track in self.song().tracks and not track.is_foldable:
            if args in MON_STATES:
                track.current_monitoring_state = MON_STATES[args]
            else:
                if track.current_monitoring_state == 2:
                    track.current_monitoring_state = 0
                else:
                    track.current_monitoring_state += 1
    
    
    def set_xfade(self, track, xclip, ident, args):
        """ Toggles or sets crossfader assignment """
        if track != self.song().master_track:
            if args in XFADE_STATES:
                track.mixer_device.crossfade_assign = XFADE_STATES[args]
            else:
                if track.mixer_device.crossfade_assign == 2:
                    track.mixer_device.crossfade_assign = 0
                else:
                    track.mixer_device.crossfade_assign += 1
                    
            
    def set_selection(self, track, xclip, ident, args):
        """ Sets track/slot selection """
        self.song().view.selected_track = track
        if track in self.song().tracks:
            if args:
                try:
                    self.song().view.selected_scene = list(self.song().scenes)[int(args.strip())-1]
                except: pass
            else:
                if track.playing_slot_index >= 0:
                    self.song().view.selected_scene = list(self.song().scenes)[track.playing_slot_index]
    
    
    def set_jump(self, track, xclip, ident, args): 
        """ Jumps playing clip on track forward/backward """
        if track in self.song().tracks:
            try: track.jump_in_running_session_clip(float(args.strip()))
            except: pass

    
    def set_stop(self, track, xclip, ident, value = None):
        """ Stops all clips on track """
        if track in self.song().tracks:
            track.stop_all_clips()
            
            
    def set_play(self, track, xclip, ident, args): 
        """ Sets slot to play or cycles between clips """
        if track in self.song().tracks:
            args = args.strip()
            slot_to_play = -1
            play_slot = track.playing_slot_index
            select_slot = list(self.song().scenes).index(self.song().view.selected_scene)
            if args == '':
                if type(xclip) is Live.Clip.Clip:
                    slot_to_play = xclip.canonical_parent.canonical_parent.playing_slot_index
                else:
                    if play_slot >= 0:
                        slot_to_play = play_slot
                    else:
                        slot_to_play = select_slot
            elif args == 'SEL':
                slot_to_play = select_slot
            elif args == 'RND' and len(self.song().scenes) > 1:#--Don't allow randomization unless more than 1 scene
                slot_to_play = Live.Application.get_random_int(0, len(self.song().scenes))
                if slot_to_play == play_slot:
                    while slot_to_play == play_slot:
                        slot_to_play = Live.Application.get_random_int(0, len(self.song().scenes))
            elif args.startswith(('<', '>')) and len(self.song().scenes) > 1:#--Don't allow adjustment unless more than 1 scene
                if track.is_foldable:
                    return()
                factor = self._parent.get_adjustment_factor(args)
                if factor < len(self.song().scenes):
                    if abs(factor) == 1:#---Only launch slots that contain clips
                        for index in range (len(self.song().scenes)):
                            play_slot += factor
                            if play_slot >= len(self.song().scenes):
                                play_slot = 0
                            if track.clip_slots[play_slot].has_clip and track.clip_slots[play_slot].clip != xclip:
                                track.clip_slots[play_slot].fire()
                                break
                        return()
                    else:
                        play_slot += factor
                        if play_slot >= len(self.song().scenes):
                            play_slot -= len(self.song().scenes)
                        elif play_slot < 0 and abs(play_slot) >= len(self.song().scenes):
                            play_slot = -(abs(play_slot) - len(self.song().scenes))            
                        slot_to_play = play_slot
            else:
                try:
                    if int(args) in range(len(self.song().scenes)):
                        slot_to_play = int(args)-1
                except: pass
            if not track.clip_slots[slot_to_play].has_clip or (track.clip_slots[slot_to_play].has_clip and track.clip_slots[slot_to_play].clip != xclip):
                track.clip_slots[slot_to_play].fire()
        
                                
    def adjust_preview_volume(self, track, xclip, ident, args): 
        """ Adjust/set master preview volume """
        if track == self.song().master_track:
            self._parent.do_parameter_adjustment(self.song().master_track.mixer_device.cue_volume, args.strip())
    
    
    def adjust_crossfader(self, track, xclip, ident, args): 
        """ Adjust/set master crossfader """
        if track == self.song().master_track:
            self._parent.do_parameter_adjustment(self.song().master_track.mixer_device.crossfader, args.strip())
            
    
    def adjust_volume(self, track, xclip, ident, args):
        """ Adjust/set track volume """
        self._parent.do_parameter_adjustment(track.mixer_device.volume, args.strip())
    
    
    def adjust_pan(self, track, xclip, ident, args): 
        """ Adjust/set track pan """
        self._parent.do_parameter_adjustment(track.mixer_device.panning, args.strip())
    
    
    def adjust_sends(self, track, xclip, ident, args):  
        """ Adjust/set track sends """
        if track != self.song().master_track:
            args = args.split()
            if len(args) > 1:
                try:
                    param = track.mixer_device.sends[ord(args[0].strip()) - 65]
                except: param = None
                if param:
                    self._parent.do_parameter_adjustment(param, args[1].strip())
                    
                    
    def adjust_input_routing(self, track, xclip, ident, args): 
        """ Adjust track input routing """
        if track in self.song().tracks and not track.is_foldable:
            routings = list(track.input_routings)
            current_routing = 0
            if track.current_input_routing in routings:
                current_routing = routings.index(track.current_input_routing)
            track.current_input_routing = self.handle_track_routing(args, routings, current_routing)
            
            
    def adjust_input_sub_routing(self, track, xclip, ident, args): 
        """ Adjust track input sub-routing """
        if track in self.song().tracks and not track.is_foldable:
            routings = list(track.input_sub_routings)
            current_routing = 0
            if track.current_input_sub_routing in routings:
                current_routing = routings.index(track.current_input_sub_routing)
            track.current_input_sub_routing = self.handle_track_routing(args, routings, current_routing)
            
            
    def adjust_output_routing(self, track, xclip, ident, args): 
        """ Adjust track output routing """
        if track != self.song().master_track:
            routings = list(track.output_routings)
            current_routing = 0
            if track.current_output_routing in routings:
                current_routing = routings.index(track.current_output_routing)
            track.current_output_routing = self.handle_track_routing(args, routings, current_routing)
            
            
    def adjust_output_sub_routing(self, track, xclip, ident, args): 
        """ Adjust track output sub-routing """
        if track != self.song().master_track:
            routings = list(track.output_sub_routings)
            current_routing = 0
            if track.current_output_sub_routing in routings:
                current_routing = routings.index(track.current_output_sub_routing)
            track.current_output_sub_routing = self.handle_track_routing(args, routings, current_routing)

            
    def handle_track_routing(self, args, routings, current_routing):
        """ Handle track routing adjustment """
        new_routing = routings[current_routing]
        args = args.strip()
        if args in ('<', '>'):
            factor = self._parent.get_adjustment_factor(args)
            if current_routing + factor in range (len(routings)):
                new_routing = routings[current_routing + factor]
        else:
            for i in routings:
                if self._parent.get_name(i) == args: 
                    new_routing = i
                    break
        return new_routing
                                        
        
    def disconnect(self):
        pass
    
    
    def on_enabled_changed(self):
        pass
        

    def update(self):    
        pass
    
    