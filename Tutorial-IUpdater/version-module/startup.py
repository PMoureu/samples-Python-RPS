# script that is run when Revit starts in the IExternalApplication.Startup event.
from updaters import checkUpdater, removeUpdater, unreg_RoomUpdater

try:
    print('...Loading RevitPythonshell & Updaters...')
    # plug functions on events
    __uiControlledApplication__.ControlledApplication.DocumentOpened += checkUpdater
    __uiControlledApplication__.ControlledApplication.DocumentClosing += removeUpdater
    __uiControlledApplication__.ApplicationClosing += unreg_RoomUpdater
    
    
    __window__.Close()
    
except:
    import traceback       # note: add a python27 library to your search path first!
    traceback.print_exc()  # helps you debug when things go wrong
        