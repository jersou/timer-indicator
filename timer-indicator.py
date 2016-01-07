#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ⌛ ⌛ ⌛ ⌛ ⌛ ⌛ ⌛ ⌛ ⌛ ⌛ ⌛ ⌛ ⌛ ⌛ ⌛ ⌛ ⌛ ⌛ ⌛ ⌛ ⌛ ⌛ ⌛ ⌛ ⌛ ⌛ ⌛ ⌛ ⌛ ⌛ ⌛ ⌛ ⌛ ⌛ ⌛ ⌛ ⌛ ⌛ ⌛ ⌛ ⌛ ⌛ ⌛ ⌛ 
import gtk
import appindicator
import threading
import subprocess
import sys
import time
from subprocess import Popen

WAITING, PROCESSING, PAUSE = range(3)
WAITING_ICO = "waiting.png"
PROCESSING_ICO = "processing.png"
PAUSE_ICO = "pause.png"
SOUND = "/usr/share/sounds/ubuntu/stereo/message-new-instant.ogg"


class AppIndicator:
    state = WAITING
    time = time.time()
    timePause = -1
    sound = False
    
    def getTimerStr(self, *args):
      if args[1] >= 60 :
        if args[1]%60 == 0 :
          return "%i h" % (args[1]/60)
        else :
          return "%i h %i" % (args[1]/60,(args[1]%60))
      else :
        return "%i m" % args[1]
    
    def __init__(self):
        self.ind = appindicator.Indicator("timer-indicator",
            WAITING_ICO, appindicator.CATEGORY_APPLICATION_STATUS)
        self.ind.set_status (appindicator.STATUS_ACTIVE)
        self.menu = gtk.Menu()
        
        item = gtk.MenuItem("Stop")
        item.connect("activate", self.stop, None)
        self.menu.append(item)
        item = gtk.MenuItem("pause/continue")
        item.connect("activate", self.pausePlay, None)
        self.menu.append(item)
        list=[1,2,3,5,10,15,20,25,30,45,60,90,120,150,180,240,300]
        for t in list :
          item = gtk.MenuItem(self.getTimerStr(self, t))
          item.connect("activate", self.newTimer, t)
          self.menu.append(item)
        
        item = gtk.MenuItem("Custom")
        item.connect("activate", self.newCustomTimer, t)
        self.menu.append(item)
        
        item = gtk.MenuItem("Quitter")
        item.connect("activate", self.quit, None)
        self.menu.append(item)
        
        self.menu.show_all()
        self.ind.set_menu(self.menu)
        self.ind.set_label(" ")
        self.th = threading.Thread(target=self.loop)
        self.th.start()
    def quit(self, *args):
        print "quit"
        self.th._Thread__stop()
        gtk.main_quit()
        sys.exit()
        
    def stop(self, *args):
      self.state = WAITING
      self.time = time.time()
      self.ind.set_label(" ")
      self.ind.set_icon(WAITING_ICO)
      self.update()
        
    def newTimer(self, *args):
      self.sound = True
      self.state = PROCESSING
      self.time = time.time() + args[1]*60
      self.ind.set_icon(PROCESSING_ICO)
      self.update()
      
    def newCustomTimer(self, *args):
    	messagedialog = gtk.MessageDialog(parent=None, flags=0, type=gtk.MESSAGE_QUESTION, buttons=gtk.BUTTONS_OK, message_format="Nb min =")
	action_area = messagedialog.get_content_area()
	entry = gtk.Entry()
	entry.connect('activate', lambda _: messagedialog.response(gtk.RESPONSE_OK))
	action_area.pack_start(entry)
	messagedialog.show_all()
	messagedialog.run()
	nb = entry.get_text()
	messagedialog.destroy()
      	self.newTimer(self, int(nb))
        
    def pausePlay(self, *args):
      self.state = PAUSE
      self.ind.set_label("Pause !")
      if self.timePause > 0:
        self.newTimer(self, int(self.timePause/60)+1)
        self.timePause = -1
        self.update()
      else :
        self.timePause = int(self.time - time.time())
        self.ind.set_icon(PAUSE_ICO)
        self.update()
        
    def update(self):
      diff = int(self.time - time.time())
      if diff > 0:
        title = "0"
        if diff > 60:
          title = str(self.getTimerStr(self, int(diff/60)+1))
        else :
          title = str(diff)+" s"
        if self.state == PROCESSING:
          self.ind.set_label(title)
      else :
        if self.sound:
          Popen(['/usr/bin/mplayer',SOUND])
          self.sound = False
        if self.state == PROCESSING:
          if diff % 2 == 0:
            self.ind.set_icon(WAITING_ICO)
            self.ind.set_label("     - END -      ")
          else :
            self.ind.set_icon(PROCESSING_ICO)
            self.ind.set_label("PROCESS")
        if self.state == PAUSE:
          if diff % 2 == 0:
            self.ind.set_icon(WAITING_ICO)
            self.ind.set_label("END")
          else :
            self.ind.set_icon(PAUSE_ICO)
            self.ind.set_label("PAUSE")
    def loop(self):
      while 1:
        time.sleep(1)
        self.update()

gtk.gdk.threads_init()
AppIndicator()
gtk.main()
