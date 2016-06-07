from Autodesk.Revit.DB import Element, ChangePriority, SubTransaction
from Autodesk.Revit.DB import IUpdater, UpdaterId, UpdaterRegistry
from Autodesk.Revit.DB.Architecture import RoomFilter
from Autodesk.Revit.UI import TaskDialog, TaskDialogCommonButtons 
from Autodesk.Revit.UI import TaskDialogCommandLinkId, TaskDialogResult
from System import Guid

app = __revit__.Application

########## Iupdater Class

class MyRoomUpdater(IUpdater):

    def __init__(self, addinId):
        '''type UpdaterId, choose a different GUID for each updater ! '''
        self.updaterID = UpdaterId(addinId, Guid("CBCBF6B2-4C06-42d4-97C1-D1B4EB593EFF"))

    def GetUpdaterId(self):
        return self.updaterID
        
    def GetUpdaterName(self):
        '''text displayed in the warning dialog'''
        return 'MyRoomUpdater (DoubleHeight)'
    
    def GetAdditionalInformation(self):
        '''called with Execute'''
        return 'MyRoomUpdater (explanation, details, warnings...)'
        
    def GetChangePriority(self):
        '''nature of the change to let Revit order all modifications '''
        return ChangePriority.RoomsSpacesZones
        
    def Execute(self, updaterData):
        ''' UpdaterData is a parameter given by the API => scope of execution
        see last chapter and API manual for more details about members of this class'''
        
        up_doc = updaterData.GetDocument()
        elems = updaterData.GetModifiedElementIds()
        elems.AddRange(updaterData.GetAddedElementIds())
        
        #use a subtransaction in the current opened transaction
        t = SubTransaction(up_doc)
        t.Start()
        
        try:
            #comment next line to avoid dialogs
            TaskDialog.Show('MyRoomUpdater', 'Refreshing {0} elements...'.format(len(elems)))
            
            for elemID in elems:
            
                elem = up_doc.GetElement(elemID)
                list_heightx2 = elem.GetParameters('DoubleHeight')
                
                if list_heightx2:
                    heightx2 = list_heightx2[0]
                    heightx2.Set(elem.UnboundedHeight * 2)
                    
            t.Commit()
            
        except:
            t.RollBack()


########## Instance

myroomupdater = MyRoomUpdater(app.ActiveAddInId)

########## Events functions

def doc_register(proj):
    UpdaterRegistry.RegisterUpdater(myroomupdater, proj)
    filter = RoomFilter()
    UpdaterRegistry.AddTrigger(myroomupdater.GetUpdaterId(), filter, Element.GetChangeTypeGeometry())
    UpdaterRegistry.AddTrigger(myroomupdater.GetUpdaterId(), filter, Element.GetChangeTypeElementAddition())


def doc_unregister(proj):
    if UpdaterRegistry.IsUpdaterRegistered(myroomupdater.GetUpdaterId(), proj):
        UpdaterRegistry.UnregisterUpdater(myroomupdater.GetUpdaterId(), proj)
        
        
def global_unregister():
    if UpdaterRegistry.IsUpdaterRegistered(myroomupdater.GetUpdaterId()):
        UpdaterRegistry.UnregisterUpdater(myroomupdater.GetUpdaterId())


def checkUpdater(sender, args):
    '''event type function to check if updater is needed,
    if the specific parameter is found -> registering '''
    doc = args.Document
    
    paramHx2 = False
    params_proj = doc.ParameterBindings.GetEnumerator()
    params_proj.Reset()
    while params_proj.MoveNext():
        if params_proj.Key.Name == 'DoubleHeight':
            paramHx2 = True
            break
            
    if paramHx2 :
        #register the updater
        doc_register(doc)
        
        # only for the test :
        TaskDialog.Show("MyRoomUpdater", 'MyRoomUpdater is enabled for this project')
    else:
        TaskDialog.Show("MyRoomUpdater", 'MyRoomUpdater is disabled for this project')

def removeUpdater(sender, args):
    '''event type function to unregister the updater from a document'''
    doc = args.Document
    doc_unregister(doc)
    
def unreg_RoomUpdater(sender, args):
    '''event type function to globally unregister the updater'''
    global_unregister()

def dialogManager():
    '''dialogbox to manage updater state from a ribbon button'''
    #scope when dialogManager is called
    doc = __revit__.ActiveUIDocument.Document
    
    # registering state
    app_dmu = UpdaterRegistry.IsUpdaterRegistered(myroomupdater.GetUpdaterId())
    doc_dmu = UpdaterRegistry.IsUpdaterRegistered(myroomupdater.GetUpdaterId(), doc)

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
        
        doc_unregister(doc)
        
    # 2nd option : register the current doc
    elif answer == TaskDialogResult.CommandLink2:
        
        doc_register(doc)
        
    # 3rd option : disable updater for all opened documents
    elif answer == TaskDialogResult.CommandLink3:
        
        global_unregister()