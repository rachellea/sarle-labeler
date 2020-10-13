#term_search.py
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
import copy
import pickle
import pandas as pd
import numpy as np

import load
from evaluation import Perf, add_mean_and_stdev
from vocab import vocabulary_ct, vocabulary_cxr, gr1cm

import matplotlib
matplotlib.use('agg') #so that it does not attempt to display via SSH
import matplotlib.pyplot as plt
plt.ioff() #turn interactive plotting off
matplotlib.rcParams.update({'font.size': 18})

###################################
# Determine the note-level labels #---------------------------------------------
###################################
class RadLabel(object):
    def __init__(self, dataset, results_dir, setname, merged, testing=False):
        """Output for all methods: performance metrics files
        reporting label frequency, and performance of the different methods.
        
        Output for each method:
        pandas dataframe with note-level labels on the test set.
        Filname is the index and columns are different findings of interest.
        e.g. out.loc['12345.txt','atelectasis'] = 1 if note 12345.txt is
        positive for atelectasis (0 if negative for atelectasis.)
        Saved as files with prefix "Test_Set_Labels"
        
        Variables:
        <results_dir>: path to directory in which results will be saved
        <setname> is a string that will be prepended to any saved files,
            e.g. 'train' or 'test' or 'predict'
        <merged> is a pandas dataframe produced by sentence_classifier.py
            which contains the following columns:
            ['Count','Sentence','Filename','Section','PredLabel','PredProb']
            For the test and train sets it also contains these columns:
            ['Label', 'BinLabel'] which are the ground truth sentence labels"""
        self.dataset = dataset
        if self.dataset == 'duke_ct':
            self.vocabmodule = vocabulary_ct
        elif self.dataset == 'openi_cxr':
            self.vocabmodule = vocabulary_cxr
        assert setname in ['train','test','predict']
        self.setname = setname
        print('\nTerm search for',setname)
        self.results_dir = results_dir
        self.merged = merged
        self.merged['Sentence'] = [' '+x+' ' for x in self.merged['Sentence'].values.tolist()] #pad with spaces to facilitate term search of words at the beginning
        print('merged shape',merged.shape)
        
        #More initializations:
        if self.setname == 'test':
            self.load_ground_truth_and_perf_dfs()#Load ground truth for disease-level labels
        self.uniq_set_files = [x for x in set(self.merged['Filename'].values.tolist())]
        self.uniq_set_files.sort()
        self.sickdf, self.healthydf = self.pick_out_sick_sentences() #Pick out sick sentences
        self.initialize_vocabulary_dicts() #Initialize term dictionaries and keyterms
        
        #Run and save output:
        self.obtain_safra_complex_labels() #predict with Safra
        self.obtain_safra_lung_missingness() #missingness
        self.disease_out = self.binarize_complex_labels(chosen_labels=list(self.mega_path_dict.keys()), label_type='disease')
        if not testing: self.save_complex_output_files()
        
        #Evaluate and save output if indicated:
        if self.setname == 'test':
            print('***Comparing Safra to True***') #evaluate on disease-level ground truth
            self.disease_out_gt = self.binarize_complex_labels(chosen_labels=self.true_set_labels.columns.values, label_type='disease')
            self.disease_out_gt = self.disease_out_gt.sort_index()
            self.allperf.update(out = self.disease_out_gt)
            self.allperf.save_all_performance_metrics() #Save accuracy, precision, recall, and fscore
            self.report_test_set_mistakes() #Report all of the note-level model mistakes on the test set
    
    #Load ground truth and dataframes for tracking performance #----------------
    def load_ground_truth_and_perf_dfs(self):
        """Load the ground truth labels, calculate the frequency df, and
        initialize the performance tracking dataframes"""
        self.true_set_labels = load.load_ground_truth(self.dataset)
        self.frequency_df = pd.DataFrame((self.true_set_labels.sum(axis = 0)), columns = ['Freq_'+self.setname]).sort_index()
        #Initialize evaluation dfs
        self.allperf = Perf(true_labels = self.true_set_labels,
                frequency_df = self.frequency_df, setname = self.setname,
                results_dir = self.results_dir)
        
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
    
    #############################
    # Predict Note-Level Labels #-----------------------------------------------
    #############################
    def obtain_safra_complex_labels(self): #Done with testing
        """Generate location and path labels
        Produces self.out_bin which is a dictionary where the keys are filenames
        (report IDs), and the values are binary pandas dataframes (since I don't
        think counts make sense in this context.) A single pandas dataframe is
        organized with path as rows and locations as columns."""
        self.out_bin = {}
        if self.setname == 'train':            
            other_path = open(os.path.join(self.results_dir,'train_other_path_sentences.txt'),'a')
            other_location = open(os.path.join(self.results_dir,'train_other_location_sentences.txt'),'a')

        #Fill self.out with dataframes of predicted labels:
        for filename in self.uniq_set_files:
            #selected_out is for this filename only:
            selected_out = pd.DataFrame(np.zeros((len(list(self.mega_path_dict.keys()))+1,
                                              len(list(self.mega_loc_dict.keys()))+1)),
                           columns = list(self.mega_loc_dict.keys())+['other_location'],
                           index = list(self.mega_path_dict.keys())+['other_path'])     
            selected_sickdf = self.sickdf[self.sickdf['Filename']==filename]
            for sentence in selected_sickdf['Sentence'].values.tolist():
                #the temp dfs, index is keyterms and column is 'SentenceValue'
                temp_location = self.return_temp_for_location_search(sentence)
                temp_path = self.return_temp_for_path_search(sentence)
                
                #iterate through locations first
                for location in temp_location.index.values.tolist():
                    if temp_location.at[location,'SentenceValue'] > 0:
                        #once you know the location, figure out the path
                        location_recorded = False
                        for path in temp_path.index.values.tolist():
                            if temp_path.at[path,'SentenceValue'] > 0 :
                                selected_out.at[path, location] = 1
                                location_recorded = True
                        if not location_recorded:
                            #makes sure every location gets recorded
                            selected_out.at['other_path', location] = 1
                            if self.setname == 'train':
                                other_path.write(location+'\t'+sentence+'\n')
                
                #iterate through path second and make sure none were missed
                for path in temp_path.index.values.tolist():
                    if temp_path.at[path,'SentenceValue'] > 0:
                        if np.sum(selected_out.loc[path,:].values) == 0:
                            #i.e. if we haven't recorded that path yet,
                            selected_out.at[path,'other_location'] = 1
                            if self.setname == 'train':
                                other_location.write(path+'\t'+sentence+'\n')
            #Save the labels for this patient (filename):
            self.out_bin[filename] = selected_out
    
    # Initialize term dictionaries #--------------------------------------------
    def initialize_vocabulary_dicts(self):
        #Load dictionaries from self.vocabmodule.py
        self.lung_loc_dict, self.lung_path_dict = self.vocabmodule.return_lung_terms()
        self.heart_path_dict = self.vocabmodule.return_heart_terms()
        self.generic_path_dict = self.vocabmodule.return_generic_terms()
        
        #Make super dicts:
        self.mega_loc_dict = self.lung_loc_dict
        self.mega_path_dict = self.aggregate_dicts([self.lung_path_dict,
                        self.heart_path_dict, self.generic_path_dict])
        
    def aggregate_dicts(self, dicts):
        super_dict = {}
        keylens = 0
        for d in dicts:
            keylens+=len(list(d.keys()))
            for k, v in d.items():
                super_dict[k] = v
        assert len(list(super_dict.keys())) == keylens
        return super_dict
    
    # Location Helper Functions #----------------------------------------------
    def return_temp_for_location_search(self, sentence):
        """Return a dataframe called <temp> which reports the results of
        the location term search using rules defined by <loc_dict> and
        <path_dict>, for the string <sentence>"""
        #temp is a dataframe for this particular sentence ONLY
        temp = pd.DataFrame(np.zeros((len(list(self.mega_loc_dict.keys())),1)),
                                        index = list(self.mega_loc_dict.keys()),
                                        columns = ['SentenceValue'])
        
        #look for location phrases
        for locterm in self.mega_loc_dict.keys():
            locterm_present = RadLabel.label_for_keyterm_and_sentence(locterm, sentence, self.mega_loc_dict)
            if locterm_present: #update out dataframe for specific lung location
                temp.at[locterm,'SentenceValue'] = 1
        
        #use location-specific pathology
        #Look for lung-specific pathology with right vs left
        right, left, lung = RadLabel.label_for_right_and_left_from_pathology(sentence, self.lung_path_dict)
        if lung:
            temp.at['lung','SentenceValue'] = 1
        if right:
            temp.at['right_lung','SentenceValue'] = 1
        if left:
            temp.at['left_lung','SentenceValue'] = 1
        
        #Lung detailed--> general. If you have already decided something is in
        #the right_mid lobe, then right_lung and lung should be positive too.
        #(We need this step because the previous step using 'lung-specific
        #pathology with right vs left' applies ONLY to lung-specific pathology
        #and here we need to address generic pathology e.g. nodules.
        for right_lobe in ['right_upper','right_mid','right_lower']:
            if temp.at[right_lobe,'SentenceValue'] == 1:
                temp.at['right_lung','SentenceValue'] = 1
                temp.at['lung','SentenceValue'] = 1
        for left_lobe in ['left_upper','left_mid','left_lower']:
            if temp.at[left_lobe,'SentenceValue'] == 1:
                temp.at['left_lung','SentenceValue'] = 1
                temp.at['lung','SentenceValue'] = 1
        
        return temp
    
    # Path Helper Functions #------------------------------------------------
    def return_temp_for_path_search(self, sentence):
        """Return a dataframe called <temp> which reports the results of
        the path term search defined by <path_dict> for the string <sentence>"""
        #temp is a dataframe for this particular sentence ONLY
        temp = pd.DataFrame(np.zeros((len(list(self.mega_path_dict.keys())),1)),
                                        index = list(self.mega_path_dict.keys()),
                                        columns = ['SentenceValue'])
        #Look for path phrases
        for pathterm in self.mega_path_dict.keys():
            pathterm_present = RadLabel.label_for_keyterm_and_sentence(pathterm, sentence, self.mega_path_dict)
            if pathterm_present: #update out dataframe for specific lung location
                temp.at[pathterm,'SentenceValue'] = 1
        
        #Special lymphadenopathy and nodulegr1cm handling that uses measurements
        if self.dataset == 'duke_ct':
            if gr1cm.lymphadenopathy_handling(sentence) == 1:
                temp.at['lymphadenopathy','SentenceValue'] = 1
            if gr1cm.nodulegr1cm_handling(sentence) == 1:
                temp.at['nodulegr1cm','SentenceValue'] = 1
        
        return temp
    
    # Lung Missingness #--------------------------------------------------------
    def obtain_safra_lung_missingness(self):
        """Obtain a missingness indicator for each lobe of the lung as well
        as each lung, based on the previously created labels.
        e.g. if lung = 1 but both right_lung and left_lung are 0, we know
        right_lung and left_lung are missing.
        if right_lung = 1 but all of the right lobes are 0, we know
        all of the right lobes are missing.
        NOTE: If a label is missing, the value is ZERO. If a label is present,
        the value is ONE"""
        print('Working on missingness estimation')
        #First, get a binary representation of the lung location predictions:
        lung_bin = self.binarize_complex_labels(chosen_labels = list(self.lung_loc_dict.keys()), label_type='location')
        
        #Initialize and fill in missingness df:
        cols = ['left_lobes_all','right_lobes_all','lungs_right_left']
        missing = pd.DataFrame(np.ones((len(self.uniq_set_files), len(cols))),
                    index = self.uniq_set_files, columns = cols)
        for filename in missing.index.values.tolist():
            if ((lung_bin.at[filename,'lung']==1)
                and (lung_bin.at[filename,'right_lung']==0)
                and (lung_bin.at[filename,'left_lung']==0)):
                missing.at[filename,'lungs_right_left'] = 0
            if ((lung_bin.at[filename,'right_lung']==1)
                and (lung_bin.at[filename,'right_lower']==0)
                and (lung_bin.at[filename,'right_upper']==0)
                and (lung_bin.at[filename,'right_mid']==0)):
                missing.at[filename,'right_lobes_all'] = 0
            if ((lung_bin.at[filename,'left_lung']==1)
                and (lung_bin.at[filename,'left_lower']==0)
                and (lung_bin.at[filename,'left_upper']==0)
                and (lung_bin.at[filename,'left_mid']==0)):
                missing.at[filename,'left_lobes_all'] = 0
        self.missing = missing
    
    # General Helper Functions #------------------------------------------------
    def pick_out_sick_sentences(self):
        """Separate sick sentences and healthy sentences and return
        as separate dataframes"""
        sickdf = copy.deepcopy(self.merged)
        healthydf = copy.deepcopy(self.merged)
        if self.dataset == 'duke_ct':
            sets_use_grtruth = []
            sets_use_pred = ['train','test','predict']
        elif self.dataset == 'openi_cxr':
            #you have the sentence-level ground truth for the training set
            #so you might as well use it
            sets_use_grtruth = ['train']
            sets_use_pred = ['test','predict']
        if self.setname in sets_use_grtruth:
            print('Using ground truth sentence-level labels for',self.setname)
            #BinLabel is 1 or 0 based off of Label which is 's' or 'h'
            sickdf = sickdf[sickdf['BinLabel'] == 1]
            healthydf = healthydf[healthydf['BinLabel'] == 0]
        elif self.setname in sets_use_pred:
            print('Using predicted sentence-level labels for',self.setname)
            sickdf = sickdf[sickdf['PredLabel'] == 1]
            healthydf = healthydf[healthydf['PredLabel'] == 0]
        sickdf = sickdf.reset_index(drop=True)
        healthydf = healthydf.reset_index(drop=True)
        assert (sickdf.shape[0]+healthydf.shape[0])==self.merged.shape[0]
        print('Sickdf shape is',sickdf.shape)
        print('Healthydf shape is',healthydf.shape)
        return sickdf, healthydf
    
    def save_complex_output_files(self):
        """Save output files for location_and_path
        out_bin is a dictionary of pandas dataframes and gets pickled"""
        if self.setname == 'train' or self.setname == 'test':
            self.disease_out.to_csv(os.path.join(self.results_dir, 'imgtrain_note'+self.setname+'_DiseaseBinaryLabels.csv'))
            self.merged.to_csv(os.path.join(self.results_dir, 'imgtrain_note'+self.setname+'_Merged.csv'))
            self.missing.to_csv(os.path.join(self.results_dir, 'imgtrain_note'+self.setname+'_Missingness.csv'))
        elif self.setname == 'predict':
            def save_set(description, out_bin, disease_out, merged, missing):
                all_ids, available_accs = load.load_all_ids_and_accs()
                ids = all_ids[all_ids['Set_Assigned']==description]['Accession'].values.tolist()
                ids = [x for x in ids if x in available_accs]
                #Select out_bin filenames and save
                out_bin = {}
                for key in ids:
                    out_bin[key] = self.out_bin[key]
                #Select disease_out filenames and save
                disease_out = disease_out.loc[ids,:]
                disease_out.to_csv(os.path.join(self.results_dir, description+'_DiseaseBinaryLabels.csv'))
                #Select merged filenames and save
                merged = merged[merged['Filename'].isin(ids)]
                merged.to_csv(os.path.join(self.results_dir, description+'_Merged.csv'))
                #Select missing filenames and save
                missing = missing.loc[ids,:]
                missing.to_csv(os.path.join(self.results_dir, description+'_Missingness.csv'))
                return len(list(out_bin.keys())), merged.shape[0]
            outshape = len(list(self.out_bin.keys())); mergedshape = self.merged.shape[0]
            o1, m1 = save_set('imgtrain_extra', self.out_bin, self.disease_out, self.merged, self.missing)
            o2, m2 = save_set('imgvalid', self.out_bin, self.disease_out, self.merged, self.missing)
            o3, m3 = save_set('imgtest', self.out_bin, self.disease_out, self.merged, self.missing)
            assert o1+o2+o3 == outshape
            assert m1+m2+m3 == mergedshape
    
    ##################
    # Model Mistakes #----------------------------------------------------------
    ##################
    def report_test_set_mistakes(self):
        """Report all note-level mistakes of all methods and save to a CSV"""
        summary_df = pd.DataFrame(np.empty((5,4),dtype='str'),
                                  columns=['Filename','Safra_Healthy_Sentences',
                                    'Safra_Sick_Sentences','Safra_Mistakes'])
        #Fill in the summary_df
        idx=0
        for fname in self.uniq_set_files:
            summary_df.at[idx,'Filename']=fname
            #Get the full text, which is contained in self.merged
            summary_df.at[idx,'Safra_Healthy_Sentences'] = self.stringify(self.healthydf,fname)
            #Get the sick sentences, which is contained in self.sickdf
            summary_df.at[idx,'Safra_Sick_Sentences'] = self.stringify(self.sickdf,fname)
            #Get the mistakes
            summary_df.at[idx,'Safra_Mistakes'] = self.mistakes_as_string('Safra',fname,self.results_dir)
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

    ##################
    # Static Methods #----------------------------------------------------------
    ##################
    @staticmethod
    def label_for_keyterm_and_sentence(keyterm, sentence, termdict):
        """Return label = 1 if <keyterm> in <sentence> else return label = 0"""
        sentence = ' ' + sentence + ' '
        label = 0
        for any_term in termdict[keyterm]['Any']:
            if any_term in sentence:
                label = 1
        if label == 0: #if label is still 0 check for secondary equivalent terms
            if 'Term1' in termdict[keyterm].keys():
                for term1 in termdict[keyterm]['Term1']:
                    for term2 in termdict[keyterm]['Term2']:
                        if (term1 in sentence) and (term2 in sentence):
                            label = 1
                            break
        #Dealing with 'Exclude'
        if 'Exclude' in termdict[keyterm].keys():
            for banned_term in termdict[keyterm]['Exclude']:
                if banned_term in sentence:
                    return 0
        return label
    
    @staticmethod
    def label_for_right_and_left_from_pathology(sentence, lung_path_dict):
        """Produce labels for right lung, left lung, and lungs overall based on
        lung-specific pathology terms"""
        right = 0; left = 0; lung = 0
        for pathterm in lung_path_dict.keys():
            pathterm_present = RadLabel.label_for_keyterm_and_sentence(pathterm, sentence, lung_path_dict)
            if pathterm_present == 1: #if you find any lung-specific pathology in the sentence
                lung = 1
                if 'right' in sentence: #e.g. "right pneumonia"
                    right = 1
                if ('left' in sentence) or ('lingula' in sentence):
                    left = 1
                break
        return right, left, lung
