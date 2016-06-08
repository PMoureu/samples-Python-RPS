#Dynamic Model Updaters (DMU)

1. [First step : Simple External File](#i-first-step--simple-external-file)
2. [Registration Improvement : startup.py](#ii-registration-improvement--startuppy)
 1. [Simple Case : Application Wide](#simple-case--application-wide)
 2. [Less Simple Case : Specific Documents](#less-simple-case--specific-documents)
3. [About ChangeType and Newly Added/Deleted Elements](#iii-about-changetype-and-newly-addeddeleted-elements)
4. [Ergonomic Improvement](#iv-ergonomic-improvement)

## Intro

This tool is made to improve user experience by executing some tasks (Updaters) 
in the projects (Model) when specific changes are detected (Dynamic), like 
creating/recalculating parameters, or any operation allowed by Revit API during 
a current transaction (see all forbidden changes :
http://help.autodesk.com/view/RVT/2016/ENU/?guid=GUID-9D74F988-4AB6-4F7E-9493-7B58A26C4EF5 )

With RevitPythonShell, setting a DMU sounds like child's play with a piece of cake : 
assuming the model is ready, there are only two steps left, the updater and the dynamic part.

   - updater => a special class in charge of executing the task (5 methods to override)
   - dynamic part => registering the updater in Revit and matching with events (3 lines)

What matters is where and when register those updaters. This step defines the general behavior 
and the limits of your tool, depending on how documents are targeted and what kind of 
transparency you want (meaning how many warnings will be displayed). RPS allows different paths,
from a simple external file to a combination with the startup module. Please refer to this [manual 
for details about RPS configuration](https://daren-thomas.gitbooks.io/scripting-autodesk-revit-with-revitpythonshell/content/the_configure_dialog/index.html).


## I. First step : Simple External File

This example focuses on the class and outlines the general syntax.
The updater reacts to a geometric change in a room and rectifies a shared parameter.

It uses a very easy way for registering the updater in a single document, you can paste
code in IronPython Pad or plug it as an external file with a ribbon button,
good enough to test your class BUT don't keep this way, unless users are your enemies...
```python

__window__.Close()
from Autodesk.Revit.DB import Element, ChangePriority, SubTransaction
from Autodesk.Revit.DB import IUpdater, UpdaterId, UpdaterRegistry
from Autodesk.Revit.DB.Architecture import RoomFilter
from Autodesk.Revit.UI import TaskDialog
from System import Guid

app = __revit__.Application
doc = __revit__.ActiveUIDocument.Document

########## Iupdater Class

class MyRoomUpdater(IUpdater):

    def __init__(self, addinId):
        '''type UpdaterId, mix of Addin ID and updater GUID
           choose a different GUID for each updater !!! '''
        self.updaterID = UpdaterId(addinId, Guid("CBCBF6B2-4C06-42d4-97C1-D1B4EB593EFF"))

    def GetUpdaterId(self):
        return self.updaterID
        
    def GetUpdaterName(self):
        '''text also displayed in the warning dialog'''
        return 'MyRoomUpdater (DoubleHeight)'
    
    def GetAdditionalInformation(self):
        '''called with Execute, stored where ?'''
        return 'MyRoomUpdater (explanation, details, warnings)'
        
    def GetChangePriority(self):
        '''nature of the change to let Revit order all modifications 
           look at ChangePriority http://revitapisearch.com/html/9db16841-106b-23bb-0c29-42017edcf69f.htm'''
        return ChangePriority.RoomsSpacesZones
        
    def Execute(self, updaterData):
        ''' UpdaterData is a parameter given by Revit API => scope of execution
        refer to API manual for more details about all members of this class'''
        #get the scope
        up_doc = updaterData.GetDocument()
        
        # selecting only created elements, not new or deleted
        elems = updaterData.GetModifiedElementIds()
        
        # use a subtransaction in the current opened transaction
        t = SubTransaction(up_doc)
        t.Start()
        
        try:
            TaskDialog.Show('MyRoomUpdater', 'Refreshing {0} elements...'.format(len(elems)))
            
            # elements update if parameter is found
            for elemID in elems:
            
                elem = up_doc.GetElement(elemID)
                list_heightx2 = elem.GetParameters('DoubleHeight')
                
                if list_heightx2:
                    heightx2 = list_heightx2[0]
                    heightx2.Set(elem.UnboundedHeight * 2)
                    
            t.Commit()
            
        except:
            t.RollBack()

# create an instance thanks to RevitPythonShell addin ID
my_updater = MyRoomUpdater(app.ActiveAddInId)


########## Registration

# Switch with a simple bool based on registering state
if UpdaterRegistry.IsUpdaterRegistered(my_updater.GetUpdaterId(), doc):

    # unregister from the current doc
    UpdaterRegistry.UnregisterUpdater(my_updater.GetUpdaterId(), doc)
    
    TaskDialog.Show('MyRoomUpdater', 'MyRoomUpdater is disabled.')
    
else:

    # registering only for the current doc
    UpdaterRegistry.RegisterUpdater(my_updater, doc)
    
    # simple filter to select the rooms
    roomfilter = RoomFilter()
    
    # connect the updater to geometry changes applied on filtered elements (rooms)
    UpdaterRegistry.AddTrigger(my_updater.GetUpdaterId(), roomfilter, Element.GetChangeTypeGeometry())
    
    TaskDialog.Show('MyRoomUpdater', 'MyRoomUpdater is enabled.')
```


## II. Registration Improvement : startup.py


### What could be better about registration ?

The first example requires users actions to launch and stop. If you let them manage the switch, 
they WILL have some suprises. Also, each time they open a project, the warning will remind them how boring it is.
We could make it better. 

In fact, the updater GUID is also stored in the project (only if an event triggered a change and modified the model).
At the next opening, this GUID allows Revit to check if the updater is ready, otherwise it displays the warning.
In order to avoid those dialogs, you have to register updaters as soon as Revit starts or a project is loading.
You can also create an optional updater, but without warnings, users will have to check if updaters are running or not.


### So, where and when register a DMU ?

Where -> 'As soon as Revit starts' within RPS means : in the startup.py file.

When -> depends...As shown above, the registration calls 2 methods (3 or 4 with unregistering) :

- register the updater (application-wide or document)  => bind the updater to a(ll) document(s) 
```python
UpdaterRegistry.RegisterUpdater(my_updater)
UpdaterRegistry.RegisterUpdater(my_updater, doc)
```
- add trigger to events => what elements and what type of changes to watch
```python
UpdaterRegistry.AddTrigger(my_updater.GetUpdaterId(), roomfilter, Element.GetChangeTypeGeometry())
UpdaterRegistry.AddTrigger(my_updater.GetUpdaterId(), doc, roomfilter, Element.GetChangeTypeGeometry())
```
Note : without a document reference in AddTrigger, it applies to all documents using this updater.

That gives us many options :
- application-wide registering and trigger all documents
- application-wide registering and trigger specific documents 
- specific document registering and triggering...


#### Simple Case : Application Wide

Your updater applies to all projects opened in Revit ? 
You only have to register a global DMU on startup (startup.py) and unregister it on shutdown.
Every single opened documents will trigger the DMU, everybody's happy !

There is still a risk of applying unwanted updates to coworker's project :
"Hi, i fixed your roof issue ! however...my updater added separation walls into each room. Good evening !"
You may add some tests in the Execute method to prevent massive destructions 
(special path, specific parameter, user confirm...)

We also use a new function with ApplicationClosing event to unregister the updater,
check the next chapter for more details.

startup.py content :

```python
# script that is run when Revit starts in the IExternalApplication.Startup event.
__window__.Close()
from Autodesk.Revit.DB import Element, ChangePriority, SubTransaction
from Autodesk.Revit.DB import IUpdater, UpdaterId, UpdaterRegistry
from Autodesk.Revit.DB.Architecture import RoomFilter
from Autodesk.Revit.UI import TaskDialog
from System import Guid

########## Iupdater Class

class MyRoomUpdater(IUpdater):
'''
    /!\ copy the whole class here

'''

########## Registering

def unreg_RoomUpdater(sender, args):
    '''event type function to plug unregistering operation'''
    if UpdaterRegistry.IsUpdaterRegistered(my_updater.GetUpdaterId()):
        
        UpdaterRegistry.UnregisterUpdater(my_updater.GetUpdaterId())
    
try:
    # create an instance with RevitPythonShell addin ID
    app = __revit__.Application
    my_updater = MyRoomUpdater(app.ActiveAddInId)
    
    # global registration
    UpdaterRegistry.RegisterUpdater(my_updater)
    roomfilter = RoomFilter()
    UpdaterRegistry.AddTrigger(my_updater.GetUpdaterId(), roomfilter, Element.GetChangeTypeGeometry())
    
    # plug the unregistering function to ApplicationClosing event
    __uiControlledApplication__.ApplicationClosing += unreg_RoomUpdater
    
except:
    import traceback       # note: add a python27 library to your search path first!
    traceback.print_exc()  # helps you debug when things go wrong


```
#### Less Simple Case : Specific Documents

Your updater applies only to some specific projects, and you want to automate the process ?
In this case, you need to add events since Revits starts to check if a project needs the DMU.

startup.py gives access to _ _uiControlledApplication_ _ in order to define new events functions.

For example, the DocumentOpened event allows to read project informations and check a condition.
DocumentClosing sounds good to unregister the updater.

In the below code, we create 2 functions, 
- checkUpdater() to check if our specific parameter 'DoubleHeight' is 
found in the project (you can replace this with any test) then run the updater,
- removeUpdater() to unregister the updater 

These "events functions" need to implement two specific parameters : sender and args.
- sender is the object who called event
- args gives access to the scope.


startup.py content :

```python
# script that is run when Revit starts in the IExternalApplication.Startup event.
__window__.Close()
from Autodesk.Revit.DB import Element, ChangePriority, SubTransaction
from Autodesk.Revit.DB import IUpdater, UpdaterId, UpdaterRegistry
from Autodesk.Revit.DB.Architecture import RoomFilter
from Autodesk.Revit.UI import TaskDialog
from System import Guid

########## Iupdater Class

class MyRoomUpdater(IUpdater):
'''
    /!\ copy your whole class here

'''
########## Events functions

def checkUpdater(sender, args):
    '''event type function to check if updater is needed,
    if the specific parameter is found -> registering '''
    
    doc = args.Document
    #search the specific shared parameter DoubleHeight
    paramHx2 = False
    params_proj = doc.ParameterBindings.GetEnumerator()
    params_proj.Reset()
    while params_proj.MoveNext():
        if params_proj.Key.Name == 'DoubleHeight':
            paramHx2 = True
            break
            
    if paramHx2 :
        # register the updater
        UpdaterRegistry.RegisterUpdater(my_updater, doc)
        roomfilter = RoomFilter()
        UpdaterRegistry.AddTrigger(my_updater.GetUpdaterId(), 
                                   roomfilter, Element.GetChangeTypeGeometry())
        
        # only for testing :
        TaskDialog.Show("MyRoomUpdater", 'MyRoomUpdater is enabled for this project')
    else:
        TaskDialog.Show("MyRoomUpdater", 'MyRoomUpdater is disabled for this project')

        
def removeUpdater(sender, args):
    '''event type function to unregister the updater from a document'''
    doc = args.Document
    if UpdaterRegistry.IsUpdaterRegistered(my_updater.GetUpdaterId(), doc):
        UpdaterRegistry.UnregisterUpdater(my_updater.GetUpdaterId(), doc)

 
def unreg_RoomUpdater(sender, args):
    '''event type function to globally unregister the updater'''
    if UpdaterRegistry.IsUpdaterRegistered(my_updater.GetUpdaterId()):
        UpdaterRegistry.UnregisterUpdater(my_updater.GetUpdaterId())
        
        
try:
    # create an instance 
    app = __revit__.Application
    my_updater = MyRoomUpdater(app.ActiveAddInId)
    
    # plug functions on events
    __uiControlledApplication__.ControlledApplication.DocumentOpened += checkUpdater
    __uiControlledApplication__.ControlledApplication.DocumentClosing += removeUpdater
    __uiControlledApplication__.ApplicationClosing += unreg_RoomUpdater
    
except:
    import traceback       # note: add a python27 library to your search path first!
    traceback.print_exc()  # helps you debug when things go wrong


```
## III. About ChangeType and Newly Added/Deleted Elements
    
GetChangeTypeGeometry() only works with created elements.
In our first example, a new created room will not trigger the updater.

New elements are catched by GetChangeTypeElementAddition() 
and the list is returned by UpdaterData.GetAddedElementIds() in the Execute method

So we only have to add a second trigger for those new elements :
```python
UpdaterRegistry.AddTrigger(my_updater.GetUpdaterId(), roomfilter, Element.GetChangeTypeElementAddition())
```

and deal with them in the Execute method :
```python
new_elems = updaterData.GetAddedElementIds()
```
if they use the same process, you can extend the first list :
```python
elems = updaterData.GetModifiedElementIds()
elems.AddRange(updaterData.GetAddedElementIds())
```

=> Check the whole code in version-startup\startup.py

Deleted elements are catched by GetChangeTypeElementDeletion, it may be useful depending on your updater
the list is return by UpdaterData.GetDeletedElementIds() in the Execute method

Other change types :
- GetChangeTypeAny, any change will trigger the updater 
    (caution : The API Bible teaches us that "Changes to an element by an Updater using this trigger 
    will result in re-triggering of the Updater" --> enough to summon an evil loop !)
    
- GetChangeTypeParameter, to check a specific parameter 
    (in our case, we could also watch unboundheight rather than the whole room geometry)
```python
UpdaterRegistry.AddTrigger(my_updater.GetUpdaterId(), roomfilter, Element.GetChangeTypeParameter("PARAM_OR_ID"))
```    
    
    
## IV. Ergonomic Improvement

I told you it was easy, i lied.
First, user had to do everything, now he is stuck with an automatic behavior... bravo !

In order to combine both systems, you can implement a dialogbox to offer a direct access to 
- display registering state information
- 'Enable' button for a newly created project
- 'Disable' button to stop the updater in this doc
- 'Disable all opened doc' (note : don't prevent from next opening)
- ...

### Startup + External file

This can be done into an external file plugged to a ribbon button.
Good new, no need to write your class again, import is allowed from the startup.py file .
    from startup import MyRoomUpdater

It can be useful to factorize and centralize some functions too.

Be careful with global variables like _ _window_ _ in startup.py, you can wrap them into :
```python
if __name__ == '__main__': 
```
=> Check the whole code for this version :

https://github.com/PMoureu/samples-Python-RPS/tree/master/Tutorial-IUpdater/version-startup

### Module + Startup + External file

Another approach, about factorizing and centralizing, you can also add the class and 
functions in a file in RevitPythonShell folder, next to startup.py and init.py, 
then import only what you need in startup and dialogmanager.
It takes one file more, but __everything is cleaner__ with many updaters:
- version-module\updater.py : contains all declarations (class, functions, updater reference)
- version-module\startup.py : only import and plug functions 
- version-module\dialogmanager.py  : only import and plug functions

=> Check the whole code for this version :

https://github.com/PMoureu/samples-Python-RPS/tree/master/Tutorial-IUpdater/version-module

Et voilà ! Thanks to RevitPythonShell our dynamic updater is ready and we didn't even talk about IExternalApplication, 
or other weird Revit Addins stuffs, we only have to borrow RPS AddinID for registration. I hope these examples could help
you to build powerful updaters.


##Special thanks to :
- Cyril Cros (MC BIM)
- Daren Thomas for letting us cast Python spells
- Jeremy Tammik 
- And ALL Revit/Python contributors
