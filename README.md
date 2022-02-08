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

        Coloriezed Plots
        Compute R vs lamba vs layerpairs ?
        Add Function Docstrings EVERYWHERE !!!
        Ask for feedback     
            Angle of Incidence ? ---> This would be a huge upgrade to the programm, thus: Would imply version 2.0
        Add feedback/terminal window in programm (Nothing selected, errors, comp time, etc...)
        Improve speed of: Refl vs Wavelength; And: Dont allow button inputs while running
        if "Description" of material already exists add a number !
        Multi-Processing ?
        Improve: OnDouble Click function !
        Compute E_MAX vs Parameter, E_MAX at Position
        iF interpol range is reached, plot until this values and update range max
        Changable speed of animation
