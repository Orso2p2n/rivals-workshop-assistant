make_attack(AT_JAB,
    AG_SPRITE, sprite_get("jab"),
    AG_HURTBOX_SPRITE, sprite_get("jab_hurt")
);

// #region vvv LIBRARY DEFINES AND MACROS vvv
// DANGER File below this point will be overwritten! Generated defines and macros below.
// Write NO-INJECT in a comment above this area to disable injection.
#define make_attack // Version 0
    // make_attack(_attack_name, (value_name, value)... )
    // Sets attack values for the given attack.
    // e.g. make_attack(AT_BAIR,
    //     AG_CATEGORY, 1,
    //     AG_SPRITE, sprite_get("bair")
    // )
    var _attack_name = argument[0]
    for(var i=1; i<=argument_count-1; i+=2) {
        set_attack_value(
            _attack_name, argument[i], argument[i+1]
        )
    }

#macro STARTUP_FRAMES 1
#define _get_startup_frames()
    return STARTUP_FRAMES
#macro STARTUP_FRAME_START 0
#define _get_startup_frame_start()
    return STARTUP_FRAME_START

#macro ACTIVE_FRAMES 4
#define _get_active_frames()
    return ACTIVE_FRAMES
#macro ACTIVE_FRAME_START 1
#define _get_active_frame_start()
    return ACTIVE_FRAME_START

#macro ENDLAG_FRAMES 2
#define _get_endlag_frames()
    return ENDLAG_FRAMES
#macro ENDLAG_FRAME_START 5
#define _get_endlag_frame_start()
    return ENDLAG_FRAME_START
// DANGER: Write your code ABOVE the LIBRARY DEFINES AND MACROS header or it will be overwritten!
// #endregion