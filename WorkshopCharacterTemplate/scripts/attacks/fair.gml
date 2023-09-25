set_attack_value(AT_FAIR, AG_CATEGORY, 1);
set_attack_value(AT_FAIR, AG_SPRITE, sprite_get("fair"));
set_attack_value(AT_FAIR, AG_HAS_LANDING_LAG, 1);
set_attack_value(AT_FAIR, AG_HURTBOX_SPRITE, sprite_get("fair_hurt"));

// #region vvv LIBRARY DEFINES AND MACROS vvv
// DANGER File below this point will be overwritten! Generated defines and macros below.
// Write NO-INJECT in a comment above this area to disable injection.
#macro STARTUP_FRAMES 2
#define _get_startup_frames()
    return STARTUP_FRAMES
#macro STARTUP_FRAME_START 0
#define _get_startup_frame_start()
    return STARTUP_FRAME_START

#macro ACTIVE_FRAMES 3
#define _get_active_frames()
    return ACTIVE_FRAMES
#macro ACTIVE_FRAME_START 2
#define _get_active_frame_start()
    return ACTIVE_FRAME_START

#macro ENDLAG_FRAMES 1
#define _get_endlag_frames()
    return ENDLAG_FRAMES
#macro ENDLAG_FRAME_START 5
#define _get_endlag_frame_start()
    return ENDLAG_FRAME_START
// DANGER: Write your code ABOVE the LIBRARY DEFINES AND MACROS header or it will be overwritten!
// #endregion