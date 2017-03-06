'''
    This module can help you to explore the Revit API by providing details of any Revit Class or Python object
    (or other .Net assemblies), work is in progress to analyse any object called in a script with more accuracy.


    This is not a clone of RevitLookup, the first goal is to provide doc, not datas,
    some values are still displayed for simple builtins types (todo : read nested arrays, maps...)

    Usage
    In the console REPL, call the form with an object to flesh out its members and try to extract any available doc  :

    >>>from rph import h
    >>>h(doc)

    >>>h(rph)

    Tips: 
    - Double-click on a member to open a new tab.
    - Add "from rph import h" in the RevitPythonShell __init__.py file to call the form more easily.

    Contact:
    https://github.com/PMoureu
'''
import os
import re
import clr
import webbrowser

clr.AddReference('System.Windows.Forms')
clr.AddReference('System.Drawing')

import System.Object
import System.String
from System.Drawing import (FontStyle, Point, Color, Size, Font, Image)
from System.Windows.Forms import (Form, ToolTip, Padding, SplitContainer, CheckBox,
    FixedPanel, FormStartPosition, DataGridViewAutoSizeRowsMode, FlowLayoutPanel,
    RichTextBox, Button, DockStyle, DataGridView, DataGridViewTextBoxColumn,
    DataGridViewAutoSizeColumnMode, AutoSizeMode, Orientation, DataGridViewContentAlignment,
    DataGridViewSelectionMode, DataGridViewAutoSizeRowsMode, DataGridViewTriState)


#               #               #
#           MAIN FORM 
#               #               #

class RevitPythonHelper(Form):
    '''
    '''
    def __init__(self, ref_obj):
        super(RevitPythonHelper, self).__init__()
        
        self.ref_obj = ref_obj
        self.filter_sys_memb = True
        
        self.Size = Size(650, 800)
        self.Text = 'Explorer'
        self.tooltips = ToolTip()
        self.StartPosition = FormStartPosition.Manual
        # self.Location = Point(600,0) # to display in your favorite corner
        
        self.panright = SplitContainer()
        self.panright.Parent = self
        self.panright.Dock = DockStyle.Fill
        self.panright.Orientation = Orientation.Horizontal
        self.panright.SplitterDistance = 100

        self.top_info = RichTextBox()
        self.top_info.Dock = DockStyle.Fill
        self.top_info.DetectUrls = True        
        
        self.table = DataGridView()
        self.table.Dock = DockStyle.Fill
        self.table.RowHeadersVisible = False
        self.table.AutoSizeRowsMode = DataGridViewAutoSizeRowsMode.AllCellsExceptHeaders
        self.table.RowTemplate.Height = 30
        self.table.SelectionMode = DataGridViewSelectionMode.RowHeaderSelect
        self.table.DefaultCellStyle.WrapMode = DataGridViewTriState.True
        self.table.DefaultCellStyle.BackColor = Color.GhostWhite
        self.table.ColumnHeadersDefaultCellStyle.Alignment = DataGridViewContentAlignment.MiddleCenter

        col1 = DataGridViewTextBoxColumn()
        col1.HeaderText = 'Name'
        col1.AutoSizeMode = DataGridViewAutoSizeColumnMode.Fill
        col1.FillWeight = 20
        col1.DefaultCellStyle.Font = Font(self.table.DefaultCellStyle.Font, FontStyle.Underline)
        
        col2 = DataGridViewTextBoxColumn()
        col2.HeaderText = 'Type'
        col2.AutoSizeMode = DataGridViewAutoSizeColumnMode.Fill
        col2.FillWeight = 5
        col2.DefaultCellStyle.Alignment = DataGridViewContentAlignment.MiddleCenter
        
        col3 = DataGridViewTextBoxColumn()
        col3.HeaderText = 'Value'
        col3.AutoSizeMode = DataGridViewAutoSizeColumnMode.Fill
        col3.FillWeight = 15
        
        col4 = DataGridViewTextBoxColumn()
        col4.HeaderText = 'Infos'
        col4.AutoSizeMode = DataGridViewAutoSizeColumnMode.Fill
        col4.FillWeight = 60

        self.table.Columns.AddRange((col1,col2, col3, col4))
        self.table.AutoGenerateColumns = False

        self.panright.Panel1.Controls.Add(self.top_info)
        self.panright.Panel2.Controls.Add(self.table)
        self.panright.FixedPanel = FixedPanel.Panel1

        self.toolpan = FlowLayoutPanel()
        self.toolpan.Parent = self
        self.toolpan.Dock = DockStyle.Top
        self.toolpan.Height = 25

        self.check = CheckBox()
        self.check.Parent = self.toolpan
        self.check.Text = "Hide Sys"
        self.check.Checked = True

        self.close = Button()
        self.close.Parent = self
        self.close.Dock = DockStyle.Bottom
        self.close.Text = 'Close'
        self.close.Height = 30

        # LOAD DATAS

        self.update_info(extract_main(self.ref_obj))
        self.update_table(extract_members(self.ref_obj, self.filter_sys_memb))
        self.Show()

        # EVENTS 

        self.top_info.LinkClicked += self.on_link_clicked
        self.check.CheckedChanged  += self.on_hide_member_clicked
        self.close.Click += self.on_close
        self.table.MouseEnter += self.get_focus
        self.table.CellContentDoubleClick += self.on_val_double_click
        self.table.SortCompare += self.sort_by_name
        
    def update_info(self, text):
        '''Display main info in the richtextbox
            arg : text as string
        '''
        self.top_info.Text = text
        self.top_info.SelectionStart = 0
        self.top_info.SelectionLength = len(self.top_info.Text.split('\n')[0])
        self.top_info.SelectionFont = Font(self.top_info.Font, FontStyle.Bold)
        self.top_info.SelectionLength = 0

    def update_table(self, sourcelist):
        '''Populate listview with selected  member or group
            arg: a list of tuples (member, type, val, docstring)
        '''
        self.table.Rows.Clear()
        self.table.SuspendLayout()
        for member, mtype, val, doc in sourcelist:
            self.table.Rows.Add(member, mtype, val, doc)
        self.table.ResumeLayout()
    
    def on_close(self, sender, event):
        '''Get out! 
        '''
        self.Close()
        
    def on_link_clicked(self, sender, event):
        ''' Open tab in default browser
        '''
        webbrowser.open_new_tab(event.LinkText)
    
    def on_hide_member_clicked(self, sender, event):
        ''' Update views to hide/show object base members
        '''
        self.filter_sys_memb = sender.Checked
        self.update_table(extract_members(self.ref_obj, self.filter_sys_memb))
        
    def on_val_double_click(self, sender, event):
        ''' Open a new form to display clicked member
        '''
        try:
            if event.ColumnIndex == 0: 
                member = sender.Rows[event.RowIndex].Cells[event.ColumnIndex].Value
                new_ref = getattr(self.ref_obj, member)
                RevitPythonHelper(new_ref)
        except:
            print("Can't reach this reference")
            
    def get_focus(self, sender, event):
        '''Add convenient focus for scroll in datagrid
        '''
        if not sender.Focused:
            sender.Focus()

    def sort_by_name(self, sender, event):
        ''' Overide the automatic grid sort
        '''
        event.SortResult = System.String.Compare(
            event.CellValue1.ToString(), event.CellValue2.ToString())
            
        if not(event.SortResult and event.Column.Index == 0):
            event.SortResult = System.String.Compare(
            sender.Rows[event.RowIndex1].Cells[0].Value.ToString(),
            sender.Rows[event.RowIndex2].Cells[0].Value.ToString())
        event.Handled = True


#               #               #
#             UTILS
#               #               #

def extract_main(obj):
    ''' extract the main info for the richtextbox
        args : 
            obj : ref to object
    '''   
    try:
        top_name = obj.__name__
        
    except AttributeError:
        top_name = type(obj).__name__
        
    except Exception:
        top_name = str(obj)
    
    try:
        if '__module__' in dir(obj):
            top_parent = obj.__module__
        
        elif 'ToString' in dir(obj):
            top_parent = obj.ToString()
        
        else:
            top_parent = str(type(obj))
    except:
        top_parent = str(type(obj))
        
    top_link = apidoc_linker(obj)
    
    try:
        top_doc =  obj.__doc__
        
    except Exception:
        top_doc =  'No doc available'
    
    return '\n'.join(
        [el for el in [top_name, top_parent, top_link, top_doc] if el])


def extract_members(obj, filtersys=False):
    ''' extract the max from each member to populate the datagridview
        args : 
            obj : ref to object
            filtersys : bool True to hide members inherited from System.Object
    '''
    grid_infos = []
    
    dir_obj = dir(obj)
    
    if filtersys:
        dir_obj = sorted(set(dir_obj) - set(dir(System.Object)))

    for member in dir_obj:
        try:
            ref_memb = getattr(obj, member)
            val = ''
            doc = ref_memb.__doc__
            
            if type(ref_memb).__name__ == 'builtin_function_or_method':
                mtype = 'Func'
                
            elif type(ref_memb).__name__ == 'BoundEvent':
                mtype = 'Event'
                handler = ref_memb.Event.Info.EventHandlerType.ToString()
                val = handler.split('.').pop()[:-1]
                doc = ref_memb.Event.__doc__
            
            elif type(ref_memb).__name__ == 'indexer#':
                mtype = 'Prop'
                doc = ref_memb.PropertyType.__doc__
                
            elif type(ref_memb).__name__ == 'getset_descriptor':
                mtype = 'Prop'
                doc = ref_memb.PropertyType.__doc__
                
            elif isinstance(ref_memb, type): 
                mtype = 'Class'
                val = type(ref_memb).__name__
                
            elif (isinstance(ref_memb, str)
               or isinstance(ref_memb, bool)
               or isinstance(ref_memb, int)
               or isinstance(ref_memb, float)):
                mtype = 'Prop'
                val = ref_memb
                doc = 'Builtin : '+ type(ref_memb).__name__
                
            elif clr.GetClrType(type(ref_memb)).IsEnum:
                mtype = 'Enum'
                val = ref_memb
                
            elif clr.GetClrType(type(ref_memb)).IsClass:
                mtype = 'Class'
                val = type(ref_memb).__name__
                
            else:
                mtype = 'TODO'
                val = ref_memb
            
            if doc:
                doc = doc.strip()

            grid_infos.append((member, mtype, val, doc))
            
        except Exception as error:
            grid_infos.append((member, 'n/a', '', str(error)))
    
    return grid_infos


def apidoc_linker(obj):
    ''' create an url query from the name (only Revit API)
         arg : ref of object
    '''
    txt = ''
    try:
        version = __revit__.Application.VersionNumber
        querypath = obj.ToString().split('.')
        if querypath and querypath[0] == 'Autodesk':
            querystr = querypath.pop()
            txt = 'http://www.revitapidocs.com/'
            txt += '{vernum}/?query={name}#searchModal'.format(
                vernum=version, name=querystr)
    except:
        pass # find a .Net or ironpython online doc
    return txt


#               #               #
#          EXTERNAL CALL
#               #               #

h = RevitPythonHelper