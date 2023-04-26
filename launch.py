import os
import sys
import queue
import os.path
import imageio
import shutil
import threading
import tkinter as tk
from tkinter import ttk
import tkinter.ttk as ttk
from tkinter.constants import *
from PIL import Image, ImageTk
from dotenv import load_dotenv
from lib.img2img import ImageGenerator
from lib.frames2video import BashScriptRunner
from lib.gui import Toplevel1, MessageStream
_script = sys.argv[0]
_location = os.path.dirname(_script)
_bgcolor = '#d9d9d9'  # X11 color: 'gray85'
_fgcolor = '#000000'  # X11 color: 'black'
_compcolor = 'gray40'  # X11 color: #666666
_ana1color = '#c3c3c3'  # Closest X11 color: 'gray76'
_ana2color = 'beige'  # X11 color: #f5f5dc
_tabfg1 = 'black'
_tabfg2 = 'black'
_tabbg1 = 'grey75'
_tabbg2 = 'grey89'
_bgmode = 'light'
_style_code_ran = 0

# Load the environment variables from the .env file
load_dotenv()

MODEL = os.environ.get('MODEL')
FRAMES = os.environ.get('FRAMES')
OUTPUT = os.environ.get('OUTPUT')
OUTPUTVIDEOS = os.environ.get('OUTPUTVIDEOS')
VIDEO = os.environ.get('VIDEO')
SCRIPT = os.environ.get('SCRIPT')


if __name__ == "__main__":
    '''Main entry point for the application.'''
    global root
    root = tk.Tk()
    root.protocol('WM_DELETE_WINDOW', root.destroy)
    # Creates a toplevel widget.
    global _top1, _w1
    _top1 = root
    _w1 = Toplevel1(VIDEO, ImageGenerator, BashScriptRunner, FRAMES=FRAMES, OUTPUT=OUTPUT,
                    MODEL=MODEL, SCRIPT=SCRIPT,
                    OUTPUTVIDEOS=OUTPUTVIDEOS, VIDEO=VIDEO, top=_top1)
    _w1.reset_frames()
    sys.stdout = MessageStream(_w1.Message1)
    root.mainloop()
