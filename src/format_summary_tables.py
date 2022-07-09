#format_summary_tables.py
#Copyright (c) 2021 Rachel Lea Ballantyne Draelos

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
import numpy as np
import pandas as pd

def create_table(hybrid_amb_neg_path,
                 hybrid_amb_pos_path,
                 rules_amb_neg_path,
                 rules_amb_pos_path,
                 metricname,
                 locfilt_string,
                 results_dir):
    """The paths are the paths to the file test_Final_Performance.csv
    which has columns ['FScore','Precision_Calc','Precision','Recall_Calc',
    'Recall','Accuracy_Calc','Accuracy','TN','FP','FN','TP','Freq_test']
    
    Format a unified table for the performance metric of interest and save
    it in results_dir."""
    assert metricname in ['FScore','Precision','Recall','Accuracy']
    assert locfilt_string in ['no-loc-filt','with-loc-filt']
    for chosen_path in [hybrid_amb_neg_path, hybrid_amb_pos_path, rules_amb_neg_path, rules_amb_pos_path,]:
        assert locfilt_string in chosen_path
    for chosen_path in [hybrid_amb_neg_path, hybrid_amb_pos_path]:
        assert 'hybrid' in chosen_path
    for chosen_path in [rules_amb_neg_path, rules_amb_pos_path]:
        assert 'rules' in chosen_path
    for chosen_path in [hybrid_amb_neg_path, rules_amb_neg_path]:
        assert 'ambneg' in chosen_path
    for chosen_path in [hybrid_amb_pos_path, rules_amb_pos_path]:
        assert 'ambpos' in chosen_path
    
    #Load
    hybrid_amb_neg_df = pd.read_csv(hybrid_amb_neg_path,header=0,index_col=0)
    hybrid_amb_pos_df = pd.read_csv(hybrid_amb_pos_path,header=0,index_col=0)
    rules_amb_neg_df = pd.read_csv(rules_amb_neg_path,header=0,index_col=0)
    rules_amb_pos_df = pd.read_csv(rules_amb_pos_path,header=0,index_col=0)
    
    #Gather performance metrics
    outdf = pd.DataFrame(index=hybrid_amb_neg_df.index.values.tolist(),
                         columns=[metricname+' Hybrid AmbNeg', metricname+' Hybrid AmbPos', metricname+' Rules AmbNeg', metricname+' Rules AmbPos'])
    outdf[metricname+' Hybrid AmbNeg'] = hybrid_amb_neg_df[metricname]
    outdf[metricname+' Hybrid AmbPos'] = hybrid_amb_pos_df[metricname]
    outdf[metricname+' Rules AmbNeg'] = rules_amb_neg_df[metricname]
    outdf[metricname+' Rules AmbPos'] = rules_amb_pos_df[metricname]
    
    #multiply all percentages by 100 and round to 2 decimal points
    outdf = outdf.multiply(100)
    outdf = outdf.round(decimals=2)
    
    #Add in test frequency and do sanity checks
    outdf['Test Freq'] = hybrid_amb_neg_df['Freq_test']
    assert (hybrid_amb_neg_df['Freq_test']==hybrid_amb_pos_df['Freq_test']).all()
    assert (rules_amb_neg_df['Freq_test']==rules_amb_pos_df['Freq_test']).all()
    assert (hybrid_amb_neg_df['Freq_test']==rules_amb_pos_df['Freq_test']).all()
    
    #filter by test frequency
    outdf = outdf[outdf['Test Freq']>=20]
    
    #re-order the columns to put 'Test Freq' first
    outdf = outdf[['Test Freq',metricname+' Hybrid AmbNeg', metricname+' Hybrid AmbPos', metricname+' Rules AmbNeg', metricname+' Rules AmbPos']]
    
    #get rid of underscores in abnormality names
    outdf.index = outdf.index.map(lambda x: x.replace('_',' '))
    
    #add a mean row at the bottom
    #also, pad so there are always 2 characters after the decimal, e.g. 90.1 -> 90.10
    for colname in [metricname+' Hybrid AmbNeg', metricname+' Hybrid AmbPos', metricname+' Rules AmbNeg', metricname+' Rules AmbPos']:
        column_mean = np.mean(outdf[colname])
        outdf.at['Mean',colname] = round(column_mean,2)
        outdf[colname] = outdf[colname].astype(str).str.pad(5,side='right',fillchar='0')
    
    outdf.to_csv(os.path.join(results_dir,locfilt_string+'_'+metricname+'_Summary.csv'),header=True,index=True)
