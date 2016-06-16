from clr import AddReference
from inspect import getargspec

AddReference("System.Windows.Forms")
AddReference("System.Drawing")

from System.Windows.Forms import Application, Form, Label, TextBox
from System.Windows.Forms import Button, Panel, ToolTip
from System.Drawing import Size, Point, Color

class Cfg:
    types = { #caution : linked with checkType
        'text': [str,'Enter some text'],
        
        'float': [float,'Enter some Decimal Number'],
        
        'int': [int,'Enter some integer number'],
        
        'bool': [bool,'Enter Yes/No - 0/1 - false/true...']
    }
    
    nope = {'0','no','n','false','nope','non','faux'}
    
    yup = {'1','yes','y','true','yup','oui','vrai'}

class PanelParameter(Panel):
    '''
    wrap label and textbox in a panel
    '''
    def __init__(self, ind, param):
        self.Height = 20
        self.paramtype = param[1]
        tooltips = ToolTip()
        self.textlabel = Label()
        self.textlabel.Parent = self
        self.textlabel.Text = '{0} ({1})'.format(param[0],param[1])
        self.textlabel.Location = Point(10, ind*self.Height)
        self.textlabel.AutoSize = True
        
        self.value = TextBox()
        self.value.Parent = self
        self.value.Location = Point(130, ind*self.Height)
        self.value.Width = 220
        tooltips.SetToolTip(self.value, Cfg.types[param[1]][1])
        self.value.KeyUp += self.onInput
        
    def onInput(self, sender, arg):
        '''Display focus background'''
        if (len(sender.Text) > 0 and 
            not InputFormParameters.checkType(sender.Text, self.paramtype)):
            
            sender.BackColor = Color.LightYellow
        else:
            sender.BackColor = Color.Empty
        
        
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
        
        self.infomain = Label()
        self.infomain.Parent = self
        self.infomain.Text = funct.__doc__ #todo split x char/line
        self.infomain.Location = Point(10, 10)
        self.infomain.AutoSize = True
        
    def showBox(self):
        '''
        set the box and launch
        '''
        hpanel = 40 * len(self.signature)
        self.Text = 'Enter all parameters'
        self.Width = 400
        self.Height = 120 + hpanel
        tooltips = ToolTip()
        
        self.panelparams = []
        for i, param in enumerate(self.signature):
            p = PanelParameter(i, param)
            p.Parent = self
            p.Location = Point(10, 35 + i * 20)
            p.AutoSize = True
            self.panelparams.append(p)
            
            
        self.warning = Label()
        self.warning.Parent = self
        self.warning.Location = Point(10, 25 + hpanel)
        self.warning.AutoSize = True
        
        okay = Button()
        okay.Parent = self
        okay.Text = "Ok"
        okay.Location = Point(150, 30 + hpanel)
        okay.Width = 150
        okay.Click += self.onValidate
        
        cancel = Button()
        cancel.Text = "Cancel"
        cancel.Parent = self
        cancel.Location = Point(300, 30 + hpanel)
        cancel.Click += self.onCancel
            
        tooltips.SetToolTip(self, "Enter all parameters")
        tooltips.SetToolTip(okay, "Click to Confirm and Execute")
        tooltips.SetToolTip(cancel, "Let me out !")
        
        self.CenterToScreen()
        
        return Application.Run(self)
        
    @staticmethod
    def checkType(val, type):
        '''
        return formated parameter or False
        '''
        formatval = [] #wrap in list to avoid 0.0 == False
        try: 
            if type == 'text':
                formatval.append(val)
                
            elif type == 'float':
                formatval.append(float(val))
                
            elif type == 'int':
                formatval.append(int(float(val)))
                
            elif type == 'bool':
                if val.lower() in Cfg.nope :
                    formatval.append(False)
                    
                elif val.lower() in Cfg.yup:
                    formatval.append(True)
            '''
            todo : dynamic radio button...
            and other types, paths, date
            '''
        except:
            formatval = []
            
        return formatval
    
    def formatType(self, input_params):
        '''
        return true and format values if all parameters match the types
        '''
        typeOK = 0
        for i, param in enumerate(self.signature):
        
            checking = self.checkType(input_params[i],param[1])
            
            if checking:
                self.parameters.append(checking[0])
                typeOK += int(isinstance(self.parameters[i], Cfg.types[param[1]][0]))
            else:
                self.panelparams[i].value.BackColor = Color.LightYellow
                
        return typeOK == len(self.signature)
        
        
    def onValidate(self, sender, event):
        '''
        count parameters and call formating
        '''
        input_params = [p.value.Text for p in self.panelparams if p.value.Text]
        
        fsignature = getargspec(self.infunction).args
        
        if not (len(self.signature) == len(fsignature) 
            and len(input_params) == len(fsignature)):
            self.warning.Text = 'A parameter is missing...'
            
        elif not self.formatType(input_params):
            self.warning.Text = 'A parameter is messing...'
            self.parameters = []
            
        else:
            self.infunction(*self.parameters)
            self.Close()
    
    
    def onCancel(self, sender, event):
        '''
        Close the form
        '''
        self.Close()
