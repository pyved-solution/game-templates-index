from . import pimodules

pyv = pimodules.pyved_engine
enum = pyv.custom_struct.enum


TetColors = enum(
    'Clear',
    'Gray',
    'Pink'
)
