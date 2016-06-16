__window__.Close()
from userform import InputFormParameters

from Autodesk.Revit.UI import TaskDialog
from Autodesk.Revit.DB import FilteredElementCollector, ElementId, Element, Transaction
from Autodesk.Revit.DB.Architecture import RoomFilter
from System.Collections.Generic import List

#function definition
def selectRoomByNameHeight(text, height, bool1, int1):
    '''Select Rooms in view containing 'text' where unbounded height < height'''
    uidoc = __revit__.ActiveUIDocument
    doc = uidoc.Document
    view = uidoc.ActiveGraphicalView
    roomfilter = RoomFilter()
    rooms = FilteredElementCollector(doc, view.Id).WherePasses(roomfilter).ToElements()
    select = [room.Id for room in rooms if room.UnboundedHeight <= height and \
         text.lower() in Element.Name.GetValue(room).lower()]
         
    uidoc.Selection.SetElementIds(List[ElementId](select))
    
    TaskDialog.Show('Select Rooms', 
        '{0} Rooms named "{1}" where UnboundedHeight < "{2}":'.format(len(select), format(text), height))


#creation of input box + ref function
dialog = InputFormParameters(selectRoomByNameHeight, 
    ['Wanted Name','text'], 
    ['Limited Height','float'], 
    ['Example bool','bool'],
    ['Example int','int'],
    )

#display the form
dialog.showBox()


'''
#other way 

dialog = InputFormParameters(selectRoomByNameHeight)

dialog.signature = [
    ['Text to search','text'],
    ['Limited Height','float']
    ]

dialog.infomain.Text = 'Give another description'

dialog.showBox()

'''
