from clr import AddReference
from inspect import getargspec

AddReference("System.Windows.Forms")
AddReference("System.Drawing")

from Autodesk.Revit.UI import TaskDialog
from System.Windows.Forms import Application, Form, HorizontalAlignment 
from System.Windows.Forms import Label, TextBox, Button, Panel
from System.Windows.Forms import ToolTip, RadioButton, MonthCalendar
from System.Windows.Forms import DockStyle, AnchorStyles
from System.Drawing import Size, Point, Color, SystemFonts
from System.Drawing import Font, FontStyle, ContentAlignment
from System import DateTime, Convert

class Fconfig:
    width = 400
    margin = 15
    smwidth = 370    # width - 2*margin
    lblwidth = 125   # labels size
    unitline = 40    # basic element panel height
    basefont = 'Tahoma'
    sizefont = 8.6
    formtitle = 'Enter all parameters'
    buttonOK = 'OK'
    buttonCANCEL = 'Cancel'
    buttonYES = 'Yes'
    buttonNO = 'No'
    defdate = 'DD/MM/YYYY'
    warnMiss = 'One parameter is missing...'
    warnMess = 'One parameter is messing...'
    
class Types:

    @staticmethod
    def types(type, option):
        '''
        return the needed option depending on the type
        you can change the keys in typeslist to use 
        other names when you define signatures in your scripts
        '''
        typeslist = {
            'text': {
                'type': str,
                'tooltip': 'Enter some text', 
                'panel': PanelParameter, 
                'converter' : lambda x: x
                },
            
            'float': {
                'type': float,
                'tooltip': 'Enter some Decimal Number', 
                'panel': PanelParameter, 
                'converter' : Types.getFloat
                },
            
            'int': {
                'type': int,
                'tooltip': 'Enter integer number', 
                'panel': PanelParameter, 
                'converter' : Types.getInt
                },
            
            'bool': {
                'type': bool,
                'tooltip': 'Make your choice', 
                'panel': PanelBool, 
                'converter' : lambda x: x
                },
            
            'date': {
                'type': DateTime,
                'tooltip': 'Make your choice', 
                'panel': PanelDate, 
                'converter' : Types.getDate
                }
            }
        return typeslist[type][option]
        
    @staticmethod
    def getFloat(val):
        try:
            formatval = float(val)
        except:
            formatval = None
        return formatval
    
    @staticmethod
    def getInt(val):
        try:
            formatval = int(float(val))
        except:
            formatval = None    
        return formatval
        
    @staticmethod
    def getDate(val):
        try:
            if isinstance(val, DateTime):
                formatval = val
            else:
                formatval = Convert.ToDateTime(val)
        except:
            formatval = None    
        return formatval
        
# # # # # # # # # # # # # # # # # # # # # # # #  Textbox
    
class PanelParameter(Panel):
    '''
    wrap label and textbox in a panel
    '''
    def __init__(self, param):
        super(PanelParameter, self ).__init__()
        
        self.Height = Fconfig.unitline
        self.paramtype = param[1]
        tooltips = ToolTip()
        self.value = ''
        
        
        self.textlabel = Label()
        self.textlabel.Parent = self
        self.textlabel.Text = '{0} ({1}) :'.format(param[0],param[1])
        self.textlabel.Location = Point(0, 0)
        self.textlabel.Size = Size(Fconfig.lblwidth, Fconfig.unitline)
        self.textlabel.TextAlign = ContentAlignment.MiddleLeft
        
        self.textbox = TextBox()
        self.textbox.Parent = self
        self.textbox.Location = Point(self.textlabel.Right+Fconfig.margin, 10)
        self.textbox.Width = Fconfig.smwidth-self.textlabel.Width- 2*Fconfig.margin
        self.textbox.TextChanged += self.onInput
        
        tooltips.SetToolTip(self.textbox, Types.types(param[1], 'tooltip'))
        
        
    def onInput(self, sender, arg):
        '''Display focus background'''
        self.value = sender.Text
        checker = Types.types(self.paramtype, 'converter')
        if (len(sender.Text) > 0 and 
            checker(sender.Text) == None):
            
            sender.BackColor = Color.LightYellow
        else:
            sender.BackColor = Color.Empty
            
# # # # # # # # # # # # # # # # # # # # # # # #  Radiobutton
        
class PanelBool(Panel):
    '''
    wrap label and radiobutton in a panel
    '''
    def __init__(self, param):
        super(PanelBool, self ).__init__()
        
        self.Height = Fconfig.unitline
        tooltips = ToolTip()
        self.value = True
        
        self.textlabel = Label()
        self.textlabel.Parent = self
        self.textlabel.Text = param[0]+' :'
        self.textlabel.Location = Point(0, 0)
        self.textlabel.Size = Size(Fconfig.lblwidth, Fconfig.unitline)
        self.textlabel.TextAlign = ContentAlignment.MiddleLeft
        
        self.checkyes = RadioButton()
        self.checkyes.Parent = self
        self.checkyes.Location = Point(self.textlabel.Right+2*Fconfig.margin, 10)
        self.checkyes.Text = Fconfig.buttonYES
        self.checkyes.Checked = True
        self.checkyes.CheckedChanged += self.onChanged
        
        self.checkno = RadioButton()
        self.checkno.Parent = self
        self.checkno.Location = Point(self.checkyes.Right, 10)
        self.checkno.Text = Fconfig.buttonNO
        self.checkno.CheckedChanged += self.onChanged
        
        tooltips.SetToolTip(self, Types.types(param[1], 'tooltip'))
        
    def onChanged(self, sender, arg):
        if sender.Checked:
            self.value = not self.value
            
    def invert(self):
        self.checkno.Checked = True
        
# # # # # # # # # # # # # # # # # # # # # # # #  Calendar

class PanelDate(Panel):
    '''
    wrap label and calendar in a panel
    '''
    def __init__(self, param):
        super(PanelDate, self ).__init__()
        
        self.Height = 170
        self.paramtype = param[1]
        tooltips = ToolTip()
        self.value = ''
        
        self.textlabel = Label()
        self.textlabel.Parent = self
        self.textlabel.Text = param[0] + ' :'
        self.textlabel.Location = Point(0, 0)
        self.textlabel.Size = Size(Fconfig.lblwidth, Fconfig.unitline*2)
        self.textlabel.TextAlign = ContentAlignment.MiddleLeft
        
        self.textbox = TextBox()
        self.textbox.Parent = self
        self.textbox.Text = Fconfig.defdate
        self.textbox.Location = Point(0, Fconfig.unitline*2)
        self.textbox.Width = Fconfig.lblwidth-Fconfig.margin
        self.textbox.TextAlign = HorizontalAlignment.Center
        self.textbox.TextChanged += self.onInput
        
        self.calend = MonthCalendar()
        self.calend.Parent = self
        self.calend.Location = Point(Fconfig.lblwidth+5, 0)
        self.calend.MaxSelectionCount = 1
        self.calend.DateChanged += self.onSelect
        
        tooltips.SetToolTip(self.calend, Types.types(param[1], 'tooltip'))
        
    def onSelect(self, sender, arg):
        date = sender.SelectionStart
        self.value = date
        #'{0}/{1}/{2}'.format(date.Year, date.Month, date.Day)
        
        zero = lambda x : '0'+str(x) if x < 10 else str(x)
        self.textbox.Text = '{0}/{1}/{2}'.format(
            zero(date.Day), zero(date.Month), date.Year)
        
    def onInput(self, sender, arg):
        self.value = Types.getDate(sender.Text)
        
        if (len(sender.Text) > 9 and self.value == None): # check constraints
            sender.BackColor = Color.LightYellow
        else:
            sender.BackColor = Color.Empty
        
        
# # # # # # # # # # # # # # # # # # # # # # # #  Main Class

class InputFormParameters(Form):
    '''
    Generate a form depending on the given parameters
    '''
    def __init__(self, funct,*signature):
        '''
        funct : reference to function 
        (use __doc__ to give details or overide infomain.Text after creation)
        signature : optional, given with array ['str','str'] title, type
        '''
        self.infunction = funct
        self.signature = list(signature)
        self.parameters = []
        
        self.Text = Fconfig.formtitle
        self.Font = Font(Fconfig.basefont, Fconfig.sizefont)
        #SystemFonts.DialogFont

        self.infomain = Label()
        self.infomain.Parent = self
        self.infomain.Text = funct.__doc__
        self.infomain.Location = Point(Fconfig.margin, Fconfig.margin)
        self.infomain.Size = Size(Fconfig.smwidth, Fconfig.unitline)
        
        self.panel = Panel()
        self.panel.Parent = self
        self.panel.Location = Point(0, self.infomain.Bottom)
        self.panel.AutoSize = True               
        
        self.panelparams = []
        ref = 0
        for i, param in enumerate(self.signature):
            p = Types.types(param[1],'panel')(param)
            p.Parent = self.panel
            p.Location = Point(Fconfig.margin, ref)
            p.Width = Fconfig.smwidth
            self.panelparams.append(p)
            ref += p.Height
            
    def showBox(self):
        '''
        set the remaining box controls and launch
        '''
        self.buttonpanel = Panel()
        self.buttonpanel.Parent = self
        self.buttonpanel.Location = Point(0,self.panel.Bottom)
        self.buttonpanel.Size = Size(Fconfig.smwidth, 2* Fconfig.unitline)
        self.buttonpanel.Dock = DockStyle.Bottom
        
        self.warning = Label()
        self.warning.Parent = self.buttonpanel
        self.warning.Location = Point(Fconfig.margin, 0)
        self.warning.Size = Size(Fconfig.smwidth, Fconfig.unitline)
        self.warning.Font = Font(Fconfig.basefont, Fconfig.sizefont, FontStyle.Bold)
        self.warning.ForeColor = Color.Coral
        self.warning.TextAlign = ContentAlignment.MiddleCenter
        
        okay = Button()
        okay.Parent = self.buttonpanel
        okay.Text = Fconfig.buttonOK
        okay.Location = Point(50, Fconfig.unitline)
        okay.Width = 140
        okay.Click += self.onValidate
        okay.Anchor = AnchorStyles.Right
        
        cancel = Button()
        cancel.Text = Fconfig.buttonCANCEL
        cancel.Parent = self.buttonpanel
        cancel.Location = Point(okay.Right, Fconfig.unitline)
        cancel.Click += self.onCancel
        cancel.Anchor = AnchorStyles.Right
        
        self.Width = Fconfig.width
        self.Height = self.panel.Bottom + 105
        self.CenterToScreen()
        
        try:
            if Application.MessageLoop:
                TaskDialog.Show('UserForm', 'Another window is running...')
            else:
                Application.Run(self) # todo : dig in ApplicationContext ...
                
        except:
            TaskDialog.Show('UserForm','Loading failed...')
        
        
    def onValidate(self, sender, event):
        '''
        count parameters and format before executing function
        '''
        input_params = [p.value for p in self.panelparams if not p.value == '']
        
        fsignature = getargspec(self.infunction).args #get the given function parameters
        
        if not (len(self.signature) == len(fsignature) #compare the signature you set
            and len(input_params) == len(fsignature)): #compare user's parameters 
            
            self.warning.Text = Fconfig.warnMiss
            
        elif not self.formatType(input_params): #get format value
        
            self.warning.Text = Fconfig.warnMess
            
        else:
            try:
                self.infunction(*self.parameters) # call the given function
                self.Close()
                
            except:
                TaskDialog.Show('UserForm','The function can\'t run.')
                self.Close()
            
    def formatType(self, input_params):
        '''
        return true and save formated values if all parameters match the types
        '''
        typeOK = 0
        self.parameters = []
        self.warning.Text = ''
        for i, param in enumerate(self.signature):
            
            converter = Types.types(param[1],'converter')
            formatvalue = converter(input_params[i])
            
            if formatvalue == None:
                self.panelparams[i].textbox.BackColor = Color.LightYellow
                break
            else:
                self.parameters.append(formatvalue)
                typeOK += int(isinstance(self.parameters[i], 
                    Types.types(param[1],'type')))

        return typeOK == len(self.signature)
        
        
    def onCancel(self, sender, event):
        '''
        Close the form
        '''
        self.Close()
