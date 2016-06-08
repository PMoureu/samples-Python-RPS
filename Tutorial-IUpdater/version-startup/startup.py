# script that is run when Revit starts in the IExternalApplication.Startup event.
from Autodesk.Revit.DB import Element, ChangePriority, SubTransaction
from Autodesk.Revit.DB import IUpdater, UpdaterId, UpdaterRegistry
from Autodesk.Revit.DB.Architecture import RoomFilter
from Autodesk.Revit.UI import TaskDialog
from System import Guid

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
            
########## Events functions

def unreg_RoomUpdater(sender, args):
    '''event type function to globally unregister the updater'''
    if UpdaterRegistry.IsUpdaterRegistered(my_updater.GetUpdaterId()):
        
        UpdaterRegistry.UnregisterUpdater(my_updater.GetUpdaterId())

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
        UpdaterRegistry.RegisterUpdater(my_updater, doc)
        roomfilter = RoomFilter()
        UpdaterRegistry.AddTrigger(my_updater.GetUpdaterId(), 
                                   roomfilter, Element.GetChangeTypeGeometry())
                                   
        UpdaterRegistry.AddTrigger(my_updater.GetUpdaterId(), 
                                   roomfilter, Element.GetChangeTypeElementAddition())
        
        # only for the test :
        TaskDialog.Show("MyRoomUpdater", 'MyRoomUpdater is enabled for this project')
    else:
        TaskDialog.Show("MyRoomUpdater", 'MyRoomUpdater is disabled for this project')

def removeUpdater(sender, args):
    '''event type function to unregister the updater from a document'''
    doc = args.Document
    
    if UpdaterRegistry.IsUpdaterRegistered(my_updater.GetUpdaterId(), doc):
    
        UpdaterRegistry.UnregisterUpdater(my_updater.GetUpdaterId(), doc)

########## Launch

if __name__ == '__main__':
    
    try:
        #create an instance 
        app = __revit__.Application
        my_updater = MyRoomUpdater(app.ActiveAddInId)
        
        # plug functions on events
        __uiControlledApplication__.ControlledApplication.DocumentOpened += checkUpdater
        __uiControlledApplication__.ControlledApplication.DocumentClosing += removeUpdater
        __uiControlledApplication__.ApplicationClosing += unreg_RoomUpdater
        
        __window__.Close()
        
    except:
        import traceback       # note: add a python27 library to your search path first!
        traceback.print_exc()  # helps you debug when things go wrong
        
