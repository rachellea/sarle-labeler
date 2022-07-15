#evaluation.py
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
import numpy as np
import pandas as pd
import sklearn.metrics

##############################
# Sentence-Level Performance #--------------------------------------------------
##############################
def report_sentence_level_eval(merged, setname, methodname):
    predicted_labels = merged['PredLabel'].values.tolist()
    predicted_probs =  merged['PredProb'].values.tolist()
    print('\tPercent of '+setname+' predicted labels that are 1(sick):',str( round(sum(predicted_labels)/len(predicted_labels),4) ))
    if setname=='train' or setname=='test':
        true_labels = merged['BinLabel'].values.tolist()
        print('\tPercent of '+setname+' true labels that are 1 (sick):',str( round(sum(true_labels)/len(true_labels),4) ))
        acc, auc, ap = calculate_eval_metrics(predicted_labels, predicted_probs, true_labels)
        print('\t', setname, methodname, 'Sentence Accuracy:', round(acc,4),
              '\n\t',setname, methodname, 'Sentence AUC:', round(auc,4),
              '\n\t', setname, methodname, 'Sentence Average Precision:', round(ap,4))

def calculate_eval_metrics(predicted_labels, predicted_probs, true_labels):
        """Report accuracy, AUC, and average precision"""
        correct_sum = (np.array(true_labels) == np.array(predicted_labels)).sum()
        acc = (float(correct_sum)/len(true_labels))
        fpr, tpr, thresholds = sklearn.metrics.roc_curve(y_true = true_labels,
                                         y_score = predicted_probs,
                                         pos_label = 1) #sick is 1; healthy is 0
        auc = sklearn.metrics.auc(fpr, tpr)
        ap = sklearn.metrics.average_precision_score(true_labels, predicted_probs)
        return acc, auc, ap

###########################################
# Overall Performance (After Term Search) #-------------------------------------
###########################################
class Perf(object):
    def __init__(self, true_labels, frequency_df, setname, results_dir):
        """Variables:
        <true_labels> is a dataframe where the index is filename and the
            columns are labels (e.g. pneumonia). It represents the ground truth
            for this data set.
        <frequency_df> is a dataframe defining frequency (count of each label)
            that will be used to calculate weighted mean and stdev.
        <setname> is a string that will be prepended to any saved files,
            e.g. 'train' or 'test'"""
        self.true_labels = true_labels #these are the ground truth labels
        self.frequency_df = frequency_df
        assert (setname=='train' or setname=='test')
        self.setname = setname
        self.results_dir = results_dir
    
    def update(self, out):
        """Log performance metrics for a method.
        
        Variables:
        <out> is a dataframe where the index is filenames and the columns are
            labels. <out> represents the model's predictions."""
        #Make sure index of true matches index of out. If reports are in the
        #wrong order then performance will be calculated incorrectly
        assert self.true_labels.index.values.tolist() == out.index.values.tolist()
        self.perf_df = pd.DataFrame(np.zeros((len(out.columns.values),11)), index = out.columns.values,
                                    columns=['FScore','Precision_Calc','Precision','Recall_Calc','Recall','Accuracy_Calc','Accuracy','TN','FP','FN','TP'])    
        for col in ['Precision_Calc','Recall_Calc','Accuracy_Calc']:
            self.perf_df[col]=''
        
        #Fill in the performance calculations for each label (each disease):
        for label in out.columns.values:
            predicted = out[label].values
            true = self.true_labels[label].values
            
            #Precision, recall, fscore
            precision, recall, fscore, _ = sklearn.metrics.precision_recall_fscore_support(y_true=true, y_pred=predicted, pos_label=1, average='binary')
            self.perf_df.at[label, 'Precision'] = precision
            self.perf_df.at[label, 'Recall'] = recall
            self.perf_df.at[label, 'FScore'] = fscore
            
            #Accuracy
            accuracy = float(np.sum(predicted==true))/len(true)
            self.perf_df.at[label, 'Accuracy'] = accuracy
            
            #Numerators and Denominators
            confusion_matrix = sklearn.metrics.confusion_matrix(y_true=true, y_pred=predicted)
            TN = confusion_matrix[0,0]
            #if all elements of <true> and <predicted> are 0, then we only have
            #TNs returned as a 1x1 confusion matrix
            if confusion_matrix.shape[0]==1:
                assert np.sum(true)==0
                assert np.sum(predicted)==0
                FP=0; FN=0; TP=0
            else: #we have a full confusion matrix
                FP = confusion_matrix[0,1]
                FN = confusion_matrix[1,0]
                TP = confusion_matrix[1,1]
            self.perf_df.at[label, 'TN'] = TN
            self.perf_df.at[label, 'FP'] = FP
            self.perf_df.at[label, 'FN'] = FN
            self.perf_df.at[label, 'TP'] = TP
            
            #Precision = (TP) / (TP+FP)
            #Recall = (TP) / (TP+FN)
            #Accuracy = (TP+TN)/(TP+TN+FP+FN)
            self.perf_df.at[label, 'Precision_Calc'] = '('+str(TP)+') / ('+str(TP)+'+'+str(FP)+')'
            self.perf_df.at[label, 'Recall_Calc'] ='('+str(TP)+') / ('+str(TP)+'+'+str(FN)+')'
            self.perf_df.at[label, 'Accuracy_Calc'] = '('+str(TP)+'+'+str(TN)+') / ('+str(TP)+'+'+str(TN)+'+'+str(FP)+'+'+str(FN)+')'
    
    def save_all_performance_metrics(self):
        """Save CSV of all performance metrics (with the frequency added)"""
        final = self.perf_df.merge(self.frequency_df,
                                    how = 'inner',
                                    left_index = True, right_index=True,
                                    validate = 'one_to_one')
        final = final.sort_values(by = 'Freq_'+self.setname, ascending=False)
        #final = add_mean_and_stdev(final, self.setname) #TODO adapt this function
        final.to_csv(os.path.join(self.results_dir,self.setname+'_Final_Performance.csv'), header=True, index=True)


# Using the Perf class #--------------------------------------------------------
def eval_on_report_level_ground_truth(dataset_descriptor, disease_out, results_dir):
    """Run disease-level evaluation on report-level ground truth if available.
    This function is called from term_search.py"""
    if dataset_descriptor not in ['duke_ct_2019_09_25','openi_cxr']:
        print('Comparison to ground truth NOT run because ground truth was NOT '\
              'available. See evaluation.py function '\
              'eval_on_report_level_ground_truth() to define a ground truth.')
    else:
        #Load the ground truth
        true_set_labels = load.load_ground_truth(dataset_descriptor)

        #Calculate the frequency_df
        frequency_df = pd.DataFrame((true_set_labels.sum(axis = 0)), columns = ['Freq_test']).sort_index()

        #Initialize performance tracking dfs
        allperf = evaluation.Perf(true_labels = true_set_labels,
                frequency_df = frequency_df, setname = 'test',
                results_dir = results_dir)
        
        #Compare predictions to ground truth
        print('***Comparing SARLE Predictions to Ground Truth***')
        #ensure index and columns are in a particular order
        disease_out_ordered = disease_out[true_set_labels.columns.values.tolist()]
        self.disease_out_ordered = self.disease_out_ordered.sort_index()
        self.allperf.update(out = self.disease_out_ordered)
        self.allperf.save_all_performance_metrics() #Save accuracy, precision, recall, and fscore
        self.report_test_set_mistakes() #Report all of the note-level model mistakes on the test set


# Additional Functions #--------------------------------------------------------
def add_mean_and_stdev(df, setname):
    """Return modified <df>:
    > Calculate weighted mean and weighted stdev and add those as rows
    
    <df> has an index of labels (e.g. pneumonia) and columns that are
    different performance metrics, as well as a frequency column."""
    freq_setname = 'Freq_'+setname
    assert (freq_setname=='Freq_test' or freq_setname=='Freq_train')
    #new_df = df[df[freq_setname]>50]
    
    #Add mean and stdev
    mean, stdev = calculate_weighted_mean_and_stdev(df, freq_setname)
    #For some reason now I have to first set them to zero before I can set them
    #to the calculated values...???
    df.loc['Mean',:] = 0; df.loc['StDev',:] = 0
    df.loc['Mean',:] = mean
    df.loc['StDev',:] = stdev
    return df

def calculate_weighted_mean_and_stdev(df, freq_setname):
    """Return the weighted mean and weighted stdev of the df.
    The weight is based on the test set frequency."""
    #Calculate regular mean and std for the frequencies themselves
    mean = np.zeros((1,df.shape[1]))
    stdev = np.zeros((1,df.shape[1]))
   
    #Calculate weighted mean and weighted std for the performance metric
    weights = df.loc[:,freq_setname].values / np.sum(df.loc[:,freq_setname].values)
    assert np.sum(weights)-1 < 10e-6 #weights should sum to 1
    
    def column_mean_stdev(colsetname, df, weights):
        #https://en.wikipedia.org/wiki/Weighted_arithmetic_mean#Weighted_sample_variance
        vals = df.loc[:,colsetname].values
        colmean = np.average(vals, weights = weights)
        colstd = np.sqrt(np.sum(np.multiply((vals - colmean)**2, weights)))
        return colmean, colstd
    
    for val in range(df.shape[1]):
        mean[0,val], stdev[0,val] = column_mean_stdev(colsetname = df.columns.values.tolist()[val],
                                df = df, weights = weights)
    return mean, stdev


##################
# Model Mistakes #--------------------------------------------------------------
##################

#FROM HERE HERE need to update these so they're not "self" (not methods of termsearch)


    def report_test_set_mistakes(self):
        """Report all note-level mistakes of all methods and save to a CSV"""
        summary_df = pd.DataFrame(np.empty((5,4),dtype='str'),
                                  columns=['Filename','sarle_Healthy_Sentences',
                                    'sarle_Sick_Sentences','sarle_Mistakes'])
        #Fill in the summary_df
        idx=0
        for fname in self.uniq_set_files:
            summary_df.at[idx,'Filename']=fname
            #Get the full text, which is contained in self.data
            summary_df.at[idx,'sarle_Healthy_Sentences'] = self.stringify(self.healthydf,fname)
            #Get the sick sentences, which is contained in self.sickdf
            summary_df.at[idx,'sarle_Sick_Sentences'] = self.stringify(self.sickdf,fname)
            #Get the mistakes
            summary_df.at[idx,'sarle_Mistakes'] = self.mistakes_as_string('sarle',fname,self.results_dir)
            idx+=1
        summary_df.to_csv(os.path.join(self.results_dir,'Test_Set_Mistakes_All_Methods.csv'))
    
    # Helper functions for report_test_set_mistakes() #----------------------------
    def stringify(self, df,filename):
        """Collapse all the entries of <df> corresponding to <filename>
        into a single string"""
        return '. '.join(((df[df['Filename']==filename])['Sentence']).values.tolist())
    
    def mistakes_as_string(self, method_name,filename,results_dir):
        """Format the model's mistakes on report specified by
        <filename> as a string, e.g.
        'pneumonia(true0,pred1),cardiomegaly(true1,pred0)'
        All of the dfs that this function uses have labels as columns and
        filenames as the index."""
        true = self.true_set_labels
        pred = self.disease_out_gt
        final_string = ''
        for label in true.columns.values:
            true_label = int(true.at[filename,label])
            pred_label = int(pred.at[filename,label])
            if true_label!=pred_label:
                final_string+=label+'(true'+str(true_label)+',pred'+str(pred_label)+'),'
        return final_string

