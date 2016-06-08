__window__.Close()
from Autodesk.Revit.DB import Element, ChangePriority, SubTransaction
from Autodesk.Revit.DB import IUpdater, UpdaterId, UpdaterRegistry
from Autodesk.Revit.UI import TaskDialog, TaskDialogCommonButtons 
from Autodesk.Revit.UI import TaskDialogCommandLinkId, TaskDialogResult
from Autodesk.Revit.DB.Architecture import RoomFilter

from startup import MyRoomUpdater

app = __revit__.Application
doc = __revit__.ActiveUIDocument.Document

# create an instance
my_updater = MyRoomUpdater(app.ActiveAddInId)

# registering state
app_dmu = UpdaterRegistry.IsUpdaterRegistered(my_updater.GetUpdaterId())
doc_dmu = UpdaterRegistry.IsUpdaterRegistered(my_updater.GetUpdaterId(), doc)

# note : the global will be unregistered when the last document is unregistered
# note2 : look at IsUpdaterEnabled and EnableUpdater/DisableUpdater too 
# note3 : enabled or not, an updater may be suspended by Revit for misbehaving


# build the dialog box
box = TaskDialog('Dynamic Model Updaters')
box.MainInstruction  = 'DoubleHeight Updater Manager'

box.MainContent = '- Document Updater is :{0} Registered'.format(' NOT' * (not doc_dmu))
box.MainContent += '\n- Global Updater is :{0} Registered'.format(' NOT' * (not app_dmu))


# add command options
if doc_dmu:
    box.AddCommandLink(TaskDialogCommandLinkId.CommandLink1, 'Disable document Updater')
    
else :
    box.AddCommandLink(TaskDialogCommandLinkId.CommandLink2, 'Enable document Updater')
    
if app_dmu:
    box.AddCommandLink(TaskDialogCommandLinkId.CommandLink3, 'Disable all documents Updater ')

# box.FooterText = 'Add comments in the footer'

# close button to abort 
box.CommonButtons = TaskDialogCommonButtons.Close

# show the dialogbox and capture the answer
answer = box.Show()


# 1st option : disable updater for current document
if answer == TaskDialogResult.CommandLink1:
    
    UpdaterRegistry.UnregisterUpdater(my_updater.GetUpdaterId(), doc)
    
# 2nd option : register the current doc
elif answer == TaskDialogResult.CommandLink2:
    
    UpdaterRegistry.RegisterUpdater(my_updater, doc)
    roomfilter = RoomFilter()
    UpdaterRegistry.AddTrigger(my_updater.GetUpdaterId(), roomfilter, Element.GetChangeTypeGeometry())
    UpdaterRegistry.AddTrigger(my_updater.GetUpdaterId(), roomfilter, Element.GetChangeTypeElementAddition())
    
# 3rd option : disable updater for all opened documents
elif answer == TaskDialogResult.CommandLink3:
    
    UpdaterRegistry.UnregisterUpdater(my_updater.GetUpdaterId())
