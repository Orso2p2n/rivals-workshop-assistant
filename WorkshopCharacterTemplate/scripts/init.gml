hurtbox_spr = asset_get("ex_guy_hurt_box");
crouchbox_spr = asset_get("ex_guy_crouch_box");
air_hurtbox_spr = -1;
hitstun_hurtbox_spr = -1;

char_height = 52;
idle_anim_speed = .1;
crouch_anim_speed = .1;
walk_anim_speed = .125;
dash_anim_speed = .2;
pratfall_anim_speed = .25;

walk_speed = 3.25;
walk_accel = 0.2;
walk_turn_time = 6;
initial_dash_time = 14;
initial_dash_speed = 8;
dash_speed = 7.5;
dash_turn_time = 10;
dash_turn_accel = 1.5;
dash_stop_time = 4;
dash_stop_percent = .35; //the value to multiply your hsp by when going into idle from dash or dashstop
ground_friction = .5;
moonwalk_accel = 1.4;

jump_start_time = 5;
jump_speed = 13;
short_hop_speed = 8;
djump_speed = 12;
leave_ground_max = 7; //the maximum hsp you can have when you go from grounded to aerial without jumping
max_jump_hsp = 7; //the maximum hsp you can have when jumping from the ground
air_max_speed = 7; //the maximum hsp you can accelerate to when in a normal aerial state
jump_change = 3; //maximum hsp when double jumping. If already going faster, it will not slow you down
air_accel = .3;
prat_fall_accel = .85; //multiplier of air_accel while in pratfall
air_friction = .02;
max_djumps = 1;
double_jump_time = 32; //the number of frames to play the djump animation. Can't be less than 31.
walljump_hsp = 7;
walljump_vsp = 11;
walljump_time = 32;
max_fall = 13; //maximum fall speed without fastfalling
fast_fall = 16; //fast fall speed
gravity_speed = .65;
hitstun_grav = .5;
knockback_adj = 1.0; //the multiplier to KB dealt to you. 1 = default, >1 = lighter, <1 = heavier

land_time = 4; //normal landing frames
prat_land_time = 3;
wave_land_time = 8;
wave_land_adj = 1.35; //the multiplier to your initial hsp when wavelanding. Usually greater than 1
wave_friction = .04; //grounded deceleration when wavelanding

//crouch animation frames
crouch_startup_frames = 1;
crouch_active_frames = 1;
crouch_recovery_frames = 1;

//parry animation frames
dodge_startup_frames = 1;
dodge_active_frames = 1;
dodge_recovery_frames = 3;

//tech animation frames
tech_active_frames = 3;
tech_recovery_frames = 1;

//tech roll animation frames
techroll_startup_frames = 2
techroll_active_frames = 2;
techroll_recovery_frames = 2;
techroll_speed = 10;

//airdodge animation frames
air_dodge_startup_frames = 1;
air_dodge_active_frames = 2;
air_dodge_recovery_frames = 3;
air_dodge_speed = 7.5;

//roll animation frames
roll_forward_startup_frames = 2;
roll_forward_active_frames = 4;
roll_forward_recovery_frames = 2;
roll_back_startup_frames = 2;
roll_back_active_frames = 4;
roll_back_recovery_frames = 2;
roll_forward_max = 9; //roll speed
roll_backward_max = 9;

land_sound = asset_get("sfx_land_med");
landing_lag_sound = asset_get("sfx_land");
waveland_sound = asset_get("sfx_waveland_zet");
jump_sound = asset_get("sfx_jumpground");
djump_sound = asset_get("sfx_jumpair");
air_dodge_sound = asset_get("sfx_quick_dodge");

//visual offsets for when you're in Ranno's bubble
bubble_x = 0;
bubble_y = 8;

lib_draw_sprite()

// #region vvv LIBRARY DEFINES AND MACROS vvv
// DANGER File below this point will be overwritten! Generated defines and macros below.
// Write NO-INJECT in a comment above this area to disable injection.
trackpoints = [
	{
		anim_name: "fair", anim_id: sprite_get("fair"), name: "track_1", data: [
			{frame: 2, x: 37 - sprite_get_xoffset(sprite_get("fair")), y: 45 - sprite_get_xoffset(sprite_get("fair")), width: 28, height: 28},
			{frame: 3, x: 39 - sprite_get_xoffset(sprite_get("fair")), y: 45 - sprite_get_xoffset(sprite_get("fair")), width: 28, height: 28},
			{frame: 4, x: 15 - sprite_get_xoffset(sprite_get("fair")), y: 48 - sprite_get_xoffset(sprite_get("fair")), width: 28, height: 28},
		]
	},
	{
		anim_name: "fair", anim_id: sprite_get("fair"), name: "track_2", data: [
			{frame: 1, x: 18 - sprite_get_xoffset(sprite_get("fair")), y: 16 - sprite_get_xoffset(sprite_get("fair")), width: 28, height: 28},
			{frame: 2, x: 18 - sprite_get_xoffset(sprite_get("fair")), y: 16 - sprite_get_xoffset(sprite_get("fair")), width: 28, height: 28},
		]
	},
	{
		anim_name: "jab", anim_id: sprite_get("jab"), name: "hitbox_1", data: [
			{frame: 1, x: 46 - sprite_get_xoffset(sprite_get("jab")), y: 27 - sprite_get_xoffset(sprite_get("jab")), width: 28, height: 28},
			{frame: 2, x: 46 - sprite_get_xoffset(sprite_get("jab")), y: 27 - sprite_get_xoffset(sprite_get("jab")), width: 28, height: 28},
			{frame: 3, x: 46 - sprite_get_xoffset(sprite_get("jab")), y: 27 - sprite_get_xoffset(sprite_get("jab")), width: 28, height: 28},
			{frame: 4, x: 48 - sprite_get_xoffset(sprite_get("jab")), y: 16 - sprite_get_xoffset(sprite_get("jab")), width: 28, height: 28},
		]
	},
];

#define lib_draw_sprite // Version 0
    // sprite, subimg, x, y, ?{rot=0, col=c_white, alpha=1}
    var sprite = argument[0]
    if is_string(sprite) {
        sprite = sprite_get(sprite)
    }

    var subimg = argument[1]
    var x = argument[2]
    var y = argument[3]
    var params = {}
    if argument_count == 5 {
        params = argument[4]
    }
    if argument_count > 5 {
        print("draw_sprite called with too many arguments. Use a parameter struct instead. `lib_draw_sprite(_sprite, _subimg, _x, _y, {alpha:0.5})`") // Todo, improve this with instructions.
        var die = 1/0
    }

    var xscale = 1
    if 'xscale' in params {
        xscale = params.xscale
    }
    var yscale = 1
    if 'yscale' in params {
        yscale = params.yscale
    }
    var rot = 0
    if 'rot' in params {
        rot = params.rot
    }
    var col = c_white
    if 'col' in params {
        col = params.col
    }
    var alpha = 1
    if 'alpha' in params {
        alpha = params.alpha
    }
    draw_sprite_ext(sprite, subimg, x, y, xscale, yscale, rot, col, alpha)
// DANGER: Write your code ABOVE the LIBRARY DEFINES AND MACROS header or it will be overwritten!
// #endregion