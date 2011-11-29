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

#--- NOTE: Action names and their corresponding values can't contain a '/' or '-' within the first four chars like this 'EX/ONE', but 'EXMP/ONE' is okay. 

GLOBAL_ACTIONS = {
    'B2A' : 'set_back_to_arrange',
    'BPM' : 'adjust_tempo',  
    'DEVFIRST' : 'move_to_first_device', 
    'DEVLAST' : 'move_to_last_device', 
    'DEVLEFT' : 'move_to_prev_device', 
    'DEVRIGHT' : 'move_to_next_device', 
    'GQ' : 'adjust_global_quantize',
    'GRV' : 'adjust_groove',
    'UP' : 'move_up',
    'DOWN' : 'move_down',
    'LEFT' : 'move_left',
    'RIGHT' : 'move_right',
    'LOOP' : 'do_loop_action',
    'LOC' : 'do_locator_action',
    'METRO' : 'set_metronome', 
    'MIDI': 'send_midi_message',
    'OVER' : 'set_overdub',    
    'PIN' : 'set_punch_in',
    'POUT' : 'set_punch_out',
    'REC' : 'set_record',
    'REDO' : 'set_redo',
    'UNDO' : 'set_undo',
    'RESTART' : 'restart_transport',
    'RQ' : 'adjust_record_quantize',
    'SIG' : 'adjust_time_signature',
    'SCENE' : 'set_scene',
    'SHOWCLIP' : 'show_clip_view',
    'SHOWDEV' : 'show_track_view',
    'STOPALL' : 'set_stop_all',
    'SETSTOP' : 'set_stop_transport',
    'SETFOLD' : 'set_fold_all',
    'SETJUMP' : 'set_jump_all',
    'TAPBPM' : 'set_tap_tempo',
    'UNARM' : 'set_unarm_all',
    'UNMUTE' : 'set_unmute_all',
    'UNSOLO' : 'set_unsolo_all'}

TRACK_ACTIONS = {
    'ARM' : 'set_arm', 
    'MUTE' : 'set_mute', 
    'SOLO' : 'set_solo',
    'MON' : 'set_monitor',
    'XFADE' : 'set_xfade',
    'SEL' : 'set_selection',
    'FOLD' : 'set_fold',
    'PLAY' : 'set_play',
    'STOP' : 'set_stop',
    'JUMP' : 'set_jump',
    'VOL' : 'adjust_volume',
    'PAN' : 'adjust_pan',
    'SEND' : 'adjust_sends',
    'CUE' : 'adjust_preview_volume',
    'XFADER' : 'adjust_crossfader',
    'IN' : 'adjust_input_routing',
    'INSUB' : 'adjust_input_sub_routing',
    'OUT' : 'adjust_output_routing',
    'OUTSUB' : 'adjust_output_sub_routing',
    'NAME' : 'set_name',
    'TOGGLEDEV' : 'set_toggle_devices_enabled'}  

CLIP_ACTIONS = {
    'CENT' : 'adjust_detune',
    'SEMI' : 'adjust_transpose',
    'CUE' : 'adjust_cue_point', 
    'END' : 'adjust_end',
    'START' : 'adjust_start',
    'LOOP' : 'do_clip_loop_action',
    'SIG' : 'adjust_time_signature',
    'WARP' : 'set_warp'} 

DEVICE_ACTIONS = {
    'CS' : 'adjust_chain_selector', 
    'RESET' : 'reset_params', 
    'RND' : 'randomize_params', 
    'SEL' : 'select_device',
    'P1' : 'adjust_best_of_bank_param', 
    'P2' : 'adjust_best_of_bank_param', 
    'P3' : 'adjust_best_of_bank_param', 
    'P4' : 'adjust_best_of_bank_param',
    'P5' : 'adjust_best_of_bank_param', 
    'P6' : 'adjust_best_of_bank_param', 
    'P7' : 'adjust_best_of_bank_param', 
    'P8' : 'adjust_best_of_bank_param', 
    'B1' : 'adjust_banked_param', 
    'B2' : 'adjust_banked_param', 
    'B3' : 'adjust_banked_param', 
    'B4' : 'adjust_banked_param', 
    'B5' : 'adjust_banked_param', 
    'B6' : 'adjust_banked_param', 
    'B7' : 'adjust_banked_param', 
    'B8' : 'adjust_banked_param'}

LOOPER_ACTIONS = {
    'LOOPER' : 'set_looper_on_off', 
    'REV' : 'set_looper_rev', 
    'OVER' : 'set_looper_state',
    'PLAY' : 'set_looper_state', 
    'REC' : 'set_looper_state', 
    'STOP': 'set_looper_state'}   

KEYWORDS = {'ON' : 1, 'OFF' : 0} 

GQ_STATES = {'NONE' : 0, '8 BARS' : 1, '4 BARS' : 2, '2 BARS' : 3, '1 BAR' : 4, '1/2' : 5, '1/2T' : 6, '1/4' : 7, '1/4T' : 8, '1/8' : 9, '1/8T' : 10, '1/16' : 11, '1/16T' : 12, '1/32' : 13}
RQ_STATES = {'NONE' : 0, '1/4' : 1, '1/8' : 2, '1/8T' : 3, '1/8 + 1/8T' : 4, '1/16' : 5, '1/16T' : 6, '1/16 + 1/16T' : 7, '1/32' : 8}

XFADE_STATES = {'A': 0, 'OFF' : 1, 'B' : 2}
MON_STATES = {'IN' : 0, 'AUTO' : 1, 'OFF' : 2}

LOOPER_STATES = {'STOP': 0.0, 'REC' : 1.0, 'PLAY' : 2.0, 'OVER' : 3.0}
