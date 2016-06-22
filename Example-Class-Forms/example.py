__window__.Close()

# example function definition
from Autodesk.Revit.UI import TaskDialog
from Autodesk.Revit.DB import FilteredElementCollector, ElementId, Element, Transaction
from Autodesk.Revit.DB.Architecture import RoomFilter
from System.Collections.Generic import List

def selectRoomByNameHeight(text, height,bool1,int1, date1):
    '''Select all Rooms in this view containing 'Name' and the given limited height \
(only the two first parameters matter in this example) :'''
    uidoc = __revit__.ActiveUIDocument
    doc = uidoc.Document
    view = uidoc.ActiveGraphicalView
    roomfilter = RoomFilter()
    rooms = FilteredElementCollector(doc, view.Id).WherePasses(roomfilter).ToElements()
    select = [room.Id for room in rooms if room.UnboundedHeight <= height and \
         text.lower() in Element.Name.GetValue(room).lower()]
         
    uidoc.Selection.SetElementIds(List[ElementId](select))
    
    #feedback test
    TaskDialog.Show('Test feedback', 
        '{0} Rooms named "{1}" UnboundedHeight < "{2}":\
            \nbool: {3}\n number{4}\n date :{5}'.format(
                len(select), text, height, bool1, int1, date1))

            
# import class winforms
from userform import InputFormParameters

listheight = ['2.80','2.90','3.10','3.50']
listdays = ['10','15','20','25']

# creation of input box
dialog = InputFormParameters(
    selectRoomByNameHeight,                 # ref function
    
    ['Wanted Room Name', 'text'],            # type text
    
    ['Limited Height', 'float', listheight],  # type decimal with a combobox
    
    ['Activate option ', 'bool'],            # type boolean
    
    ['Number of days', 'int', listdays, False], # type integer with a combobox (read only)
    
    ['Choose The Date', 'date']             # type date
    )

# display the form
dialog.showBox()

'''
#other way 

dialog = InputFormParameters(selectRoomByNameHeight)

dialog.signature = [
    ['Text to search','text'],
    ['Limited Height','float'],
    ['Activate option ','bool'],
    ['Number of days','int'],
    ['Choose The Date', 'date']
    ]
    
dialog.Text = 'Window title'

dialog.infomain.Text = 'Give another description'

dialog.panelparams[2].invert() #Default : True

dialog.showBox()

'''
