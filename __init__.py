import sys,os
from cudatext import *
import cudatext_keys as keys
import cudatext_cmd as cmds
from subprocess import Popen, PIPE, STDOUT
from threading import Thread, Lock, active_count
from time import sleep

fn_icon = os.path.join(os.path.dirname(__file__), 'terminal.png')
fn_config = os.path.join(app_path(APP_DIR_SETTINGS), 'cuda_terminal.ini')
MAX_HISTORY = 20
DEF_SHELL = r'%windir%\system32\cmd' if os.name=='nt' else 'bash'
CODE_TABLE = 'cp866' if os.name=='nt' else 'utf8'

class ControlTh(Thread):
    def __init__(self, Cmd):
        Thread.__init__(self)
        self.Cmd = Cmd
    def run(self):
        if os.name != 'nt':
            while True:
                s = self.Cmd.p.stdout.read(1)
                if self.Cmd.p.poll() != None:
                    s = "\nConsole process was terminated.\n".encode(CODE_TABLE)
                    self.Cmd.block.acquire()
                    self.Cmd.btextchanged = True
                    self.Cmd.btext=self.Cmd.btext+s
                    self.Cmd.p=None
                    self.Cmd.block.release()
                    break
                if s != '':
                    self.Cmd.block.acquire()
                    self.Cmd.btextchanged = True
                    self.Cmd.btext=self.Cmd.btext+s
                    self.Cmd.block.release()
        else:
            while True:
                pp1 = self.Cmd.p.stdout.tell()
                self.Cmd.p.stdout.seek(0, 2)
                pp2 = self.Cmd.p.stdout.tell()
                self.Cmd.p.stdout.seek(pp1)
                if self.Cmd.p.poll() != None:
                    s = "\nConsole process was terminated.\n".encode(CODE_TABLE)
                    self.Cmd.block.acquire()
                    self.Cmd.btextchanged = True
                    self.Cmd.btext=self.Cmd.btext+s
                    self.Cmd.p=None
                    self.Cmd.block.release()
                    break
                if pp2!=pp1:
                    s = self.Cmd.p.stdout.read(pp2-pp1)
                    self.Cmd.block.acquire()
                    self.Cmd.btextchanged = True
                    self.Cmd.btext=self.Cmd.btext+s
                    self.Cmd.block.release()
                sleep(0.02)
    

class Command:

    def __init__(self):
    
        global CODE_TABLE
        CODE_TABLE = ini_read(fn_config, 'op', 'encoding', CODE_TABLE)
    
        self.shell_path = ini_read(fn_config, 'op', 'shell_path', DEF_SHELL)
        self.color_back = int(ini_read(fn_config, 'colors', 'back', '0x0'), 16)
        self.color_font = int(ini_read(fn_config, 'colors', 'font', '0xFFFFFF'), 16)
        self.history = []
        self.h_menu = menu_proc(0, MENU_CREATE)
        
        self.menu_calls = []
        self.menu_calls += [ lambda: self.run_cmd_n(0) ]
        self.menu_calls += [ lambda: self.run_cmd_n(1) ]
        self.menu_calls += [ lambda: self.run_cmd_n(2) ]
        self.menu_calls += [ lambda: self.run_cmd_n(3) ]
        self.menu_calls += [ lambda: self.run_cmd_n(4) ]
        self.menu_calls += [ lambda: self.run_cmd_n(5) ]
        self.menu_calls += [ lambda: self.run_cmd_n(6) ]
        self.menu_calls += [ lambda: self.run_cmd_n(7) ]
        self.menu_calls += [ lambda: self.run_cmd_n(8) ]
        self.menu_calls += [ lambda: self.run_cmd_n(9) ]
        self.menu_calls += [ lambda: self.run_cmd_n(10) ]
        self.menu_calls += [ lambda: self.run_cmd_n(11) ]
        self.menu_calls += [ lambda: self.run_cmd_n(12) ]
        self.menu_calls += [ lambda: self.run_cmd_n(13) ]
        self.menu_calls += [ lambda: self.run_cmd_n(14) ]
        self.menu_calls += [ lambda: self.run_cmd_n(15) ]
        self.menu_calls += [ lambda: self.run_cmd_n(16) ]
        self.menu_calls += [ lambda: self.run_cmd_n(17) ]
        self.menu_calls += [ lambda: self.run_cmd_n(18) ]
        self.menu_calls += [ lambda: self.run_cmd_n(19) ]
        self.menu_calls += [ lambda: self.run_cmd_n(20) ]
        self.p=None
        timer_proc(TIMER_START, self.timer_update, 150, tag="")
        self.title = 'Terminal'
        self.h_dlg = self.init_form()
        app_proc(PROC_BOTTOMPANEL_ADD_DIALOG, (self.title, self.h_dlg, fn_icon))
        app_proc(PROC_BOTTOMPANEL_ACTIVATE, self.title)
        self.block = Lock()
        self.block.acquire()
        self.btext=b''


    def open(self):
        if self.p == None:
            self.p = Popen(
                os.path.expandvars(self.shell_path),
                stdin = PIPE,
                stdout = PIPE,
                stderr = STDOUT,
                shell = True,
                bufsize = 0
                )

            #w,self.r=os.pipe()
            self.p.stdin.flush()
            self.CtlTh=ControlTh(self)
            self.CtlTh.start()
            self.s = ''
                

    def init_form(self):
    
        h = dlg_proc(0, DLG_CREATE)
        dlg_proc(h, DLG_PROP_SET, prop={
            'border': False,
            'keypreview': True,
            'on_key_down': self.form_key_down,
            })
        
        n = dlg_proc(h, DLG_CTL_ADD, 'editor')
        nn = dlg_proc(h, DLG_CTL_ADD, 'editor')
        
        self.memo = Editor(dlg_proc(h, DLG_CTL_HANDLE, index=n))
        self.input = Editor(dlg_proc(h, DLG_CTL_HANDLE, index=nn))
        
        dlg_proc(h, DLG_CTL_PROP_SET, index=n, prop={
            'name': 'memo',
            'align': ALIGN_CLIENT,
            })
        
        dlg_proc(h, DLG_CTL_PROP_SET, index=nn, prop={
            'name': 'input',
            'border': True,
            'align': ALIGN_BOTTOM,
            'h': 25,
            })
            
        dlg_proc(h, DLG_CTL_FOCUS, name='input')
        
        self.memo.set_prop(PROP_RO, True)
        self.memo.set_prop(PROP_CARET_VIRTUAL, False)
        self.memo.set_prop(PROP_GUTTER_ALL, False)
        self.memo.set_prop(PROP_COLOR, (COLOR_ID_TextFont, self.color_font))
        self.memo.set_prop(PROP_COLOR, (COLOR_ID_TextBg, self.color_back))
        
        self.input.set_prop(PROP_GUTTER_ALL, False)
        self.input.set_prop(PROP_ONE_LINE, True)
        self.input.set_prop(PROP_COLOR, (COLOR_ID_TextFont, self.color_font))
        self.input.set_prop(PROP_COLOR, (COLOR_ID_TextBg, self.color_back))
        
        return h


    def config(self):

        ini_write(fn_config, 'op', 'encoding', CODE_TABLE)
        ini_write(fn_config, 'op', 'shell_path', self.shell_path)
        ini_write(fn_config, 'colors', 'back', hex(self.color_back))
        ini_write(fn_config, 'colors', 'font', hex(self.color_font))
        
        file_open(fn_config)


    def timer_update(self, tag='', info=''):
        self.btextchanged = False
        self.block.release()
        sleep(0.03)
        self.block.acquire()
        if self.btextchanged:
            self.update_output(self.btext.decode(CODE_TABLE))


    def form_key_down(self, id_dlg, id_ctl, data='', info=''):
    
        if id_ctl==13: #Enter
            text = self.input.get_text_line(0)
            self.input.set_text_all('')
            self.input.set_caret(0, 0)
            self.run_cmd(text)
            return False
            
        if (id_ctl==keys.VK_DOWN):
            self.show_history()
            return False
            

    def show_history(self):
    
        menu_proc(self.h_menu, MENU_CLEAR)
        for (index, item) in enumerate(self.history):
            menu_proc(self.h_menu, MENU_ADD, 
                index=0, 
                caption=item, 
                command=self.menu_calls[index],
                )
                
        prop = dlg_proc(self.h_dlg, DLG_CTL_PROP_GET, name='input')
        x, y = prop['x'] + prop['w'], prop['y']
        x, y = dlg_proc(self.h_dlg, DLG_COORD_LOCAL_TO_SCREEN, index=x, index2=y)
        menu_proc(self.h_menu, MENU_SHOW, command=(x, y))
        
    def run_cmd(self, text):

        while len(self.history) > MAX_HISTORY:
            del self.history[0]

        try:
            n = self.history.index(text)
            del self.history[n]
        except:
            pass
            
        self.history += [text]
        
        if self.p != None: 
            self.p.stdin.write((text+'\n').encode(CODE_TABLE))
            self.p.stdin.flush()


    def run_cmd_n(self, n):
    
        self.run_cmd(self.history[n])        
        
        
    def add_output(self, s):
        self.memo.set_prop(PROP_RO, False)
        text = self.memo.get_text_all()
        self.memo.set_text_all(text+s)
        self.memo.set_prop(PROP_RO, True)
        
        self.memo.cmd(cmds.cCommand_GotoTextEnd)

    def update_output(self, s):
        self.memo.set_prop(PROP_RO, False)
        self.memo.set_text_all(s)
        self.memo.set_prop(PROP_RO, True)
        
        self.memo.cmd(cmds.cCommand_GotoTextEnd)

    def Exit(self, s):
        if self.p == None:
            self.p.stdout.write('exit\n')
