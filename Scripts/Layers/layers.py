#!/usr/bin/python
# --*-- coding:UTF-8 --*--
'''
 Get the layers details from the types hosting a compound structure
 format values and display to excel via csv

'''
print('Loading API Components...')
import os
import csv
import clr

from Autodesk.Revit.DB import Element, FilteredElementCollector, CategoryType
from Autodesk.Revit.DB import UnitUtils, DisplayUnitType 
from Autodesk.Revit.UI import TaskDialog

__doc__ = 'Get the layers details from the types hosting a compound structure'

###################################################### UI PART #################

clr.AddReference("System.Windows.Forms")
clr.AddReference("System.Drawing")

from System.Windows.Forms import Form, CheckedListBox
from System.Windows.Forms import Button, DialogResult 
from System.Drawing import Size, Point
from System import Object
from System.Collections.Generic import List

class Checklist(Form):
    '''this form eats a list of items to build a checklistbox
       access to the list of Enabled items via the getValid method (return a simple list)
    '''
    def __init__(self, itemlist):
        
        height = len(itemlist)*17
        self.Text = "Select the categories to export"
        self.Size = Size(300, height + 80)
        
        self.check = CheckedListBox()
        self.check.Parent = self
        self.check.Location = Point(5, 5)
        self.check.Size = Size(270, height)
        
        # load the list of relevant categories found in the project
        list_items = List[Object](itemlist)
        self.check.Items.AddRange(list_items.ToArray())
        self.check.CheckOnClick = True
        
        # set checked by default
        for i in range(len(itemlist)):
            self.check.SetItemChecked(i , True)
            
        okay = Button()
        okay.Parent = self
        okay.Text = 'OK'
        okay.Location = Point(50, height+10)
        okay.Width = 140
        okay.Click += self.onValidate
        
        cancel = Button()
        cancel.Parent = self
        cancel.Text = 'Cancel'
        cancel.Location = Point(okay.Right, height+10)
        cancel.Click += self.onCancel
        
        self.CenterToScreen()
        
    def getValid(self):
        checked = self.check.CheckedItems
        return [checked[i] for i in range(checked.Count)]
            
    def onValidate(self, sender, event):
        self.DialogResult = DialogResult.OK
        self.Close()
        
    def onCancel(self, sender, event):
        self.DialogResult = DialogResult.Cancel
        self.Close()
        
###################################################### CONFIG PART #############

# Anchors
uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document
view = uidoc.ActiveGraphicalView

# Base Units for conversion
USER_UNIT_IN = DisplayUnitType.DUT_DECIMAL_FEET
USER_UNIT_OUT = DisplayUnitType.DUT_MILLIMETERS

# destination and engine (reader after export)
USER_destination = os.path.expandvars('%temp%\\')
USER_engine = 'excel' #'scalc'

filename = os.path.basename(doc.PathName)
filename = os.path.splitext(filename)[0] + '_layers.txt'
full_filepath = os.path.join(USER_destination, filename)

def format_csv(onetype):
    ''' format the details
    '''
    # shortcut on strings to avoid encoding troubles 
    u = lambda txt: unicode(txt).encode("utf-8")

    structure = None
    if is_compound(onetype):
        
        structure = layers_from(onetype)
        
        pattern = [ [] ,
            [ u(structure['cat']),       ''       ,        u(structure['name'])        ,    ''   ],
            [      ''            ,       ''       ,       'Layers from ext. :'         , 'Width'] 
            ]
        
        for layer in structure['layers']:
            pattern.append([ ''  , layer['idlayer'],        u(layer['matos'])      , layer['conv_width'] ])
        
        pattern.append([   ''    ,       ''       ,         'Total :'         ,  int(structure['sum']) ])
        
        return pattern
        
    else:
        pass # return TODO structure = name + width or height directly from type
         
        
def layers_from(onetype):
    '''returns a dict with formated parameters for each layer from the given type
    '''
    comp = onetype.GetCompoundStructure()
    structure = { 'name': Element.Name.GetValue(onetype) ,
                  'cat': onetype.Category.Name ,
                  'layers': [],
                  'sum': 0 
                }
                
    layers = comp.GetLayers()
    
    for layer in layers:
        details = {'conv_width' : int(set_unit(layer.Width)),
                   'idlayer' : layer.LayerId+1,
                   'matos' : doc.GetElement(layer.MaterialId).Name,
                   'matosid' : layer.MaterialId,
                   'function' : layer.Function
                  }
        structure['layers'].append(details)
        structure['sum'] += layer.Width
        
    structure['sum'] = set_unit(structure['sum'])

    return structure

###################################################### FUNCT PART ###############

def is_compound(onetype):
    ''' return True/False if type contain a valid compound struct
    '''
    cmp = False
    if 'GetCompoundStructure' in dir(onetype) and onetype.GetCompoundStructure():
        cmp = True
    return cmp
    
    
def get_types_by(idcat):
    '''get types by category and filter if compound struct.
    '''
    types = None
    tfilter =  FilteredElementCollector(doc).OfCategoryId(idcat)
    types = tfilter.WhereElementIsElementType().ToElements()
    
    return [ltype for ltype in types if is_compound(ltype)]
    
    ''' todo: select types by cat > checklist 
        filter by view /levels
    '''
    
        
def set_unit(val):
    '''display given value with the conversion variables on top
    '''
    val_out = None
    try:
        val_out = UnitUtils.Convert (val, USER_UNIT_IN, USER_UNIT_OUT)
        
    except:
        val_out = val
        
    return val_out
    
    
def export_csv_group(group):
    '''write to file and open editor
    '''
    ready = False
    with open(full_filepath, 'wb') as csvfile:
        try: 
            writer = csv.writer(csvfile, delimiter='\t', quoting=csv.QUOTE_ALL)
            ready = False
            for categ in group:
                for onetype in get_types_by(categ):
                    rows = format_csv(onetype)
                    if rows:
                        writer.writerows(rows)
                    
            ready = True
            
        except Exception as er:
            TaskDialog.Show('LayerTool','An Error occured...{}'.format(er.message))
        
    if ready:
        try:
            os.system('start {0} \"{1}\"'.format(USER_engine, full_filepath))
        except Exception as er:
            TaskDialog.Show('LayerTool','Can\'t open an editor...{}'.format(er.message))
                
###################################################### RUNNING PART ##############

print('Searching and Looping...')
# Build a dict of categories from the project, exclude non-compound types and non-model category
categories_cmp = {}

categories = doc.Settings.Categories.ForwardIterator()
categories.Reset()

while categories.MoveNext():
    cat = categories.Current
    
    if cat.CategoryType == CategoryType.Model:
        if get_types_by(cat.Id):
            categories_cmp[cat.Name] = cat

__window__.Close()

# call dialog to check the relevant types
dialog_topics = sorted(categories_cmp.keys())
dialog = Checklist(dialog_topics)

if dialog.ShowDialog() == DialogResult.OK:    
    # build list of categoryID from selected items
    select_cat = [categories_cmp[item].Id for item in dialog.getValid()]
    
    if select_cat:
        export_csv_group(select_cat)
        