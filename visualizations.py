#visualizations.py
#Copyright (c) 2020 Rachel Lea Ballantyne Draelos

#MIT License

#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:

#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE

import os
import pickle
import numpy as np
import pandas as pd

import matplotlib
matplotlib.use('agg') #so that it does not attempt to display via SSH
import matplotlib.pyplot as plt
plt.ioff() #turn interactive plotting off
matplotlib.rcParams.update({'font.size': 18})

import load 

class RepeatedSentenceHistograms(object):
    def __init__(self, dataset, results_dir):
        #Load count_label_sent via loading 'merged' so that only radiology reports
        #for which volumes are actually present in the data set are included.
        train_merged, _, _ = load.load_merged_with_style(dataset, 'trainall_testall')
        grouped = train_merged.groupby(['Sentence','Label']).size().reset_index(name='Count')
        self.count_label_sent = grouped[['Count','Label','Sentence']]
        
        #Make Sentence Histograms
        self.make_histogram(filtering='all', plot_title='Repeated Sentences (all)',
            file_title=os.path.join(results_dir, 'notetrain_RepeatSentsAll_Hist.pdf'))
        self.make_histogram(filtering='s', plot_title='Repeated Sentences (sick)',
            file_title=os.path.join(results_dir, 'notetrain_RepeatSentsSick_Hist.pdf'))
        self.make_histogram(filtering='h', plot_title='Repeated Sentences (healthy)',
            file_title=os.path.join(results_dir, 'notetrain_RepeatSentsHealthy_Hist.pdf'))
    
    def make_histogram(self, filtering, plot_title, file_title):
        """Make histogram of number of repeated sentences and also print off
        the top 10 most common sentences in the category"""
        df = self.count_label_sent
        if filtering=='s':
            df = df[df['Label'] == 's']
            print('Using s only there are',str(df.shape[0]),'rows')
        elif filtering=='h':
            df = df[df['Label'] == 'h']
            print('Using h only there are',str(df.shape[0]),'rows')
        else:
            print('Using all data there are',str(df.shape[0]),'rows')
        self._print_most_common(df, filtering)
        
        #Get histogram data
        histdata = []
        for indexname in df.index.values:
            count = df.loc[indexname,'Count']
            histdata = histdata + [count]*count
        
        #Plot histogram
        #http://www.randalolson.com/2014/06/28/how-to-make-beautiful-data-visualizations-in-python-with-matplotlib/
        plt.figure(figsize=(10, 7.5))  
        ax = plt.subplot(111)  
        ax.spines["top"].set_visible(False)  
        ax.spines["right"].set_visible(False)  
        ax.get_xaxis().tick_bottom()  
        ax.get_yaxis().tick_left()  
        plt.xticks(fontsize=18)  
        plt.yticks(fontsize=18)
        plt.xlabel("# Repeats", fontsize=20)  
        plt.ylabel("# Sentences", fontsize=20)  
        plt.hist(histdata, bins=25, rwidth = 0.7, color="#3F5D7D")
        plt.savefig(file_title, bbox_inches="tight")
        plt.close()

    def _print_most_common(self, df, filtering):
        print('The top 10 most common '+filtering+' sentences are:')
        top = df.sort_values(by=['Count'], ascending=False).iloc[0:10,:]
        for sublist in top.values.tolist():
            print(sublist)
