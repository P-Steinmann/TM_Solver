'''
    Transfer-Matrix-Solver Programm with Gui
    author: Paul Steinmann <p.steinmann@uni-bonn.de>
    Started : 10.01.2022
    Released: 28.01.2022
    Version: 1.0

        Version Added: 1.0.1
            Changed Gui style to ttks 'clam'
            Changed Style of the Progressbar
            Fixed a Bug for Electric Field displayment of the Im Part got too big.
        
        Version Added: 1.0.2
            Fixed a Bug in the displayment of the animated el. Field
            Added Design for new 'Compute' 'Parameter' vs 'Parameter' functionality
            Added a Generate_Eps_Th helper function for epsilon/thickness stack calculation to safe space/improve visuality
            Changed width of Thickness entry in 'Define Geometry'
            Adjusted the R vs Wavelength Precision to be fixed: 200 points
        
        Version Added: 1.0.3
            Hot Fix: Lambda as Thickness can be safed to geometry again
            Hot Fix: Resulting from above: Geometries can be loaded properly again
            Hot Fix: E_Field in Animation and in static are comparable and correct (hopefully)
        
        Version Added: 1.0.4
            Hot Fix: Reflectivity was computed starting from Vacuum, giving slightly wrong values, this was adjusted
            Final Fixes for E_Field/ E_Field animation (this time really, i hope)
            Added assertion errors in 'RvsParameter'
            Worked on RvsParameter... Soon there might be E_Field available ! Needs: Compute EMax in Layer... vs Thickness/Pairs of Layer ...
                Maybe if mode "E_Max" is selected then open up window where one can chose a medium
        
        Version Added: 1.0.5
            Plot labels for 'RvsParameter' adjusted
            Added in 'Add Layerstack' individual custom thicknesses
            Added some docstrings and smoothed some function
        
        Version Added: 1.0.6
            Changed the order of last row in Simulation Settings
            Added label 'of' in last row in Simulation Settings
            Beta Version of: Compute E_Field (in Material) vs "Thickness/Pairs" of Medium is done !
            Adjusted sample Geometries a little bit... Version 1.1 can come soon !!!
        
        Version Added: 1.0.7 -> New Version: 1.1.0
            Hot Fix: Corrected MgF2 refr. index, added absorbance of material
            RvsParameter now prints maximum and minimum
            Added some docstrings
            RvsParameter looks a little better...
            Combobox for RvsParameter functionalities added with automatic adjustment !
            Repositioned Set Range Top window
    
    Version: 1.1 08.02.2022

        Version Added: 1.1.1
            Repositioned "OnDoubleClick" window, added combobox
            Added options to enter AOI in Simulation Settings Frame
            Added automatic name adjustment if layername already exists
    
        Version Added: 1.1.2 -> New Version: 1.2.0
            Added Full AOI and Polarisation Mode Functionality !
            Tested with results from: https://www.jstage.jst.go.jp/article/matertrans/51/6/51_M2010003/_pdf/-char/en
            Added 'read only to all comboboxes
            
    Version: 1.2 10.02.2022

        Version Added: 1.2.1
            Improved Material functions for SiO2 and Si3N4, Added source
            Fixed an error in the GetDBRStack function
        
        Version Added: 1.2.2 -> New Version: 1.3.0
            Added functional "Reflectivity vs Wavelength vs LayerPairs" option
            Some adjustments to the plotting function were made

    Version: 1.3 12.02.2022

        Version Added: 1.3.1
            Added MaterialToList function
            Added Button "Add New Material To List" allowing own custom materials
            Added the window helper function
            Added some docstrings
        
        Version Added: 1.3.2 -> 1.4
            Changed Name "E_max_selected" to "EorN_selected"
            Added "n+ik" to Compute combobox
            Made some adjustments to RVsParameter -> n+ik is functional !
    
    Version: 1.4 19.02.2022
        
        Version Added: 1.4.1
            Added Docstring to every function
            Improved some function Designs
            Hot Fix for OnDoubleClick Function

    Progress until V2:
            
        Possible Upgrades:
            #'Compute R/E (in material) vs thickness/pairs of material' Clean up !
            #Add: Pairs Option !
            #make 'get data' into a helper function
            #layerStack: Thickness can be l/4, l/8, l/2, l, custom ?
            #Improve Design
            # / R vs layerpairs
            #Add More Materials
            #Add Combobox for RvsParameter functionalities!
            #on Double Click: topwindow position, material combobox !
            #if "Description" of material already exists add a number !
            #Compute E_MAX vs Parameter, E_MAX at Position
            #Angle of Incidence ?
            #read only comboboxes !
            #Add mode: Compute R vs: wavelength/AOI
            #polarisation mode
            #Compute R vs lamba vs layerpairs ?
            #Add Custom refr. index
            #Add Function Docstrings EVERYWHERE !!!
            #Add Option: Compute 'refractive index (n,k)' vs 'wavelength' of 'material'
            #Improve: OnDouble Click function !

            Adjust n+ik vs wavelength prints of material range excesission
            Allow saving and loading of custom materials
            Allow saving and loading of Geometries with custom materials
            Coloriezed Plots
            Ask for feedback     
            Add feedback/terminal window in programm (Nothing selected, errors, comp time, etc...)
            Improve speed of: Refl vs Wavelength; And: Dont allow button inputs while running
            Multi-Processing ?
            iF interpol range is reached, plot until this values and update range max
            Changable speed of animation
        
'''

# Non standard libaries are: Matplotlib, scipy, cmapy, pandas
#region ***** Imports *****

from optparse import Values
from tkinter import *
from tkinter import ttk
import os

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
try:
    from matplotlib.backends.backend_tkagg import NavigationToolbar2TkAgg
except ImportError:
    from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk as NavigationToolbar2TkAgg
import time
from PIL import Image
from PIL import ImageTk
from tkinter import filedialog as fd
import pandas as pd
from matplotlib import animation
import numpy as np
from numpy import sqrt
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
import threading
import queue
import cmapy
import random
import sys
#endregion 


Infotext = str('''Transfer-Matrix-Solver Programm with Gui: All Distances are in [um]!
Workflow: Geometry can be Designed in the upper region, edit entries by 'Double Clicking'. Example Geometries can be loaded.
Incident and Exit Media have to be well defined
Simulation: Center Wavelength is always used for layerstack thickness if not 'Custom'
Program Version 1.4.1                                                                                      Author: Paul Steinmann''')



class ROOT(Tk):

    def __init__(self):
    # Main Window Setup
        super().__init__()
        s = ttk.Style()
        s.theme_use('clam')
        #TROUGH_COLOR = 'grey55'
        #BAR_COLOR = 'lime green'
        s.configure("bar.Horizontal.TProgressbar", troughcolor="grey85", bordercolor= "grey30", background= "green3", lightcolor= "lawn green", darkcolor= "green4")
        self.title("TM Solver -- Nanophotonics")
        image = PhotoImage(file = os.path.join(os.path.dirname(__file__), "TM.PNG"))
        self.iconphoto(False, image)
        self.configure(background=('grey80'))
        self.minsize(1110, 710)
        self.maxsize(1110, 710)
        self.custom_mat = []
        self.custom_r_index = []
        self.material_list = ['Gold', 'Silver', 'Air','BK7', 'GaAs', 'AlAs', 'InAs', 'Si', 'TiO2', 'SiO2', 'Si3N4','Chrom', 'Copper', 'Water', 'FusedSilica', 'MgF2', 'h-BN', 'MoSe2-1L', 'WS2-1L']
        self.custom_index = complex(1, 0)
    # Frame for 'Define Geometry'
        self.frame0 = Frame(self, highlightbackground="gray", highlightthickness= 3, bg = "grey90")
        self.frame0.place(x=0,y=0, width = 600, height = 330)
        
        self.label_framehead = Label(self.frame0, text = "Define Geometry", bg = "red3", height = 1, font = ("Times New Roman", 20), relief = RIDGE, fg = "white", width = 38)
        self.label_framehead.grid(row = 0, column = 0, columnspan= 5, pady = 2)
        
        # Row 1
        self.label_name = Label(self.frame0, text = "Name of Layer", width = 15, bg = "grey90").grid(row = 1, column = 1)
        self.label_type = Label(self.frame0, text = "Type", width = 15, bg = "grey90").grid(row = 1, column= 2)
        self.label_th = Label(self.frame0, text = "Thickness [um]", width = 15, bg = "grey90").grid(row = 1, column= 3)

        self.button_custom = Button(self.frame0, text = "Add New\n Material To List", width = 13, height = 2, bg = "grey90", command = self.material_to_list)
        self.button_custom.grid(row = 1, column = 4, rowspan = 2)
        
        # Row 2
        self.button_Material = Button(self.frame0, text = "Add Material", width = 15, bg = "grey90", command = self.add_material).grid(row = 2, column = 0)
        self.entry_name = Entry(self.frame0, width = 15, highlightbackground="grey", highlightthickness= 1)
        self.entry_name.grid(row = 2, column= 1, pady = 5, padx = 1)
        self.entry_name.insert(END, "Medium1")
        self.var_Mat = StringVar()
        #S = ttk.Style() # Selectbackground: Color of Selected entry; Fieldbackground: Color of field where text is; background: arrow field color; (selected)foreground: text color
        #S.configure('TCombobox', parent='clam', settings = {'TCombobox':{'configure':{'foreground': 'black', 'selectbackground': 'grey1','selectedforeground': 'black','fieldbackground': 'navajo white','background': 'indian red'}}})
        #S.theme_use('combostyle')
        self.mode_Mat  = ttk.Combobox(self.frame0, textvariable=self.var_Mat, values= self.material_list, width = 10, state="readonly")
        self.mode_Mat.grid(row = 2, column = 2, pady = 5, columnspan= 1)
        self.mode_Mat.current(2)
        self.entry_th = Entry(self.frame0, width = 12, highlightbackground="grey", highlightthickness= 1)
        self.entry_th.grid(row = 2, column = 3, pady = 5, padx = 3)
        self.entry_th.insert(END, 1)

        # Row 3 & 4: Layer Stack Configurations
        self.button_LS = Button(self.frame0, text = "Add Layer-Stack", width = 15, bg = "grey90", command = self.add_layerstack).grid(row = 3, column = 0)
        self.entry_l1 = Entry(self.frame0, width = 15, highlightbackground="grey", highlightthickness= 1)
        self.entry_l1.grid(row = 3, column= 1, pady = 0, padx = 1)
        self.entry_l1.insert(END, "Layer1")
        self.var_l1 = StringVar()
        self.mode_l1  = ttk.Combobox(self.frame0, textvariable=self.var_l1, values= self.material_list, width = 10, state="readonly")
        self.mode_l1.grid(row = 3, column = 2, pady = 0, columnspan= 1)
        self.mode_l1.current(8)
        self.var_stack = StringVar()
        self.mode_stack = ttk.Combobox(self.frame0, textvariable=self.var_stack, values= [u'\u03bb / 4', u'\u03bb / 2', u'\u03bb / 1', 'Custom'], width = 10, state="readonly")
        self.mode_stack.grid(row = 3, column = 3, pady = 0, columnspan= 1)
        self.mode_stack.current(0)
        
        self.entry_l2 = Entry(self.frame0, width = 15, highlightbackground="grey", highlightthickness= 1)
        self.entry_l2.grid(row = 4, column= 1, pady = 0, padx = 1)
        self.entry_l2.insert(END, "Layer2")
        self.var_l2 = StringVar()
        self.mode_l2  = ttk.Combobox(self.frame0, textvariable=self.var_l2, values= self.material_list, width = 10, state="readonly")
        self.mode_l2.grid(row = 4, column = 2, pady = 0, columnspan= 1)
        self.mode_l2.current(9)
        self.var_stack.trace('w', self.is_custom)
            
        
        self.label_Npairs = Label(self.frame0, text = "No. of Pairs:", bg = "grey90").grid(row = 3, column = 4)
        self.entry_Npairs = Entry(self.frame0, width = 5, highlightbackground="grey", highlightthickness= 1)
        self.entry_Npairs.grid(row = 4, column= 4, pady = 0, padx = 1)
        self.entry_Npairs.insert(END, 10)
        
        # Row 5 & 6: Treeview Columns and Button For Geometry Plotting
        self.tree = ttk.Treeview(self.frame0, selectmode= "browse", height = 5)
        self.tree["columns"] = ('Description', 'Material Type', 'Thickness[um]', 'If Stack: Pairs')
        self.tree.column('#0', width = 0, stretch = NO) # Ghost column
        self.tree.column("Description", minwidth = 0, width = 120, stretch = NO, anchor=CENTER)
        self.tree.column("Material Type", minwidth = 0, width = 120, stretch = NO, anchor=CENTER)
        self.tree.column("Thickness[um]", minwidth = 0, width = 120, stretch = NO, anchor=CENTER)
        self.tree.column("If Stack: Pairs", minwidth = 0, width = 120, stretch = NO, anchor=CENTER)
        self.tree.heading('#0', text = '') # Ghost column
        self.tree.heading('Description', text = 'Description')
        self.tree.heading('Material Type', text = 'Material Type')
        self.tree.heading('Thickness[um]', text = 'Thickness[um]')
        self.tree.heading('If Stack: Pairs', text = 'If Stack: Pairs')
        self.tree.grid(row = 5, column = 0, rowspan= 3, columnspan = 4, sticky='nsew', padx = 1, pady = 5)
        self.tree['show'] = 'headings'
        
        # Row 5-7 Buttons
        self.button_remove = Button(self.frame0, text = "Remove Selection", bd = 3, width = 13, command = self.remove_selection).grid(row = 7, column = 4)
        self.button_MoveUp = Button(self.frame0, text = "Move Up", bd = 3, width = 13, command = self.move_up).grid(row = 5, column = 4)
        self.button_MoveDown = Button(self.frame0, text = "Move Down", bd = 3, width = 13, command = self.move_down).grid(row = 6, column = 4)
        self.tree.bind('<Double-1>', self.OnDoubleClick)
        
        # Row 8: Buttons for Treeview
        self.button_save = Button(self.frame0, text = "Save Geometry", bd = 3, width = 13, command = self.save_geometry).grid(row = 8, column = 0, pady = 2)
        self.button_load = Button(self.frame0, text = "Load Geometry", bd = 3, width = 13, command = self.load_geometry).grid(row = 8, column = 1)
        self.button_clearAll = Button(self.frame0, text = "Clear All", bd = 3, width = 13, command = self.remove_all).grid(row = 8, column = 3)
        self.button_showGeo = Button(self.frame0, text = "Show Geometry", bd = 5, width = 13, height = 1, command = self.show_geometry, background = "coral")
        self.button_showGeo.grid(row = 8, column = 4, padx = 3)
               
    # Frame to Display: 'Show Geometry'
        self.frame_ShowGeo = Frame(self, padx = 0, pady = 0, highlightbackground="gray", highlightthickness= 3, bg = 'grey90')
        self.frame_ShowGeo.place(x = 610, y  = 0, width = 500, height = 330)
    
    # Frame to Display: Simulation Results
        self.frame_ShowSim = Frame(self, padx = 0, pady = 0, highlightbackground="gray", highlightthickness= 3)
        self.frame_ShowSim.place(x = 610, y  = 355, width = 500, height = 355)
        
    # Frame for Simulation/Calculation Controls
        self.frame_Sim = Frame(self, padx = 5, pady = 10, highlightbackground="gray", highlightthickness= 3, bg = "grey90")
        self.frame_Sim.place(x = 0, y  = 355, width = 600, height = 270)
        
        self.label_framehead_Sim = Label(self.frame_Sim, text = "Simulation Settings", bg = "red3", height = 1, font = ("Times New Roman", 20), relief = RIDGE, fg = "white", width = 38)
        self.label_framehead_Sim.grid(row = 0, column = 0, columnspan= 5, pady = 2)
        # Row 1
        color_wav = "DarkOrange3"
        color_AOI = "darkblue"
        
        self.label_Wavelength = Label(self.frame_Sim, text = 'Settings [um]/[deg]:', bg = "grey90").grid(row = 1, column = 0)
        
        dummyframe_label = Frame(self.frame_Sim, bg = 'grey90')
        dummyframe_label.grid(row = 1, column = 1, columnspan = 1)
        self.label_wlCentre = Label(dummyframe_label, text = "Wavelength", bg = "grey90", fg = color_wav).grid(row = 0, column = 0)
        self.label_wlCentre2 = Label(dummyframe_label, text = "/", bg = "grey90").grid(row = 0, column = 1)
        self.label_AOI = Label(dummyframe_label, text = "AOI", bg = "grey90", fg = color_AOI).grid(row = 0, column = 2)
        
        self.label_wlRangeFrom = Label(self.frame_Sim, text = "Range Minimum", width = 15, bg = "grey90").grid(row = 1, column = 2)
        self.label_wlRangeTo = Label(self.frame_Sim, text = "Range Maximum", width = 15, bg = "grey90").grid(row = 1, column = 3)
        # Row 2
        self.var_pol= StringVar()
        self.mode_pol  = ttk.Combobox(self.frame_Sim, textvariable=self.var_pol, values= ['TM Polarisation', 'TE Polarisation'], state="readonly", width = 15)
        self.mode_pol.grid(row = 2, column = 0, pady = 0, columnspan= 1)
        self.mode_pol.current(1)
        
        dummyframe_w_aoi = Frame(self.frame_Sim, bg = 'grey90')
        dummyframe_w_aoi.grid(row = 2, column = 1, columnspan = 1)
        self.entry_wlCentre = Entry(dummyframe_w_aoi, width = 6, highlightbackground=color_wav, highlightthickness= 2)
        self.entry_wlCentre.grid(row = 0, column= 0, pady = 5, padx = 3)
        self.entry_wlCentre.insert(END, 0.780)
        self.entry_AOI = Entry(dummyframe_w_aoi, width = 6, highlightbackground=color_AOI, highlightthickness= 2)
        self.entry_AOI.grid(row = 0, column= 1, pady = 5, padx = 3)
        self.entry_AOI.insert(END, 0)
        
        dummyframe_w_aoi_range = Frame(self.frame_Sim, bg = 'grey90')
        dummyframe_w_aoi_range.grid(row = 2, column = 2, columnspan = 2)
        self.entry_wlRangeFrom = Entry(dummyframe_w_aoi_range, width = 6, highlightbackground=color_wav, highlightthickness= 2)
        self.entry_wlRangeFrom.grid(row = 0, column= 0, pady = 5, padx = 0)
        self.entry_wlRangeFrom.insert(END, 0.600)
        self.entry_AOIRangeFrom = Entry(dummyframe_w_aoi_range, width = 6, highlightbackground=color_AOI, highlightthickness= 2)
        self.entry_AOIRangeFrom.grid(row = 0, column = 1, pady = 5, padx = 12)
        self.entry_AOIRangeFrom.insert(END, 30)
        self.entry_wlRangeTo= Entry(dummyframe_w_aoi_range, width = 6, highlightbackground=color_wav, highlightthickness= 2)
        self.entry_wlRangeTo.grid(row = 0, column= 2, pady = 5, padx = 12)
        self.entry_wlRangeTo.insert(END, 0.86)
        self.entry_AOIRangeTo = Entry(dummyframe_w_aoi_range, width = 6, highlightbackground=color_AOI, highlightthickness= 2)
        self.entry_AOIRangeTo.grid(row = 0, column = 3, pady = 5, padx = 0)
        self.entry_AOIRangeTo.insert(END, 60)
        # Row 3
        self.button_RT = Button(self.frame_Sim, text = "Compute R/T at Center Wavelength", bd = 3, width = 40, command = self.R_T_atwavelength)
        self.button_RT.grid(row = 3, column = 0, columnspan = 2, pady = 3, padx = 5)
        self.var_R = StringVar()
        self.label_RT = Label(self.frame_Sim, textvariable= self.var_R, bg = "grey90", width = 16).grid(row = 3, column = 2, columnspan = 1)
        self.var_T = StringVar()
        self.label_RT = Label(self.frame_Sim, textvariable= self.var_T, bg = "grey90", width = 16).grid(row = 3, column = 3, columnspan = 1)
        # Row 4
        self.button_RvsW = Button(self.frame_Sim, text = "Compute Reflectivity vs", bd = 3, width = 18, command = self.R_vs_wavelength)
        self.button_RvsW.grid(row = 4, column = 0, columnspan = 1, pady = 3, padx = 5)
        
        self.var_RvsW_AOI= StringVar()
        self.mode_RvsW_AOI  = ttk.Combobox(self.frame_Sim, textvariable=self.var_RvsW_AOI, values= ['Wavelength', 'Angle of Incidence', u'\u03bb Vs Pairs of'], state="readonly", width = 17)
        self.mode_RvsW_AOI.grid(row = 4, column = 1, pady = 0, columnspan= 1)
        self.mode_RvsW_AOI.current(0)
        
        # Row 5
        self.button_EFD = Button(self.frame_Sim, text = "Compute Electric Field Distribution in Structure", bd = 3, width = 40, command = self.E_field_distribution)
        self.button_EFD.grid(row = 5, column = 0, columnspan = 2, pady = 3, padx = 5)
        
        self.abs = Image.open(os.path.join(os.path.dirname(__file__), "abs.png"))
        self.abs = self.abs.resize((80,20), Image.ANTIALIAS)
        self.abs = ImageTk.PhotoImage(self.abs)
        self.norm = Image.open(os.path.join(os.path.dirname(__file__), "norm.png"))
        self.norm = self.norm.resize((80,20), Image.ANTIALIAS)
        self.norm = ImageTk.PhotoImage(self.norm)
        self.button_sw = Button(self.frame_Sim, image = self.abs, bd = 3, command = self.switch)
        self.button_sw.grid(row = 5, column = 2, columnspan = 1, pady = 3)
        self.var_ani = IntVar()
        self.tickbox_ani = Checkbutton(self.frame_Sim, text = "Toggle Animation", variable=self.var_ani, onvalue=1, offvalue=0, width = 14)
        self.tickbox_ani.grid(row = 5, column = 3, columnspan=1, rowspan=1)
        
        # Row 6
        self.button_RvT = Button(self.frame_Sim, text = "Compute", bd = 3, width = 18, command = self.RvsParameter)
        self.button_RvT.grid(row = 6, column = 0, columnspan = 1, pady = 3, padx = 5)
        
        self.dummyframeS = Frame(self.frame_Sim, bg = 'grey80')
        self.dummyframeS.grid(row = 6, column = 1, pady = 0, columnspan = 2, padx = 0)
        self.var_Eval= StringVar()
        self.var_Eval.trace('w', self.EorN_selected)
        self.mode_Eval  = ttk.Combobox(self.dummyframeS, textvariable=self.var_Eval, values= ['Reflectivity', 'E_Field', 'n+ik'], state="readonly", width = 10)
        self.mode_Eval.grid(row = 0, column = 0, pady = 0, columnspan= 1, padx = 3)
        self.mode_Eval.current(0)
        self.label_vs = Label(self.dummyframeS, text = 'vs', bg = "grey80").grid(row = 0, column = 1, columnspan = 1, padx = 0)
        self.var_Para= StringVar()
        self.mode_Para  = ttk.Combobox(self.dummyframeS, textvariable=self.var_Para, values= ['Thickness', 'Pairs'], state="readonly", width = 10)
        self.mode_Para.grid(row = 0, column = 2, pady = 0, columnspan= 1, padx = 3)
        self.mode_Para.current(0)
        self.label_vs = Label(self.dummyframeS, text = 'of', bg = "grey80").grid(row = 0, column = 3, columnspan = 1, padx = 0)
        
        material_list_para = ['']
        self.var_Mat_para = StringVar()
        mode_Mat_para  = ttk.Combobox(self.dummyframeS, textvariable= self.var_Mat_para, values= material_list_para, state="readonly", width = 12)
        mode_Mat_para.grid(row = 0, column = 4, pady = 5, padx = 3, columnspan= 1)
        mode_Mat_para.current(0)

        self.button_ParaRange = Button(self.frame_Sim, text = "set Range", bd = 3, command = self.parameter_range, bg = "grey80")
        self.button_ParaRange.grid(row = 6, column = 3, padx = 5)
        
        self.ParamRange_upper = 10
        self.ParamRange_lower = 1
        self.ParamRange_Step  = 1
        
    # Info Frame
        self.frameI = Frame(self, highlightbackground="gray", highlightthickness= 3, bg = 'grey90')
        self.frameI.place(x = 0, y  = 630 , width = 600, height = 80)
        self.label_Info = Label(self.frameI, text = Infotext, justify = "left", font = ("Times New Roman", 8), width = 98, height = 5).place(x = 0, y  = 0)
        self.UBonn_Image = Image.open(os.path.join(os.path.dirname(__file__), "unibonn.jpg"))
        self.UBonn_Image = self.UBonn_Image.resize((42, 42))
        self.UBonn_Image = ImageTk.PhotoImage(self.UBonn_Image)
        self.image_UBonn = Label(self.frameI, image = self.UBonn_Image).place(x = 548, y = 30)

    # Geometry Functions
    def materials(self, Material, wavelength): 
        '''
        Returns the Effective Refractive Index for a given Material, depending on the wavelength.
        Values are for room temperature !
        
        Function Parameters
        ----------
        Material  :      str, String descr. the Material
        Materials : 'Chrom', 'Copper', Gold', 'Silver', 'Air','BK7', 'FusedSilica', 'GaAs', 'AlAs', 'InAs', 'Si', 'TiO2', 'SiO2', 'Si3N4', 'MgF2', 'h-BN', 'MoSe2-1L', 'WS2-1L'
        wavelength: int or float, Wavelength at which the Refr. Index will be determined [in nm!]
        
        Returns
        -------
        r_index : complex, eff. Refr. Index of Material at the given Wavelength
        '''
        # Gold Data
        dataGold = pd.read_csv(os.path.join(os.path.dirname(__file__), "Materials/JandCGold.txt"), delimiter = "\t", header = None)
        dataGoldi = pd.read_csv(os.path.join(os.path.dirname(__file__), "Materials/JandCGoldi.txt"), delimiter = "\t", header = None)
        dataGold = pd.DataFrame(data=dataGold)
        dataGoldi= pd.DataFrame(data=dataGoldi)
        dataGoldWl = dataGold[dataGold.columns[0]]
        dataGoldn  = dataGold[dataGold.columns[1]]
        dataGoldiWl = dataGoldi[dataGoldi.columns[0]]
        dataGoldin  = dataGoldi[dataGoldi.columns[1]]
        # Silver Data
        dataSilver= pd.read_csv(os.path.join(os.path.dirname(__file__), "Materials/JandCSilver.txt"), delimiter = "\t", header = None)
        dataSilveri = pd.read_csv(os.path.join(os.path.dirname(__file__), "Materials/JandCSilveri.txt"), delimiter = "\t", header = None)
        dataSilver = pd.DataFrame(data=dataSilver)
        dataSilveri= pd.DataFrame(data=dataSilveri)
        dataSilverWl = dataSilver[dataSilver.columns[0]]
        dataSilvern  = dataSilver[dataSilver.columns[1]]
        dataSilveriWl = dataSilveri[dataSilveri.columns[0]]
        dataSilverin  = dataSilveri[dataSilveri.columns[1]]
        # Chrom Data
        dataChrom= pd.read_csv(os.path.join(os.path.dirname(__file__), "Materials/chrom_real.txt"), delimiter = "\t", header = None)
        dataChromi = pd.read_csv(os.path.join(os.path.dirname(__file__), "Materials/chromIm.txt"), delimiter = "\t", header = None)
        dataChrom = pd.DataFrame(data=dataChrom)
        dataChromi= pd.DataFrame(data=dataChromi)
        dataChromWl = dataChrom[dataChrom.columns[0]]
        dataChromn  = dataChrom[dataChrom.columns[1]]
        dataChromiWl = dataChromi[dataChromi.columns[0]]
        dataChromin  = dataChromi[dataChromi.columns[1]]
        # Copper Data
        dataCopper= pd.read_csv(os.path.join(os.path.dirname(__file__), "Materials/cu_real.txt"), delimiter = "\t", header = None)
        dataCopperi = pd.read_csv(os.path.join(os.path.dirname(__file__), "Materials/cu_im.txt"), delimiter = "\t", header = None)
        dataCopper = pd.DataFrame(data=dataCopper)
        dataCopperi= pd.DataFrame(data=dataCopperi)
        dataCopperWl = dataCopper[dataCopper.columns[0]]
        dataCoppern  = dataCopper[dataCopper.columns[1]]
        dataCopperiWl = dataCopperi[dataCopperi.columns[0]]
        dataCopperin  = dataCopperi[dataCopperi.columns[1]]
        
        def n_Water(wavelength):
            if wavelength < 400 or wavelength > 1200:
                print("WARNING: Wavelength range for Material exceeded (Water)")
            w = (wavelength/1000)**2 # For sellmeier equation
            n = 1 + (5.684027565e-1*w)/(w-5.101829712e-3) + (1.726177391e-1*w)/(w-1.821153936e-2) + (2.086189578e-2*w)/(w-2.620722293e-2) + (1.130748688e-1*w)/(w-1.069792721e1)
            n = sqrt(n)
            k = 0 # Good Approximation above 400nm
            n = complex(n , k)
            return n
        def n_WS2_1L(wavelength):
            if wavelength < 400 or wavelength > 860:
                print("WARNING: Wavelength range for Material exceeded (WS2)")
            n = [3.78014, 4.51156, 5.20, 4.54, 4.64, 4.485, 4.782, 3.119, 5.895, 5.32, 4.85, 4.66, 4.4887, 4.11, 3.372, 3.22, 3.3345, 3.56, 3.78, 3.9]
            wn= [400, 428, 455, 505, 521, 540, 566, 605, 616, 625, 645, 700, 720, 740, 770, 796, 808, 834, 850, 860]
            n = interp1d(wn, n)
            n = n(wavelength)
            k = [2.2147, 1.6603, 1.5333, 1.1790, 0.86496, 0.98117, 1.4506, 1.106, 0.9551, 0.89614, 0.42446, 0.31879, 0.43512, 0.844, 2.959, 1.6916, 0.354, 0.27, 0.027, 0, 0]
            w = [400, 420, 440, 460, 484, 497, 515, 528, 538, 545, 570, 582, 592, 600, 610, 615, 625, 630, 670, 680, 860]
            k = interp1d(w, k)
            k = k(wavelength)
            n = complex(n, k)
            return n
        def n_MoSe2_1L(wavelength):
            if wavelength < 400 or wavelength > 860:
                print("WARNING: Wavelength range for Material exceeded (MoSe2_1L)")
            n = [3.8419, 3.2728, 4.2731, 5.3052, 5.5808, 5.5911, 5.6060, 5.3484, 5.1067, 4.8654, 5.4026, 5.0180, 4.9667, 5.7362, 5.6004, 4.9953, 4.8555, 4.7873]
            wn= [400, 420, 450, 480, 500, 540, 560, 600, 650, 678, 710, 750, 770, 795, 810, 840, 850, 860]
            n = interp1d(wn, n)
            n = n(wavelength)
            k = [1.3288, 2.2652, 2.9507, 3.0271, 2.3792, 1.5541, 1.1436, 1.0412, 0.90040, 0.9639, 1.3212, 1.1870, 0.52812, 0.3824, 0.4444, 0.70512, 0.5176, 0.00136, 0]
            w = [400, 420, 450, 465, 500, 550, 580, 600, 645, 660, 687, 695, 720, 740, 760, 779.5, 788, 808, 860]
            k = interp1d(w, k)
            k = k(wavelength)
            n = complex(n, k)
            return n
        # Add Absorbance !
        def n_hBN(wavelength):
            if wavelength < 400 or wavelength > 1200:
                print("WARNING: Wavelength range for Material exceeded (h-BN)")
            w = (wavelength/1000)**2 # For sellmeier equation
            n = 1 + 3.263*w/(w-0.1644**2)
            n = sqrt(n)
            k = 0 # Unknown
            n = complex(n , k)
            return n
        def n_MgF2(wavelength):
            if wavelength < 200 or wavelength > 2000:
                print("WARNING: Wavelength range for Material exceeded (MgF2)")
            if wavelength >= 500:
                n = (1.4168-1.424)/1800 * wavelength + 1.425
            else:
                n = (1.424 - 1.474)/300 * wavelength + 1.507
            k =  (1.69e-4 - 1.827e-3)/(2000 - 200) * wavelength + 0.002012 # Good Approximation
            n = complex(n , k)
            return n
        def n_InAs(wavelength):
            # Sellmeier Equation
            if wavelength < 400 or wavelength > 4000:
                print("WARNING: Wavelength range for Material exceeded (AlAs)")
            n = [3.7063, 4.3064, 4.8263, 4.2098, 3.9974, 3.8527, 3.7518, 3.6782, 3.6231, 3.5889, 3.5814, 3.5744, 3.5493, 3.5057, 3.4516, 3.4483, 3.4835, 3.5413, 3.5119]
            wn= [400, 450, 500, 550, 600, 650, 700, 750, 800, 840, 850, 860, 900, 1000, 1500, 2000, 2500, 3000, 4000]
            n = interp1d(wn, n)
            n = n(wavelength)
            k = [0.1285, 0.04260, 0.021, 3.4e-5, 8.8e-7, 1e-7]
            w = [400, 420, 440, 1000, 2000, 3000]
            k = interp1d(w, k)
            k = k(wavelength)
            n = complex(n, k)
            return n  
        def n_AlAs(wavelength):
            # Sellmeier Equation
            if wavelength < 400 or wavelength > 3000:
                print("WARNING: Wavelength range for Material exceeded (AlAs)")
            wavelength = wavelength / 1000 # thus in um
            n_2 = 2.0792 + 6.084*wavelength**2/(wavelength**2-0.2822**2) + 1.9*wavelength**2/(wavelength**2-27.62**2) # Dispersion Formula
            k = [0.1285, 0.04260, 0.021, 3.4e-5, 8.8e-7, 1e-7]
            w = [400, 420, 440, 1000, 2000, 3000]
            k = interp1d(w, k)
            k = k(wavelength*1000)
            n = complex(sqrt(n_2), k)
            return n  
        def n_GaAs(wavelength):
            if wavelength < 440 or wavelength > 2000:
                print("WARNING: Wavelength range for Material exceeded (GaAs)")
                n = 1
            if wavelength >= 970:
                w = wavelength/1000 # For Sellmeier Equation
                w = w**2
                n = sqrt(1 + 4.372514 + 5.4667*w/(w-0.44313**2) + 0.0243*w/(w-0.8746**2)+1.9575*w/(w-36.9166**2))
            if 440 <= wavelength < 970: # Papatryfonos et al. 2021
                n = [4.825, 4.6755, 4.551, 4.448, 4.361, 4.223, 4.1183, 4.0357, 3.9164, 3.872, 3.8194, 3.7662, 3.7223, 3.6765, 3.652, 3.618, 3.5845, 3.5708, 3.5461, 3.533, 3.51, 3.488]
                w = [440, 450, 460, 470, 480, 500, 520, 540, 580, 600, 630, 670, 700, 750, 800, 820, 840, 850, 880, 900, 940, 970]
                n = interp1d(w, n)
                n = n(wavelength)
            k = [1.258, 0.945, 0.76517, 0.5643, 0.4533, 0.306, 0.23, 0.18, 0.1296, 0.0988, 0.076, 0.0647, 0.0453, 0.0243, 0.01267, 2e-4, 0, 0, 0, 0]
            w = [440, 450, 460, 480, 500, 550, 600, 650, 700, 750, 800, 820, 840, 850, 860, 900, 1000, 1500, 1800, 2000]
            k = interp1d(w, k)
            k = k(wavelength)
            n = complex(n , k)
            return n
        def n_SiO2(wavelength):
            if wavelength < 250 or wavelength > 2500:
                print("WARNING: Wavelength range for Material exceeded (Si3N4)")
            # Source:  Opt. Express 20, 15734-15751 (2012)
            w = wavelength/1000 # For own fit to data
            A = 0.324
            B = 8.089
            C = 1.475
            D = -0.00955
            E = 0.00227898
            n = A * np.exp(-w*B) + C + D*w + E*w**2
            k = 0 # Good Approximation above 400nm
            n = complex(n , k)
            return n
        def n_Si3N4(wavelength):
            if wavelength < 310 or wavelength > 5500:
                print("WARNING: Wavelength range for Material exceeded (Si3N4)")
            # Source: Opt. Lett. 40, 4823-4826 (2015)
            w = (wavelength/1000)**2 # For sellmeier equation
            n0 = 1
            C0 = 3.0249
            C00 = 0.1353406**2
            C1 = 40314
            C11 = 1239.842**2
            n = n0 + C0*w/(w-C00) + C1*w/(w-C11)
            n = sqrt(n)
            k = 0 # Good Approximation below 3 um, okay below 5.5 um
            n = complex(n , k)
            return n
        def n_Chrom(wavelength):
            if wavelength < 190 or wavelength > 1900:
                print("WARNING: Wavelength range for Material exceeded (Chrom)")
            # Wavelength data in microns
            n = interp1d(dataChromWl, dataChromn)
            n = n(wavelength/1000)
            k = interp1d(dataChromiWl, dataChromin)
            k = k(wavelength/1000)
            n = complex(n , k)
            return n
        def n_Copper(wavelength):
            if wavelength < 190 or wavelength > 1900:
                print("WARNING: Wavelength range for Material exceeded (Copper)")
            # Wavelength data in microns
            n = interp1d(dataCopperWl, dataCoppern)
            n = n(wavelength/1000)
            k = interp1d(dataCopperiWl, dataCopperin)
            k = k(wavelength/1000)
            n = complex(n , k)
            return n
        def n_Gold(wavelength):
            if wavelength < 190 or wavelength > 1900:
                print("WARNING: Wavelength range for Material exceeded (Gold)")
            # Wavelength data in microns
            n = interp1d(dataGoldWl, dataGoldn)
            n = n(wavelength/1000)
            k = interp1d(dataGoldiWl, dataGoldin)
            k = k(wavelength/1000)
            n = complex(n , k)
            return n
        def n_Silver(wavelength):
            if wavelength < 190 or wavelength > 1900:
                print("WARNING: Wavelength range for Material exceeded (Silver)")
            # Wavelength data in microns
            n = interp1d(dataSilverWl, dataSilvern)
            n = n(wavelength/1000)
            k = interp1d(dataSilveriWl, dataSilverin)
            k = k(wavelength/1000)
            n = complex(n , k)
            return n
        def n_Air(wavelength):
            a = 0.0579211
            b = 0.0016792
            n = a/(238.0185-pow(wavelength, -2)) + b/(57.362 - pow(wavelength, -2)) + 1
            k = 0 # Good Approximation always
            n = complex(n , k)
            return n
        def n_FusedSilica(wavelength):
            w = (wavelength/1000)**2 # For sellmeier equation
            n = 1 + 0.696166*w/(w-0.068404**2) + 0.407943*w/(w-0.1162414**2) + 0.8974794*w/(w-9.896161**2)
            n = sqrt(n)
            k = 0 # Good Approximation above 400nm
            n = complex(n , k)
            return n
        def n_BK7(wavelength):
            # lambda in microns
            wavelength = wavelength / 1000 # thus in um
            one   = 1.03961212*wavelength**2/(wavelength**2-0.0060007)
            two   = 0.23179234*wavelength**2/(wavelength**2-0.0200179)
            three = 1.01046945*wavelength**2/(wavelength**2-103.56065)
            sum = one + two + three + 1
            n = np.sqrt(sum)
            k = 0 # Good Approximation above 400nm
            n = complex(n , k)
            return n
        def n_Si(wavelength):
            # 0.4 - 10 um
            if wavelength < 400 or wavelength > 3000:
                print("WARNING: Wavelength range for Material exceeded (Si)")
            # Wavelength in um: Sellmeier Equation
            if wavelength < 0.4:
                print("Error in Material wavelength")
            w2 = (wavelength/1000)**2
            A = 10.6684293 * w2/(w2 - 0.3015165**2)
            B = 0.0030434748 * w2/(w2 - 1.13475115**2)
            C = 1.54133408 * w2/(w2 - 1104**2)
            n2 = 1 + A + B + C
            n = sqrt(n2)
            k = [0.386, 0.1703, 0.14851, 0.07053, 0.0274, 0.00654, 5e-4, 1e-13, 0]
            w = [400, 440, 450, 500, 600, 800, 1000, 1500, 3000]
            k = interp1d(w, k)
            k = k(wavelength)
            n = complex(n , k)
            return n
        def n_TiO2(wavelength):
            n2 = 5.913 + 0.2441/(wavelength**2 - 0.0803)
            n = sqrt(n2)
            k = 0 # Good Approximation always
            n = complex(n , k)
            return n
        # Assigning values to the Material
        # 'Chrom', 'Copper', Gold', 'Silver', 'Air','BK7', 'GaAs', 'AlAs', 'Si', 'TiO2', 'SiO2', 'Si3N4', 'FusedSilica'
        if Material == 'SiO2':
            r_index = n_SiO2(wavelength)
        elif Material == 'Chrom':
            r_index = n_Chrom(wavelength)
        elif Material == 'Copper':
            r_index = n_Copper(wavelength)  
        elif Material == 'Gold':
            r_index = n_Gold(wavelength)  
        elif Material == 'Silver':
            r_index = n_Silver(wavelength)
        elif Material == 'Air':
            r_index = n_Air(wavelength) 
        elif Material == 'BK7':
            r_index = n_BK7(wavelength)
        elif Material == 'Si':
            r_index = n_Si(wavelength)
        elif Material == 'Si3N4':
            r_index = n_Si3N4(wavelength)
        elif Material == 'GaAs':
            r_index = n_GaAs(wavelength)
        elif Material == 'AlAs':
            r_index = n_AlAs(wavelength)
        elif Material == 'TiO2':
            r_index = n_TiO2(wavelength) 
        elif Material == 'FusedSilica':
            r_index = n_FusedSilica(wavelength) 
        elif Material == 'InAs':
            r_index = n_InAs(wavelength)
        elif Material == 'MgF2':
            r_index = n_MgF2(wavelength)
        elif Material == 'MoSe2-1L':
            r_index = n_MoSe2_1L(wavelength)
        elif Material == 'WS2-1L':
            r_index = n_WS2_1L(wavelength)
        elif Material == 'h-BN':
            r_index = n_hBN(wavelength)
        elif Material == 'Water':
            r_index = n_Water(wavelength)
        elif Material in self.custom_mat:
            for i in range(len(self.custom_mat)):
                if Material == self.custom_mat[i]:
                    r_index = self.custom_r_index[i]

        else:
            print("Error while recieving material for layers")
        # Return Indicees for Materials
        return r_index

    def material_to_list(self):
        '''
        Function to Button "Add New Material To List", allows the user to open up
        a Toplevel window and Enter new Material description/Properties

        Function Parameters
        ----------
        None
        
        Returns
        -------
        None
        '''
        win = self.window(400, 60, 195, 120, "Add custom material to material list")

        col0Lbl = Label(win, text = "Material Name: ", width = 12)
        col0Ent = Entry(win, highlightbackground="grey", highlightthickness= 1, width = 12)
        col0Ent.insert(END, "Custom")
        col0Lbl.grid(row = 0, column = 0, pady = 3, padx = 3)
        col0Ent.grid(row = 1, column = 0, pady = 3, padx = 3)

        col1Lbl = Label(win, text = "Index Real Part: ", width = 12)
        col1Ent = Entry(win, highlightbackground="grey", highlightthickness= 1, width = 12)
        col1Ent.insert(END, 1)
        col1Lbl.grid(row = 0, column = 1, pady = 3, padx = 3)
        col1Ent.grid(row = 1, column = 1, pady = 3, padx = 3)
        col2Lbl = Label(win, text = "Index Imag Part: ", width = 12)
        col2Ent = Entry(win, highlightbackground="grey", highlightthickness= 1, width = 12)
        col2Ent.insert(END, 1)
        col2Lbl.grid(row = 0, column = 2, pady = 3, padx = 3)
        col2Ent.grid(row = 1, column = 2, pady = 3, padx = 3)

        def UpdateThenDestroy():
            n = float(col1Ent.get())
            k = float(col2Ent.get())
            custom_r_index = complex(n, k)
            if col0Ent.get() in self.material_list:
                print("Material Name is not unique")
            else:
                self.material_list.append(col0Ent.get())
                self.mode_Mat.config(values = self.material_list)
                self.mode_l1.config(values = self.material_list)
                self.mode_l2.config(values = self.material_list)
                self.custom_mat.append(col0Ent.get())
                self.custom_r_index.append(custom_r_index)
                win.destroy()
                
        okButt = Button(win, text = "Apply")
        okButt.bind("<Button-1>", lambda e: UpdateThenDestroy())
        okButt.grid(row = 1, column = 3, pady = 3, padx = 5)

        canButt = Button(win, text = "Cancel")
        canButt.bind("<Button-1>", lambda c: win.destroy())
        canButt.grid(row = 1, column = 4, pady = 3, padx = 5)

    def add_material(self):
        '''
        Adds an in the GUI defined Material to the Treeview Layer list

        Reads the parameters of material description, type and thickness

        Function Parameters
        ----------
        None
        
        Returns
        -------
        None
        '''
        # check if name already exists:
        wavel = float(self.entry_wlCentre.get())*1000
        desc_list, r_index_list, n_list, t_list, is_stack  = self.Get_GeometryData(wavel)
        name = self.entry_name.get()    #str
        for desc in desc_list: # For every Description in Treeview
            if desc == name:   # Check if the new Description is equal
                name_new = ''
                for letter in name: # If so, check every letter
                    if letter.isdigit(): # If there is a digit, increment by one
                        letter = str(int(letter) + 1)
                    name_new = name_new + letter
                if not name[-1].isdigit():
                    name_new = name + "1"
                name = name_new
        
        type = self.mode_Mat.get()     #str
        thickness = float(self.entry_th.get()) #float
        self.tree.insert('', 'end', text='', values=(name, type, thickness, 0))
        
        # Create Combobox of Layers
        wavel = float(self.entry_wlCentre.get())*1000
        desc_list, r_index_list, n_list, t_list, is_stack  = self.Get_GeometryData(wavel)
        self.material_list_para = desc_list
        self.var_Mat_para = StringVar()
        mode_Mat_para  = ttk.Combobox(self.dummyframeS, textvariable= self.var_Mat_para, values= self.material_list_para, width = 12, state="readonly")
        mode_Mat_para.grid(row = 0, column = 4, pady = 5, padx = 3, columnspan= 1)
        mode_Mat_para.current(0)
        self.frame_Sim.update_idletasks()
        
    def add_layerstack(self):
        '''
        Adds an in the GUI defined Layerstack to the Treeview Layer list

        Reads the parameters of both layer descriptions, types and thicknesses
            Thicknesses are either a fraction of the center wavelength or custom given
        
        Function Parameters
        ----------
        None
        
        Returns
        -------
        None
        '''
        # check if name already exists:
        wavel = float(self.entry_wlCentre.get())*1000
        desc_list, r_index_list, n_list, t_list, is_stack  = self.Get_GeometryData(wavel)
        
        nameL1 = self.entry_l1.get()
        nameL2 = self.entry_l2.get()
        for desc in desc_list:   # For every Description in Treeview
            if desc == nameL1:   # Check if the new Description is equal
                name_new = ''
                for letter in nameL1:    # If so, check every letter
                    if letter.isdigit(): # If there is a digit, increment by one
                        letter = str(int(letter) + 1)
                    name_new = name_new + letter
                if not nameL1[-1].isdigit():
                    name_new = nameL1 + "1"
                nameL1 = name_new
            if desc == nameL2 or nameL1 == nameL2:
                name_new = ''
                for letter in nameL2:    # If so, check every letter
                    if letter.isdigit(): # If there is a digit, increment by one
                        letter = str(int(letter) + 1)
                    name_new = name_new + letter
                if not nameL2[-1].isdigit():
                    name_new = nameL2 + "2"
                nameL2 = name_new
                
        if nameL1 == nameL2:
            nameL2 = nameL2 + '1'
        
        typeL1 = self.mode_l1.get() 
        typeL2 = self.mode_l2.get()
        Pairs = int(self.entry_Npairs.get())

        thickness = self.mode_stack.get()
        thickness2= thickness
        if thickness == 'Custom':   
            thickness = self.entry_custom.get()
            thickness2= self.entry_custom2.get()

        self.tree.insert('', 'end', text='', values=(nameL1, typeL1, thickness, Pairs))
        self.tree.insert('', 'end', text='', values=(nameL2, typeL2, thickness2, Pairs))
        
        # Create Combobox of Layers
        wavel = float(self.entry_wlCentre.get())*1000
        desc_list, r_index_list, n_list, t_list, is_stack  = self.Get_GeometryData(wavel)
        self.material_list_para = desc_list
        self.var_Mat_para = StringVar()
        mode_Mat_para  = ttk.Combobox(self.dummyframeS, textvariable= self.var_Mat_para, values= self.material_list_para, width = 12, state="readonly")
        mode_Mat_para.grid(row = 0, column = 4, pady = 5, padx = 3, columnspan= 1)
        mode_Mat_para.current(0)
        self.frame_Sim.update_idletasks()
    
    def save_geometry(self):
        '''
        Similar to the Get_GeometryData function, reads treeview content and writes it to a desired data file.
        Entries are separated by tab and each row starts in a new line.

        Function Parameters
        ----------
        None
        
        Returns
        -------
        None
        '''

        # Open Explorer: Save file as ...
        tf = fd.asksaveasfile(mode='w', title ="Save file", defaultextension=".txt")
        
        # Get data from treeview content and write to lists.
        data = ''
        type_list = []
        desc_list = []
        d_list = []
        Pairs  = []
        for line in self.tree.get_children():
            line_content = ''
            for value in self.tree.item(line)['values']:
                if line_content == '':
                    line_content = line_content+str(value)
                else:
                    line_content = line_content + '\t' + str(value)
            words = line_content.split('\t')
            type_list.append(words[1])
            try:
                d_list.append(float(words[2]))
            except:
                words[2] = int(words[2].encode().replace(b"\xce\xbb / ",b"").decode()) # translate 'lambda' sign to wavelength
                if words[2] == 4:
                    d_list.append("wavelength/4")
                if words[2] == 2:
                    d_list.append("wavelength/2")
                if words[2] == 1:
                    d_list.append("wavelength/1")
            Pairs.append(int(words[3]))
            desc_list.append(words[0])
            
        for i in range(len(Pairs)):
            data = data + desc_list[i] + '\t' + type_list[i] + '\t' + str(d_list[i])  + '\t' + str(Pairs[i])
            if i < len(Pairs)-1:
                data = data + '\n'
        
        tf.write(data)
        tf.close()
                   
    def load_geometry(self):
        '''
        Opens the Explorer file selection to load a data file 
        and writes the files content into the treeview tabular

        Function Parameters
        ----------
        None
        
        Returns
        -------
        None
        '''
        # Select a File and open it
        filetypes = (("text files", "*.txt"), ("All files", "*.*"))
        filename = fd.askopenfilename(title='Open a file', initialdir='Geometries', filetypes=filetypes)
        file = open(filename)
        file_cont = file.read()
        
        # Create Lists of words from file...
        words = file_cont.split('\t')
        
        # And Split words connected by \n
        for i in range(len(words)):
            words[i] = words[i].split('\n')
        # Here the last entry of a row is still connected to the first of the next
        
        # This is corrected here: Now create the final list of all words in the file 
        new = []
        for content in words:
            if len(content) == 2:
                new.append(content[0])
                new.append(content[1])
            if len(content) == 1:
                new.append(content[0])
        words = new
        
        # Each line has 4 words: Insert content line by line in treeview
        for i in range(0, len(words), 4):
            
            # Change from 'wavelength' to 'lambda-symbol'
            if words[i+2].split('/')[0] == "wavelength":
                Num = words[i+2].split('/')[1]
                words[i+2] = (b"\xce\xbb / ").decode() + Num
            
            self.tree.insert('', 'end', text='', values=(words[i], words[i+1], words[i+2], words[i+3]))

        file.close()
        
        # Create Combobox of Layers
        wavel = float(self.entry_wlCentre.get())*1000
        desc_list, r_index_list, n_list, t_list, is_stack  = self.Get_GeometryData(wavel)
        self.material_list_para = desc_list
        self.var_Mat_para = StringVar()
        mode_Mat_para  = ttk.Combobox(self.dummyframeS, textvariable= self.var_Mat_para, values= self.material_list_para, width = 12)
        mode_Mat_para.grid(row = 0, column = 4, pady = 5, padx = 3, columnspan= 1)
        mode_Mat_para.current(0)
        self.frame_Sim.update_idletasks()
    
    def remove_selection(self):
        '''
        Deletes an in the treeview tabular selected row

        Function Parameters
        ----------
        None
        
        Returns
        -------
        None
        '''
        selected = self.tree.selection()[0]
        self.tree.delete(selected)
        
        # Create Combobox of Layers
        wavel = float(self.entry_wlCentre.get())*1000
        desc_list, r_index_list, n_list, t_list, is_stack  = self.Get_GeometryData(wavel)
        self.material_list_para = desc_list
        self.var_Mat_para = StringVar()
        mode_Mat_para  = ttk.Combobox(self.dummyframeS, textvariable= self.var_Mat_para, values= self.material_list_para, width = 12)
        mode_Mat_para.grid(row = 0, column = 4, pady = 5, padx = 3, columnspan= 1)
        mode_Mat_para.current(0)
        self.frame_Sim.update_idletasks()
    
    def remove_all(self):
        '''
        Removes all treeview tabular content

        Function Parameters
        ----------
        None
        
        Returns
        -------
        None
        '''
        self.tree.delete(*self.tree.get_children())
        
        # Create Combobox of Layers
        wavel = float(self.entry_wlCentre.get())*1000
        desc_list, r_index_list, n_list, t_list, is_stack  = self.Get_GeometryData(wavel)
        self.material_list_para = ['']
        self.var_Mat_para = StringVar()
        mode_Mat_para  = ttk.Combobox(self.dummyframeS, textvariable= self.var_Mat_para, values= self.material_list_para, width = 12)
        mode_Mat_para.grid(row = 0, column = 4, pady = 5, padx = 3, columnspan= 1)
        mode_Mat_para.current(0)
        self.frame_Sim.update_idletasks()
    
    def move_up(self):
        '''
        A selected entry in the treeview tabular is moved up by one position

        Function Parameters
        ----------
        None
        
        Returns
        -------
        None
        '''
        leaves = self.tree.selection() #Get all leaves of the tree
        for i in reversed(leaves):
            self.tree.move(i, self.tree.parent(i), self.tree.index(i)-1)
        
        # Create Combobox of Layers
        wavel = float(self.entry_wlCentre.get())*1000
        desc_list, r_index_list, n_list, t_list, is_stack  = self.Get_GeometryData(wavel)
        self.material_list_para = desc_list
        self.var_Mat_para = StringVar()
        mode_Mat_para  = ttk.Combobox(self.dummyframeS, textvariable= self.var_Mat_para, values= self.material_list_para, width = 12)
        mode_Mat_para.grid(row = 0, column = 4, pady = 5, padx = 3, columnspan= 1)
        mode_Mat_para.current(0)
        self.frame_Sim.update_idletasks()
    
    def move_down(self):
        '''
        A selected entry in the treeview tabular is moved down by one position

        Function Parameters
        ----------
        None
        
        Returns
        -------
        None
        '''
        leaves = self.tree.selection() #Get all leaves of the tree
        for i in reversed(leaves):
            self.tree.move(i, self.tree.parent(i), self.tree.index(i)+1)
        
        # Create Combobox of Layers
        wavel = float(self.entry_wlCentre.get())*1000
        desc_list, r_index_list, n_list, t_list, is_stack  = self.Get_GeometryData(wavel)
        self.material_list_para = desc_list
        self.var_Mat_para = StringVar()
        mode_Mat_para  = ttk.Combobox(self.dummyframeS, textvariable= self.var_Mat_para, values= self.material_list_para, width = 12)
        mode_Mat_para.grid(row = 0, column = 4, pady = 5, padx = 3, columnspan= 1)
        mode_Mat_para.current(0)
        self.frame_Sim.update_idletasks()
    
    def show_geometry(self):
        '''
        Displayes the Desiged Geometry in a Plot: Ref.index vs thickness

        Function Parameters
        ----------
        None
        
        Returns
        -------
        None
        '''
        # Analyse Treeview content and extract: Materials, Thicknesses and if it is a layerstack or not
        wavel = float(self.entry_wlCentre.get())*1000
        desc_list, r_index_list, n_list, t_list, is_stack  = self.Get_GeometryData(wavel)

        # Generate XDATA: list of thicknesses
        x_data = t_list
        # Generate YDATA: list of refr. Indicees
        y_data = []
        for material in r_index_list:
            y_data.append(self.materials(material, wavel))
        eps = []
        for y in y_data:
            n_r = y.real
            n_i = y.imag
            eps_r = n_r**2 - n_i**2
            eps_i = 2*n_r*n_i
            eps.append(complex(round(eps_r,5), round(eps_i,5)))
        print("Geometry:")
        print("Stack Length:", [round(x,5) for x in x_data])
        print("Stack Index :", [round(y.real,5)+round(y.imag, 5)*1j for y in y_data])
        print("Stack Eps.  :", eps)
        # Generate Plot Data ('l' steps per material)
        x_list = []
        y_list = []
        l = 2
        x_t = 0
        k = 0
        while k < (len(x_data)):
            num = t_list[k]/(l-1)
            if is_stack[k] == 0:
                for i in range(l):
                    x_list.append(x_t+num*i)
                    y_list.append(y_data[k].real)
                x_t = x_t + t_list[k]
            else:
                for _ in range(int(is_stack[k])):
                    for i in range(l):
                        num = t_list[k]/(l-1)
                        x_list.append(x_t+num*i)
                        y_list.append(y_data[k].real)
                    x_t = x_t + t_list[k]
                    for i in range(l):
                        
                        num = t_list[k+1]/(l-1)
                        x_list.append(x_t+num*i)
                        y_list.append(y_data[k+1].real)
                    x_t = x_t + t_list[k+1]
                k = k + 1
            k = k +1
        # Display the final data:
        self.matplotCanvas(frame = self.frame_ShowGeo, x = x_list, y = y_list, xlabel= 'length [um]', label = "Material index",
                           ylabel= 'Eff. Refractive Index', color = 'orange', ylower = 0, yupper = 5, figsize=(4.94, 2.8))
                  
    # Simulation Functions
    def R_T_atwavelength(self):
        '''
        Computes the Reflectivity and Transmission of the,
        in the treeview tabular, given structure at the defined center wavelength.

        Uses the T_R_Calculation function
        
        Function Parameters
        ----------
        None
        
        Returns
        -------
        None
        '''
        print("***** Compute Reflectivity/Transmission at given Wavelength *****")
        # Get data:
        wavelength = float(self.entry_wlCentre.get()) #um
        epsilon, thickness = self.Generate_Eps_Th(wavelength)
        t,r,T,R =  self.T_R_Calculation(thickness, epsilon, np.array([wavelength]), Medium_in = sqrt(epsilon[0]), Medium_out = sqrt(epsilon[-1]), angle = float(self.entry_AOI.get())) #test
        
        R_formatted = '{0:.4f}'.format(R[0])
        T_formatted = '{0:.4f}'.format(T[0])
        
        self.var_R.set(f'Reflectivity: {R_formatted}')
        self.var_T.set(f'Transmittivity: {T_formatted}')

        print(f"Reflectivity: {np.round(R,6)}, Transmittivity {np.round(T,6)}")
    
    def R_vs_wavelength(self): # Can this be faster ? /AOI
        '''
        Derives the Reflectivity of the whole structure in dependency of the incident wavelength/ Angle of Incidence
        
        Function Parameters
        ----------
        None
        
        Returns
        -------
        None
        '''
        print("***** Compute Reflectivity vs Wavelength *****")
        threading.Thread().start()
        self.Prog_RvsW = ttk.Progressbar(self.frame_Sim, style="bar.Horizontal.TProgressbar", orient = "horizontal", mode = "determinate", length = 300)
        self.Prog_RvsW.grid(row = 7, column = 0, padx = 3, columnspan = 4)
        self.label_RvsW = Label(self.frame_Sim, text = "Computing...", width = 18, bg = 'grey90').grid(row = 4, column = 2, columnspan = 1)
        
        mode = self.mode_RvsW_AOI.get()
        AOI_center = float(self.entry_AOI.get())
        wavelength_center = float(self.entry_wlCentre.get())
        if mode == 'Wavelength':
            w_min = float(self.entry_wlRangeFrom.get())
            w_max = float(self.entry_wlRangeTo.get())
            diff = w_max - w_min
            step = diff/200
            R_list = []
            w_list = []
            while w_min <= w_max:
                # Get data:
                wavelength = w_min #in um
                epsilon, thickness = self.Generate_Eps_Th(wavelength)
                
                t,r,T,R =  self.T_R_Calculation(thickness, epsilon, np.array([wavelength]), Medium_in = sqrt(epsilon[0]), Medium_out = sqrt(epsilon[-1]), angle = AOI_center)
                R_list.append(R)
                w_list.append(w_min)
                
                w_min = w_min + step
                self.Prog_RvsW["value"] = 100*(diff - (w_max - w_min))/(diff)
                self.frame_Sim.update_idletasks()
            
            self.matplotCanvas(self.frame_ShowSim, w_list, R_list, xlabel = 'Wavelength [um]', ylabel = 'Reflectivity', color = "tab:red", figsize=(4.9, 3.05), label = "R")
            self.label_RvsW = Label(self.frame_Sim, text = "Finished !", width = 18, bg = 'grey90').grid(row = 4, column = 2, columnspan = 1)
        
        if mode == u'\u03bb Vs Pairs of':
            self.lower_dbr = 0
            self.upper_dbr = 0
            self.LayerIndex = 0
            self.R_V_Wavelength_Pairs()
            lower = self.lower_dbr
            upper = self.upper_dbr
            LayerIndex = self.LayerIndex
            
            w_min = float(self.entry_wlRangeFrom.get())
            w_max = float(self.entry_wlRangeTo.get())
            diff = w_max - w_min
            step = diff/100
            R_total = []
            w_total = []
            count = 0
            color = []
            label = []
            while lower < upper:
                Pairamount = lower
                R_total.append(0)
                w_total.append(0)
                w_min = w_max - diff
                R_list = []
                w_list = []
                random.seed(lower)
                rgb_color = cmapy.color('viridis', random.randrange(0, 256, 10), rgb_order=True)
                new_label = f"LayerPairs: {lower}"
                while w_min <= w_max:
                    # Get data:
                    wavelength = w_min #in um
                    
                    epsilon, thickness = self.Generate_Eps_Th_Pairvariation(wavelength, LayerIndex, Pairamount)
                    t,r,T,R =  self.T_R_Calculation(thickness, epsilon, np.array([wavelength]), Medium_in = sqrt(epsilon[0]), Medium_out = sqrt(epsilon[-1]), angle = AOI_center)
                    R_list.append(R[0])
                    w_list.append(float(w_min))
                    
                    w_min = w_min + step
                    self.Prog_RvsW["value"] = 100*(diff - (w_max - w_min))/(diff)
                    self.frame_Sim.update_idletasks()
                R_total[count] = np.array(R_list)
                w_total[count] = np.array(w_list)
                color.append(np.array(rgb_color)/255)
                label.append(new_label)
                count = count + 1

                self.matplotCanvas(self.frame_ShowSim, w_total, R_total, xlabel = 'Wavelength [um]', ylabel = 'Reflectivity', figsize=(4.8, 3.05), label = label, color=color)
                lower = lower + 2
                
            self.label_RvsW = Label(self.frame_Sim, text = "Finished !", width = 18, bg = 'grey90').grid(row = 4, column = 2, columnspan = 1)
            
            print("Not implemented yet.")
        
        if mode == "Angle of Incidence":
            A_min = float(self.entry_AOIRangeFrom.get())
            A_max = float(self.entry_AOIRangeTo.get())
            diff = A_max - A_min
            step = diff/200
            R_list = []
            A_list = []
            while A_min <= A_max:
                # Get data:
                AOI = A_min #in um
                epsilon, thickness = self.Generate_Eps_Th(wavelength_center)
                t,r,T,R =  self.T_R_Calculation(thickness, epsilon, np.array([wavelength_center]), Medium_in = sqrt(epsilon[0]), Medium_out = sqrt(epsilon[-1]), angle = AOI)
                R_list.append(R)
                A_list.append(A_min)
                
                A_min = A_min + step
                self.Prog_RvsW["value"] = 100*(diff - (A_max - A_min))/(diff)
                self.frame_Sim.update_idletasks()
            
            self.matplotCanvas(self.frame_ShowSim, A_list, R_list, xlabel = 'AOI [deg°]', ylabel = 'Reflectivity', color = "tab:red", figsize=(4.9, 3.05), label = "R")
            self.label_RvsW = Label(self.frame_Sim, text = "Finished !", width = 18, bg = 'grey90').grid(row = 4, column = 2, columnspan = 1)
            
    def E_field_distribution(self): # ADD X,Y LABEL
        '''
        Compute the El. Field Distribution for in 'Geometry' given Materials
        Uses the Entered Center Wavelength to calculate the stack

        Function Parameters
        ----------
        None
        
        Returns
        -------
        None
        '''
        print("***** Compute E Field Distribution *****")
        # Init Progressbar
        self.Prog_E = ttk.Progressbar(self.frame_Sim, style="bar.Horizontal.TProgressbar", orient = "horizontal", mode = "determinate", length = 300)
        self.Prog_E.grid(row = 7, column = 0, padx = 3, columnspan = 4)
        
        # Get data:
        w_centre = float(self.entry_wlCentre.get())
        wavelength = w_centre #in um
        epsilon, thickness = self.Generate_Eps_Th(wavelength)

        # Derive Field
        E_Field, x, index = self.E_Field_Calculation(thickness, epsilon, w_centre, 5000)

 
        # Animation of Field:
        if self.var_ani.get() == 1:
            
            #threading.Thread(target = self.E_Field_Animation, args = (x, E_Field, index)).start() 
            ani = self.E_Field_Animation(x, E_Field, index, 200, 10)
            if is_on == True:
                E_Field = abs(E_Field)
            
        # Static view:
        elif self.var_ani.get() == 0:
            # Phase of E_Field is adjusted to show maximum amplitude
            i_max = 0
            E_old = E_Field.max()
            for i in range(91):
                E_new = E_Field*np.exp(-1.0j*np.pi*i/90)
                if E_new.max() > E_old:
                    i_max = i
                    E_old = E_new.max()
            # Absolute Field or norm. Field:
            if is_on == True:
                E_Field = np.real(E_Field*np.exp(-1.0j*np.pi*i_max/90))/abs(E_Field).max()*index.real.max()
                E_Field = abs(E_Field)
            else:
                E_Field = np.real(E_Field*np.exp(-1.0j*np.pi*i_max/90))/abs(E_Field).max()*index.real.max()
            self.matplotCanvas(self.frame_ShowSim, [x, x], [E_Field, index.real], color = ['tab:red', 'orange'], label = ["E Field", "Ref. Index"], figsize=(4.9, 3.05))
    
    def RvsParameter(self):
        '''
        Derives the Reflectivity (or the Electric Field Maximum) of the whole structure (in a desired medium)
        in dependency of the Thickness/(No. of layer-pairs) of a certain layer(-stack)
        
        Function Parameters
        ----------
        None
        
        Returns
        -------
        None
        '''
        print("***** Compute Value vs Parameter *****")
        
        # Initialising Progressbar
        self.Prog_RvsP = ttk.Progressbar(self.frame_Sim, style="bar.Horizontal.TProgressbar", orient = "horizontal", mode = "determinate", length = 300)
        self.Prog_RvsP.grid(row = 7, column = 0, padx = 3, columnspan = 4)
        counter = 0
        # Get data from GUI:
        main_mode = self.mode_Eval.get()
        sec_mode = self.mode_Para.get()
        wavelength = float(self.entry_wlCentre.get()) # this is in um
        Chosen_Medium = self.var_Mat_para.get()

        # Generate Stacks of the starting geometry
        descr, r_index_list, n_list, d_list, Pairs = self.Get_GeometryData(wavelength * 1000) # Wavelength in nm

        # Range for Parameter Scan
        lower = float(self.ParamRange_lower)
        upper = float(self.ParamRange_upper)
        step  = float(self.ParamRange_Step)
        if main_mode == "n+ik": # Adjust range for mode:n+ik
            # This depends on the wavelength range of the chosen material
            for i in range(len(descr)):
                if descr[i] == Chosen_Medium:
                    MediaIndex = i
                    counter = counter + 1
            stop = False
            w_min = 0
            while stop == False:
                print("Estimating available lower wavelength range ...", end = "\r")
                try:
                    sys.stdout = open(os.devnull, 'w') #disable print 
                    self.materials(r_index_list[i], w_min)
                    sys.stdout = sys.__stdout__ #enable print
                    stop = True
                except:
                    w_min = w_min + 5
            stop = False
            w_max = 2000
            while stop == False:
                print("Estimating available upper wavelength range ...", end = "\r")
                try:
                    sys.stdout = open(os.devnull, 'w') #disable print
                    self.materials(r_index_list[i], w_max)
                    sys.stdout = sys.__stdout__ #enable print
                    stop = True
                except:
                    w_max = w_max - 5
            print("\n")     
            lower = w_min
            upper = w_max
        
        print(f"Scanning from {lower} to {upper} in steps of {step}.")
        current = lower
        
       
        R_list = []
        E_list = []
        L_list = []
        wavelength = np.array([wavelength])
        
        
        # User has to input an Medium where the E_Field has to be analysed
        if main_mode == "E_Field":
            try:
                print("Deriving Electric Field Maximum in '", self.Analysed_Medium, "'")
                Analysed_Medium = self.Analysed_Medium
            except:
                print("No Medium for analysis has been selected.")

        # Adjust xlabel for later plotting, Adjust scan parameters and get Index of chosen media
        if sec_mode == "Pairs":
            lower = int(self.ParamRange_lower)
            upper = int(self.ParamRange_upper)
            step  = int(self.ParamRange_Step)
            for i in range(len(descr)):
                if descr[i] == Chosen_Medium:
                    MediaIndex = i
                    counter = counter + 1
                if main_mode == "E_Field":
                    if descr[i] == Analysed_Medium: AnalysedIndex = i 
            xlabel = f"Pairs of {descr[MediaIndex]}-{descr[MediaIndex+1]} Stack"                 
        if sec_mode == "Thickness":
            for i in range(len(descr)):
                if descr[i] == Chosen_Medium:
                    MediaIndex = i
                    counter = counter + 1
                if main_mode == "E_Field":
                    if descr[i] == Analysed_Medium: AnalysedIndex = i
            xlabel = f"Length of {Chosen_Medium} [um]"        
        if sec_mode == "Wavelength":
            xlabel = f"Wavelength [nm]"
        
        # Adjust ylabel for later plotting
        if main_mode == "Reflectivity": 
            ylabel = "Reflectivity"           
        if main_mode == "E_Field":  
            ylabel = f"norm. Electric Field in {Analysed_Medium}"
            n_media = float(n_list[AnalysedIndex].real)
            print("Refractive Index of analysed Medium:", n_media) 
        if main_mode == "n+ik":
            ylabel = f"Effective refractive index of {r_index_list[MediaIndex]}"
            r_list = []
            w_list = []
            
        # Stop Computation if Layer is not correctly assigned 
        assert counter != 0, "WARNING: Layer name not found in given geometry."      
        assert counter == 1, "WARNING: Layer name is not unique."

        while current <= upper: #Iterate over the Parameter range
            if main_mode == "n+ik":
                r_index = self.materials(r_index_list[MediaIndex],current)
                r_list.append(r_index)
                w_list.append(current)
                self.Prog_RvsP["value"] = 100*(current-lower)/(upper-lower)
                current = current + step*5
                self.frame_Sim.update_idletasks()
                continue
            # For each Parameter Value create a Layer-Stack:
            k = 0
            epsilon = []
            thickness = []
            if sec_mode == 'Thickness':
                d_list[MediaIndex] = current
            if sec_mode == 'Pairs':
                Pairs[MediaIndex] = int(current)
            while k < (len(Pairs)): #Iterate for each Parameter Value over Geometry List
                if Pairs[k] != 0:
                    eps, thick = self.Generate_DBR_Stack(n_list[k], n_list[k+1], d_list[k], d_list[k+1], Pairs[k])
                    epsilon = np.concatenate((epsilon, eps))
                    thickness = np.concatenate((thickness, thick))
                    k = k + 1
                else:
                    epsilon = np.concatenate((epsilon, [n_list[k]**2]))
                    thickness = np.concatenate((thickness, [d_list[k]]))
                k = k + 1
            
            # With the Stack derive the Reflectivity/E-Field of whole structure/in medium
            if main_mode == 'Reflectivity':
                # Deribe the Reflectivity of the whole structure
                t,r,T,R =  self.T_R_Calculation(thickness, epsilon, wavelength, sqrt(epsilon[0]), sqrt(epsilon[-1]))
                L_list.append(current)
                R_list.append(R)
                          
            if main_mode == 'E_Field': 
                # Derive the maximum el. Field at chosen Medium
                E_Field, x, index = self.E_Field_Calculation(thickness, epsilon, wavelength, 5000, Progressbar = False)
                
                # Phase of E_Field is adjusted to show maximum amplitude
                E = np.real(abs(E_Field))/abs(E_Field).max()*index.real.max()
                
                # Use Media Index, find thickness before this medium and of this medium
                d_below = 0
                for i in range(len(d_list)):
                    if i < AnalysedIndex:
                        if Pairs[i] != 0:   d_below += d_list[i]*Pairs[i]
                        else: d_below += d_list[i]
                d_total = d_below + d_list[AnalysedIndex]
                
                # Generate a list with all the E_Field values in this medium
                E_in_Med = []
                for i in range(len(x)):
                    if x[i] >= d_below and x[i] <= d_total:
                        E_in_Med.append(E[i])
                
                # There might be a standing wave pattern in Media, make sure to be on anti-node:
                E_list.append(max(E_in_Med))
                L_list.append(current)

            self.Prog_RvsP["value"] = 100*(current-lower)/(upper-lower)
            current = current + step
            self.frame_Sim.update_idletasks()
         
        if main_mode == 'E_Field':
            print("\n***** Computation Complete *****")
            self.matplotCanvas(self.frame_ShowSim, L_list, E_list, xlabel = xlabel, ylabel = ylabel, figsize = (4.8, 3))
            print("El Field Maximum of Medium'", Analysed_Medium, "' at Parameter Value '", L_list[E_list.index(max(E_list))], "' of Medium", descr[MediaIndex] )
            print("El Field Minimum of Medium'", Analysed_Medium, "' at Parameter Value '", L_list[E_list.index(min(E_list))], "' of Medium", descr[MediaIndex] )
        
        if main_mode == 'Reflectivity':
            print("\n***** Computation Complete *****")
            self.matplotCanvas(self.frame_ShowSim, L_list, R_list, xlabel = xlabel, ylabel = ylabel, figsize = (4.9, 3))
            print("Reflection Maximum at: ", L_list[R_list.index(max(R_list))])
            print("Reflection Minimum at: ", L_list[R_list.index(min(R_list))])

        if main_mode == "n+ik":
            print("\n***** Computation Complete *****")
            self.matplotCanvas(self.frame_ShowSim, [w_list, w_list], [np.array(r_list).real, np.array(r_list).imag], color = ["red", "blue"], label = ["real", "imaginary"], xlabel = xlabel, ylabel = ylabel, figsize = (4.9, 3))

    
    # Helper Functions:
    def window(self, width, height, xoffset = 0, yoffset = 0, title = ''):
        '''
        Function that creates a Toplevel widget of desired dimensions at 
        specified position

        Function Parameters
        ---
        width  : int, width of the toplevel window
        height : int, height of the toplevel window
        xoffset: int, horizontal offset from parent position
        yoffset: int, vertical offset from parent position
        title  : str, title of the toplevel window
        Returns
        ---
        win : class, Toplevel widget with the parent MASTER
        '''
        # Set up window and position it
        x = root.winfo_x()
        y = root.winfo_y()
        win = Toplevel()
        win.geometry("%dx%d+%d+%d" % (width, height, x + xoffset, y + yoffset))
        win.title(title)
        win.attributes("-toolwindow", True)
        return win
    
    def R_V_Wavelength_Pairs(self):
        '''
        Allows user to chose a Layer for Layer Pair variation and the range of variation
        
        Function Parameters
        ----------
        None
        
        Returns
        -------
        None, But Sets:
        LayerIndex: int, Index of Layer getting varied
        From      : int, Starting point of Layer Pair variation
        To        : int, End point of Layer Pair variaton
        '''
        # Set up window and position it
        win = self.window(380, 60, 165, 470)
        
        # Create Combobox of Layers
        wavel = float(self.entry_wlCentre.get())*1000
        desc_list, r_index_list, n_list, t_list, is_stack  = self.Get_GeometryData(wavel)
        desc_dbr = []
        i = 0
        while i < (len(desc_list)):
            if is_stack[i] != 0:
                desc_dbr.append(desc_list[i])
                i = i + 1
            i = i + 1
        self.material_list_dbr = desc_dbr
        
        col0Lbl = Label(win, text = "DBR Stack: ", width = 12)
        col0Lbl.grid(row = 0, column = 0, pady = 3, padx = 3)
        var_Mat = StringVar()
        mode_Mat  = ttk.Combobox(win, textvariable= var_Mat, values= self.material_list_dbr, width = 12, state="readonly")
        mode_Mat.grid(row = 1, column = 0, pady = 5, padx = 5, columnspan= 1)
        mode_Mat.current(0)
        
        col1Lbl = Label(win, text = "From: ", width = 8)
        col1Ent = Entry(win, highlightbackground="grey", highlightthickness= 1, width = 8)
        col1Ent.insert(END, 1)
        col1Lbl.grid(row = 0, column = 1, pady = 3, padx = 3)
        col1Ent.grid(row = 1, column = 1, pady = 3, padx = 3)

        col2Lbl = Label(win, text = "To: ")
        col2Ent = Entry(win, width = 8, highlightbackground="grey", highlightthickness= 1)
        col2Ent.insert(END, 7)
        col2Ent.grid(row = 1, column = 2, pady = 3, padx = 3)
        col2Lbl.grid(row = 0, column = 2, pady = 3, padx = 3)
        
        def UpdateThenDestroy():
                LayerDescr = mode_Mat.get()
                LayerIndex = 99
                for i in range(len(desc_list)):
                    if desc_list[i] == LayerDescr:
                        LayerIndex = i
                From = int(col1Ent.get())
                To = int(col2Ent.get())
                self.LayerIndex = LayerIndex 
                self.lower_dbr = From
                self.upper_dbr = To
                win.destroy()
                
        okButt = Button(win, text = "Apply")
        okButt.bind("<Button-1>", lambda e: UpdateThenDestroy())
        okButt.grid(row = 1, column = 3, pady = 3, padx = 5)

        canButt = Button(win, text = "Cancel")
        canButt.bind("<Button-1>", lambda c: win.destroy())
        canButt.grid(row = 1, column = 4, pady = 3, padx = 5)

        win.wait_window()

    def EorN_selected(self, index, value, op):
        '''
        Part of Compute RvsParameter:
        If 'E_Field' mode is selected the user can select a Layer where the El. Field
        should be calculated.

        Function Parameters
        ---
        index: callback return parameters
        value: Not sure what they do
        op   : Should be changed to "trace_add" anyways

        Returns
        ---
        None
        '''
        mode = self.mode_Eval.get()
        if mode == "E_Field":
            self.mode_Para.config(values = ['Thickness', 'Pairs'])
            self.mode_Para.current(0)
            # Set up window and position it
            win = self.window(230, 30, 165, 535, "Layer where E Field is computed:")

            # Create Combobox of Layers
            wavel = float(self.entry_wlCentre.get())*1000
            desc_list, r_index_list, n_list, t_list, is_stack  = self.Get_GeometryData(wavel)
            material_list = desc_list
            var_Mat = StringVar()
            mode_Mat  = ttk.Combobox(win, textvariable= var_Mat, values= material_list, width = 15, state="readonly")
            mode_Mat.grid(row = 1, column = 0, pady = 5, padx = 5, columnspan= 1)
            mode_Mat.current(0)

            def UpdateThenDestroy():
                self.Analysed_Medium = var_Mat.get()
                win.destroy()

            okButt = Button(win, text = "Apply")
            okButt.bind("<Button-1>", lambda e: UpdateThenDestroy())
            okButt.grid(row = 1, column = 1, pady = 3, padx = 5)

            canButt = Button(win, text = "Cancel")
            canButt.bind("<Button-1>", lambda c: win.destroy())
            canButt.grid(row = 1, column = 2, pady = 3, padx = 5)

        if mode == "n+ik":
            self.mode_Para.config(values = "Wavelength")
            self.mode_Para.current(0)
            
        else:
            self.mode_Para.config(values = ['Thickness', 'Pairs'])
            self.mode_Para.current(0)
    
    def Generate_Eps_Th(self, wavelength):
        '''
        Creates the 1D-Arrays of all Epsilons / Thicknesses of the Defined Geometry,
        using the Get_GeometryData and Generate_DBR_Stack function.

        Function Parameters
        ---
        wavelength: int or float, wavelength in mircometer, at which the parameters are derived

        Returns
        ---
        epsilon  : 1D-Array (complex), Complete permittivity array of the geometry
        thickness: 1D-Array (float)  , Complete thickness array of the geometry
        '''
        desc_list, r_index_list, n_list, d_list, Pairs = self.Get_GeometryData(wavelength * 1000) # Wavelength in nm
        k = 0
        epsilon = []
        thickness = []
        while k < (len(Pairs)):
            if Pairs[k] != 0:
                eps, thick = self.Generate_DBR_Stack(n_list[k], n_list[k+1], d_list[k], d_list[k+1], Pairs[k])
                epsilon = np.concatenate((epsilon, eps))
                thickness = np.concatenate((thickness, thick))
                k = k + 1
            else:
                n_r = n_list[k].real
                n_i = n_list[k].imag
                eps_r = n_r**2 - n_i**2
                eps_i = 2*n_r*n_i

                eps = complex(eps_r, eps_i)
                epsilon = np.concatenate((epsilon, [eps]))
                thickness = np.concatenate((thickness, [d_list[k]]))
            k = k + 1
        
        return epsilon, thickness
    
    def Generate_Eps_Th_Pairvariation(self, wavelength, Layerindex, Pairamount):
        '''
        Similar to Generate_Eps_Th, but allowing to set the amount of Pairs for a given Layerindex. Might be 
        integrated in this function later...

        Creates the 1D-Arrays of all Epsilons / Thicknesses of the Defined Geometry,
        using the Get_GeometryData and Generate_DBR_Stack function.

        Function Parameters
        ---
        wavelength: int or float, wavelength in mircometer, at which the parameters are derived
        Layerindex: int         , Index of Layer where the Pairamount is changed
        Pairamount: int         , New Pairamount of Indexed Layer

        Returns
        ---
        epsilon  : 1D-Array (complex), Complete permittivity array of the geometry
        thickness: 1D-Array (float)  , Complete thickness array of the geometry
        '''
        desc_list, r_index_list, n_list, d_list, Pairs = self.Get_GeometryData(wavelength * 1000) # Wavelength in nm
        Pairs[Layerindex] = Pairamount
        k = 0
        epsilon = []
        thickness = []
        while k < (len(Pairs)):
            if Pairs[k] != 0:
                eps, thick = self.Generate_DBR_Stack(n_list[k], n_list[k+1], d_list[k], d_list[k+1], Pairs[k])
                epsilon = np.concatenate((epsilon, eps))
                thickness = np.concatenate((thickness, thick))
                k = k + 1
            else:
                n_r = n_list[k].real
                n_i = n_list[k].imag
                eps_r = n_r**2 - n_i**2
                eps_i = 2*n_r*n_i

                eps = complex(eps_r, eps_i)
                epsilon = np.concatenate((epsilon, [eps]))
                thickness = np.concatenate((thickness, [d_list[k]]))
            k = k + 1
        
        return epsilon, thickness
    
    def parameter_range(self):
        '''
        Is called by the "Set Range" Button, allows the User to change the range and stepsize of
        the "Compute ... vs ... in ... " function.

        Function Parameters
        ---
        None

        Returns
        ---
        None
        '''
        def UpdateThenDestroy():
            self.ParamRange_lower = float(col1Ent.get())
            self.ParamRange_upper = float(col2Ent.get())
            self.ParamRange_Step  = float(col3Ent.get())
            win.destroy()
        
        # Set up PopUp-Window:
        win = self.window(300, 60, 200, 535, "Insert Parameter Range")
        
        # Create 2 rows and 5 columns with label, entry, button widgets
        col1Lbl = Label(win, text = "From: ", width = 8)
        col1Ent = Entry(win, highlightbackground="grey", highlightthickness= 1, width = 8)
        col1Lbl.grid(row = 0, column = 0, pady = 3, padx = 3)
        col1Ent.grid(row = 1, column = 0, pady = 3, padx = 3)

        col2Lbl = Label(win, text = "To: ")
        col2Ent = Entry(win, width = 8, highlightbackground="grey", highlightthickness= 1)
        col2Ent.grid(row = 1, column = 1, pady = 3, padx = 3)
        col2Lbl.grid(row = 0, column = 1, pady = 3, padx = 3)
        
        col3Lbl = Label(win, text = "Step: ")
        col3Ent = Entry(win, width = 8, highlightbackground="grey", highlightthickness= 1)
        col3Ent.grid(row = 1, column = 2, pady = 3, padx = 3)
        col3Lbl.grid(row = 0, column = 2, pady = 3, padx = 3)
        
        okButt = Button(win, text = "Apply")
        okButt.bind("<Button-1>", lambda e: UpdateThenDestroy())
        okButt.grid(row = 1, column = 4, pady = 3, padx = 3)

        canButt = Button(win, text = "Cancel")
        canButt.bind("<Button-1>", lambda c: win.destroy())
        canButt.grid(row = 1, column = 5, pady = 3, padx = 3)
    
    def OnDoubleClick(self, entry): # Adjusted from: https://stackoverflow.com/questions/18562123/how-to-make-ttk-treeviews-rows-editable
        '''
        Allows Double Clicking on Treeview row and open up a Toplevel Window widget, allowing
        for editing of the content.

        Function Parameters:
        ---
        None

        Returns
        ---
        None
        '''
        # First check if a blank space was selected
        treeView = self.tree
        entryIndex = treeView.focus()
        if '' == entryIndex: return

        # Set up window and position it
        win = self.window(480, 58, 5, 90, "Change Selected Layer")
        
        # Grab the entry's values
        for child in treeView.get_children():
            if child == entryIndex:
                values = treeView.item(child)["values"]
                break
        
        # Set up the window's other attributes and geometry
        col1Lbl = Label(win, text = "Description: ", width = 12)
        col1Ent = Entry(win, highlightbackground="grey", highlightthickness= 1, width = 12)
        col1Ent.insert(0, values[0]) # Default is column 1's current value
        col1Lbl.grid(row = 0, column = 0, pady = 3, padx = 3)
        col1Ent.grid(row = 1, column = 0, pady = 3, padx = 3)

        col2Lbl = Label(win, text = "Material Type: ")
        col2Lbl.grid(row = 0, column = 1, pady = 3, padx = 3)
        
        count = 0
        current = 0
        for material in self.material_list:
            if material == values[1]:
                current = count
            count = count + 1  
        self.col2var_Mat = StringVar()
        materials = self.material_list
        self.col2mode_Mat  = ttk.Combobox(win, textvariable=self.col2var_Mat, values= materials, width = 10)
        self.col2mode_Mat.grid(row = 1, column = 1, padx = 3)
        self.col2mode_Mat.current(int(current))

        col3Lbl = Label(win, text = "Thickness[um]: ")
        col3Ent = Entry(win, width = 12, highlightbackground="grey", highlightthickness= 1)
        col3Ent.insert(0, values[2]) # Default is column 3's current value
        col3Lbl.grid(row = 0, column = 2, pady = 3, padx = 3)
        col3Ent.grid(row = 1, column = 2, pady = 3, padx = 3)
        
        col4Lbl = Label(win, text = "If Stack: Pairs: ")
        col4Ent = Entry(win, width = 12, highlightbackground="grey", highlightthickness= 1)
        col4Ent.insert(0, values[3]) # Default is column 3's current value
        col4Lbl.grid(row = 0, column = 3, pady = 3, padx = 3)
        col4Ent.grid(row = 1, column = 3, pady = 3, padx = 3)
        
        def ConfirmEntry(treeView, entry1, entry2, entry3, entry4):
            # Grab the current index in the tree
            currInd = treeView.index(treeView.focus())
            # Remove it from the tree
            def DeleteCurrentEntry(treeView):
                curr = treeView.focus()
                if '' == curr: return
                treeView.delete(curr)
            DeleteCurrentEntry(treeView)
            # Put it back in with the upated values
            treeView.insert('', currInd, values = (entry1, entry2, entry3, entry4))
            return True
        
        def UpdateThenDestroy():
            if ConfirmEntry(treeView, col1Ent.get(), self.col2mode_Mat.get(), col3Ent.get(), col4Ent.get()):
                win.destroy()
        
        okButt = Button(win, text = "Apply")
        okButt.bind("<Button-1>", lambda e: UpdateThenDestroy())
        okButt.grid(row = 1, column = 4, pady = 3, padx = 3)

        canButt = Button(win, text = "Cancel")
        canButt.bind("<Button-1>", lambda c: win.destroy())
        canButt.grid(row = 1, column = 5, pady = 3, padx = 3)
             
    def is_custom(self, index, value, op):
        '''
        If thickness of "Layer-Stack" Materials is chosen to be "Custom", two entry fields appear
        and allow for the custom input.
        Function Parameters Result from the tracing functionality

        Function Parameters
        ---
        index: callback return parameters
        value: Not sure what they do
        op   : Should be changed to "trace_add" anyways

        Returns
        ---
        None
        '''
        if self.var_stack.get() == 'Custom':
            dummyframe = Frame(self.frame0)
            dummyframe.grid(row = 4, column= 3)
            self.entry_custom = Entry(dummyframe, width = 7, highlightbackground="grey", highlightthickness= 1)
            self.entry_custom.grid(row = 0, column = 0, padx = 1)
            self.entry_custom.insert(END, 1.0)
            self.entry_custom2 = Entry(dummyframe, width = 7, highlightbackground="grey", highlightthickness= 1)
            self.entry_custom2.grid(row = 0, column = 1, padx = 1)
            self.entry_custom2.insert(END, 1.0)

        if self.var_stack.get() != 'Custom':
            self.entry_custom.destroy()
            
    def Get_GeometryData(self, wavelength):
        '''
        Helper Function to get treeview content
        
        Function Parameters
        ----------
        wavelength: Wavelength in nm at which the values are derived

        Returns
        -------
        desc_list: list of strings , List of Names of treeview Materials listed in "Description"
        type_list: list of strings , List of Types of treeview Materials listen in "Material Type"
        n_list   : list of complex , List of Refr. Indicies of treeview Materials
        d_list   : list of floats  , List of thicknesses of the treeview Materials
        Pairs    : list of integers, Amount of Layer Pairs of a material: 
                        If 0 its a single layer, else its a layer stack of alternating layers with the next material
        '''
        # Get data:
        w_centre = float(self.entry_wlCentre.get())
        type_list = []
        desc_list = []
        n_list = []
        d_list = []
        Pairs  = []
        for line in self.tree.get_children():
            line_content = ''
            for value in self.tree.item(line)['values']:
                if line_content == '':
                    line_content = line_content+str(value)
                else:
                    line_content = line_content + '\t' + str(value)
            words = line_content.split('\t')
            
            n_list.append(self.materials(words[1], wavelength))
            type_list.append(words[1])
            try:
                d_list.append(float(words[2]))
            except:
                words[2] = int(words[2].encode().replace(b"\xce\xbb / ",b"").decode())
                if words[2] == 4:
                    d_list.append((w_centre/(4*n_list[-1])).real)
                if words[2] == 2:
                    d_list.append((w_centre/(2*n_list[-1])).real)
                if words[2] == 1:
                    d_list.append((w_centre/(n_list[-1])).real)

            Pairs.append(int(words[3]))
            desc_list.append(words[0])
        return desc_list, type_list, n_list, d_list, Pairs       
    
    def Generate_DBR_Stack(self, n1, n2, d1, d2, No_Pairs):
        '''
        Generate Bragg Mirror Stack of Material 1 and Material 2
        
        Bragg Layerstack always starts with Material 1 and ends with Material 2
        
        Function Parameters
        ----------
        n1, n2 : float or complex, Refractive Index of Material 1 & 2
        d1, d2 : float, Quarter-Wave Thickness of Material 1 & 2
        No_Pairs  : Number of Pairs of the Layer-Stack

        Returns
        -------
        epsilon   : 1D-array, Vector containing the permittivities
        thickness : 1D-array, Vector containing the thicknesses
        '''
        dt = np.common_type(np.array([n1]), np.array([n2])) #Allows complex values of n
        n1_r = n1.real
        n1_i = n1.imag
        n2_r = n2.real
        n2_i = n2.imag

        # Derive Epsilon Values: abs would do the job, but ...
        eps_r_1 = n1_r**2 - n1_i**2
        eps_i_1 = 2*n1_r*n1_i
        eps_r_2 = n2_r**2 - n2_i**2
        eps_i_2 = 2*n2_r*n2_i
        
        # Create Layer Stack
        epsilon = np.zeros(2*No_Pairs, dtype = dt)
        epsilon[::2]  = complex(eps_r_1, eps_i_1)    # Make every 0,2,4th.. Entry n1 & every other n2
        epsilon[1::2] = complex(eps_r_2, eps_i_2)   # Using x[start:stop:step]
        
        thickness = np.zeros(2*No_Pairs)
        thickness[::2] = d1
        thickness[1::2] = d2
        return epsilon, thickness
    
    def TM_Calculation(self, thickness, epsilon, wavelength, kz = 0): #enter docstring kz
        '''
        Derive the Transfer Matrix of a given Stack

        Function Parameters
        ----------
        thickness : 1D-array, Vector containing the thicknesses
        epsilon   : 1D-array, Vector containing the permittivities
        wavelength: 1D-array, Incident wavelength in µm
        kz        :  complex, Transverse wave vector

        Returns
        -------
        Matrix : 2D-array,  To the Layer-Stack corresponding Transfer Matrix
        '''

        # initialize system transfer matrix to identity matrix
        Matrix = np.eye(2, dtype=np.complex128)

        # Wavevector
        k0 = 2.0*np.pi/wavelength
        kx = np.sqrt(k0**2*epsilon - kz**2, dtype=np.complex128) 
        
        # Adjust Polarisation Mode
        polarisation = self.mode_pol.get()
        if polarisation == 'TE Polarisation':   alpha = np.ones_like(epsilon)
        elif polarisation == 'TM Polarisation': alpha = 1.0/epsilon

        ##### Iteration over each Stack of the Layer-Stack #####
        for kxi, di, alphai in zip(kx, thickness, alpha):
            c = np.cos(kxi*di)
            s = np.sin(kxi*di)
            ka = kxi*alphai
            m = np.array([[    c, s/ka],
                        [-ka*s,    c]])
            # Stack-TM is added to Total TM 
            Matrix = m@Matrix

        return Matrix

    def T_R_Calculation(self, thickness, epsilon, wavelength, Medium_in, Medium_out, angle = 0):
        '''
        Computes the reflection and transmission of a stratified medium.

        Function Parameters
        ----------
        thickness     : 1D-array, Vector containing the thicknesses
        epsilon       : 1D-array, Vector containing the permittivities
        wavelength    : 1D-array, Incident wavelength in µm
        Medium_in/out :    float, Refractive indicee of Medium before/after Layer-Stack
        angle         :    float, Angle of Incidence of the first medium in degree

        Returns
        -------
        t : 1D-array,   The amplitude transmission coefficient
        r : 1D-array,   The amplitude reflection coefficient 
        T : 1D-array,   The intensity transmission coefficient
        R : 1D-array,   The intensity reflection coefficient
        '''
        # Wavevector
        k0 = 2.0*np.pi/wavelength
        kz = k0*Medium_in*np.sin(np.deg2rad(angle)) #test angle in deg.
        kx_s = sqrt(Medium_in**2 * k0**2 - kz**2, dtype=np.complex128) #test
        kx_c = sqrt(Medium_out**2 * k0**2 - kz**2, dtype=np.complex128) #test

        r = np.zeros(wavelength.shape, dtype=np.complex128)
        N = np.zeros(wavelength.shape, dtype=np.complex128)
        
        polarisation = self.mode_pol.get()
        if polarisation == 'TE Polarisation':
            alpha_in = 1
            alpha_out = 1
        elif polarisation == 'TM Polarisation':
            alpha_in = 1/Medium_in**2 # test
            alpha_out = 1/Medium_out**2 #test

        ##### Iteration over all the wavelengths in 'wavelength'#####
        for i, (wavelength_i, kzi, kx_ci, kx_si) in enumerate(zip(wavelength, kz, kx_c, kx_s)): #test
            M = self.TM_Calculation(thickness, epsilon, wavelength_i, kzi) # test
            N[i] = (alpha_in*kx_si*M[1,1] + alpha_out*kx_ci*M[0,0]
                + 1j*(M[1,0] - alpha_in*kx_si*alpha_out*kx_ci*M[0,1])) #De-Nominator of r
            r[i] = (alpha_in*kx_si*M[1,1] - alpha_out*kx_ci*M[0,0]       
                - 1j*(M[1,0] + alpha_in*kx_si*alpha_out*kx_ci*M[0,1])) #Nominator of r
        r /= N # Well known formular for reflectivity
        R = np.real(r*np.conj(r)) # The intensity reflection coefficient
        
        # The transmission coefficients
        t = alpha_in*2.0*kx_s/N
        T = np.real(alpha_out*kx_c)/np.real(alpha_in*kx_s)*np.real(t*np.conj(t)) # Transmissivity test

        return t, r, T, R
    
    def E_Field_Calculation(self, thickness, epsilon, wavelength, Precision, Progressbar = True, kz = 0):
        '''
        Calculation of the Electric Field strengh at different layers.
        
        The Field E_T is set to 1. 

        Function Parameters
        ----------
        thickness     : 1D-array, Vector containing the thicknesses
        epsilon       : 1D-array, Vector containing the permittivities
        wavelength    : 1D-array, Incident wavelength in µm
        Precision     :      int, Sampling value of the Electric Field
        Progressbar   :     bool, Toggle Progressbar of calculation On/Off
        kz            :  complex, transverse  wave vector used for AOI calculations
        
        Returns
        -------
        E_Field : 1D-array, Electric field strength at the different 'x'-positions
        x       : 1D-array, Spatial Positions at which the Field is computed
        index   : 1D-array, Spatial Distribution of refractive indicees
        '''
        # LayerIn and Out defined as the corner layers, Illumination from the input layer side
        epsilon_in = epsilon[0]
        epsilon_out = epsilon[-1]

        # extension of the vectors epsilon and thickness to take the input and output layer into account
        thickness = np.concatenate(([0], thickness, [0]))
        epsilon = np.concatenate(([epsilon_in], epsilon, [epsilon_out]))

        ##### MAIN IDEA OF THE METHOD #####
        # Calculation is done starting from the transmitted field: Layers are flipped
        epsilon = epsilon[::-1]
        thickness = thickness[::-1]
        
        # Adjust Polarisation Mode:
        polarisation = self.mode_pol.get()
        if polarisation == 'TE Polarisation':   alpha = np.ones_like(epsilon)
        elif polarisation == 'TM Polarisation': alpha = 1.0/epsilon

        # Wavenumber & Wavevector (Taking transverse components into account)
        k0 = 2.0*np.pi/wavelength
        kx = np.sqrt(epsilon*k0**2 - kz**2, dtype=np.complex128)

        # k-vector 'OUT'
        kx_o= kx[0]

        # Start calculation from transmitted field backwards..., Normalized transmitted field
        # (The field at the end is easily known, since it depends only on the transmitted wave)
        # The Minus sign comes from invertion of the structure
        alpha_out = alpha[0]
        incident_vec = np.array([[1.0], [-1.0j*alpha_out*kx_o]])

        # Necessary Variables:
        x = np.linspace(0, np.sum(thickness), Precision)
        curr_layer = 0
        pos_in_layer = 0.0
        thickness_below = 0.0
        M = np.eye(2, dtype=np.complex128)
        E_Field = np.zeros(x.shape, dtype=np.complex128)
        index = np.zeros(x.shape, dtype=epsilon.dtype)

        for i, xi in enumerate(x):
        # Current Layer Position (At first = 0)
            pos_in_layer = xi - thickness_below
        # Check if next Layer is reached: 'next layer interface'
            if pos_in_layer >= thickness[curr_layer]:
                # At last position in Layer: Derive k-Vector
                c = np.cos(kx[curr_layer]*thickness[curr_layer])
                s = np.sin(kx[curr_layer]*thickness[curr_layer])
                ka = kx[curr_layer]*alpha[curr_layer]
                m = np.array([[  c, s/ka],
                            [-ka*s,    c]])
                # update Total TM
                M = m@M
                # update Position-in-Layer, Layer No. & Thickness of passed layers
                pos_in_layer = pos_in_layer - thickness[curr_layer]
                thickness_below = thickness_below + thickness[curr_layer]
                curr_layer += 1

        # At diff. positions in Layer: Derive k-Vector (Starts with 'k' of last layer) up to next boundary
            
            # In Time/Position Oscillating Field
            c = np.cos(kx[curr_layer]*pos_in_layer) 
            s = np.sin(kx[curr_layer]*pos_in_layer)
            try:
                ka = kx[curr_layer]*alpha[curr_layer]
            except: pass
            m = np.array([[    c, s/ka],
                        [-ka*s,    c]])
            out_vector = m@M@incident_vec
            #print("M", m , "at", x.max()-xi)

            E_Field[i] = out_vector[0,0]
            try:
                index[i] = np.sqrt(epsilon[curr_layer])
            except:
                index[i] = np.sqrt(epsilon[curr_layer-1])

            if 1e-48 >= M.max().real >= 1e48 or 1e-48 >= M.max().imag >= 1e48:
                print("WARNING: MATRIX CALCULATION FAILED !!! NUMERICAL ERROR DUE TO ONE MATERIAL BEING TOO THICK.")
            #print(f"Calculating E-Field Distribution ... ({round(100*xi/np.sum(thickness),1)})%", end = '\r')
            if Progressbar == True:
                self.Prog_E["value"] = 100*(i/len(x))
                self.frame_Sim.update_idletasks()
            if Progressbar == False:
                pass
        # First Entry in 'E_Field' is the Amplitude at the end of Stack: Flip Arrays!
        E_Field = E_Field[::-1]
        index = index[::-1]
        x = np.linspace(0, np.sum(thickness), Precision)
        return E_Field, x, index
     
    def switch(self):
        '''
        Helper function to switch between absolute E-Field mode and normal E-Field mode

        Function Parameters
        ---
        None

        Returns
        ---
        None
        '''
        global is_on
        if is_on:
            self.button_sw.config(image = self.norm)
            is_on = False
        else:         
            self.button_sw.config(image = self.abs)
            is_on = True    

    def matplotCanvas(self, frame, x, y, xlabel = '', ylabel = '', label = '', color = 'black', ylower = None, yupper = None, grid = True, figsize = (5, 3)):
        '''
        Helper function that generates a plot in the defined frame of the given data.

        Function Parameters
        ---
        frame  :      widget, Master frame widget
        x      :  n-dim list, x values of the plot either int or float,
                    if a list is given, different plots can be displayed in the graph
        y      :  n-dim list, y values of the plot either int or float,
                    if a list is given, different plots can be displayed in the graph
        xlabel :         str, X-label of the graph
        ylabel :         str, Y-label of the graph
        label  :(list of)str, label of the data set; for n-data sets a list of str
                    can be given to point a label to each data set
        color  :(list of)str, color of the data set; for n-data sets a list of str 
                    can be given to point a color to each data set
        ylower :lowerY limit, Lower plot range of the graph, either int or float
        yupper :upperY limit, Upper plot range of the graph, either int or float
        grid   :        bool, toggle grid on/off
        figsize:    2D-tuple, adapts the figure size in the graph-frames

        Returns
        ---
        None
        '''
        fig = Figure(figsize=figsize, tight_layout = True)
        ax = fig.add_subplot(111)
        try:
            for i in range(len(x)):
                ax.plot(x[i], y[i], label = label[i], color = color[i])
        except:
            try:
                ax.plot(x, y, label = label, color = color)
            except: 
                ax.plot(x, y, label = label[0], color = color[0])
        if ylower != None:
            ax.set_ylim(ylower, yupper)
        ax.set_xlabel(xlabel, fontsize = 10)
        ax.set_ylabel(ylabel, fontsize = 10)
        if grid == True:
            ax.grid()
        if label != '':
            ax.legend()
        
        canvas = FigureCanvasTkAgg(fig, frame)
        canvas.get_tk_widget().grid(row = 0, column = 0, padx = 0, pady = 0)
        canvas.draw()
        dummy_frame = Frame(frame)
        NavigationToolbar2TkAgg(canvas, dummy_frame)
        dummy_frame.grid(row = 1, column = 0, pady = 0)

    def E_Field_Animation(self, x, E_Field, index, steps = 200, periods = 10):
        ''' 
        Time animation of the Electric Field in the Layer-Stack-Structure

        Function Parameters
        ----------
        E_Field  : 1D-array, Electric field strength at the different 'x'-positions
        x        : 1D-array, Spatial Positions at which the Field is computed
        index    : 1D-array, Spatial Distribution of refractive indicees
        steps    :      int, Number of Time Steps
        periods  :      int, Number of the oscillation periods.

        Returns
        -------
        ani : matplotlib.animation.FuncAnimation; The time animation of the field
        '''
        # based on https://matplotlib.org/gallery/animation/simple_anim.html

        freq = periods/(steps - 1)
        w = freq*2*np.pi
        max_E_Field = abs(E_Field).max()
        max_index = index.real.max()

        # helper function to calculate field at step n
        def field_at_step(n):
            if is_on == True:
                result = abs(np.real(E_Field*np.exp(-1.0j*w*n)))/max_E_Field*max_index
            else:
                result = np.real(E_Field*np.exp(-1.0j*w*n))/max_E_Field*max_index
            return result

        # set up initial plot
        fig = plt.figure(figsize = (4.9, 3), tight_layout = True)
        ax = fig.add_subplot(111)
        
        line_E_Field, line_eps = ax.plot(x, field_at_step(0), x, index.real)
        ax.set_xlabel('x [µm]')
        ax.set_ylabel('normalized field (real part)')
        ax.legend(['EM field', 'refr. index'], frameon=False)
        ax.set_xlim(x[[0,-1]])
        ax.set_ylim(np.array([-1.1, 1.1])*max_index)
        frame = self.frame_ShowSim
        canvas = FigureCanvasTkAgg(fig, frame)
        canvas.get_tk_widget().grid(row = 0, column = 0, padx = 0, pady = 0)
        
        dummy_frame = Frame(frame)
        NavigationToolbar2TkAgg(canvas, dummy_frame)
        dummy_frame.grid(row = 1, column = 0, pady = 0)
        # function that updates plot data during animation
        def animate(i):
            line_E_Field.set_ydata(field_at_step(i))
            return (line_E_Field,)

        # function that inits plot data for animation (clean state for blitting)
        def init():
            line_E_Field.set_ydata(x*np.nan)
            return (line_E_Field,)

        self.ani = animation.FuncAnimation(fig, animate, init_func=init, blit=True,
                                    save_count=steps, interval=100)
        canvas.draw()
        return self.ani
    
    




if __name__ == "__main__":
    
    # Additional Variables:
    is_on = True
    
    # Set GUI and start mainloop
    root = ROOT()
    root.mainloop()
    



    

