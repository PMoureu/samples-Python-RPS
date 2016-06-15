"""
Example of !startup! script to create a textbox input linked to a combobox.
The parser allows to enter these 4 types : text, integer, float, boolean
and uses ',' as separator, with no limit for parameters.
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
To setup and adapt this example :

- use the custom init.py in order to import lookup (or delete import and 1st ComboMember)
- create a folder 'IconsPanel' with all icons in %APPDATA%\RevitPythonShell2016 
- set a global variable in RPS configuration with your path
    Name : RevitPythonSpell
    Value : "C:\USERNAME\AppData\Roaming\RevitPythonShell2016\IconsPanel" (default directory)

1. Gather all your input-type functions (declared here or imported from a reachable module)
(2. Modify panel config if you choosed another global variable name)
3. Modify list_options to target your own functions :
    - add/remove ComboMember lines as you want (be careful with comas)
    - replace titles and functions names : check twice the list of 'parameters types'
    - update the tooltips and placeholders(tip or example)
    - launch Revit !
    
More details here : https://github.com/PMoureu/samples-Python-RPS
"""
from os import path
from clr import AddReference
from inspect import getargspec
AddReference('PresentationCore')
from System.Windows.Media.Imaging import BitmapImage
from System import Uri
from Autodesk.Revit.UI import TextBoxData
from Autodesk.Revit.UI import ComboBoxData
from Autodesk.Revit.UI import ComboBoxMemberData
from Autodesk.Revit.UI import TaskDialog

########## Configuration ##########

### Functions
from Autodesk.Revit.DB import FilteredElementCollector, ElementId, Element, Transaction
from Autodesk.Revit.DB.Architecture import RoomFilter
from System.Collections.Generic import List

from init import lookup # look at the cheated init.py to allow this import

def select_room_height(height):
    '''Select rooms where unbounded height < param'''
    uidoc = __revit__.ActiveUIDocument
    doc = uidoc.Document
    view = uidoc.ActiveGraphicalView
    roomfilter = RoomFilter()
    rooms = FilteredElementCollector(doc, view.Id).WherePasses(roomfilter).ToElements()
    select = [room.Id for room in rooms if room.UnboundedHeight <= height]
    uidoc.Selection.SetElementIds(List[ElementId](select))
    TaskDialog.Show('Select Rooms', 
        '{0} Rooms where UnboundedHeight < "{1}":'.format(len(select), height))
    
def select_room_name(text):
    '''Select rooms where unbounded height < param'''
    uidoc = __revit__.ActiveUIDocument
    doc = uidoc.Document
    view = uidoc.ActiveGraphicalView
    roomfilter = RoomFilter()
    rooms = FilteredElementCollector(doc, view.Id).WherePasses(roomfilter).ToElements()
    select = [room.Id for room in rooms if text.lower() in Element.Name.GetValue(room).lower()]
    uidoc.Selection.SetElementIds(List[ElementId](select))
    TaskDialog.Show('Select Room', 'Rooms containing "{0}":'.format(text))

def make_some_coffee(sugar, milk, donut):
    TaskDialog.Show('CoffeeMaker', 
        '{0} tons of sugar\n{1} galons of milk\nwith{2} bonus donut\n\
            OK ! Wait a minute...'.format(sugar, milk, (not donut)*'out'))

class ComboMember:
    def __init__(self, *combo_cfg):
        '''TODO improve config ! please be careful with each instance'''
        (self.apiname, self.title, self.group, 
            self.funct_ref, self.signature, 
            self.icon, self.tooltip, self.placeholder) = combo_cfg
            
### Panel config

panel_name = "RevitPythonSpell"
panel_res_path = __vars__['RevitPythonSpell']
panel_iconsmall = path.join(panel_res_path, "PythonScript16x16.png") 
panel_iconlarge = path.join(panel_res_path, "PythonScript32x32.png")

### Options list : to plug your functions

list_options = [
    # ComboMember Name, Title, Group, 
    #   Function, Signature, 
    #   Icon, Tooltip, Placeholder/Example
    
    ComboMember('lookup', 'Lookup element', 'API',
        lookup, ['int'],
        'green-01.png', 
        '''Enter the element id to lookup (integer)''', 'ex : 857279'),
        
    ComboMember('roomsheight', 'Select Rooms by Height', 'Rooms',
        select_room_height, ['float'],
        'blue-02.png', 
        '''Enter the max height to filter (float)''', 'ex : 2.80'),
    
    ComboMember('roomsname', 'Select Rooms by Name', 'Rooms',
        select_room_name, ['text'],
        'orange-03.png', 
        '''Enter the text to select rooms (text)''', 'ex : chamber'),
    
    ComboMember('coffee', 'Make some Coffee', 'IoT',
        make_some_coffee, ['int','float', 'bool'],
        'red-04.png', 
        '''nb sugar(int), milk(float), bonus donut(bool)''', 'ex : 1,1.5,Yes')
]


########## Ribbon builder (dynamic part) ##########

def getbool(val):
    if val in {'0','no','n','false','nope','non','faux'}:
        bval = False
    elif val in {'1','yes','y','true','yup','ofcourse','oui','vrai'}:
        bval = True
    else :
        bval = None
    return bval
    
def create_ribbon_panel():
    panel = __uiControlledApplication__.CreateRibbonPanel(panel_name)
    add_stacked_buttons(panel)

def answer_parser(sender, args):
    '''test parameters and call function '''
    app = args.Application
    panel_items = get_panel_items(app)
    sel_option = get_option( panel_items[0].Current.Name )
    sel_funct = sel_option.funct_ref
    
    #parsing answer
    values = sender.Value.split(',')
    
    # check number of parameters
    funct_signat = getargspec(sel_funct).args
    
    if not (len(values) == len(funct_signat) and len(values) == len(sel_option.signature)):
        TaskDialog.Show('Answer Check', 'A parameter is missing somewhere :\
            \nNeeded : {0}\nGiven : {1}'.format(len(funct_signat), len(values)))
            
    else:            
        # check the type and convert
        form_values = check_types(values, sel_option)
        if not form_values:
            TaskDialog.Show('Answer Check', 'A parameter is messing up:\
                \nNeeded : {0}\nGiven : {1}'.format(', '.join(sel_option.signature), ', '.join(values)))
        else :
            # call selected function
            sel_funct(*form_values)
        
def check_types(values, option):
    '''return format values if all parameters match the types'''
    form_values = values[:]
    typeOK = 0
    try:
        for i, type_param in enumerate(option.signature):
            if type_param == 'text':
                typeOK += 1
                
            elif type_param == 'float':
                form_values[i] = float(values[i])
                typeOK += int(isinstance(form_values[i], float))
                
            elif type_param == 'int':
                form_values[i] = int(float(values[i]))
                typeOK += int(isinstance(form_values[i], int))
                
            elif type_param == 'bool':
                form_values[i] = getbool(values[i].lower())
                typeOK += int(isinstance(form_values[i], bool))
            #TODO : date, paths, allow yes/no
    except:
        typeOK = -1
        
    return form_values if typeOK == len(option.signature) else False
    
def switch_manager(sender, args):
    '''update the textbox depending on the choosen option'''
    pan_items = get_panel_items(args.Application)
    if args.NewValue.Name == 'blank':
        pan_items[1].Enabled = False
        pan_items[1].ToolTip = "First, select a function in the combolist"
        pan_items[1].Value = ''
        
    else:
        sel_option = get_option(args.NewValue.Name)
        pan_items[1].Enabled = True
        pan_items[1].Value = ''
        pan_items[1].ToolTip = sel_option.tooltip
        pan_items[1].PromptText = sel_option.placeholder
        pan_items[1].LongDescription = '''Enter the given parameters separated by ","'''

def get_panel_items(app):
    '''return a handle to panel items '''
    pan = [panel for panel in app.GetRibbonPanels() if panel.Name == panel_name][0]
    return pan.GetItems()
    
def get_option(name):
    '''return a handle to the selected option'''
    return [option for option in list_options if option.apiname == name][0]
    
def add_stacked_buttons(panel):
    """Add a text box and combo box as stacked items"""
    #set comboboxdata and textboxdata
    combo_box_data = ComboBoxData("comboBox")
    text_data = TextBoxData("Text Box")
    text_data.Image = BitmapImage(Uri(panel_iconsmall))
    text_data.Name = "Text Box"
    text_data.ToolTip = "First, select a function in the combolist"
    text_data.ToolTipImage = BitmapImage(Uri(panel_iconlarge))
    text_data.LongDescription = """
    This is text that will appear next to the image when the user hovers the mouse over the control"""
    
    #generate panel objects
    stacked_items = panel.AddStackedItems(combo_box_data, text_data)
    
    #set combobox 
    combo_box = stacked_items[0]
    combo_box.ItemText = "ComboBox"
    combo_box.ToolTip = "Select an Option"
    combo_box.LongDescription = """
    Select an option to enable the textbox and enter some parameters"""
    combo_box.CurrentChanged += switch_manager # plug combo change manager
    
    #combobox members
    member_data_blank = ComboBoxMemberData('blank', 'Select...')
    combo_box.AddItem(member_data_blank)
    
    for option in list_options:
        lcombo = ComboBoxMemberData(option.apiname, option.title)
        lcombo.GroupName = option.group
        lcombo.Image = BitmapImage(Uri(path.join(panel_res_path, option.icon)))
        combo_box.AddItem(lcombo)
    
    #set textbox
    text_box = stacked_items[1]
    text_box.Width = 220
    text_box.PromptText = "User input..."
    text_box.Enabled = False 
    text_box.SelectTextOnFocus = True
    text_box.ShowImageAsButton = True
    text_box.EnterPressed += answer_parser # plug input manager function
    
if __name__ == '__main__':

    try:
        print('...Creating new ribbon panels...')
        create_ribbon_panel()
        __window__.Close()
        
    except:
        import traceback
        traceback.print_exc()
