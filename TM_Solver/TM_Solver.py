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
        
    Progress until V2:
        Main Tasks:
            Is Problem?: Wave in last material osc., which changes the physics if length is changed.
            
        Possible Upgrades:
            Add Function Docstrings EVERYWHERE !!!
            Add: Pairs Option !
            #make 'get data' into a helper function
            #layerStack: Thickness can be l/4, l/8, l/2, l, custom ?
            #Improve Design
            Coloriezed Plots
            Compute R vs lamba vs layerpairs ? / R vs layerpairs
            #Add More Materials
            Ask for feedback     
            Angle of Incidence ?
            Add feedback/terminal window in programm (Nothing selected, errors, comp time, etc...)
            Improve speed of: Refl vs Wavelength; And: Dont allow button inputs while running
            if "Description" of material already exists add a number !
            Improve: OnDouble Click function !
            Compute E_MAX vs Parameter, E_MAX at Position
            iF interpol range is reached, plot until this values and update range max
        
'''
#region ***** Imports *****
from tkinter_custom_button import TkinterCustomButton
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
#endregion 


Infotext = str('''Transfer-Matrix-Solver Programm with Gui: All Distances are in [um]!
Workflow: Geometry can be Designed in the upper region, edit entries by 'Double Clicking'. Example Geometries can be loaded.
Incident and Exit Media have to be well defined
Simulation: Center Wavelength is always used for layerstack thickness if not 'Custom'
Program Version 1.0.3                                                                                      Author: Paul Steinmann''')





class ROOT(Tk):

    def __init__(self):
    # Main Window Setup
        super().__init__()
        s = ttk.Style()
        s.theme_use('clam')
        TROUGH_COLOR = 'grey55'
        BAR_COLOR = 'lime green'
        s.configure("bar.Horizontal.TProgressbar", troughcolor="grey85", bordercolor= "grey30", background= "green3", lightcolor= "lawn green", darkcolor= "green4")
        self.title("TM Solver -- Nanophotonics")
        image = PhotoImage(file = os.path.join(os.path.dirname(__file__), "TM.PNG"))
        self.iconphoto(False, image)
        self.configure(background=('grey80'))
        self.minsize(1110, 710)
        self.maxsize(1110, 710)

        self.material_list = ('Gold', 'Silver', 'Air','BK7', 'GaAs', 'AlAs', 'InAs', 'Si', 'TiO2', 'SiO2', 'Si3N4','Chrom', 'Copper', 'FusedSilica', 'MgF2', 'h-BN', 'MoSe2-1L', 'WS2-1L') # 12
        
    # Frame for 'Define Geometry'
        self.frame0 = Frame(self, highlightbackground="gray", highlightthickness= 3, bg = "grey90")
        self.frame0.place(x=0,y=0, width = 600, height = 330)
        
        self.label_framehead = Label(self.frame0, text = "Define Geometry", bg = "red3", height = 1, font = ("Times New Roman", 20), relief = RIDGE, fg = "white", width = 38)
        self.label_framehead.grid(row = 0, column = 0, columnspan= 5, pady = 2)
        
        # Row 1
        self.label_name = Label(self.frame0, text = "Name of Layer", width = 15, bg = "grey90").grid(row = 1, column = 1)
        self.label_type = Label(self.frame0, text = "Type", width = 15, bg = "grey90").grid(row = 1, column= 2)
        self.label_th = Label(self.frame0, text = "Thickness [um]", width = 15, bg = "grey90").grid(row = 1, column= 3)
        
        # Row 2
        self.button_Material = Button(self.frame0, text = "Add Material", width = 15, bg = "grey90", command = self.add_material).grid(row = 2, column = 0)
        self.entry_name = Entry(self.frame0, width = 15, highlightbackground="grey", highlightthickness= 1)
        self.entry_name.grid(row = 2, column= 1, pady = 5, padx = 1)
        self.entry_name.insert(END, "Medium1")
        self.var_Mat = StringVar()
        self.mode_Mat  = ttk.Combobox(self.frame0, textvariable=self.var_Mat, values= self.material_list, width = 10)
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
        self.mode_l1  = ttk.Combobox(self.frame0, textvariable=self.var_l1, values= self.material_list, width = 10)
        self.mode_l1.grid(row = 3, column = 2, pady = 0, columnspan= 1)
        self.mode_l1.current(8)
        self.var_stack = StringVar()
        self.mode_stack = ttk.Combobox(self.frame0, textvariable=self.var_stack, values= [u'\u03bb / 4', u'\u03bb / 2', u'\u03bb / 1', 'Custom'], width = 10)
        self.mode_stack.grid(row = 3, column = 3, pady = 0, columnspan= 1)
        self.mode_stack.current(0)
        
        self.entry_l2 = Entry(self.frame0, width = 15, highlightbackground="grey", highlightthickness= 1)
        self.entry_l2.grid(row = 4, column= 1, pady = 0, padx = 1)
        self.entry_l2.insert(END, "Layer2")
        self.var_l2 = StringVar()
        self.mode_l2  = ttk.Combobox(self.frame0, textvariable=self.var_l2, values= self.material_list, width = 10)
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
        self.label_wlCentre = Label(self.frame_Sim, text = "Center Wavelength", width = 15, bg = "grey90").grid(row = 1, column = 1)
        self.label_wlRangeFrom = Label(self.frame_Sim, text = "Range Minimum", width = 15, bg = "grey90").grid(row = 1, column = 2)
        self.label_wlRangeTo = Label(self.frame_Sim, text = "Range Maximum", width = 15, bg = "grey90").grid(row = 1, column = 3)
        # Row 2
        self.label_Wavelength = Label(self.frame_Sim, text = 'Wavelength Settings [um]', bg = "grey90").grid(row = 2, column = 0)
        self.entry_wlCentre = Entry(self.frame_Sim, width = 8, highlightbackground="grey", highlightthickness= 2)
        self.entry_wlCentre.grid(row = 2, column= 1, pady = 5, padx = 3)
        self.entry_wlCentre.insert(END, 0.780)
        self.entry_wlRangeFrom = Entry(self.frame_Sim, width = 8, highlightbackground="grey", highlightthickness= 2)
        self.entry_wlRangeFrom.grid(row = 2, column= 2, pady = 5, padx = 3)
        self.entry_wlRangeFrom.insert(END, 0.600)
        self.entry_wlRangeTo= Entry(self.frame_Sim, width = 8, highlightbackground="grey", highlightthickness= 2)
        self.entry_wlRangeTo.grid(row = 2, column= 3, pady = 5, padx = 3)
        self.entry_wlRangeTo.insert(END, 0.86)
        # Row 3
        self.button_RT = Button(self.frame_Sim, text = "Compute R/T at Center Wavelength", bd = 3, width = 40, command = self.R_T_atwavelength)
        self.button_RT.grid(row = 3, column = 0, columnspan = 2, pady = 3, padx = 5)
        self.var_R = StringVar()
        self.label_RT = Label(self.frame_Sim, textvariable= self.var_R, bg = "grey90", width = 18).grid(row = 3, column = 2, columnspan = 1)
        self.var_T = StringVar()
        self.label_RT = Label(self.frame_Sim, textvariable= self.var_T, bg = "grey90", width = 18).grid(row = 3, column = 3, columnspan = 1)
        # Row 4
        self.button_RvsW = Button(self.frame_Sim, text = "Compute Reflectivity vs Wavelength", bd = 3, width = 40, command = self.R_vs_wavelength)
        self.button_RvsW.grid(row = 4, column = 0, columnspan = 2, pady = 3, padx = 5)
        
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
        self.tickbox_ani = Checkbutton(self.frame_Sim, text = "Toggle Animation", variable=self.var_ani, onvalue=1, offvalue=0)
        self.tickbox_ani.grid(row = 5, column = 3, columnspan=1, rowspan=1)
        
        # Row 6
        self.button_RvT = Button(self.frame_Sim, text = "Compute", bd = 3, width = 20, command = self.RvsParameter)
        self.button_RvT.grid(row = 6, column = 0, columnspan = 1, pady = 3, padx = 3)
        
        self.dummyframeS = Frame(self.frame_Sim, bg = 'grey80')
        self.dummyframeS.grid(row = 6, column = 1, pady = 0, columnspan = 2, padx = 0)
        self.var_Eval= StringVar()
        self.mode_Eval  = ttk.Combobox(self.dummyframeS, textvariable=self.var_Eval, values= ['Reflectivity', 'E_Field_Max'], width = 13)
        self.mode_Eval.grid(row = 0, column = 0, pady = 0, columnspan= 1, padx = 3)
        self.mode_Eval.current(0)
        self.label_vs = Label(self.dummyframeS, text = 'vs', bg = "grey80").grid(row = 0, column = 1, columnspan = 1, padx = 0)
        self.var_Para= StringVar()
        self.mode_Para  = ttk.Combobox(self.dummyframeS, textvariable=self.var_Para, values= ['Thickness', 'Pairs'], width = 10)
        self.mode_Para.grid(row = 0, column = 2, pady = 0, columnspan= 1, padx = 3)
        self.mode_Para.current(0)
        self.button_ParaRange = Button(self.dummyframeS, text = "set Range", bd = 3, command = self.parameter_range, bg = "grey80")
        self.button_ParaRange.grid(row = 0, column = 3, padx = 3)
        self.entry_Para = Entry(self.frame_Sim, width = 15, highlightbackground="grey", highlightthickness= 2)
        self.entry_Para.grid(row = 6, column = 3, pady = 5, padx = 0)
        self.entry_Para.insert(END, 'Medium1')
        if self.mode_Para.get() == 'Pairs':
            self.ParamRange_upper = 20
            self.ParamRange_lower = 0
            self.ParamRange_Step  = 1
        else:
            self.ParamRange_lower = 0
            self.ParamRange_upper = 1
            self.ParamRange_Step  = 0.0005
        
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
        Returns the Effective Refractive Index for a given Material, depending on the wavelength
        
        Function Parameters
        ----------
        Material :      str, String descr. the Material
            Materials: 'Chrom', 'Copper', Gold', 'Silver', 'Air','BK7', 'FusedSilica', 'GaAs', 'AlAs', 'InAs', 'Si', 'TiO2', 'SiO2', 'Si3N4', 'MgF2', 'h-BN', 'MoSe2-1L', 'WS2-1L'
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
            w = (wavelength/1000)**2 # For sellmeier equation
            n = 1 + 0.4875511*w/(w-0.0433841**2) + 0.39875031*w/(w-0.09461442**2) + 2.3120353*w/(w-23.793604**2)
            n = sqrt(n)
            k = 0 # Good Approximation
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
            n0 = 1.489
            n1 = 3.9
            n2 = 36.7
            C0 = 1e2
            C1 = 1e7
            n = n0 + C0*n1/wavelength**2 + C1*n2/wavelength**4
            k = 0 # Good Approximation above 400nm
            n = complex(n , k)
            return n
        def n_Si3N4(wavelength):
            n0 = 1.997
            n1 = 148.1
            n2 = 273.2
            C0 = 1e2
            C1 = 1e7
            n = n0 + C0*n1/wavelength**2 + C1*n2/wavelength**4
            k = 0 # Good Approximation above 400nm
            n = complex(n , k)
            return n
        def n_Chrom(wavelength):
            # Wavelength data in microns
            n = interp1d(dataChromWl, dataChromn)
            n = n(wavelength/1000)
            k = interp1d(dataChromiWl, dataChromin)
            k = k(wavelength/1000)
            n = complex(n , k)
            return n
        def n_Copper(wavelength):
            # Wavelength data in microns
            n = interp1d(dataCopperWl, dataCoppern)
            n = n(wavelength/1000)
            k = interp1d(dataCopperiWl, dataCopperin)
            k = k(wavelength/1000)
            n = complex(n , k)
            return n
        def n_Gold(wavelength):
            # Wavelength data in microns
            n = interp1d(dataGoldWl, dataGoldn)
            n = n(wavelength/1000)
            k = interp1d(dataGoldiWl, dataGoldin)
            k = k(wavelength/1000)
            n = complex(n , k)
            return n
        def n_Silver(wavelength):
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
        else:
            print("Error while recieving material for layers")
        # Return Indicees for Materials
        return r_index

    def add_material(self):
        name = self.entry_name.get()    #str
        type = self.mode_Mat.get()     #str
        thickness = float(self.entry_th.get()) #float
        print(f"Layer Name: '{name}', Type: '{type}', thickness: '{thickness} [um]'")
        self.tree.insert('', 'end', text='', values=(name, type, thickness, 0))
        
    def add_layerstack(self):
        nameL1 = self.entry_l1.get()
        nameL2 = self.entry_l2.get()
        typeL1 = self.mode_l1.get() 
        typeL2 = self.mode_l2.get()
        Pairs = int(self.entry_Npairs.get())
        thickness = self.mode_stack.get()
        if thickness == 'Custom':
            thickness = self.entry_custom.get()
        
        self.tree.insert('', 'end', text='', values=(nameL1, typeL1, thickness, Pairs))
        self.tree.insert('', 'end', text='', values=(nameL2, typeL2, thickness, Pairs))
    
    def save_geometry(self):
        '''
        Similar to the Get_GeometryData function, reads treeview content and writes it to a desired data file.
        Entries are separated by tab and each row starts in a new line.
        '''
        tf = fd.asksaveasfile(mode='w', title ="Save file", defaultextension=".txt")
        data = ''
        
        # Get data:
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
                words[2] = int(words[2].encode().replace(b"\xce\xbb / ",b"").decode())
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
    
    def remove_selection(self):
        selected = self.tree.selection()[0]
        self.tree.delete(selected)
    
    def remove_all(self):
        self.tree.delete(*self.tree.get_children())
    
    def move_up(self):
        leaves = self.tree.selection() #Get all leaves of the tree
        for i in reversed(leaves):
            self.tree.move(i, self.tree.parent(i), self.tree.index(i)-1)
    
    def move_down(self):
        leaves = self.tree.selection() #Get all leaves of the tree
        for i in reversed(leaves):
            self.tree.move(i, self.tree.parent(i), self.tree.index(i)+1)
    
    def show_geometry(self):
        '''
        Displayes the Desiged Geometry in a Plot: Ref.index vs thickness
        Might need improvement since plots are weird if 1 material is long
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
        print("Geometry:")
        print("Stack Length:", [round(x,5) for x in x_data])
        print("Stack Index :", [round(y.real,5)+round(y.imag, 5)*1j for y in y_data])
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
        self.matplotCanvas(frame = self.frame_ShowGeo, x = x_list, y = y_list, xlabel= 'length [um]',
                           ylabel= 'Eff. Refractive Index', label = '', color = 'orange', ylower = 0, yupper = 5, figsize=(4.94, 2.8))
                  
    # Simulation Functions
    def R_T_atwavelength(self):
        '''
        '''
        # Get data:
        wavelength = float(self.entry_wlCentre.get()) #um
        epsilon, thickness = self.Generate_Eps_Th(wavelength)

        t,r,T,R =  self.T_R_Calculation(thickness, epsilon, np.array([wavelength]), Medium_in = 1, Medium_out = 1)
        R_formatted = '{0:.4f}'.format(R[0])
        T_formatted = '{0:.4f}'.format(T[0])
        
        self.var_R.set(f'Reflectivity: {R_formatted}')
        self.var_T.set(f'Transmittivity: {T_formatted}')
    
    def R_vs_wavelength(self): # Can this be faster ? 
        threading.Thread().start()
        self.Prog_RvsW = ttk.Progressbar(self.frame_Sim, style="bar.Horizontal.TProgressbar", orient = "horizontal", mode = "determinate", length = 300)
        self.Prog_RvsW.grid(row = 7, column = 0, padx = 3, columnspan = 4)
        self.label_RvsW = Label(self.frame_Sim, text = "Computing...", width = 18, bg = 'grey90').grid(row = 4, column = 2, columnspan = 1)
        
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
            
            t,r,T,R =  self.T_R_Calculation(thickness, epsilon, np.array([wavelength]), Medium_in = 1, Medium_out = 1)
            R_list.append(R)
            w_list.append(w_min)
            
            
            w_min = w_min + step
            self.Prog_RvsW["value"] = 100*(diff - (w_max - w_min))/(diff)
            self.frame_Sim.update_idletasks()
        
        self.matplotCanvas(self.frame_ShowSim, w_list, R_list, xlabel = 'Wavelength [um]', ylabel = 'Reflectivity', color = "tab:red", figsize=(4.9, 3.05))
        self.label_RvsW = Label(self.frame_Sim, text = "Finished !", width = 18, bg = 'grey90').grid(row = 4, column = 2, columnspan = 1)
        
    def E_field_distribution(self):
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
        # Init Progressbar
        self.Prog_E = ttk.Progressbar(self.frame_Sim, style="bar.Horizontal.TProgressbar", orient = "horizontal", mode = "determinate", length = 300)
        self.Prog_E.grid(row = 7, column = 0, padx = 3, columnspan = 4)
        
        # Get data:
        w_centre = float(self.entry_wlCentre.get())
        wavelength = w_centre #in um
        epsilon, thickness = self.Generate_Eps_Th(wavelength)

        # Derive Field
        E_Field, x, index = self.E_Field_Calculation(thickness, epsilon, w_centre, 5000)

        # Absolute Field or norm. Field:
        if is_on == True:
            E_Field = abs(E_Field)
        
        # Animation of Field or Static View:
        if self.var_ani.get() == 1:
            #threading.Thread(target = self.E_Field_Animation, args = (x, E_Field, index)).start() 
            
            ani = self.E_Field_Animation(x, E_Field, index, 200, 10)

        elif self.var_ani.get() == 0:
            i_max = 0
            E_old = E_Field.max()
            for i in range(91):
                E_new = E_Field*np.exp(-1.0j*np.pi*i/90)
                if E_new.max() > E_old:
                    i_max = i
                    E_old = E_new.max()
            print(i_max)
            E_Field = np.real(E_Field*np.exp(-1.0j*np.pi*i_max/90))/abs(E_Field).max()*index.real.max()
            self.matplotCanvas(self.frame_ShowSim, [x, x], [E_Field, index.real], color = ['tab:red', 'orange'])
    
    def RvsParameter(self):
        '''
        '''
        self.Prog_RvsP = ttk.Progressbar(self.frame_Sim, style="bar.Horizontal.TProgressbar", orient = "horizontal", mode = "determinate", length = 300)
        self.Prog_RvsP.grid(row = 7, column = 0, padx = 3, columnspan = 4)
        
        # Get data:
        main_mode = self.mode_Eval.get()
        sec_mode = self.mode_Para.get()
        
        wavelength = float(self.entry_wlCentre.get()) #um
        Chosen_Medium = self.entry_Para.get()
        
        lower = self.ParamRange_lower
        upper = self.ParamRange_upper
        step  = self.ParamRange_Step
        
        # Generate Stacks
        descr, r_index_list, n_list, d_list, Pairs = self.Get_GeometryData(wavelength * 1000) # Wavelength in nm
        R_list = []
        T_list = []
        E_list = []
        L_list = []
        wavelength = np.array([wavelength])
        counter = 0
        
        if main_mode == "Reflectivity":
            if sec_mode == "Pairs":
                lower = int(self.ParamRange_lower)
                upper = int(self.ParamRange_upper)
                step  = int(self.ParamRange_Step)
                for i in range(len(descr)):
                    if counter > 1:
                        print("WARNING: Layer name is not unique.")
                    if descr[i] == Chosen_Medium:
                        MediaIndex = i
                        counter = counter + 1
                        current = lower
                        
            if sec_mode == "Thickness":
                for i in range(len(descr)):
                    if counter > 1:
                        print("WARNING: Layer name is not unique.")
                    if descr[i] == Chosen_Medium:
                        MediaIndex = i
                        counter = counter + 1
                        current = lower
        if main_mode == "E_Field_max":
            if sec_mode == "Pairs":
                lower = int(self.ParamRange_lower)
                upper = int(self.ParamRange_upper)
                step  = int(self.ParamRange_Step)
                for i in range(len(descr)):
                    if counter > 1:
                        print("WARNING: Layer name is not unique.")
                    if descr[i] == Chosen_Medium:
                        MediaIndex = i
                        counter = counter + 1
                        current = lower
                        
            if sec_mode == "Thickness":
                for i in range(len(descr)):
                    if counter > 1:
                        print("WARNING: Layer name is not unique.")
                    if descr[i] == Chosen_Medium:
                        MediaIndex = i
                        counter = counter + 1
                        current = lower
        
        
                
                
        while current <= upper: #Iterate over the Parameter range
            k = 0
            epsilon = []
            thickness = []
            d_list[MediaIndex] = current
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
                
            t,r,T,R =  self.T_R_Calculation(thickness, epsilon, wavelength, 1, 1)
            #E_Field, x, index = self.E_Field_Calculation(thickness, epsilon, wavelength, 5000)
            #E = E_Field.real/abs(E_Field.real).max()*index.real.max()
            R_list.append(R)
            
            ind = []
            ind2 = []
            #for i in range(len(index)):
            #    if round(index.real[i], 3) == round(1., 3):
            #        ind.append(abs(E[i]))
            #    if round(index.real[i], 2) == round(1.45, 2):
            #        ind2.append(abs(E[i]))
            #E_list.append(max(ind))
            #T_list.append(max(ind2))
            L_list.append(current)
            current = current + step
            self.Prog_RvsP["value"] = 100*(current-lower)/(upper-lower)
            self.frame_Sim.update_idletasks()
            

        print("\n***** Computation Complete *****")
        #self.matplotCanvas(self.frame_ShowSim, [L_list, L_list], [T_list, E_list], xlabel = f"Length of {Chosen_Medium} [um]", ylabel = "Reflectivity")
        self.matplotCanvas(self.frame_ShowSim, L_list, R_list, xlabel = f"Length of {Chosen_Medium} [um]", ylabel = "Reflectivity")

        print("Reflection Minimum at: ", L_list[R_list.index(min(R_list))])
        return min(R_list) 
    
    # Helper Functions:
    def Generate_Eps_Th(self, wavelength):
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
                epsilon = np.concatenate((epsilon, [n_list[k]**2]))
                thickness = np.concatenate((thickness, [d_list[k]]))
            k = k + 1
        return epsilon, thickness
    
    def parameter_range(self):
        def UpdateThenDestroy():
            self.ParamRange_lower = float(col1Ent.get())
            self.ParamRange_upper = float(col2Ent.get())
            self.ParamRange_Step  = float(col3Ent.get())
            win.destroy()
        
        # Set up PopUp-Window:
        win = Toplevel()
        win.title("Insert Parameter Range")
        win.attributes("-toolwindow", True)
        
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
    
    def OnDoubleClick(self, event): # Adjusted from: https://stackoverflow.com/questions/18562123/how-to-make-ttk-treeviews-rows-editable
        treeView = self.tree
        # First check if a blank space was selected
        entryIndex = treeView.focus()
        if '' == entryIndex: return

        # Set up window
        win = Toplevel()
        win.title("Change Selected Layer")
        win.attributes("-toolwindow", True)

        ####
        # Set up the window's other attributes and geometry
        ####

        # Grab the entry's values
        for child in treeView.get_children():
            if child == entryIndex:
                values = treeView.item(child)["values"]
                break

        col1Lbl = Label(win, text = "Description: ", width = 15)
        col1Ent = Entry(win, highlightbackground="grey", highlightthickness= 1)
        col1Ent.insert(0, values[0]) # Default is column 1's current value
        col1Lbl.grid(row = 0, column = 0, pady = 3, padx = 3)
        col1Ent.grid(row = 1, column = 0, pady = 3, padx = 3)

        col2Lbl = Label(win, text = "Material Type: ") # Add current correctly
        col2Ent = Entry(win, width = 15, highlightbackground="grey", highlightthickness= 1)
        #col2var_Mat = StringVar()
        #col2mode_Mat  = ttk.Combobox(win, textvariable=col2var_Mat, values= self.material_list, width = 10)
        #col2mode_Mat.current(0)
        col2Ent.insert(0, values[1])
        col2Ent.grid(row = 1, column = 1, pady = 3, padx = 3)
        col2Lbl.grid(row = 0, column = 1, pady = 3, padx = 3)
        #col2mode_Mat.grid(row = 1, column = 1)

        col3Lbl = Label(win, text = "Thickness[um]: ")
        col3Ent = Entry(win, width = 15, highlightbackground="grey", highlightthickness= 1)
        col3Ent.insert(0, values[2]) # Default is column 3's current value
        col3Lbl.grid(row = 0, column = 2, pady = 3, padx = 3)
        col3Ent.grid(row = 1, column = 2, pady = 3, padx = 3)
        
        col4Lbl = Label(win, text = "If Stack: Pairs: ")
        col4Ent = Entry(win, width = 15, highlightbackground="grey", highlightthickness= 1)
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
            if ConfirmEntry(treeView, col1Ent.get(), col2Ent.get(), col3Ent.get(), col4Ent.get()):
                win.destroy()

        okButt = Button(win, text = "Apply")
        okButt.bind("<Button-1>", lambda e: UpdateThenDestroy())
        okButt.grid(row = 1, column = 4, pady = 3, padx = 3)

        canButt = Button(win, text = "Cancel")
        canButt.bind("<Button-1>", lambda c: win.destroy())
        canButt.grid(row = 1, column = 5, pady = 3, padx = 3)
    
    def is_custom(self, index, value, op):
        if self.var_stack.get() == 'Custom':
            self.entry_custom = Entry(self.frame0, width = 15, highlightbackground="grey", highlightthickness= 1)
            self.entry_custom.grid(row = 4, column = 3)
            self.entry_custom.insert(END, 1.0)
        if self.var_stack.get() != 'Custom':
            self.entry_custom.destroy()
            
    def Get_GeometryData(self, wavelength):
        '''
        Helper Function to get treeview content
        
        wavelength in nm!
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
        epsilon = np.zeros(2*No_Pairs, dtype = dt)
        epsilon[::2] = n1**2.    # Make every 0,2,4th.. Entry n1 & every other n2
        epsilon[1::2] = n2**2.   # Using x[start:stop:step]
        
        thickness = np.zeros(2*No_Pairs)
        thickness[::2] = d1
        thickness[1::2] = d2
        return epsilon, thickness
    
    def TM_Calculation(self, thickness, epsilon, wavelength):
        '''
        Derive the Transfer Matrix of a given Stack

        Function Parameters
        ----------
        thickness : 1D-array, Vector containing the thicknesses
        epsilon   : 1D-array, Vector containing the permittivities
        wavelength: 1D-array, Incident wavelength in µm

        Returns
        -------
        Matrix : 2D-array,  To the Layer-Stack corresponding Transfer Matrix
        '''

        # initialize system transfer matrix to identity matrix
        Matrix = np.eye(2)

        # Wavevector
        k0 = 2.0*np.pi/wavelength
        kx = k0*np.sqrt(epsilon)

        ##### Iteration over each Stack of the Layer-Stack #####
        for kxi, di in zip(kx, thickness):
            c = np.cos(kxi*di)
            s = np.sin(kxi*di)
            m = np.array([[    c, s/kxi],
                        [-kxi*s,    c]])
            # Stack-TM is added to Total TM 
            Matrix = m@Matrix

        return Matrix

    def T_R_Calculation(self, thickness, epsilon, wavelength, Medium_in, Medium_out):
        '''
        Computes the reflection and transmission of a stratified medium.

        Function Parameters
        ----------
        thickness     : 1D-array, Vector containing the thicknesses
        epsilon       : 1D-array, Vector containing the permittivities
        wavelength    : 1D-array, Incident wavelength in µm
        Medium_in/out :    float, Refractive indicee of Medium before/after Layer-Stack

        Returns
        -------
        t : 1D-array,   The amplitude transmission coefficient
        r : 1D-array,   The amplitude reflection coefficient 
        T : 1D-array,   The intensity transmission coefficient
        R : 1D-array,   The intensity reflection coefficient
        '''

        # Wavevector
        k0 = 2.0*np.pi/wavelength
        kx_s = Medium_in*k0
        kx_c = Medium_out*k0

        r = np.zeros(wavelength.shape, dtype=np.complex128)
        N = np.zeros(wavelength.shape, dtype=np.complex128)

        ##### Iteration over all the wavelengths in 'wavelength'#####
        for i, (wavelength_i, kx_ci, kx_si) in enumerate(zip(wavelength, kx_c, kx_s)):
            M = self.TM_Calculation(thickness, epsilon, wavelength_i)
            N[i] = (kx_si*M[1,1] + kx_ci*M[0,0]
                + 1j*(M[1,0] - kx_si*kx_ci*M[0,1])) #De-Nominator of r
            r[i] = (kx_si*M[1,1] - kx_ci*M[0,0]       
                - 1j*(M[1,0] + kx_si*kx_ci*M[0,1])) #Nominator of r
        r /= N # Well known formular for reflectivity
        R = np.real(r*np.conj(r)) # The intensity reflection coefficient
        
        # The transmission coefficients
        t = 2.0*kx_s/N
        T = np.real(kx_c)/np.real(kx_s)*np.real(t*np.conj(t)) # Transmissivity

        return t, r, T, R
    
    def E_Field_Calculation(self, thickness, epsilon, wavelength, Precision):
        '''
        Calculation of the Electric Field strengh at different layers.
        
        The Field E_T is set to 1. 

        Function Parameters
        ----------
        thickness     : 1D-array, Vector containing the thicknesses
        epsilon       : 1D-array, Vector containing the permittivities
        wavelength    : 1D-array, Incident wavelength in µm
        Precision     :      int, Sampling value of the Electric Field
        
        length_in/out :    float, Length of the Medium before/after Layer-Stack... set to 0
        Medium_in/out :    float, Refractive indicee of Medium before/after Layer-Stack... set to 1
        
        Returns
        -------
        E_Field : 1D-array, Electric field strength at the different 'x'-positions
        x       : 1D-array, Spatial Positions at which the Field is computed
        index   : 1D-array, Spatial Distribution of refractive indicees
        '''
        # Input layer for x < 0; output layer for x > 0; illumination from the input layer side
        epsilon_in = 1
        epsilon_out = 1

        # extension of the vectors epsilon and thickness to take the input and
        # output layer into account
        thickness = np.concatenate(([0], thickness, [0]))
        epsilon = np.concatenate(([epsilon_in], epsilon, [epsilon_out]))

        ##### MAIN IDEA OF THE METHOD #####
        # Calculation is done starting from the transmitted field: Layers are flipped
        epsilon = epsilon[::-1]
        thickness = thickness[::-1]

        # Wavenumber & Wavevector
        k0 = 2.0*np.pi/wavelength
        kx = k0*np.sqrt(epsilon)

        # k-vector 'OUT'
        kx_o= kx[0]

        # Start calculation from transmitted field backwards..., Normalized transmitted field
        # (The field at the end is easily known, since it depends only on the transmitted wave)
        # The Minus sign comes from invertion of the structure
        alpha = np.ones_like(epsilon)
        
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
                ka = kx[curr_layer]
                m = np.array([[  c, s/ka],
                            [-ka*s,    c]])
                # update Total TM
                M = m@M
                # update Position-in-Layer, Layer No. & Thickness of passed layers
                pos_in_layer = pos_in_layer - thickness[curr_layer]
                thickness_below = thickness_below + thickness[curr_layer]
                curr_layer += 1

        # At diff. positions in Layer: Derive k-Vector (Starts with 'k' of last layer) up to next boundary
            try:
                ka = kx[curr_layer]*alpha[curr_layer]
            except: pass
            # In Time/Position Oscillating Field
            c = np.cos(ka*pos_in_layer) 
            s = np.sin(ka*pos_in_layer)
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
            self.Prog_E["value"] = 100*(i/len(x))
            self.frame_Sim.update_idletasks()
        # First Entry in 'E_Field' is the Amplitude at the end of Stack: Flip Arrays!
        E_Field = E_Field[::-1]
        index = index[::-1]
        x = np.linspace(0, np.sum(thickness), Precision)
        return E_Field, x, index
     
    def switch(self):
        global is_on
        if is_on:
            self.button_sw.config(image = self.norm)
            is_on = False
        else:         
            self.button_sw.config(image = self.abs)
            is_on = True    

    def matplotCanvas(self, frame, x, y, xlabel = '', ylabel = '', label = '', color = 'black', ylower = None, yupper = None, grid = True, figsize = (5, 3)):
        fig = Figure(figsize=figsize, tight_layout = True)
        ax = fig.add_subplot(111)
        try:
            for i in range(len(x)):
                ax.plot(x[i], y[i], label = label, color = color[i])
        except:
            ax.plot(x, y, label = label, color = color)

        if ylower != None:
            ax.set_ylim(ylower, yupper)
        ax.set_xlabel(xlabel, fontsize = 12)
        ax.set_ylabel(ylabel, fontsize = 12)
        #self.a.set_title("Reflection of p-polarized light with Surface Plasmon Resonance", fontsize = 8)
        if grid == True:
            ax.grid()
        #self.a.legend()
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
        fig = plt.figure(figsize = (5, 3), tight_layout = True)
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
    



    

