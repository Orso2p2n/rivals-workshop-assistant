set_attack_value(AT_JAB, AG_SPRITE, sprite_get("jab"));
set_attack_value(AT_JAB, AG_HURTBOX_SPRITE, sprite_get("jab_hurt"));

// #region vvv LIBRARY DEFINES AND MACROS vvv
// DANGER File below this point will be overwritten! Generated defines and macros below.
// Write NO-INJECT in a comment above this area to disable injection.
#macro STARTUP_FRAMES 1
#define _get_startup_frames()
    return STARTUP_FRAMES
#macro STARTUP_FRAME_START 0
#define _get_startup_frame_start()
    return STARTUP_FRAME_START

#macro ACTIVE_FRAMES 5
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