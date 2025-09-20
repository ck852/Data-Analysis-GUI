Welcome to PatchBatch! The purpose of this program is to streamline electrophysiology data analysis workflows by enabling batch-analysis of data files that share the same analysis parameters. I developed this after growing impatient with the long, tedious workflows that require defining the same parameters repeatedly for every file, followed by further rote transformations that could be defined algorithmically. This is typically a repetitive process that, while not technically complicated, requires extended periods of focus to do reproducibly without errors. I developed this program because I wanted to conserve this cognitive effort for more worthy downstream processes including data interpretation and further experiments. 

================================= HOW TO USE =================================

If you are starting with WCP files, start by converting them to .abf using the native export option in WinWCP. 


<img src="images/main_winwcp.PNG" alt="main_wcp" width="450"/>

<img src="images/winwcp_export.PNG" alt="winwcp_export" width="900"/>


**IMPORTANT NOTE FOR TIME-COURSE ANALYSIS: Due to file constraints with the ABF1 file format (as well as .mat format), sweep times cannot be derived from these files. To circumvent this, if you are doing a time-course analysis, it is necessary to fill in the "Stimulus Period (ms)" box. You can find this information as the "Stimulus Repeat Period" within the WinWCP protocol used for recording. Read on for more information. This is only necessary if you are analyzing time course data.**


<img src="images/repeat_period.PNG" alt="repeat_period" width="1000"/>


Then, in PatchBatch, start by clicking "Open" in the top left corner. Select a single file to analyze. The sweeps should appear in the plot. The right and left arrows next to the "Open" button adjust which sweep is displayed. You can drag the green cursors to desired positions to define your analysis time range, very similar to WinWCP. You can also define them in the "Range 1 Start (ms)" and similar fields under "Analysis Settings". Note that you can check "Use Dual Analysis" to extract data from two regions in one output. **IMPORTANT: If you are doing a time-course analysis, you must enter the "Stimulus Period (ms)".** Below, adjust "Plot Settings" for your desired analysis. This program includes the same four peak analysis modes (absolute, positive, negative, and peak-peak) available in WinWCP. The peak mode can be adjusted in the corresponding drop-down menu in the main window. **All peak modes have aligned with WinWCP in preliminary tests, but final validation with figures is still in progress.**


<img src="images/mainwindow.PNG" alt="main_window" width="1000"/>


 If you'd like to preview the output plot, click "Generate Analysis Plot". From there, you can export a CSV file with the analyzed data. If you only want the data without seeing the plot first, just click "Export Analysis Data" at the bottom of the window. 


This program makes it possible to analyze several electrophysiology files with the same analysis parameters. To use this feature, start by setting all of the desired parameters as you would do for a single file. It is optional to open a single file in the main window first - if you know all of your parameters, you can skip loading the single file and go straight to batch analysis. The "Batch Analyze" button is under the "Analysis" menu at the top. A new window will appear which will prompt you to select files for analysis. Click "Start Analysis", then "View Results". A new window will appear that plots the analysis results. From this window, you can export individual CSV files for each analyzed file. These can be directly imported into Graphpad Prism. 


<img src="images/batch_analysis.PNG" alt="batch_analysis" width="300"/>


<img src="images/ba_results.PNG" alt="batchresultswindow" width="750"/>


If you are doing I-V analyses, the program allows you to create summary IV curves from batch analyses. When Current and Voltage are chosen as the Plot Settings, the Batch Analysis window will have an option to "Export IV Summary". This will output a single CSV that contains the voltage set from your first analyzed file, rounded to the nearest integer, in the first column. All subsequent columns will contain the analyzed current data from all sweeps from all input files. You also have the option to generate a current density IV curve. 
**IMPORTANT FOR SUMMARY IV: the user is responsible for their own data inputs; input files that use different voltage sets will yield erroneous results. Also note that voltages are rounded to the nearest integer. If the voltage sweeps are leaky, unstable, or otherwise inconsistent, the Summary CSV will likely be missing data points.** Click the "Current Density IV" button in the Batch Analysis window. You will be prompted to enter Cslow values for all files. Then, a new window will appear that plots the current densities against voltages. 


<img src="images/cd_cslow.PNG" alt="Cslows" width="500"/>


<img src="images/cd_results.PNG" alt="cdresultswindow" width="800"/>


Similarly to the batch analysis, you have the option to export individual CSV files for every analyzed file, as well as a single Summary IV that follows the same format described above. The only difference is that these outputs contain current densities, rather than raw currents. All output CSVs are designed to be easily imported into Graphpad Prism. 


<img src="images/prism_import.PNG" alt="prismimport" width="300"/>


<img src="images/prism_cd_summary.PNG" alt="prism_cd_import" width="1100"/>

The workflow for other analyses, such as Time vs Current, proceeds in a very similar manner. The primary distinction is the requirement for the Stimulus Repeat Period. For such time-course analyses, it is sometimes desirable to extract data from more than one analysis range per sweep. To this end, the "Use Dual Analysis" box enables the user to define a second analysis range.


<img src="images/dual_analysis_main.PNG" alt="dual_range_main" width="1100"/>


This enables the user to quickly plot both analysis ranges against the sweep times. The user can also output a CSV containing this data, ready for import into downstream analysis procedures.


<img src="images/dual_analysis_plot.PNG" alt="dual_analysis_plot" width="800"/>


It is important to note that the time-course analysis workflow uses an **approximation** of the true sweep times. During a recording, the sweeps do not occur at perfectly spaced intervals that match the exact stimulus repeat period each time. This results in a small deviation in the sweep times that becomes more apparent in longer recordings, on the order of 2 seconds of drift per 100 seconds of recording. This likely varies by experimental setup and is affected by physical hardware constraints. This should not present a major complication for most uses, but is worth considering when analyzing longer recordings. See the "Validation" section for more information.

**Note that this software is currently in beta, not all analysis modes and parameter combinations have been tested yet. You are encouraged to validate outputs against WinWCP outputs if using, for example, the swapped channels feature or peak analysis. Testing and final validation of these features is in progress.**


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

The input abf files are available in the file repository. In the case of the WinWCP-analyzed files, current density calculations were performed in Graphpad Prism. The comparison found excellent agreement between both analysis methods. Each recording contained 11 sweeps, thus 132 data points were compared. The maximum discrepancy in the analyzed current values was 0.049 pA, a negligible difference in the context of typical patch-clamp recordings which often range from tens to hundreds or even thousands of pA. The distinction is likely due to floating point precision differences when the .wcp file is converted to .abf. WinWCP may also use interpolation in its analysis process depending on the analysis range used. Regardless, this distinction does not present a concern unless currents are being analyzed on a sub-pA basis. Similarly, the distinction in the measured voltage was 0.01147 mV, an insignificant difference unless experiments require sub-mV precision. These results are summarized as follows:

<img src="images/discrepancy.png" alt="discrepancy" width="1000"/>


A direct comparison of a Current Density vs. Voltage relationship plot produced by either process shows that the WinWCP results are faithfully reproduced:


<img src="images/data_comparison.png" alt="data_comparison" width="750"/>


The disparity in time values as a result of the stimulus repeat period approximation of sweep times is characterized as follows:


<img src="images/Time.png" alt="time_comparison" width="450"/>


The disparity appears to increase with the length of the recordings. While not a concern for many use cases, this could present a concern for very long recordings (> 10 minutes). Mitigation strategies are under consideration.


The following data validates the Dual Analysis mode by comparing the average current outputs from two analysis ranges to the same measurement output by WinWCP:


<img src="images/dual_range_comparison.png" alt="dual_range_comparison" width="750"/>