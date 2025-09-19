Welcome to PatchBatch! The purpose of this program is to streamline electrophysiology data analysis workflows by enabling batch-analysis of data files that share the same analysis parameters. I developed this after growing impatient with the long, tedious workflows that require defining the same parameters repeatedly for every file. A full day of patch-clamp recordings could take an hour to extract a current density-voltage relationship from. This is typically a repetitive process that, while not technically complicated, requires significant mental energy to do reproducibly and without errors. I developed this program because I wanted to spend less time and focus on raw data extraction, and more time on data interpretation and further experiments. 

================================= HOW TO USE =================================

If you are starting with WCP files, start by converting them to .abf using the native export option in WinWCP. 


<img src="images/main_winwcp.PNG" alt="main_wcp" width="900"/>

<img src="images/winwcp_export.PNG" alt="winwcp_export" width="900"/>


**IMPORTANT NOTE FOR TIME-COURSE ANALYSIS: Due to file constraints with the ABF1 file format (as well as .mat format), sweep times cannot be derived from these files. To circumvent this, if you are doing a time-course analysis, it is necessary to fill in the "Stimulus Period (ms)" box. You can find this information as the "Stimulus Repeat Period" within the WinWCP protocol used for recording. This is only necessary if you are analyzing time course data.**


<img src="images/repeat_period.PNG" alt="repeat_period" width="1000"/>


Then, in PatchBatch, start by clicking "Open" in the top left corner. Select a single file to analyze. The sweeps should appear in the plot in the center of the window. You can drag the green cursors to desired positions, very similar to WinWCP. You can also define them in the "Range 1 Start (ms)" and similar fields under "Analysis Settings". Below, adjust "Plot Settings" for your desired analysis.


<img src="images/mainwindow.PNG" alt="main_window" width="1000"/>


 If you'd like to preview the output plot, click "Generate Analysis Plot". From there, you can export a CSV file with the analyzed data. If you only want the data without seeing the plot first, just click "Export Analysis Data" in the main window. You may check the box "Use Dual Analysis" to define two separate analysis ranges to analyze simulataneously, assuming you want the same plotting parameters. 


This program makes it possible to analyze a set of electrophysiology files with the same analysis parameters. To use this feature, start by setting all of the desired parameters as you would do for a single file. It is optional to open a single file in the main window first - if you know all of your parameters, you can skip loading the single file and go straight to batch analysis. The "Batch Analyze" button is under the "Analysis" menu at the top. A new window will appear which will prompt you to select files for analysis. Click "Start Analysis", then "View Results". A new window will appear that plots the analysis results. From this window, you can export individual CSV files for each analyzed file. These can be directly imported into Graphpad Prism. 


<img src="images/batch_analysis.PNG" alt="batch_analysis" width="300"/>


<img src="images/ba_results.PNG" alt="batchresultswindow" width="750"/>


If you are doing I-V analyses, the program allows you to create summary IV curves from batch analyses. When Current and Voltage are chosen as the Plot Settings, the Batch Analysis window will have an option to "Export Summary CSV". This will output a single CSV that contains the voltage set from your first analyzed file, rounded to the nearest integer, in the first column. All subsequent columns will contain the analyzed current data from all sweeps from all input files. You also have the option to generate a current density IV curve. Click the "Current Density IV" button in the Batch Analysis window. You will be prompted to enter Cslow values for all files. Then, a new window will appear that plots the current densities against voltages. 


<img src="images/cd_cslow.PNG" alt="Cslows" width="500"/>


<img src="images/cd_results.PNG" alt="cdresultswindow" width="800"/>


Similarly to the batch analysis, you have the option to export individual CSV files for every analyzed file, as well as a single Summary IV that follows the same format described above. The only difference is that these outputs contain current densities, rather than raw currents. All output CSVs are designed to be easily imported into Graphpad Prism. 


<img src="images/prism_import.PNG" alt="prismimport" width="300"/>


<img src="images/prism_cd_summary.PNG" alt="prism_cd_import" width="1100"/>


This program includes full functionality for the same four peak modes (absolute, positive, negative, and peak-peak) available in WinWCP. The peak mode can be adjusted in the corresponding drop-down menu in the main window. **All peak modes have been functional in tests, but final validation is still in progress.**

===================== GENERAL ELECTROPHYSIOLOGY OVERVIEW =====================

The program is designed to allow users to visualize electrophysiology data sweeps, define one or two analysis time ranges within the sweeps, and extract the measured current and voltage values from all sweeps from those time ranges. The user can measure average or peak values within the analysis ranges, with four different peak modes (absolute, positive, negative, and peak-peak). 

Briefly, patch-clamp is an electrophysiology method in which an electrode is attached to a cell membrane and the experimenter can either:
	Set a command voltage and measure resulting currents, or
	Set a command current and measure resulting voltages

The data is measured in sweeps, during which the command voltage (or command current) is defined by the experimenter. Both channels are measured during the sweeps. This validates that the command voltage (or current) reached the expected values. It also measures the resulting currents (or voltages) that occur. Generally, it is this resulting value of the dependent variable that is of the most interest, though analysis both channels is necessary for useful data. A typical electrophysiology sweep is visualized in the "HOW TO USE" section. In biophysics experiments, these sweeps typically occur for a duration of 0.5 seconds (s) to over 10 s. The sweeps occur consecutively, and command protocols can be designed to produce a wide array of sweeps. For example, one protocol may be designed to assess currents in response to a range of voltages. Meanwhile, other protocols may repeat the exact same 0.5 s voltage sweep for several minutes or longer. In most cases, the experimenter needs to extract average or peak values from a particular time range, with millisecond resolution, for all sweeps in a recording.

The program is designed for several analysis modes. One of the main features is the ability to plot the values from one channel against values from the other channel, both from the same analyzed time range per sweep. The same analysis range is always applied to each sweep, so that each sweep provides an analyzed voltage and an analyzed current value. The user can then plot all sweeps to visualize the behavior of both data channels through the duration of a recording. This mode of analysis will be referred to hereafter as current-voltage or I-V analysis. 

I-V analysis is commonly used in ion channel electrophysiology to assess determinants of ion channel gating. Often times, it is desirable to account for cell size when interpreting I-V data. For this reason, current density, rather than raw current, is often plotted against voltage to obtain more meaningful data interpretations. The current density is simply the raw current divided by the slow capacitance (referred to as "Cslow" in this program). Cslow is measured during an experiment after the electrode has formed a stable seal with the cell, before the recording begins. The user must log this information manually. Then, after performing an I-V batch analysis, the user can click "Current Density IV..." which will bring up a window to enter Cslow values for all files. The program will then produce a plot of current density versus voltage. In the "Current Density Results" window, the user can export all analyzed I-V data, both as individual files and as a summary file. In the individual file exports, the outputs will contain the analyzed data values for voltage and current for each file. In the Summary CSV, the first column will be the voltages common to all of the input files. IMPORTANT: the user is responsible for their own data inputs; entering input files that use different voltage sets will result in erroneous results. The batch analysis to current density workflow is designed to only be used for sets of files with the same voltage set. This enables the Summary CSV to contain analyzed current values that correspond to the voltage set in the subsequent columns. This file can be conveniently imported into a more powerful plotting program such as GraphPad Prism for creating publication-quality figures. Ultimately, this process captures the purpose of this program: to expedite the tedious process of repeatedly setting the same analysis parameters manually for data sets produced at a high frequency. 

For time-course experiments, the program allows the user to plot only one channel (typically on the Y-Axis) against the time within a recording that each sweep occurred. For example, a user may wish to plot how measured current changes with time, in conjunction with application of different drug concentrations. In this case, analyzed voltage values are not exlicitly used in the upstream analysis, but it is still important for the experimenter to verify that voltage values matched the values defined in the sweep protocol. This is because actual, measured voltages can differ significantly from command voltages for a multitude of reasons. While this is prudent for data viability, further details are beyond the scope of this software. For time-course analyses, the user must specify the Stimulus Repeat Period used in their voltage protocol. I was unable to parse sweep times from .wcp, .mat, or .abf (ABF1) metadata, so this is the most effective way to plot time-course data.

============================= STATEMENT OF NEED ==============================

I developed this program based on my data analysis workflow on WinWCP (Dempster, University of Strathclyde; https://spider.science.strath.ac.uk/sipbs/software_ses.htm), which follows the procedures explained above. WinWCP remains an excellent open-source software that I rely on for data acquisition. Thus, my raw data files are in the .wcp file format. Conveniently, WinWCP contains an export feature that enables conversion of one or multiple .wcp files to .mat and .abf file formats, both of which are supported by this program. However, this program does not support .wcp file import directly, so the initial conversion in WinWCP is necessary to use it for analyzing .wcp files. 

The central feature of this program is the "Batch Analyze" function. This is where the most time is saved compared to other data analysis software. This feature allows the user to set an analysis range (or two), as well as all other analysis and plotting parameters (average or peak or sweep time point per axis) then select a set of .mat or .abf files to analyze. The same analysis parameters will then be used to analyze all selected files in one action. It is very important that all files use the same voltage protocol, otherwise results will be invalid! The intended use of this feature is, for example, a set of 8 samples testing a particular condition's I-V relationship. It can be used for several conditions, just as long as the voltage/current protocol and desired analysis parameters are EXACTLY the same for all files. 

The Batch Analyze button will prompt the user first to select files for analysis. Then, the user is prompted to name the destination folder of the analyzed data. By default, this folder is named PB_analysis and will be located in the same folder from which the input files were selected. The program then performs the analysis for all selected files and automatically saves the output values in CSV files in the PB_analysis folder.

If the user has selected "Voltage" for the X-Axis and "Current" for the Y-Axis, then the Batch Analysis Results window will contain a "Current Density I-V" button. This enables further batch analysis of I-V data, enabling quick plotting of voltage versus current density (pA/pF), rather than voltage versus raw current. The new Current Density I-V window contains fields in which the user can enter slow capacitance (Cslow) values for each recording. Since this is not a data acquisition program, Cslow values must be recorded by the user at the time of recording, then entered during this analysis. Similar to the Batch Analysis Results window, the user can export CSV files containing analyzed voltages and current densities. The user can also export a "Summary CSV". This function rounds the voltage set of the first analyzed file to the nearest integer. It produces a single output CSV with the rounded voltages in the first column, and the corresponding currents in the next columns. Header contains the input file names. Brackets and any content within them are removed from file names, as these are only added by WinWCP during export and cause file naming issues downstream.

All output CSVs are designed for import into a larger, dedicating plotting software such as GraphPad Prism. See "HOW TO USE" for example of full workflow from raw .wcp file through plotting current density IVs in Prism.

================================= VALIDATION =================================

The following images demonstrate a comparison of analysis outputs by this software with ouputs by WinWCP. Both analyses used the same dataset of 12 patch-clamp recordings. However, WinWCP analyses used the original .wcp file, while this software used .abf conversions of the same files. File format conversions were performed in WinWCP. Each analysis used an analysis range of 150.1 ms - 649.2 ms, with the X-axis plotting Average Voltage and the Y-axis plotting Average Current. For current density analysis, the following Cslow values were used:
    250514_001: 34.4
    250514_002: 14.5
    250514_003: 20.5
    250514_004: 16.3
    250514_005: 18.4
    250514_006: 17.3
    250514_007: 14.4
    250514_008: 14.1
    250514_009: 18.4
    250514_010: 21.0
    250514_011: 22.2
    250514_012: 23.2
In the case of the WinWCP-analyzed files, current density calculations were performed in Graphpad Prism. The comparison found excellent agreement between both analysis methods. Each recording contained 11 sweeps, thus 132 data points were compared. The maximum discrepancy in the analyzed current values was 0.049 pA, a negligible difference in the context of typical patch-clamp recordings which often range from tens to hundreds or even thousands of pA. The distinction is likely due to floating point precision differences when the .wcp file is converted to .abf. WinWCP may also use interpolation in its analysis process depending on the analysis range used. Regardless, this distinction does not present a concern unless currents are being analyzed on a sub-pA basis. Similarly, the distinction in the measured voltage was 0.01147 mV, an insignificant difference unless experiments require sub-mV precision. These results are summarized as follows:

<img src="images/discrepancy.png" alt="discrepancy" width="1000"/>


A direct comparison of a Current Density vs. Voltage relationship plot produced by either process shows that the WinWCP results are faithfully reproduced:


<img src="images/data_comparison.png" alt="data_comparison" width="750"/>

**Note that this software is currently in beta, not all analysis modes and parameter combinations have been tested yet. You are encouraged to validate outputs against WinWCP outputs if using, for example, the swapped channels feature, peak analysis, or the dual analysis ranges. Testing and final validation of these features is in progress.**
