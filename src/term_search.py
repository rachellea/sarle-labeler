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

from src import load, evaluation
from src.vocab import vocabulary_ct, vocabulary_cxr, gr1cm

###################################
# Determine the note-level labels #---------------------------------------------
###################################
class RadLabel(object):
    def __init__(self, data, setname, dataset_descriptor, results_dir, 
                 run_locdis_checks, save_output_files=True):
        """Output for all methods: performance metrics files
        reporting label frequency, and performance of the different methods.
        
        Output for each method:
        pandas dataframe with note-level labels on the test set.
        Filename is the index and columns are different findings of interest.
        e.g. out.loc['12345.txt','atelectasis'] = 1 if note 12345.txt is
        positive for atelectasis (0 if negative for atelectasis.)
        Saved as files with prefix "Test_Set_Labels"
        
        Variables:
        <data> is a pandas dataframe produced by sentence_rules.py or
            sentence_classifier.py which contains the following columns:
            ['Count','Sentence','Filename','Section','PredLabel','PredProb']
            For the test and train sets it also contains these columns:
            ['Label', 'BinLabel'] which are the ground truth sentence labels
        <setname> is train' or 'test' or 'predict', a string that will be 
            prepended to any saved files,
        <dataset_descriptor>: string specifying the dataset. Used to determine
            handling of predict_set output files and if there is ground truth
            available 


            if there is ground truth available
        <results_dir>: path to directory in which results will be saved
        <run_locdis_checks>: bool. If True, run location x abnormality
            sanity checks to correct the output.
        <save_output_files> is True by default to ensure all output files
            are saved. It is only set to False within unit tests to avoid
            saving output files during unit testing."""
        self.dataset_descriptor = dataset_descriptor
        
        if self.dataset_descriptor == 'openi_cxr':
            self.vocabmodule = vocabulary_cxr
        elif self.dataset_descriptor in ['duke_ct_2019_09_25','duke_ct_2020_03_17']:
            self.vocabmodule = vocabulary_ct
        else:
            #for all other datasets, default to CT vocabulary
            self.vocabmodule = vocabulary_ct
        
        assert setname in ['train','test','predict']
        self.setname = setname
        self.results_dir = results_dir
        self.data = data

        self.run_locdis_checks = run_locdis_checks
        #Counts for tracking known mistakes in the locdis_checks
        self.wrong_lung_values = 0
        self.wrong_heart_values = 0
        self.wrong_vessel_values = 0
        
        #Run
        if not self.data.empty:
            self.run_all()
    
    def run_all(self):
        print('\nTerm search for',setname)

        #pad sentences with spaces to facilitate term search of words at 
        #the beginning and end of sentences
        self.data['Sentence'] = [' '+x+' ' for x in self.data['Sentence'].values.tolist()] 
        print('data shape',data.shape)
        if not self.run_locdis_checks:
            print('***WARNING: self.clean_up_forbidden_values() will be skipped to enable disease-ONLY prediction***')
        
        #Get unique list of filenames (used in multiple methods)
        self.uniq_set_files = [x for x in set(self.data['Filename'].values.tolist())]
        self.uniq_set_files.sort()

        #Separate out sick and healthy sentences
        self.sickdf, self.healthydf = self.pick_out_sick_sentences()

        #Initialize term dictionaries and keyterms
        self.initialize_vocabulary_dicts() 
        
        #Run SARLE term search step
        self.obtain_sarle_complex_labels()

        #Lung missingness calculation
        self.obtain_sarle_lung_missingness()

        #Obtain disease-only labels
        self.disease_out = self.binarize_complex_labels(chosen_labels=list(self.mega_disease_dict.keys()), label_type='disease')
        
       #Evaluate performance
        evaluation.eval_on_report_level_ground_truth(dataset_descriptor, self.disease_out, self.results_dir)

        #Save output
        if save_output_files: 
            self.save_complex_output_files()
    
        
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
    def obtain_sarle_complex_labels(self): #Done with testing
        """Generate location and disease labels
        Produces self.out_bin which is a dictionary where the keys are filenames
        (report IDs), and the values are binary pandas dataframes (since I don't
        think counts make sense in this context.) A single pandas dataframe is
        organized with disease as rows and locations as columns."""
        self.out_bin = {}
        if self.setname == 'train':            
            other_disease = open(os.path.join(self.results_dir,'train_other_disease_sentences.txt'),'a')
            other_location = open(os.path.join(self.results_dir,'train_other_location_sentences.txt'),'a')

        #Fill self.out with dataframes of predicted labels:
        for filename in self.uniq_set_files:
            #selected_out is for this filename only:
            selected_out = pd.DataFrame(np.zeros((len(list(self.mega_disease_dict.keys()))+1,
                                              len(list(self.mega_loc_dict.keys()))+1)),
                           columns = list(self.mega_loc_dict.keys())+['other_location'],
                           index = list(self.mega_disease_dict.keys())+['other_disease'])     
            selected_sickdf = self.sickdf[self.sickdf['Filename']==filename]
            for sentence in selected_sickdf['Sentence'].values.tolist():
                #the temp dfs, index is keyterms and column is 'SentenceValue'
                temp_location = self.return_temp_for_location_search(sentence)
                temp_disease = self.return_temp_for_disease_search(sentence)
                
                #iterate through locations first
                for location in temp_location.index.values.tolist():
                    if temp_location.at[location,'SentenceValue'] > 0:
                        #once you know the location, figure out the disease
                        location_recorded = False
                        for disease in temp_disease.index.values.tolist():
                            if temp_disease.at[disease,'SentenceValue'] > 0 :
                                selected_out.at[disease, location] = 1
                                location_recorded = True
                        if not location_recorded:
                            #makes sure every location gets recorded
                            selected_out.at['other_disease', location] = 1
                            if self.setname == 'train':
                                other_disease.write(location+'\t'+sentence+'\n')
                
                #iterate through disease second and make sure none were missed
                for disease in temp_disease.index.values.tolist():
                    if temp_disease.at[disease,'SentenceValue'] > 0:
                        if np.sum(selected_out.loc[disease,:].values) == 0:
                            #i.e. if we haven't recorded that disease yet,
                            selected_out.at[disease,'other_location'] = 1
                            if self.setname == 'train':
                                other_location.write(disease+'\t'+sentence+'\n')
            #Clean up
            if self.run_locdis_checks:
                selected_out = self.clean_up_forbidden_values(selected_out)
            #Save the labels for this patient (filename):
            self.out_bin[filename] = selected_out
        #The end
        self.report_corrected_forbidden_values()
    
    # Clean up based on forbidden values #--------------------------------------
    def clean_up_forbidden_values(self, selected_out):
        """Delete 'impossible' location-disease combinations ('impossible'
        according to medical knowledge, e.g. you cannot have an enlarged heart
        'in the lungs.')"""
        #Iterate throuh 
        for lung_disease in list(self.lung_disease_dict.keys()):
            for non_lung_loc in (list(self.heart_loc_dict.keys())+list(self.generic_loc_dict.keys())):
                if selected_out.at[lung_disease, non_lung_loc] == 1:
                    self.wrong_lung_values+=1
                    selected_out.at[lung_disease, non_lung_loc] = 0
        for heart_disease in list(self.heart_disease_dict.keys()):
            for non_heart_loc in (list(self.lung_loc_dict.keys())+list(self.generic_loc_dict.keys())):
                if selected_out.at[heart_disease, non_heart_loc] == 1:
                    self.wrong_heart_values+=1
                    selected_out.at[heart_disease, non_heart_loc] = 0
        
        #Now iterate through locations for prespecified 'forbidden diseases':
        selected_out, vessel_count = RadLabel.clean_forbidden_helper(self.vessel_loc_dict, self.vocabmodule.return_forbidden('great_vessel'), selected_out)
        self.wrong_vessel_values+=vessel_count
        
        selected_out, heart_count = RadLabel.clean_forbidden_helper(self.heart_loc_dict, self.vocabmodule.return_forbidden('heart'), selected_out)
        self.wrong_heart_values+=heart_count
        
        selected_out, lung_count = RadLabel.clean_forbidden_helper(self.lung_loc_dict, self.vocabmodule.return_forbidden('lung'), selected_out)
        self.wrong_lung_values+=lung_count
        return selected_out
    
    @staticmethod
    def clean_forbidden_helper(loc_dict, forbidden_disease, selected_out):
        """Return <selected_out> modified so that diseases in <forbidden_disease>
        is removed from locations in <loc_dict>. Also return a count of the
        number of mistakes fixed."""
        count = 0 
        for loc in list(loc_dict.keys()):
            for disease in forbidden_disease:
                if selected_out.at[disease, loc] == 1:
                    count+=1
                    selected_out.at[disease, loc] = 0
        return selected_out, count
    
    # Report total values for this set #----------------------------------------
    def report_corrected_forbidden_values(self):
        """Calculate how many individual labels are being produced for this set"""
        total_values = len(self.mega_disease_dict.keys())*len(self.mega_loc_dict.keys())*len(self.uniq_set_files)
        print(self.setname,'total values:',total_values)
        print('\tmega_disease_dict.keys():',len(self.mega_disease_dict.keys()))
        print('\tmega_loc_dict.keys():',len(self.mega_loc_dict.keys()))
        print('\tlen(uniq_set_files):',len(self.uniq_set_files))
        print('\ttotal:',total_values)
        print('wrong_lung_values (corrected):',self.wrong_lung_values,',',round(100*self.wrong_lung_values/total_values,2),'%')
        print('wrong_heart_values (corrected):',self.wrong_heart_values,',',round(100*self.wrong_heart_values/total_values,2),'%')
        print('wrong_vessel_values (corrected):',self.wrong_vessel_values,',',round(100*self.wrong_vessel_values/total_values,2),'%')
        
    # Initialize term dictionaries #--------------------------------------------
    def initialize_vocabulary_dicts(self):
        #Load dictionaries from self.vocabmodule.py
        self.lung_loc_dict, self.lung_disease_dict = self.vocabmodule.return_lung_terms()
        self.heart_loc_dict, self.heart_disease_dict = self.vocabmodule.return_heart_terms()
        self.vessel_loc_dict = self.vocabmodule.return_great_vessel_terms()
        self.generic_loc_dict, self.generic_disease_dict = self.vocabmodule.return_generic_terms()
        
        #Make super dicts:
        self.mega_loc_dict = self.aggregate_dicts([self.lung_loc_dict,
                        self.heart_loc_dict, self.vessel_loc_dict,self.generic_loc_dict])
        self.mega_disease_dict = self.aggregate_dicts([self.lung_disease_dict,
                        self.heart_disease_dict, self.generic_disease_dict])
        
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
        <disease_dict>, for the string <sentence>
        <body_region> is 'lung' or 'heart' or 'other.' Determines how/whether
            the disease_dict will be used here"""
        #temp is a dataframe for this particular sentence ONLY
        temp = pd.DataFrame(np.zeros((len(list(self.mega_loc_dict.keys())),1)),
                                        index = list(self.mega_loc_dict.keys()),
                                        columns = ['SentenceValue'])
        
        #look for location phrases
        for locterm in self.mega_loc_dict.keys():
            locterm_present = RadLabel.label_for_keyterm_and_sentence(locterm, sentence, self.mega_loc_dict)
            if locterm_present: #update out dataframe for specific lung location
                temp.at[locterm,'SentenceValue'] = 1
        
        #use location-specific diseases
        #Look for lung-specific diseases with right vs left
        right, left, lung = RadLabel.label_for_right_and_left_from_diseases(sentence, self.lung_disease_dict)
        if lung:
            temp.at['lung','SentenceValue'] = 1
        if right:
            temp.at['right_lung','SentenceValue'] = 1
        if left:
            temp.at['left_lung','SentenceValue'] = 1
        
        #Lung detailed--> general. If you have already decided something is in
        #the right_mid lobe, then right_lung and lung should be positive too.
        #(We need this step because the previous step using 'lung-specific
        #diseases with right vs left' applies ONLY to lung-specific diseases
        #and here we need to address generic diseases e.g. nodules.
        for right_lobe in ['right_upper','right_mid','right_lower']:
            if temp.at[right_lobe,'SentenceValue'] == 1:
                temp.at['right_lung','SentenceValue'] = 1
                temp.at['lung','SentenceValue'] = 1
        for left_lobe in ['left_upper','left_mid','left_lower']:
            if temp.at[left_lobe,'SentenceValue'] == 1:
                temp.at['left_lung','SentenceValue'] = 1
                temp.at['lung','SentenceValue'] = 1
        
        #Look for heart-specific diseases
        for diseaseterm in self.heart_disease_dict.keys():
            diseaseterm_present = RadLabel.label_for_keyterm_and_sentence(diseaseterm, sentence, self.heart_disease_dict)
            if diseaseterm_present:
                temp.at['heart','SentenceValue'] = 1
        return temp
    
    # Disease Helper Functions #------------------------------------------------
    def return_temp_for_disease_search(self, sentence):
        """Return a dataframe called <temp> which reports the results of
        the disease term search defined by <disease_dict> for the string <sentence>"""
        #temp is a dataframe for this particular sentence ONLY
        temp = pd.DataFrame(np.zeros((len(list(self.mega_disease_dict.keys())),1)),
                                        index = list(self.mega_disease_dict.keys()),
                                        columns = ['SentenceValue'])
        #Look for disease phrases
        for diseaseterm in self.mega_disease_dict.keys():
            diseaseterm_present = RadLabel.label_for_keyterm_and_sentence(diseaseterm, sentence, self.mega_disease_dict)
            if diseaseterm_present: #update out dataframe for specific lung location
                temp.at[diseaseterm,'SentenceValue'] = 1
        
        #Special lymphadenopathy and nodulegr1cm handling that uses measurements
        if 'lymphadenopathy' in self.mega_disease_dict.keys():
            if gr1cm.lymphadenopathy_handling(sentence) == 1:
                temp.at['lymphadenopathy','SentenceValue'] = 1
        if 'nodulegr1cm' in self.mega_disease_dict.keys():
            if gr1cm.nodulegr1cm_handling(sentence) == 1:
                temp.at['nodulegr1cm','SentenceValue'] = 1
        
        return temp
    
    # Lung Missingness #--------------------------------------------------------
    def obtain_sarle_lung_missingness(self):
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
        sickdf = copy.deepcopy(self.data)
        healthydf = copy.deepcopy(self.data)
        if self.dataset_descriptor == 'duke_ct_2019_09_25':
            sets_use_sentence_level_grtruth = ['train']
            sets_use_pred_sentence_labels = ['test','predict']
        elif self.dataset_descriptor == 'openi_cxr':
            #you have the sentence-level ground truth for the training set
            #so you might as well use it
            sets_use_sentence_level_grtruth = ['train']
            sets_use_pred_sentence_labels = ['test','predict']
        elif self.dataset_descriptor == 'duke_ct_2020_03_17':
            sets_use_sentence_level_grtruth = [] #no ground truth available 
            sets_use_pred_sentence_labels = ['train','test','predict']
        else:
            #assume a custom dataset in which there is no ground truth available
            #(same setting as for duke_ct_2020_03_17)
            sets_use_sentence_level_grtruth = [] #no ground truth available 
            sets_use_pred_sentence_labels = ['train','test','predict']
        
        if self.setname in sets_use_sentence_level_grtruth:
            print('Using ground truth sentence-level labels for',self.setname)
            #BinLabel is 1 or 0 based off of Label which is 's' or 'h'
            sickdf = sickdf[sickdf['BinLabel'] == 1]
            healthydf = healthydf[healthydf['BinLabel'] == 0]
        elif self.setname in sets_use_pred_sentence_labels:
            print('Using predicted sentence-level labels for',self.setname)
            sickdf = sickdf[sickdf['PredLabel'] == 1]
            healthydf = healthydf[healthydf['PredLabel'] == 0]
        sickdf = sickdf.reset_index(drop=True)
        healthydf = healthydf.reset_index(drop=True)
        assert (sickdf.shape[0]+healthydf.shape[0])==self.data.shape[0]
        print('Sickdf shape is',sickdf.shape)
        print('Healthydf shape is',healthydf.shape)
        return sickdf, healthydf
    
    def save_complex_output_files(self):
        """Save output files for location_and_disease
        out_bin is a dictionary of pandas dataframes and gets pickled"""
        if self.setname == 'train' or self.setname == 'test':
            self.basic_save()
        
        elif self.setname == 'predict':
            if self.dataset_descriptor not in ['duke_ct_2019_09_25','duke_ct_2020_03_17']:
                self.basic_save()
            else:
               #Custom predict set saving for Duke datasets
                def save_set(description, out_bin, disease_out, data, missing):
                    all_ids, available_accs = load.load_all_ids_and_accs(self.dataset_descriptor)
                    ids = all_ids[all_ids['Set_Assigned']==description]['Accession'].values.tolist()
                    ids = [x for x in ids if x in available_accs]
                    #Select out_bin filenames and save
                    out_bin = {}
                    for key in ids:
                        out_bin[key] = self.out_bin[key]
                    pickle.dump(out_bin, open(os.path.join(self.results_dir, description+'_BinaryLabels.pkl'), 'wb'))
                    #Select disease_out filenames and save
                    disease_out = disease_out.loc[ids,:]
                    disease_out.to_csv(os.path.join(self.results_dir, description+'_DiseaseBinaryLabels.csv'))
                    #Select data filenames and save
                    data = data[data['Filename'].isin(ids)]
                    data.to_csv(os.path.join(self.results_dir, description+'_Merged.csv'))
                    #Select missing filenames and save
                    missing = missing.loc[ids,:]
                    missing.to_csv(os.path.join(self.results_dir, description+'_Missingness.csv'))
                    return len(list(out_bin.keys())), data.shape[0]
                outshape = len(list(self.out_bin.keys())); datashape = self.data.shape[0]
                o1, m1 = save_set('imgtrain_extra', self.out_bin, self.disease_out, self.data, self.missing)
                o2, m2 = save_set('imgvalid', self.out_bin, self.disease_out, self.data, self.missing)
                o3, m3 = save_set('imgtest', self.out_bin, self.disease_out, self.data, self.missing)
                assert o1+o2+o3 == outshape
                assert m1+m2+m3 == datashape
        
    def basic_save(self):
        pickle.dump(self.out_bin, open(os.path.join(self.results_dir, 'imgtrain_note'+self.setname+'_BinaryLabels.pkl'), 'wb'))
        self.disease_out.to_csv(os.path.join(self.results_dir, 'imgtrain_note'+self.setname+'_DiseaseBinaryLabels.csv'))
        self.data.to_csv(os.path.join(self.results_dir, 'imgtrain_note'+self.setname+'_merged.csv'))
        self.missing.to_csv(os.path.join(self.results_dir, 'imgtrain_note'+self.setname+'_Missingness.csv'))
    
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
                    label = 0 #cannot write return 0 because that means the function doesn't return any value
        return label
    
    @staticmethod
    def label_for_right_and_left_from_diseases(sentence, lung_disease_dict):
        """Produce labels for right lung, left lung, and lungs overall based on
        lung-specific diseases terms"""
        right = 0; left = 0; lung = 0
        for diseaseterm in lung_disease_dict.keys():
            diseaseterm_present = RadLabel.label_for_keyterm_and_sentence(diseaseterm, sentence, lung_disease_dict)
            if diseaseterm_present == 1: #if you find any lung-specific diseases in the sentence
                lung = 1
                if 'right' in sentence: #e.g. "right pneumonia"
                    right = 1
                if ('left' in sentence) or ('lingula' in sentence):
                    left = 1
                break
        return right, left, lung
