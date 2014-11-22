#   Copyright (c) 2001-2014, The Foundry Visionmongers Ltd.
#   All Rights Reserved. Patents granted and pending.
#
import sys
import os

logfile = open("/tmp/modolog.txt", "a")


def log(msg):
    logfile.write(msg + "\n")
    logfile.flush()
    try:
        import lx
        lx.out(msg)
    except:
        pass

try:
    import lx
    import lxu
    import lxifc
    import lxtd
    import lxtd.constants
    MODO_AVAILABLE = True
    log("MODO startup")
except ImportError:
    print "not running in Modo"
    MODO_AVAILABLE = False
    log("MODO import fail")

try:
    modo_path = os.environ.get("MODO_PATH", "")
    for p in modo_path.split(':'):
        if p not in sys.path:
            sys.path.append(p)
            log("appended path '{0}'".format(p))
except:
    if MODO_AVAILABLE:
        lx.out("Error adding MODO_PATH")
    else:
        print("Error adding MODO_PATH")

from PySide import QtGui, QtCore

SHOTGUN_LOCALS = {}

_shotgun_parent = None
_shotgun_panel = None


def get_scene_filename():
    return lxtd.current_scene().filename or ""


def reset_scene():
    close_all_scenes()
    lx.eval('scene.new')


def save_scene():
    try:
        lx.eval('scene.save')
    except RuntimeError as e:
        if "Scene has not been changed" in e.message:
            # this is not really an error, accept silently
            return
        raise


def save_scene_as(filename):
    lx.eval("scene.saveAs {%s}" % filename)


def load_file(filename):
    lx.eval("scene.open {%s}" % filename)


def get_meshes():
    scene = lxtd.scene.current_scene()
    return  scene.meshes


def close_all_scenes():
    lx.eval("scene.closeAll")


def get_root_widget():
    return _shotgun_parent


def get_shotgun_widget():
    return _shotgun_panel


def get_references():

    scene_svc = lx.service.Scene()
    scene = lxu.select.SceneSelection().current()
     
    # we need to create a null terminated list of item type IDs and wrap it as a
    # storage object that we can pass to the lx.object.Scene.ItemCountByTypes &
    # lx.object.Scene.ItemByIndexByTypes methods later.
    itype_ids = [scene_svc.ItemTypeByIndex(x) for x in xrange(scene_svc.ItemTypeCount())]
    itype_ids.append(0)
    item_types = lx.object.storage()
    item_types.setType('i')
    item_types.set(itype_ids)
     
    # build a list of paths for referenced items in the scene
    refpaths = set()
    for x in xrange(scene.ItemCountByTypes(item_types)):
        try:
            refpaths.add(scene.ItemByIndexByTypes(item_types, x).Reference().Context().Filename())
        except LookupError:
            pass

    return refpaths

def item_channels(item):
    return dict([(c,item.get_channel(c)) for c in item.item.ChannelList()])
    
def all_item_channels(itemtype):
    scene = lxtd.current_scene()
    return [(item,item_channels(item)) for item in scene.items(itemtype)]

def item_types():
    return {lxtd.constants.SCENE_SVC.ItemTypeName(i):i for i in range(lxtd.constants.SCENE_SVC.ItemTypeCount())}



def add_disabled_menu():
    if not _shotgun_panel:
        return

    menu = _shotgun_panel.get_menu()
    if not menu:
        return

    disabled_title = "Shotgun is Disabled"
    disabled_menu_item = [item for item in menu.children() if item.title() == disabled_title]
    if not disabled_menu_item:
        menu.addAction(disabled_title, self.shotgun_disabled)


def remove_disabled_menu():
    if not _shotgun_panel:
        return

    menu = _shotgun_panel.get_menu()
    if not menu:
        return
    disabled_title = "Shotgun is Disabled"
    for item in menu.children():
        if item.title() == disabled_title:
            menu.removeAction(item)
    


class ModoSessionListener(lxifc.SessionListener):
    def sesl_FirstWindowOpening(self):
        lx.out('sesl_FirstWindowOpening(self):')
    def sesl_BeforeStartupCommands(self):
        lx.out('sesl_BeforeStartupCommands(self):')
    def sesl_SystemReady(self):
        lx.out('sesl_SystemReady(self):')
    def sesl_CheckQuitUI(self,quitWasAborted):
        lx.out('sesl_CheckQuitUI(self,quitWasAborted):')
    def sesl_QuittingUI(self):
        lx.out('sesl_QuittingUI(self):')
    def sesl_LastWindowClosed(self):
        lx.out('sesl_LastWindowClosed(self):')
    def sesl_ShuttingDown(self):
        lx.out('sesl_ShuttingDown(self):')



class ModoSceneListener(lxifc.SceneItemListener):
    def __init__(self):
        self.callbacks = {}


    def add_callback(self, topic,cb):
        self.callbacks.setdefault(topic,[]).append(cb)

    def remove_callback(self, topic,cb):
        callbacks =  self.callbacks.setdefault(topic,[])
        if cb in callbacks:
            callbacks.remove(cb)

    def sil_SceneDestroy(self,scene):
        #lx.out('sil_SceneDestroy(self,scene):')

        for cb in self.callbacks.get('sil_SceneDestroy',[]):
            try:
                cb(scene)
            except:
                pass


    def sil_SceneFilename(self,scene,filename):
        #lx.out('sil_SceneFilename(self,{0},{1}):'.format(scene,filename))
        for cb in self.callbacks.get('sil_SceneFilename',[]):
            try:
                cb(scene, filename)
            except:
                pass



    def sil_SceneClear(self,scene):
        #lx.out('sil_SceneClear(self,scene):')

        for cb in self.callbacks.get('sil_SceneClear',[]):
            try:
                cb(scene)
            except:
                pass
                
    def sil_ItemPreChange(self,scene):
        lx.out('sil_ItemPreChange(self,scene):')
    def sil_ItemPostDelete(self,scene):
        lx.out('sil_ItemPostDelete(self,scene):')
    def sil_ItemAdd(self,item):
        lx.out('sil_ItemAdd(self,item):')
    def sil_ItemRemove(self,item):
        lx.out('sil_ItemRemove(self,item):')
    def sil_ItemParent(self,item):
        lx.out('sil_ItemParent(self,item):')
    def sil_ItemChild(self,item):
        lx.out('sil_ItemChild(self,item):')
    def sil_ItemAddChannel(self,item):
        lx.out('sil_ItemAddChannel(self,item):')
    def sil_ItemLocal(self,item):
        lx.out('sil_ItemLocal(self,item):')
    def sil_ItemName(self,item):
        lx.out('sil_ItemName(self,item):')
    def sil_ItemSource(self,item):
        lx.out('sil_ItemSource(self,item):')
    def sil_ItemPackage(self,item):
        lx.out('sil_ItemPackage(self,item):')
    def sil_ChannelValue(self,action,item,index):
        lx.out('sil_ChannelValue(self,action,item,index):')
    def sil_LinkAdd(self,graph,itemFrom,itemTo):
        lx.out('sil_LinkAdd(self,graph,itemFrom,itemTo):')
    def sil_LinkRemBefore(self,graph,itemFrom,itemTo):
        lx.out('sil_LinkRemBefore(self,graph,itemFrom,itemTo):')
    def sil_LinkRemAfter(self,graph,itemFrom,itemTo):
        lx.out('sil_LinkRemAfter(self,graph,itemFrom,itemTo):')
    def sil_LinkSet(self,graph,itemFrom,itemTo):
        lx.out('sil_LinkSet(self,graph,itemFrom,itemTo):')
    def sil_ChanLinkAdd(self,graph,itemFrom,chanFrom,itemTo,chanTo):
        lx.out('sil_ChanLinkAdd(self,graph,itemFrom,chanFrom,itemTo,chanTo):')
    def sil_ChanLinkRemBefore(self,graph,itemFrom,chanFrom,itemTo,chanTo):
        lx.out('sil_ChanLinkRemBefore(self,graph,itemFrom,chanFrom,itemTo,chanTo):')
    def sil_ChanLinkRemAfter(self,graph,itemFrom,chanFrom,itemTo,chanTo):
        lx.out('sil_ChanLinkRemAfter(self,graph,itemFrom,chanFrom,itemTo,chanTo):')
    def sil_ChanLinkSet(self,graph,itemFrom,chanFrom,itemTo,chanTo):
        lx.out('sil_ChanLinkSet(self,graph,itemFrom,chanFrom,itemTo,chanTo):')
    def sil_ItemTag(self,item):
        lx.out('sil_ItemTag(self,item):')


class EventListener(object):
    """docstring for EventListener"""
    def __init__(self):

        self.listener_svc = lx.service.Listener()

        self.scene = ModoSceneListener()
        self.session = ModoSessionListener()

    def register(self):
        self.listener_svc.AddListener(self.scene)
        self.listener_svc.AddListener(self.session)


    def unregister(self):
        self.listener_svc.RemoveListener(self.scene)
        self.listener_svc.RemoveListener(self.session)

event_listener = EventListener()

class ShotgunWidget(QtGui.QWidget):
    def __init__(self, parent=None):        
        super(ShotgunWidget, self).__init__(parent)
        log("creating Shotgun wisget")
        self.lbl_hello = QtGui.QLabel("Hello From Shotgun")
        self.menubar = QtGui.QMenuBar()
        self.menu = self.menubar.addMenu("Shotgun")
        self.create_menu()
        self.layout = QtGui.QVBoxLayout()
        self.layout.addWidget(self.menubar)
        self.layout.addWidget(self.lbl_hello)
        self.layout.setContentsMargins(2, 2, 2, 2)
        self.setLayout(self.layout)

    def create_menu(self):
        self.menu.clear()        
        self.menu.addAction("Reload Shotgun", self.reload_shotgun)


    def shotgun_disabled(self):
        msg = ("Shotgun integration is disabled because it cannot recognize "
               "the currently opened file.  Try opening another file or "
               "restarting Maya." + repr(sys.stdout))

        QtGui.QMessageBox.information(None, "Sgtk is disabled", msg)

    def reload_shotgun(self, *args):
        log("reloading shotgun")
        try:
            #import rpdb2;rpdb2.start_embedded_debugger("1234")
            import init_tank
            reload(init_tank)
            
            init_tank.bootstrap_tank()

            import sgtk
            engine = sgtk.platform.current_engine()
            if engine:
                # ask the engine to build the menu:
                self.create_menu()
                engine.populate_shotgun_menu(self.menu)
            else:
                self.add_disabled_menu()
        except:
            import traceback
            traceback.print_exc()

    def get_menu(self):
        return self.menu

if MODO_AVAILABLE:
    class ShotgunCmd(lxu.command.BasicCommand):
        def __init__(self):
            lxu.command.BasicCommand.__init__(self)
            self.dyna_Add('command',  lx.symbol.sTYPE_STRING)      # 0
            #self.basic_SetFlags(1, lx.symbol.fCMDARG_OPTIONAL)
            
        def basic_Execute(self, msg, flags):
            command = self.dyna_String(0)
            try:
                exec command in SHOTGUN_LOCALS, SHOTGUN_LOCALS
            except:
                lx.out('SHOTGUN ERROR : {0} {1} {2}'.format(command, msg,flags))
                raise


    class ShotgunStartupCmd(lxu.command.BasicCommand):
        def __init__(self):
            lxu.command.BasicCommand.__init__(self)
            self.dyna_Add('command',  lx.symbol.sTYPE_STRING)      # 0
            #self.basic_SetFlags(1, lx.symbol.fCMDARG_OPTIONAL)
            
        def basic_Execute(self, msg, flags):
            command = self.dyna_String(0)
            #print 1/0
            try:
                lx.out('SHOTGUN Startup '+ command)
            except:
                lx.out('SHOTGUN ERROR : {0} {1} {2}'.format(command, msg,flags))
                raise


    class lxShotgunServer(lxifc.CustomView):

        def customview_Init(self, pane):
            global _shotgun_parent
            global _shotgun_panel

            log("customview_Init")

            if pane == None:
                return False

            custPane = lx.object.CustomPane(pane)

            if not custPane.test():
                return False

            # get the parent object
            parent = custPane.GetParent()

            # convert to PySide QWidget
            p = lx.getQWidget(parent)


            # Check that it suceeds
            if p != None:

                log("UI INIT")

                _shotgun_parent = p

                shotgunWidget  = ShotgunWidget(p)
                _shotgun_panel = shotgunWidget

                layout = QtGui.QVBoxLayout()
                layout.addWidget(shotgunWidget)
                layout.setContentsMargins(2,2,2,2)
                p.setLayout(layout)
                
                log("init_tank.bootstrap_tank")
                try:
                    shotgunWidget.reload_shotgun()
                    log("bootstrap completed")
                except:
                    log("bootstrap failed")
                    lx.out("can not import shotgun startup script")

                return True


            return False

        def customview_StoreState(self, pane):
            custpane = lx.object.CustomPane(pane)
            # TODO: what state needs to be saved ?


        def customview_RestoreState(self, pane):
            pass
            #custpane = lx.object.CustomPane(pane)
            # TODO: what state needs to be saved ?


        def customview_Cleanup(self, pane):
            try:
                self.customview_StoreState(pane)
            except RuntimeError, e:
                if e.message == "Internal C++ object (ShotgunWidget) already deleted.":
                    if hasattr(lx, "shotgun_widget"):
                        lx.shotgun_widget.destroy()


    log("blessing shotgun.eval")
    lx.bless(ShotgunCmd, "shotgun.eval")
    log("blessing shotgun.startup")
    lx.bless(ShotgunStartupCmd, "shotgun.startup")

    tags = {
        lx.symbol.sCUSTOMVIEW_TYPE: "vpeditors SCED shotgun @shotgun.view@Shotgun@",
    }


    event_listener.register()

    if( not lx.service.Platform().IsHeadless() ):
        lx.bless(lxShotgunServer, "Shotgun", tags)



def test():
    app = QtGui.QApplication(sys.argv)
    w = ShotgunWidget()
    w.show()
    app.exec_()

if __name__ == '__main__':
    test()