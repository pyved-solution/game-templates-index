"""
define all your actors here
"""
from . import glvars
from .glvars import pyv


def new_player():
	data = {}
	
	return pyv.new_actor('player', locals())
