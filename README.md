# TM_Solver
Fully Functional Python Based GUI for Transfer Matrix Method purposes for optical multilayer structures.

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
