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
   
class ClyphXClipActions(ControlSurfaceComponent):
    __module__ = __name__
    __doc__ = ' Clip-related actions '

    def __init__(self, parent):
        ControlSurfaceComponent.__init__(self)
        self._parent = parent
	
	
    def set_clip_on_off(self, clip, track, xclip, ident, value = None):
	""" Toggles or turns clip on/off """
	if value in KEYWORDS:
	    clip.muted = not(KEYWORDS[value])
	else:
	    clip.muted = not(clip.muted)
	    
	    
    def set_warp(self, clip, track, xclip, ident, value = None):
	""" Toggles or turns clip warp on/off """
	if clip.is_audio_clip:
	    value = value.strip()
	    if value in KEYWORDS:
		clip.warping = KEYWORDS[value]
	    else:
		clip.warping = not(clip.warping)
	    
	    
    def adjust_time_signature(self, clip, track, xclip, ident, args):
	""" Adjust clip's time signature """
	if '/' in args:
	    name_split = args.split('/')
	    try:
		clip.signature_numerator = int(name_split[0].strip())
		clip.signature_denominator = int(name_split[1].strip())
	    except: pass
	    
	    
    def adjust_detune(self, clip, track, xclip, ident, args):
	""" Adjust/set audio clip detune """
	if clip.is_audio_clip:
	    args = args.strip()
	    if args.startswith(('<', '>')):
		factor = self._parent.get_adjustment_factor(args)
		clip.pitch_fine = max(-50, min(49, (clip.pitch_fine + factor)))
	    else:
		try:
		    clip.pitch_fine = int(args)
		except: pass
		
		
    def adjust_transpose(self, clip, track, xclip, ident, args):
	""" Adjust audio or midi clip transpose, also set audio clip transpoe """
	args = args.strip()
	if args.startswith(('<', '>')):
	    factor = self._parent.get_adjustment_factor(args)
	    if clip.is_audio_clip:
		clip.pitch_coarse = max(-48, min(48, (clip.pitch_coarse + factor)))
	    elif clip.is_midi_clip:
		self.do_note_pitch_adjustment(clip, factor)
	else:
	    if clip.is_audio_clip:
		try:
		    clip.pitch_coarse = int(args)
		except: pass
		
		
    def adjust_start(self, clip, track, xclip, ident, args):
	""" Adjust/set clip start """
	args = args.strip()
	if args.startswith(('<', '>')):
	    factor = self._parent.get_adjustment_factor(args, True)
	    clip.loop_start = max(0.0, min(clip.loop_end - factor, (clip.loop_start + factor)))
	else:
	    try:
		clip.loop_start = float(args)
	    except: pass
	    
	    
    def adjust_end(self, clip, track, xclip, ident, args):
	""" Adjust/set clip end """
	args = args.strip()
	if args.startswith(('<', '>')):
	    factor = self._parent.get_adjustment_factor(args, True)
	    clip.loop_end = max((clip.loop_start - factor), (clip.loop_end + factor))
	else:
	    try:
		clip.loop_end = float(args)
	    except: pass
	    
	    
    def adjust_cue_point(self, clip, track, xclip, ident, args):
	""" Adjust clip's start point and fire (also stores cue point if not specified). Will not fire xclip itself as this causes a loop """
	if not type(xclip) is Live.Clip.Clip:
	    return()
	if clip.is_midi_clip or (clip.is_audio_clip and clip.warping):
	    if args:
		args = args.strip()
		if args.startswith(('<', '>')):
		    factor = self._parent.get_adjustment_factor(args, True)
		    args = clip.loop_start + factor
		try:
		    clip.loop_start = float(args)
		    if clip.looping:
			clip.looping = False
			clip.loop_start = float(args)
			clip.looping = True
		    if clip != xclip: 
			clip.fire()
		except: pass
	    else:
		xclip.name = xclip.name.strip() + ' ' + str(clip.loop_start)
		    
	    
    def do_clip_loop_action(self, clip, track, xclip, ident, args):
	""" Handle clip loop actions  """
	args = args.strip()
	if args == '' or args in KEYWORDS:
	    self.set_loop_on_off(clip, args)
	else:
	    if clip.looping:
		clip_stats = self.get_clip_stats(clip)
		new_start = clip.loop_start  
		new_end = clip.loop_end  
		if args.startswith(('<', '>')):
		    self.move_clip_loop_by_factor(clip, args, clip_stats)
		    return()
		elif args == 'RESET':
		    new_start = 0.0
		    new_end = clip_stats['real_end']
		elif args.startswith('*'):
		    try:
			new_end = (clip.loop_end - clip_stats['loop_length']) + (clip_stats['loop_length'] * float(args[1:]))
		    except: pass
		else:
		    self.do_loop_set(clip, args, clip_stats)
		    return()
		self.set_new_loop_position(clip, new_start, new_end, clip_stats)
		    
		    
    def set_loop_on_off(self, clip, value = None):
	""" Toggles or turns clip loop on/off """
	if value in KEYWORDS:
	    clip.looping = KEYWORDS[value]
	else:
	    clip.looping = not(clip.looping)
	    
	    
    def move_clip_loop_by_factor(self, clip, args, clip_stats):
	""" Move clip loop by its length or by a specified factor """
	factor = clip_stats['loop_length']
	if args == '<':
	    factor = -(factor)
	if len(args) > 1:
	    factor = self._parent.get_adjustment_factor(args, True)
	new_end = clip.loop_end + factor
	new_start = clip.loop_start + factor
	if new_start < 0.0:
	    new_end = new_end - new_start
	    new_start = 0.0
	self.set_new_loop_position(clip, new_start, new_end, clip_stats)
	
	
    def do_loop_set(self, clip, args, clip_stats):
	""" Set loop length and (if clip is playing) position, quantizes to 1/4 by default or bar if specified """
	try:
	    qntz = False
	    if 'B' in args:
		qntz = True
	    bars_to_loop = float(args.strip('B'))    
	    bar = (4.0 / clip.signature_denominator) * clip.signature_numerator
	    if not clip.is_playing:
		start = clip.loop_start
	    else:
		start = round(clip.playing_position)
		if qntz:
		    distance = start % bar
		    if distance <= bar / 2:
			start = start - distance
		    else:
			start = start + (bar - distance) 		
	    end = start + (bar * bars_to_loop)
	    if end <= clip_stats['clip_length']:
		new_end = end
		new_start = start
	    else:
		new_start = clip_stats['real_end'] - (bar * bars_to_loop)
		new_end = clip_stats['real_end']
	    self.set_new_loop_position(clip, new_start, new_end, clip_stats)
	except: pass
	
	
    def set_new_loop_position(self, clip, new_start, new_end, clip_stats):
	""" For use with other clip loop actions, ensures that loop settings are within range and applies in correct order """
	if new_end <= clip_stats['real_end'] and new_start >= 0:
	    if new_end > clip.loop_start:
		clip.loop_end = new_end
		clip.loop_start = new_start
	    else:
		clip.loop_start = new_start
		clip.loop_end = new_end
		
		
    def do_clip_note_action(self, clip, track, xclip, ident, args):
	""" Handle clip note actions """
	if clip.is_audio_clip:
	    return()
	note_data = self.get_notes_to_operate_on(clip, args.strip())
	if note_data['notes_to_edit']:
	    if note_data['args'] == '' or note_data['args'] in KEYWORDS:
		self.set_notes_on_off(clip, note_data['args'], note_data['notes_to_edit'], note_data['other_notes'])
	    elif note_data['args'] == 'REV':
		self.do_note_reverse(clip, note_data['args'], note_data['notes_to_edit'], note_data['other_notes'])
	    elif note_data['args'] in ('CMB', 'SPLIT'):
		self.do_note_split_or_combine(clip, note_data['args'], note_data['notes_to_edit'], note_data['other_notes'])
	    elif note_data['args'].startswith(('GATE <', 'GATE >')):
		self.do_note_gate_adjustment(clip, note_data['args'], note_data['notes_to_edit'], note_data['other_notes'])
	    elif note_data['args'] == 'DEL':
		self.do_note_delete(clip, note_data['args'], note_data['notes_to_edit'], note_data['other_notes'])
	    elif note_data['args'] in ('VELO <<', 'VELO >>'): 
		self.do_note_crescendo(clip, note_data['args'], note_data['notes_to_edit'], note_data['other_notes'])
	    elif note_data['args'].startswith('VELO'):
		self.do_note_velo_adjustment(clip, note_data['args'], note_data['notes_to_edit'], note_data['other_notes'])
		
	    
    def set_notes_on_off(self, clip, args, notes_to_edit, other_notes): 
	""" Toggles or turns note mute on/off """
	edited_notes = []
	for n in notes_to_edit:
	    new_mute = False
	    if args == '':
		new_mute = not(n[4])
	    elif args == 'ON':
		new_mute = True
	    edited_notes.append((n[0], n[1], n[2], n[3], new_mute))
	if edited_notes:
	    self.write_all_notes(clip, edited_notes, other_notes)
	
			
    def do_note_pitch_adjustment(self, clip, factor): 
	""" Adjust note pitch. This isn't a note action, it's called via Clip Semi """
	edited_notes = []
	note_data = self.get_notes_to_operate_on(clip)
	if note_data['notes_to_edit']:
	    for n in note_data['notes_to_edit']:
		new_pitch = n[0] + factor
		if not new_pitch in range (128):
		    edited_notes = []
		    return()
		else:
		    edited_notes.append((new_pitch, n[1], n[2], n[3], n[4]))
	    if edited_notes:
		self.write_all_notes(clip, edited_notes, note_data['other_notes'])
			
	    
    def do_note_gate_adjustment(self, clip, args, notes_to_edit, other_notes): 
	""" Adjust note gate """
	edited_notes = []
	factor = self._parent.get_adjustment_factor(args.split()[1], True)
	for n in notes_to_edit:
	    new_gate = n[2] + (factor * 0.03125)
	    if n[1] + new_gate > clip.loop_end or new_gate < 0.03125:
		edited_notes = []
		return()
	    else:
		edited_notes.append((n[0], n[1], new_gate, n[3], n[4]))
	if edited_notes:
	    self.write_all_notes(clip, edited_notes, other_notes)
	    
		
    def do_note_velo_adjustment(self, clip, args, notes_to_edit, other_notes): 
	""" Adjust/set/randomize note velocity """
	edited_notes = []
	args = args.replace('VELO ', '')
	args = args.strip()
	for n in notes_to_edit:
	    if args == 'RND':
		edited_notes.append((n[0], n[1], n[2], Live.Application.get_random_int(64, 64), n[4])) 
	    elif args.startswith(('<', '>')):
		factor = self._parent.get_adjustment_factor(args)
		new_velo = n[3] + factor
		if not new_velo in range (128):
		    edited_notes = []
		    return()
		else:
		    edited_notes.append((n[0], n[1], n[2], new_velo, n[4])) 
	    else:
		try:
		    edited_notes.append((n[0], n[1], n[2], float(args), n[4])) 
		except: pass
	if edited_notes:
	    self.write_all_notes(clip, edited_notes, other_notes)
	       
	    
    def do_note_reverse(self, clip, args, notes_to_edit, other_notes): 
	""" Reverse the position of notes """
	edited_notes = []
	for n in notes_to_edit:
	    edited_notes.append((n[0], abs(clip.loop_end - (n[1] + n[2]) + clip.loop_start), n[2], n[3], n[4]))
	if edited_notes:
	    self.write_all_notes(clip, edited_notes, other_notes)
		
		
    def do_note_split_or_combine(self, clip, args, notes_to_edit, other_notes):
	""" Split notes into 2 equal parts or combine each consecutive set of 2 notes """
	edited_notes = [] ; current_note = [] ; check_next_instance = False
	if args == 'SPLIT':
	    for n in notes_to_edit:
		if n[2] / 2 < 0.03125:
		    return()
		else:
		    edited_notes.append(n)
		    edited_notes.append((n[0], n[1] + (n[2] / 2), n[2] / 2, n[3], n[4]))
	else:
	    for n in notes_to_edit:
		edited_notes.append(n)
		if current_note and check_next_instance:
		    if current_note[0] == n[0] and current_note[1] + current_note[2] == n[1]:
			edited_notes[edited_notes.index(current_note)] = [current_note[0], current_note[1], current_note[2] + n[2], current_note[3], current_note[4]]
			edited_notes.remove(n)
			current_note = [] ; check_next_instance = False
		    else:
			current_note = n
		else:
		    current_note = n
		    check_next_instance = True
	if edited_notes:
	    self.write_all_notes(clip, edited_notes, other_notes)
	    
    
    def do_note_crescendo(self, clip, args, notes_to_edit, other_notes):
	""" Applies crescendo/decrescendo to notes """
	edited_notes = []; last_pos = -1; pos_index = 0; new_pos = -1; new_index = 0
	sorted_notes = sorted(notes_to_edit, key=lambda note: note[1], reverse=False)
	if args == 'VELO <<':
	    sorted_notes = sorted(notes_to_edit, key=lambda note: note[1], reverse=True)
	for n in sorted_notes:
	    if n[1] != last_pos:
		last_pos = n[1]
		pos_index += 1
	for n in sorted_notes:
	    if n[1] != new_pos:
		new_pos = n[1]
		new_index += 1
	    edited_notes.append((n[0], n[1], n[2], ((128 / pos_index) * new_index) - 1, n[4]))
	if edited_notes:
	    self.write_all_notes(clip, edited_notes, other_notes)
	    
	    
    def do_note_delete(self, clip, args, notes_to_edit, other_notes): 
	""" Delete notes """
	self.write_all_notes(clip, [], other_notes)

	
    def get_clip_stats(self, clip):
	""" Get real length and end of looping clip """
	clip.looping = 0
	length = clip.length
	end = clip.loop_end
	clip.looping = 1
	loop_length = clip.loop_end - clip.loop_start
	return {'clip_length' : length, 'real_end' : end, 'loop_length' : loop_length}	
    
    
    def get_notes_to_operate_on(self, clip, args = None):
	""" Get notes within loop braces to operate on """
	notes_to_edit = [] 
	other_notes = [] 
	new_args = None
	note_range = (0, 128)
	pos_range = (clip.loop_start, clip.loop_end)
	if args:
	    new_args = [a.strip() for a in args.split()]
	    note_range = self.get_note_range(new_args[0])
	    new_args.remove(new_args[0])
	    if new_args and '@' in new_args[0]:
		pos_range = self.get_pos_range(clip, new_args[0])
		new_args.remove(new_args[0])
	    new_args = " ".join(new_args)
	clip.select_all_notes()
	all_notes = clip.get_selected_notes()
	clip.deselect_all_notes()
	for n in all_notes:
	    if n[0] in range(note_range[0], note_range[1]) and n[1] <= pos_range[1] and n[1] >= pos_range[0]:
		notes_to_edit.append(n)
	    else:
		other_notes.append(n)
	return {'notes_to_edit' : notes_to_edit, 'other_notes' : other_notes, 'args' : new_args}
    
    
    def get_pos_range(self, clip, string):
	""" Get note position or range to operate on """
	pos_range = (clip.loop_start, clip.loop_end)
	user_range = string.split('-')
	try: start = float(user_range[0].replace('@', ''))
	except: start = None
	if start != None and start >= 0.0:
	    pos_range = (start, start)
	    if len(user_range) > 1:
		try: end = float(user_range[1])
		except: end = None
		if end != None:
		    pos_range = (start, end)
	return pos_range
		
	
    def get_note_range(self, string):
	""" Get note lane or range to operate on """
	note_range = (0,128)
	string = string.replace('NOTES', '')
	if string:
	    user_range = string.split('-')
	    start_note = self.string_to_note(user_range[0])
	    if start_note:
		note_range = (start_note, start_note + 1)
	    if len(user_range) > 1:
		end_note = self.string_to_note(user_range[1])
		if end_note:
		    note_range = (start_note, end_note + 1)
	return note_range
    
    
    def string_to_note(self, string):
	""" Get note value from string """
	notes = ['C', '', 'D', '', 'E', 'F', '', 'G', '', 'A', '', 'B']
	octaves = ['-2', '-1', '0', '1', '2', '3', '4', '5', '6', '7', '8',]
	converted_note = None
	base_note = None
	octave = None
	for s in string:
	    if s in notes:
		base_note = notes.index(s)
	    if base_note != None and s == '#':
		base_note += 1
	if base_note != None:
	    for o in octaves:
		if o in string:
		    base_note = base_note + (octaves.index(o) * 12)
		    break
	if base_note in range (128):
	    converted_note = base_note
	return converted_note
	 
    
    def write_all_notes(self, clip, edited_notes, other_notes):
	""" Writes new notes to clip """
	edited_notes.extend(other_notes)
	clip.select_all_notes()
	clip.replace_selected_notes(tuple(edited_notes))
	clip.deselect_all_notes()

		
    def disconnect(self):
	pass		
	    
    
    def on_enabled_changed(self):
	pass
        

    def update(self):    
        pass
    
