# -*- coding: utf-8 -*-

"""
* pycoQC
* [GNU General Public License v2](http://www.gnu.org/licenses/gpl-2.0.html)
* Adrien Leger - 2017
* <aleg@ebi.ac.uk>
* [Github](https://github.com/a-slide)
"""

# Standard library imports


# Third party imports
try:
    current= "Numpy 1.13.0"
    import numpy as np
    current = "Matplotlib 2.0.2"
    import pylab as pl
    current = "Pandas 0.20.2"
    import pandas as pd
    current = "Seaborn 0.7.1"
    import seaborn as sns
    current = "Jupyter 4.2.0"
    cfg = get_ipython()
    from IPython.core.display import display
    
except (NameError, ImportError):
    print ("The third party package {}+ is required by picoQC. Please verify your dependencies".format(current))
    sysexit()


##~~~~~~~ MAIN CLASS ~~~~~~~#

class pycoQC():
    
    def __init__ (self, seq_summary_file, runid=None, verbose=False):
        """
        Parse Albacore sequencing_summary.txt file and cleanup the data
        * seq_summary_file
            Path to the sequencing_summary.txt generated by Albacore
        * runid
            If you want a specific runid to be analysed. Usually there are 2 runids per minion experiment, the mux run and the sequencing
            run. By default it will analyse the runid with the most reads, ie the sequencing run. [Default: None]
        * verbose
            print additional informations. [Default: False]
        """
        self.verbose=verbose
        
        # import in a dataframe
        self.seq_summary_file = seq_summary_file
        self.df = pd.read_csv(seq_summary_file, sep ="\t")
        self.df.dropna(inplace=True)
        
        # Find or verify runid
        runid_counts = self.df['run_id'].value_counts(sort=True)
                
        if not runid:
            if self.verbose:
                print ("Runid found in the datasets")
                runid_counts.name = "Count"
                runid_df = pd.DataFrame(runid_counts)
                runid_df.columns.name = "Run_ID"
                display(runid_df)
                print ("Selecting Run_ID {}".format(runid_counts.index[0]))
                
            self.runid = runid_counts.index[0]
            self.total_reads = runid_counts.loc[self.runid]
            
            
        else:
            self.runid = runid
            self.total_reads = runid_counts.loc[self.runid]
        
        # Extract the runid data from the overall dataframe
        self.df = self.df[(self.df["run_id"] == self.runid)]
        self.df = self.df.reset_index(drop=True)
        self.df.set_index("read_id", inplace=True)
        #self.df.drop(['filename', 'run_id'], axis=1, inplace=True)
        
        if self.verbose:
            print ("Dataframe head")
            display (self.df.head())
        
    def channels_activity (self, level="reads", figsize=[24,12], cmap="OrRd", alpha=1, robust=True, annot=True, fmt="d", cbar=False,
        **kwargs):
        """
        Plot the activity of channels at read, base or event level. Based on Seaborn heatmap function. The layout does not represent the
        physical layout of the flowcell, and   
        * level
            Aggregate channel output results by "reads", "bases" or "events". [Default: "reads"]
        * figsize 
            Size of ploting area [Default: [24,12]]
        * cmap
            Matplotlib colormap code to color the space [Default: "OrRd"]
        * alpha
            Opacity of the area from 0 to 1 [Default: 1]
        * robust
            if True the colormap range is computed with robust quantiles instead of the extreme values [Default: True]
        * annot
            If True, write the data value in each cell. [Default: True]
        * fmt
            String formatting code to use when adding annotations (see matplotlib documentation) [Default: "d"]
        * cbar
            Whether to draw a colorbar scale on the right of the graph [Default: False]        
        """
        
        # Compute the count per channel
        if level == "reads":
            s = self.df['channel'].value_counts(sort=False)
            title = "Reads per channels"
        if level == "bases":
            s = n.df.groupby("channel").aggregate(np.sum)["sequence_length_template"]
            title = "Bases per channels"
        if level == "events":
            s = n.df.groupby("channel").aggregate(np.sum)["num_events"]
            title = "Events per channels"
            
        # Fill the missing values
        for i in range(1, 512):
            if i not in s.index:
                s.loc[i] = 0

        # Sort by index value 
        s.sort_index(inplace=True)

        # Reshape the series to a 2D frame similar to the Nanopore flowcell grid 
        a = s.values.reshape(16,32)

        # Plot a heatmap like grapd
        fig, ax = pl.subplots(figsize=figsize)
        ax = sns.heatmap(a, ax=ax, annot=annot, fmt=fmt, linewidths=2, cbar=cbar, cmap=cmap, alpha=alpha, robust=robust)
                    
        # Tweak the plot
        t = ax.set_title (title)
        t = ax.set_xticklabels("")
        t = ax.set_yticklabels("")
        
        for text in ax.texts:
            text.set_size(8)
    
    def mean_qual_distribution (self, figsize=[30,7], color="orangered", alpha=0.5, normed=True, win_size=0.1, xmin=0, xmax=40, **kwargs):
        """
        Plot the distribution of the mean read PHRED qualities
        * figsize
            Size of ploting area [Default:figsize=[30,7]
        * color
            Color of the plot. Valid matplotlib color code [Default "orangered"]
        * alpha
            Opacity of the area from 0 to 1 [Default: 1]
        * normed
            Normalised results. Frenquency rather than counts [Default True]
        * win_size
            Size of the bins in quality score ranging from 0 to 40 [Default 0.1]
        * xmin, xmax
            Lower and upper limits on x axis [Default 0, 40]
        """
        # Plot an histogram of the mean quality score
        fig, ax = pl.subplots(figsize=figsize)
        ax = self.df['mean_qscore_template'].plot.hist(bins=np.arange(0,40,win_size), ax=ax, normed=normed, color=color, alpha=alpha,
            histtype='stepfilled')
        
        # Tweak the plot
        t = ax.set_title ("Mean quality distribution per read")
        t = ax.set_xlabel("Mean PHRED quality Score")
        if normed:
            t = ax.set_ylabel("Frequency")
        else:
            t = ax.set_ylabel("Read count")
        t = ax.set_xlim (xmin, xmax)
    
    def output_over_time (self, level="reads", figsize=[30,7], color="orangered", alpha=0.5, win_size=0.25, cumulative=False, **kwargs):
        """
        Plot the output over the time of the experiment at read, base or event level
        * level
            Aggregate channel output results by "reads", "bases" or "events" [Default: "reads"]
        * figsize
            Size of ploting area [Default:figsize=[30,7]
        * color
            Color of the plot. Valid matplotlib color code [Default "orangered"]
        * alpha
            Opacity of the area from 0 to 1 [Default: 0.5]
        * win_size
            Size of the bins in hours [Default 0.25]
        * cumulative
            cumulative histogram [Default False]
        """
        df = n.df[["num_events", "sequence_length_template"]].copy()
        df["end_time"] = (n.df["start_time"]+n.df["duration"])/3600

        # Compute the mean, min and max for each win_size interval
        df2 = pd.DataFrame(columns=["reads", "bases", "events"])
        for t in np.arange(0, max(df["end_time"]), win_size):
            sdf = df[(df["end_time"] >= t) & (df["end_time"] < t+win_size)]
            df2.loc[t] =[len(sdf), sdf["sequence_length_template"].sum(), sdf["num_events"].sum()]

        # Plot the graph
        fig, ax = pl.subplots(figsize=figsize)
        df2[level].plot.area(ax=ax, color=color, alpha=alpha)

        # Tweak the plot
        t = ax.set_title ("Total {} over time".format(level))
        t = ax.set_xlabel("Experiment time (h)")
        t = ax.set_ylabel("Count {}".format(level))
        t = ax.set_xlim (0, max(df2.index))
        t = ax.set_ylim (0, ax.get_ylim()[1])
    
    def quality_over_time (self, figsize=[30,7], color="orangered", alpha=0.25, win_size=0.25, **kwargs):
        """
        Plot the evolution of the mean read quality over the time of the experiment at read, base or event level
        * figsize
            Size of ploting area [Default:figsize=[30,7]
        * color
            Color of the plot. Valid matplotlib color code [Default "orangered"]
        * alpha
            Opacity of the area from 0 to 1 [Default: 0.25]
        * win_size
            Size of the bins in hours [Default 0.25]
        """
        # Slice the main dataframe
        df = self.df[["mean_qscore_template"]].copy()
        df["end_time"] = (self.df["start_time"]+self.df["duration"])/3600
        
        # Compute the mean, min and max for each win_size interval
        df2 = pd.DataFrame(columns=["mean", "min", "max", "q1", "q3"])
        for t in np.arange(0, max(df["end_time"]), win_size):
            sdf = df["mean_qscore_template"][(df["end_time"] >= t) & (df["end_time"] < t+win_size)]
            df2.loc[t] =[sdf.mean(), sdf.min(), sdf.max(), sdf.quantile(0.25), sdf.quantile(0.75)]

        # Plot the graph
        fig, ax = pl.subplots(figsize=figsize)
        ax.fill_between(df2.index, df2["min"], df2["max"], color=color, alpha=alpha)
        ax.fill_between(df2.index, df2["q1"], df2["q3"], color=color, alpha=alpha)
        ax.plot(df2["mean"], color=color)
        
        # Tweak the plot
        t = ax.set_title ("Mean read quality over time (Mean, Q1-Q3, Min-Max)")
        t = ax.set_xlabel("Experiment time (h)")
        t = ax.set_ylabel("Mean read PHRED quality")
        t = ax.set_xlim (0, max(df2.index))
        t = ax.set_ylim (0, ax.get_ylim()[1])
        
    def reads_len_distribution (self, figsize=[30,7], color="orangered", alpha=0.5, win_size=1000, normed=False,
                                xlog=False, ylog=False, xmin=0, xmax=None, ymin=0, ymax=None, **kwargs):
        """
        Plot the distribution of read length in base pairs
        * figsize
            Size of ploting area [Default:figsize=[30,7]
        * color
            Color of the plot. Valid matplotlib color code [Default "orangered"]
        * alpha
            Opacity of the area from 0 to 1 [Default: 0.5]
        * win_size
            Size of the bins in base pairs [Default 1000]
        * normed
            Normalised results. Frenquency rather than counts [Default False]
        * xlog, ylog
            Use log10 scale for x and y axis [Default True, True]
        * xmin, xmax
            Lower and upper limits on x axis [Default 0, None]
        * ymin, ymax
            Lower and upper limits on y axis [Default 0, None]
        """
        if not xmax:
            xmax = max(self.df['sequence_length_template'])
        
        if xlog:
            bins = np.logspace(int(np.log10(xmin)), int(np.log10(xmax))+1, num=int(xmax/win_size), endpoint=True, base=10)
        else:
            bins = np.arange(xmin, xmax, win_size)
        
        # Plot the graph
        fig, ax = pl.subplots(figsize=figsize)
        ax = self.df['sequence_length_template'].plot.hist(bins=bins, ax=ax, normed=normed, color=color, alpha=alpha, histtype='stepfilled')
        
        # Tweak the plot       
        t = ax.set_title ("Distribution of reads length")
        t = ax.set_xlabel("Length in bp")
        if normed:
            t = ax.set_ylabel("Frequency")
        else:
            t = ax.set_ylabel("Read count")
        
        if xlog:
            ax.set_xscale("log")
        if ylog:
            ax.set_yscale("log")
        
        t = ax.set_xlim (xmin, xmax)
        if ymax:
            t = ax.set_ylim (ymin, ymax)
        else:
            t = ax.set_ylim (ymin, ax.get_ylim()[1])
