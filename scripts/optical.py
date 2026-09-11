"""Shared optical-axis contract for generation, fitting, and validation."""
MINIMUM=9
DEFAULT=14
MAXIMUM=128
TEXT_END=16
DISPLAY_START=28
MASTER_SIZES=(9,14,16,28,128)
AXIS_RANGE=[MINIMUM,DEFAULT,MAXIMUM]

def normalized(size):
    if size < DEFAULT:return (size-DEFAULT)/(DEFAULT-MINIMUM)
    return (size-DEFAULT)/(MAXIMUM-DEFAULT)

def initial_map():
    # Constant outlines are represented by masters, not an avar plateau.
    return {-1:-1,0:0,1:1,normalized(TEXT_END):normalized(TEXT_END),
            normalized(DISPLAY_START):normalized(DISPLAY_START)}
