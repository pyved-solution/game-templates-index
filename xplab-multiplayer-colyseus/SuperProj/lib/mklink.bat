@echo off
c:
CD "C:\Users\WKTA1\Documents\git_projects\extra-pyv-templates\xplab-multiplayer-colyseus\SuperProj\lib"

MKLINK /D colyseus_sdk "..\..\..\..\colyseus.py-prototype\colyseus_sdk"

ECHO "SymLink has been created"
PAUSE
