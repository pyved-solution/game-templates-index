from .glvars import pyv

# always try to keep your event number low: model->view or model->ctrl comms only
MyEvTypes = pyv.game_events_enum((
    'ConvChoice',  # contains value
    'ConvEnds',
))
