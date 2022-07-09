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
import scipy #for iqr function
import numpy as np
import pandas as pd

import matplotlib
matplotlib.use('agg') #so that it does not attempt to display via SSH
import matplotlib.pyplot as plt
plt.ioff() #turn interactive plotting off
matplotlib.rcParams.update({'font.size': 18})

import seaborn

from src import load

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


class LocationDiseaseSummary(object):
    def __init__(self, setname, term_search_dir, results_dir, out_bin, missing):
        print('Running summary for',setname)
        self.setname = setname
        self.results_dir = results_dir
        self.out_bin = out_bin #dictionary of dataframes
        self.uniq_set_files = list(set(list(self.out_bin.keys())))
        self.missing = missing
        
        #Run:
        self.make_location_and_disease_heatmap()
        self.make_disease_summary(term_search_dir)
        ##TODO uncomment this for locations paper (it just takes a while to run
        #because I do not have the location binary labels pre calculated):
        #self.make_location_summary()
        self.make_missingness_summary()
    
    # Heatmap #-----------------------------------------------------------------
    def make_location_and_disease_heatmap(self):
        print('Working on location and disease heatmap')
        #Stack all the location x disease dataframes on top of each other and
        #sum them together, then mkae a heatmap
        temp = self.out_bin[list(self.out_bin.keys())[0]]
        total = np.zeros(temp.shape)
        for key in list(self.out_bin.keys()):
            total += self.out_bin[key].values
        total = pd.DataFrame(total, columns = temp.columns.values.tolist(),
                             index = temp.index.values.tolist())
        LocationDiseaseSummary.heatmap(total, os.path.join(self.results_dir,self.setname+'_Total_Heatmap.pdf'))
    
    @staticmethod
    def heatmap(total, outpath):
        """Make a heat map of the sum across the whole data set"""
        seaborn.set()
        plt.tick_params(labelsize=3)
        a_max = int(0.8*np.amax(total.values))
        a_max = min(a_max, 800)
        center = int(a_max/2)
        print('clipping heatmap to 0.8*max = ',a_max,'and centering at',center)
        total = np.clip(total, a_min = 0, a_max = a_max)
        seaplt = (seaborn.heatmap(total.values,
                            cmap='Greys',
                            center = center,
                            xticklabels = total.columns.values.tolist(),
                            yticklabels=total.index.values.tolist())).get_figure()
        seaplt.savefig(outpath)
        seaplt.clf()
    
    # Separate Summary Tables And Barplots #------------------------------------
    def make_disease_summary(self, term_search_dir):
        """Make tables and bar plots summarizing the disease counts"""
        print('Working on make_disease_summary()')
        disease_out = pd.read_csv(os.path.join(term_search_dir, self.setname+'_DiseaseBinaryLabels.csv'),header=0,index_col=0)
        disease_out = filter_for_only_present_volumes(disease_out)
        LocationDiseaseSummary.df_column_summary(disease_out, os.path.join(self.results_dir, self.setname+'_Frequency_Diseases.csv'))
        LocationDiseaseSummary.bar_plot(disease_out.sum(axis = 0), os.path.join(self.results_dir, self.setname+'_BarPlotFreq_Diseases.pdf'), disease_out.shape[0])
    
    def make_location_summary(self):
        """Make tables and bar plots summarizing the location counts"""
        print('Working on make_location_summary()')
        temp = self.out_bin[list(self.out_bin.keys())[0]]
        all_locations = temp.columns.values.tolist()
        location_out = self.binarize_complex_labels(chosen_labels = all_locations, label_type = 'location')
        location_out = filter_for_only_present_volumes(location_out)
        LocationDiseaseSummary.df_column_summary(location_out, os.path.join(self.results_dir, self.setname+'_Frequency_Locations.csv'))
        LocationDiseaseSummary.bar_plot(location_out.sum(axis = 0), os.path.join(self.results_dir, self.setname+'_BarPlotFreq_Locations.pdf'), location_out.shape[0])
        
    def make_missingness_summary(self):
        print('Working on make_missing_summary()')
        if self.missing is not None:
           missing = 1 - self.missing #swap all the ones and zeros
           missing = filter_for_only_present_volumes(missing)
           LocationDiseaseSummary.df_column_summary(missing, os.path.join(self.results_dir, self.setname+'_Summary_of_Missingness.csv'))
        
    #Stolen from term_search.py
    def binarize_complex_labels(self, chosen_labels, label_type):
        """Return a dataframe with index of filenames (from self.uniq_set_files)
        and columns of <chosen_labels>. This is the old-fashioned output format.
        <label_type> is the type of the chosen_labels. It is either 'disease'
        (to access rows) or 'location' (to access columns)"""
        assert label_type in ['disease','location']
        binarized = pd.DataFrame(np.zeros((len(self.uniq_set_files),len(chosen_labels))),
                        index = self.uniq_set_files, columns = chosen_labels)
        for filename in self.uniq_set_files:
            for label in chosen_labels:
                if label_type == 'location':
                    value = np.sum(self.out_bin[filename].loc[:,label])
                elif label_type == 'disease':
                    value = np.sum(self.out_bin[filename].loc[label,:])
                if value > 0:
                    value = 1
                binarized.at[filename, label] = value
        return binarized
    
    @staticmethod
    def df_column_summary(df, savepath):
        """Calculate the sum of the columns and the percent of total for each
        column for dataframe <df> and save to <savepath>"""
        df_sum = df.sum(axis = 0)
        #df_sum for locations looks something like this:
        #    left_upper           6947.0
        #    left_mid             2191.0
        #    left_lower           9561.0
        #    right_upper          8521.0   ETC
        
        #grandtotal is the total number of scans, NOT the total number of
        #labels x scans, and NOT the total number of positive labels in all
        #scans (which is what you would get if you did df_sum.sum())
        grandtotal = df.shape[0] #number of scans
        print('using grandtotal number of scans =',grandtotal)
        df_percent = df_sum.divide(grandtotal)
        df_summary = pd.concat([df_sum, df_percent], axis = 1).rename(columns={0:'Count',1:'Percent'})
        df_summary.at['total','Count'] = grandtotal
        df_summary.at['total','Percent'] = 1.0
        df_summary.to_csv(savepath)
    
    @staticmethod
    def bar_plot(series, outpath, max_scans):
        """The series has labels which are either locations or diseases, and
        values which are counts"""
        series = series.sort_values(ascending=False,na_position='last')
        df = pd.DataFrame({'Count' : series})
        df.at['total_scans','Count'] = max_scans
        df = df.sort_values(by='Count')
        
        #Code to make pretty bar plot is adapted from
        #https://scentellegher.github.io/visualization/2018/10/10/beautiful-bar-plots-matplotlib.html
        # set font
        plt.rcParams['font.family'] = 'sans-serif'
        plt.rcParams['font.sans-serif'] = 'Helvetica'
        
        # set the style of the axes and the text color
        plt.rcParams['axes.edgecolor']='#333F4B'
        plt.rcParams['axes.linewidth']=0.8
        plt.rcParams['xtick.color']='#333F4B'
        plt.rcParams['ytick.color']='#333F4B'
        plt.rcParams['text.color']='#333F4B'
        
        # we first need a numeric placeholder for the y axis
        my_range=list(range(1,len(df.index)+1))
        
        fig, ax = plt.subplots(figsize=(6,int(df.shape[0]/3.6)))
        
        #get rid of background
        for item in [fig, ax]:
            item.patch.set_visible(False)
        
        # create the bars
        plt.hlines(y=my_range, xmin=0, xmax=df['Count'], color='#007ACC', alpha=0.2, linewidth=5)
        
        # create the dots at the end of the bars
        plt.plot(df['Count'], my_range, "o", markersize=5, color='#007ACC', alpha=0.6)
        
        # set labels
        ax.set_xlabel('Count', fontsize=15, fontweight='black', color = '#333F4B')
        ax.set_ylabel('Label', fontsize=15, fontweight='black', color = '#333F4B')
        
        # set axis
        ax.tick_params(axis='both', which='major', labelsize=12)
        plt.yticks(my_range, df.index)
        
        #Show the x axis labels with commas in the thousands
        #https://stackoverflow.com/questions/25973581/how-do-i-format-axis-number-format-to-thousands-with-a-comma-in-matplotlib
        ax.get_xaxis().set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
        
        # change the style of the axis spines
        ax.spines['top'].set_color('none')
        ax.spines['right'].set_color('none')
        ax.spines['left'].set_smart_bounds(True)
        ax.spines['bottom'].set_smart_bounds(True)
        
        plt.savefig(outpath, bbox_inches="tight")
        plt.close()

class AbnormalitiesPerCTHistograms(object):
    def __init__(self, setname, term_search_dir, results_dir):
        self.setname = setname
        disease_out = pd.read_csv(os.path.join(term_search_dir, setname+'_DiseaseBinaryLabels.csv'),header=0,index_col=0)
        disease_out = filter_for_only_present_volumes(disease_out)
        self.values = disease_out.sum(axis=1).values.tolist()
        self.results_dir = results_dir
        self.stats_abnormalities_per_ct()
        self.histogram_abnormalities_per_ct()
    
    def stats_abnormalities_per_ct(self):
        print('Summary of Abnormality Labels Per CT for',self.setname)
        mean = np.mean(self.values); print('\t mean abnormality labels per scan:',round(mean,3))
        std = np.std(self.values); print('\t std abnormality labels per scan:',round(std,3))
        median = np.median(self.values); print('\t median abnormality labels per scan:',round(median,3))
        iqr = scipy.stats.iqr(self.values); print('\t iqr abnormality labels per scan:',round(iqr,3))
        zeros = len([z for z in self.values if z==0]); print('\tscans with zero labels:',zeros)
    
    def histogram_abnormalities_per_ct(self):
        #See http://www.randalolson.com/2014/06/28/how-to-make-beautiful-data-visualizations-in-python-with-matplotlib/
        plt.figure(figsize=(10, 7.5))  
        ax = plt.subplot(111)
        ax.set_facecolor('white') #background is white
        ax.spines["top"].set_visible(False)  
        ax.spines["right"].set_visible(False)  
        ax.get_xaxis().tick_bottom()  
        ax.get_yaxis().tick_left()  
        plt.xticks(fontsize=18)  
        plt.yticks(fontsize=18)
        plt.xlabel("Total Abnormality Labels", fontsize=20)  
        plt.ylabel("# CT Scans", fontsize=20)  
        plt.hist(self.values, bins=25, rwidth = 0.7, color="#3F5D7D")
        plt.savefig(os.path.join(self.results_dir, self.setname+'_AbnormalitiesPerCT_Hist.pdf'), bbox_inches="tight")
        plt.close()

class AbnormalityLabelCorrelations(object):
    def __init__(self, setname, term_search_dir, results_dir):
        self.setname = setname
        disease_out = pd.read_csv(os.path.join(term_search_dir, setname+'_DiseaseBinaryLabels.csv'),header=0,index_col=0)
        self.disease_out = filter_for_only_present_volumes(disease_out)
        self.results_dir = results_dir
        self.calculate_and_plot_all_correlations()
    
    def calculate_and_plot_all_correlations(self):
        #note that pearson and spearman correlations are the same for binary
        #data: https://stats.stackexchange.com/questions/103801/is-it-meaningful-to-calculate-pearson-or-spearman-correlation-between-two-boolea
        for corr_type in ['pearson']: #could do spearman too but that would be the same result
            print('calculating abnormality label correlation:',corr_type)
            corrdf = self.disease_out.corr(method=corr_type)
            corrdf.to_csv(os.path.join(self.results_dir,self.setname+'_All_Corrs_'+corr_type+'.csv'),header=True,index=True)
            
            #Pick out the highest correlations (2 or 3 stdevs above the mean), save table, and plot
            #Save more correlations to the table than you show in the plot:
            _ = self._calculate_top_correlations(corrdf, corr_type, stdevs_above=2)
            self._plot_top_correlations(corrdf, corr_type, stdevs_above=3)
    
    def _calculate_top_correlations(self, corrdf, corr_type, stdevs_above):
        """Pick out the correlations that are three standard deviations above
        the mean correlation"""
        assert stdevs_above in [2,3]
        amountabove=np.mean(corrdf.values)+(np.std(corrdf.values)*stdevs_above)
        print('\tamountabove (3 stdev above the mean):',amountabove)
        sets_considered = []
        top_corrs_df = pd.DataFrame(np.empty((50,2),dtype='str'),columns=['Label_A','Label_B'], index=[x for x in range(50)])
        top_corrs_df['Correlation'] = 0.0
        idx = 0
        for colname in corrdf.columns.values.tolist():
            for idxname in corrdf.index.values.tolist():
                myset = set([colname,idxname])
                if myset not in sets_considered:
                    sets_considered.append(myset)
                    val = corrdf.at[idxname,colname]
                    if val > amountabove and val < 1:
                        top_corrs_df.at[idx,'Label_A'] = idxname
                        top_corrs_df.at[idx,'Label_B'] = colname
                        top_corrs_df.at[idx,'Correlation'] = float(val)
                        print('\t',idxname, colname, val)
                        idx+=1
        top_corrs_df = top_corrs_df[top_corrs_df['Correlation']>0]
        top_corrs_df = top_corrs_df.sort_values(by='Correlation',ascending=False)
        if stdevs_above == 2: #save the table as a CSV
            tablename = self.setname+'_Table_TopCorrs_'+corr_type+'_'+str(stdevs_above)+'stdvs.csv'
            top_corrs_df.to_csv(os.path.join(self.results_dir,tablename))
        return top_corrs_df
    
    def _plot_top_correlations(self, corrdf, corr_type, stdevs_above):
        """Make a triangular heat map that includes the correlations that are
        three standard deviations above the mean"""
        top_corrs_df = self._calculate_top_correlations(corrdf, corr_type, stdevs_above)
        
        #get chosen abnormalities in sorted order
        the_chosen = list(set(top_corrs_df['Label_A'].values.tolist()+top_corrs_df['Label_B'].values.tolist()))
        
        #select out chosen abnormalities from overall correlations df
        corrdf_chosen = corrdf.loc[the_chosen,the_chosen]
        
        #get a mask to make the heat map triangular (since the heat map is
        #symmetrical across the diagonal)
        mask = np.zeros_like(corrdf_chosen, dtype = np.bool)
        mask[np.triu_indices_from(mask)]=True
        
        #Plot the heat map. Code modified from the code in this post:
        #https://towardsdatascience.com/annotated-heatmaps-in-5-simple-steps-cc2a0660a27d
        f, ax = plt.subplots(figsize=(11, 15)) 
        
        heatmap = seaborn.heatmap(corrdf_chosen, 
                              mask = mask,
                              square = True,
                              linewidths = .5,
                              cbar_kws = {'shrink': .4, 'ticks': [0, 0.5, 1]},
                              vmin = 0, 
                              vmax = 1,
                              annot = True,
                              annot_kws = {'size': 8}) #font size inside the boxes
        
        #add the column names as labels
        ax.set_yticklabels(corrdf_chosen.columns, rotation = 0, fontdict={'fontsize':12}) #axis font size
        ax.set_xticklabels(corrdf_chosen.columns, fontdict={'fontsize':12})
        seaborn.set_style({'xtick.bottom': True}, {'ytick.left': True})
        
        # fix for mpl bug that cuts off top/bottom of seaborn viz
        #From https://github.com/mwaskom/seaborn/issues/1773
        b, t = plt.ylim() # discover the values for bottom and top
        b += 0.5 # Add 0.5 to the bottom
        t -= 0.5 # Subtract 0.5 from the top
        plt.ylim(b, t) # update the ylim(bottom, top) values
        figname = self.setname+'_Heatmap_TopCorrs_'+corr_type+'_'+str(stdevs_above)+'stdvs.pdf'
        heatmap.get_figure().savefig(os.path.join(self.results_dir,figname),bbox_inches='tight')
    
def filter_for_only_present_volumes(df):
    """Given a dataframe that has accession numbers as the index, return
    the same dataframe containing only the accession numbers that
    correspond to volumes which were successfully downloaded and processed"""
    print('Shape of unfiltered df',df.shape)
    available_volumes = pd.read_csv('./data_ct/Available_Volumes.csv',header=0)['Accession'].values.tolist()
    df = df.filter(items=available_volumes,axis=0)
    print('Shape of df after filtering for available volumes',df.shape)
    return df
    