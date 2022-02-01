# TM_Solver
Fully Functional Python Based GUI for Transfer Matrix Method purposes for optical multilayer structures.

author: Paul Steinmann <p.steinmann@uni-bonn.de>
Started : 10.01.2022
Released: 28.01.2022
Version: 1.0.1

    Version Added: 1.0.1
        Changed Gui style to ttks 'clam'
        Changed Style of the Progressbar
        Fixed a Bug for Electric Field displayment of the Im Part got too big.
    
Progress until V1: 100 %
    Main Tasks:
        Fix Problem: Wave in last material osc., which changes the physics if length is changed.
        
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
