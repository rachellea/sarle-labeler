#load.py
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
import re
import copy
import string
import numpy as np
import pandas as pd

from src.rules import rule_functions

#Note that os.getcwd() yields the directory containing main.py, assuming that
#main.py was used to call this script. Example:
#C:\Users\Rachel\Documents\CarinLab\Project_CT\Code\hiermodel2

"""Format of files that are loaded and then merged:
    <count_label_sent>: path to a CSV with columns Count, Label, and
        Sentence. Count is an integer describing how many times that
        sentence is repeated in the data set. Label is the manually-generated
        label, 's' for sick and 'h' for healthy. Sentence is a report
        sentence.
    <filename_section_sent>: path to a CSV with columns Filename,
        Section, Sentence. Filename is a unique identifier for a report,
        e.g. the name of a file, or a custom ID. Section is 'Findings'
        or 'Impression' and indicates which section of the report the
        sentence came from. Sentence is the report sentence."""

#####################
# Primary Functions #-----------------------------------------------------------
# ###################
def load_merged_with_style(dataset_descriptor, style):
    """Load the merged dataframe for all the splits and then filter them
    based on style.
    
    <dataset_descriptor> can be one of the following strings:
        'duke_ct_2019_09_25': Duke CT reports, parsed into sentences on
            2019-09-25. The indications and report header are excluded. Some
            actual report sentences were also (rarely) excluded due to
            challenges in parsing heterogeneous reports.
            This version of the Duke CT reports was used for the paper
            'Machine-Learning-Based Multiple Abnormality Prediction with
            Large-Scale Chest Computed Tomography Volumes' by Draelos et al.
            Report-level ground truth was also prepared for this dataset.
        'duke_ct_2020_03_17': Duke CT reports, parsed into sentences on
            2020-03-17. All sentences were preserved, including the
            indications and report header. This led to challenges in dealing
            with indications, which sometimes have a disease concept in them
            without indicating that the patient actually has this disease.
            The function split_indication_sentence() below includes logic
            to try to exclude potentially misleading indication sentence
            fragments.
            Report-level ground truth is NOT currently available for this
            dataset, although someday it could be derived relatively easily
            from the ground truth for 'duke_ct_2019_09_25' by updating
            this old ground truth to take into account the newly-included
            sentences.
        'openi_cxr': the publicly available OpenI chest x-ray report data set,
            put into the required format for SARLE.
            Report-level ground truth is available for this dataset."""
    assert dataset_descriptor in ['duke_ct_2019_09_25','duke_ct_2020_03_17','openi_cxr']
    if dataset_descriptor in ['duke_ct_2019_09_25','duke_ct_2020_03_17']:
        train_merged, test_merged, predict_merged = load_data_duke_ct(dataset_descriptor)
    elif dataset_descriptor == 'openi_cxr':
        train_merged, test_merged, predict_merged = load_data_openi_cxr()
     
    if style == 'trainall_testall':
        #Keep everything the way it is
        pass
    elif style in ['trainfilt_testfilt','trainall_testfilt']:
        if style == 'trainfilt_testfilt':
            #Remove duplicates from training set:
            print('\tdropping train duplicates.\n\t\ttrainshape before:',train_merged.shape)
            train_merged.drop_duplicates(subset='Sentence',keep='first',inplace=True)
            print('\t\ttrainshape after:',train_merged.shape)
        #Remove duplicates from test set:
        print('\tdropping test duplicates.\n\t\ttest shape before:',test_merged.shape)
        test_merged.drop_duplicates(subset='Sentence',keep='first',inplace=True)
        print('\t\ttest shape after:',test_merged.shape)
        #Remove overlapping sentences from test set:
        train_sentences = train_merged['Sentence'].values.tolist()
        for index in test_merged.index.values.tolist():
            if test_merged.at[index,'Sentence'] in train_sentences:
                test_merged.drop(index=index, inplace=True)
        print('\t\ttest shape after removing overlap with train set:',test_merged.shape)
    return train_merged, test_merged, predict_merged

def load_ground_truth(dataset_descriptor):
    assert dataset_descriptor in ['duke_ct_2019_09_25','duke_ct_2020_03_17','openi_cxr']
    if dataset_descriptor == 'duke_ct_2019_09_25':
        return load_groundtruth_duke_ct_2019_09_25()
    elif dataset_descriptor == 'duke_ct_2020_03_17':
        #No ground truth is available for 2020-03-17 data
        #(more sentences are included in 2020-03-17 relative to 2019-09-25 due
        #to including the indications/report header)
        return None
    elif dataset_descriptor == 'openi_cxr':
        return load_groundtruth_openi_cxr()

#########################
# Load Duke CT Data Set #-------------------------------------------------------
#########################
def load_data_duke_ct(dataset_descriptor):
    if dataset_descriptor == 'duke_ct_2019_09_25':
        data_dir = os.path.join(*[os.getcwd(),'data','data_ct','split_2019-09-25'])
    elif dataset_descriptor == 'duke_ct_2020_03_17':
        data_dir = os.path.join(*[os.getcwd(),'data','data_ct','split_2020-03-17'])
    train_merged = load_one_duke_ct('train', ['imgtrain_notetrain'], data_dir)
    test_merged = load_one_duke_ct('test', ['imgtrain_notetest'], data_dir)
    predict_merged = load_one_duke_ct('predict', ['imgtrain_extra','imgvalid', 'imgtest'], data_dir)
    return train_merged, test_merged, predict_merged

def load_all_ids_and_accs(dataset_descriptor):
    #used in term_search.py function save_complex_output_files()
    if dataset_descriptor == 'duke_ct_2019_09_25':
        all_ids_path = os.path.join(*[os.getcwd(),'data','data_ct','split_2019-09-25','all_identifiers.csv'])
    elif dataset_descriptor == 'duke_ct_2020_03_17':
        all_ids_path = os.path.join(*[os.getcwd(),'data','data_ct','split_2020-03-17','all_identifiers.csv'])
    all_ids = pd.read_csv(all_ids_path,header=0,index_col=False)
    
    available_accs = (pd.read_csv(os.path.join(*['data','data_ct','Available_Volumes.csv']),header=0))['Accession'].values.tolist()
    
    return all_ids, available_accs

def load_one_duke_ct(setname, files, data_dir):
    """Merge the FSS and CLS files specified by prefixes <files> and
    return one merged df."""
    print('Loading for',setname,'from',files)
    cls = pd.read_csv(os.path.join(data_dir,
            files[0]+'_count_label_sent.csv'),header=0, index_col = False)
    fss = pd.read_csv(os.path.join(data_dir,
            files[0]+'_filename_section_sent.csv'),header=0, index_col = False)
    merged = cls.merge(fss, on = 'Sentence')
    if len(files)>1:
        for prefix in files[1:]:
            cls_temp = pd.read_csv(os.path.join(data_dir,
                               prefix+'_count_label_sent.csv'),
                               header=0, index_col = False)
            fss_temp = pd.read_csv(os.path.join(data_dir,
                               prefix+'_filename_section_sent.csv'),
                               header=0, index_col = False)
            merged_temp = cls_temp.merge(fss_temp, on = 'Sentence')
           
            #Update. Must obtain unique consecutive numerical index
            fss = pd.concat([fss, fss_temp],axis=0,ignore_index=True)
            merged = pd.concat([merged, merged_temp],axis=0,ignore_index=True)
    merged = clean_merged(merged,setname)
    assert merged.shape[0]==fss.shape[0]
    print('\traw '+setname+' merged shape',merged.shape)
    merged = filter_merged_by_available_ct(merged)
    print('\tfiltered '+setname+' merged shape (only success volumes)',merged.shape)
    print('\tfiltered '+setname+' merged # filenames (only success volumes)',len(set(merged['Filename'].values.tolist())))
    merged = expand_by_indication(merged)
    print('\texpanded by indication '+setname+' merged shape',merged.shape)
    return merged

def filter_merged_by_available_ct(merged):
    """Return the <merged> dataframe including only the rows where Filename
    (accession number) is included in Available_Volumes.csv"""
    available_volumes = pd.read_csv(os.path.join(*['data','data_ct','Available_Volumes.csv']),header=0)
    merged = merged[merged['Filename'].isin(available_volumes['Accession'].values.tolist())]
    return merged

def load_groundtruth_duke_ct_2019_09_25():
    """Return the loaded ground truth file"""
    true_set_labels_path = os.path.join(*['data','groundtruth_ct','split_2019-09-25','ground_truth_filled.csv'])
    true_set_labels = pd.read_csv(true_set_labels_path, header=0, index_col=0)
    print('ground truth total reports raw',true_set_labels.shape[0])
    available_accs_path = os.path.join(*['data','data_ct','Available_Volumes.csv'])
    available_accs = (pd.read_csv(available_accs_path,header=0))['Accession'].values.tolist()
    true_set_labels = true_set_labels[true_set_labels.index.isin(available_accs)]
    print('ground truth total reports (available volumes only)',true_set_labels.shape[0])   
    true_set_labels = true_set_labels.sort_index() 
    true_set_labels = true_set_labels[['consolidation_Label',
                'mass_Label', 'nodule_Label', 'opacity_Label',
                'pericardial_effusion_Label', 'pleural_effusion_Label',
                'atelectasis_Label','cardiomegaly_Label','pneumothorax_Label']]
    true_set_labels.columns = true_set_labels.columns.str.replace('_Label','')
    return true_set_labels

def expand_by_indication(merged): #Done with testing
    """For each sentence that includes the word 'indication' replace it with
    multiple sentences based on splitting up the giant indication text blocks"""
    non_ind = merged[~merged['Sentence'].str.contains('indication')]
    old_ind = merged[merged['Sentence'].str.contains('indication')]
    assert non_ind.shape[0]+old_ind.shape[0]==merged.shape[0]
    #make new dataframe for the indications
    new_ind = pd.DataFrame(np.empty((old_ind.shape[0]*20,old_ind.shape[1])),
                           columns=old_ind.columns.values.tolist(),
                           dtype = 'object')
    newidx = 0
    for oldidx in old_ind.index.values.tolist():
        label = old_ind.at[oldidx,'Label']
        sentence = old_ind.at[oldidx,'Sentence']
        filename = old_ind.at[oldidx,'Filename']
        section = old_ind.at[oldidx,'Section']
        if 'BinLabel' in old_ind.columns.values.tolist():
            binlabel = old_ind.at[oldidx,'BinLabel']
        for subsent in split_indication_sentence(sentence):
            new_ind.at[newidx,'Label'] = label
            new_ind.at[newidx,'Sentence'] = subsent
            new_ind.at[newidx,'Filename'] = filename
            new_ind.at[newidx,'Section'] = section
            if 'BinLabel' in old_ind.columns.values.tolist():
                new_ind.at[newidx,'BinLabel'] = binlabel
            newidx+=1
    new_ind = new_ind[new_ind['Section'].isin(['Findings','Impression'])]
    new_merged = pd.concat([non_ind, new_ind],axis=0,ignore_index=True)
    assert new_merged.shape[0]==non_ind.shape[0]+new_ind.shape[0]
    assert new_merged.shape[0]>merged.shape[0]
    return new_merged

def split_indication_sentence(sentence):
    """Handle the huge 'sentences' that include the indication, e.g.
    'rpt ct chest wo contrast w 3d mips protocol date %date facility
    duh chest ct without contrast indication 401.9 unspecified essential
    hypertension 272.4 other and unspecified hyperlipidemia 424.1 aortic
    valve disorders 414.00 coronary atherosclerosis of unspecified type of
    vessel native or graft 428.22 chronic systolic heart failure 453.40
    acute venous embolism and thrombosis of unspecified deep vessels of
    lower extremity 416.8 other chronic pulmonary heart diseases 585.9
    chronic kidney diseas comparison none available protocol volumetric
    non contrast chest ct was performed from the lower neck through the
    adrenal glands'
    """
    x = sentence
    for word in ['comparison','compare','protocol','technique','indication',
                 'history of','history','facility duh','facility',' f u ',
                 'follow up']:
        x = x.replace(word,'.') #so that we will split on all these words too
    for word in ['%date','date','%time']:
        x = x.replace(word,'')
    x = x.split('.')
    x = [re.sub('\d','',z).strip() for z in x]
    x = [z for z in x if len(z)>1]
    x = [' '.join(z.split()) for z in x]
    
    #clean up sentences
    temp = []
    for sent in x:
        for word in ['evaluation for','evaluate for',' eval for','assess','preop',
                 'prior to','pre surgery','pre op','rule out',
                 'surgical planning','workup for','plans for']:
            _, sent = rule_functions.delete_part(sent, 'after', word)
        temp.append(sent)
    
    plagues = ['rpt ct chest wo contrast w d mips',
        'ct chest without contrast',
        'volumetric non contrast chest ct acquisition was performed from the lower neck to the adrenal glands',
        'ct chest','none','ct chest without contrast d','chest ct',
        'mm axial images with mm reconstructions were obtained from the neck base through the upper abdomen without iv contrast material',
        'ct d','ct chest without contrast with d mips',
        'ct chest without intravenous contrast','exams chest ct d',
        's for the examination','multiple prior ct examinations with the most recent',
        'ct chest d','chest ct without contrast']
    temp2 = []
    for sent in temp:
        if sent not in plagues:
            temp2.append(sent)
    return temp2

#######################
# Load OpenI Data Set #---------------------------------------------------------
#######################
def load_data_openi_cxr():
    print('Loading OpenI CXR data set')
    data_dir = os.path.join(*[os.getcwd(),'data','data_cxr'])
    all_fss = pd.read_csv(os.path.join(data_dir,'openi_filename_section_sent.csv'),header=0)
    all_cls = pd.read_csv(os.path.join(data_dir,'openi_count_label_sent.csv'),header=0)
    all_merged = all_cls.merge(all_fss, on = 'Sentence')
    
    train_ids = pd.read_csv(os.path.join(data_dir,'openi_train_filenames.csv'),header=None,names=['train'])
    train = copy.deepcopy(all_merged[all_merged['Filename'].isin(train_ids.loc[:,'train'].values.tolist())])
    #Clean sentences (CXR sentences are not by default clean)
    train['Sentence'] = [full_clean_cxr(x) for x in train['Sentence']] 
    print('shape of train',train.shape,'with',train_ids.shape[0],'filenames')
    
    test_ids = pd.read_csv(os.path.join(data_dir,'openi_test_filenames.csv'),header=None,names=['test'])
    test = copy.deepcopy(all_merged[all_merged['Filename'].isin(test_ids.loc[:,'test'].values.tolist())])
    #Clean sentences (CXR sentences are not by default clean)
    test['Sentence'] = [full_clean_cxr(x) for x in test['Sentence']]
    print('shape of test',test.shape,'with',test_ids.shape[0],'filenames')
    
    assert all_merged.shape[0]==(train.shape[0]+test.shape[0])
    
    train_merged = clean_merged(train,'train')
    test_merged = clean_merged(test,'test')
    predict_merged = pd.DataFrame() #empty dataframe as there is no predict set here
    return train_merged, test_merged, predict_merged
    
def load_groundtruth_openi_cxr():
    true_set_labels_path = os.path.join(*['data','data_cxr','openi_test_set_ground_truth.csv'])
    true_set_labels = pd.read_csv(true_set_labels_path,header=0,index_col=0)
    true_set_labels.columns = true_set_labels.columns.str.replace('_Label','')
    return true_set_labels

def full_clean_cxr(sentence):
    """Removes whitespace from beginning and end of a sentence. Lowercases.
    Replaces punctuation (except periods) with a space. Removes multiple spaces."""
    sentence = sentence.strip()
    sentence = sentence.lower()
    
    #replace punctuation with a space
    for punc in string.punctuation.replace('.',''): #for all punctuation except a period
        sentence = sentence.replace(punc,' ')
    
    #replace multiple whitespace with single
    sentence = ' '.join(sentence.split()) 
    
    #remove period from the end of sentence (don't remove all periods to
    #preserve decimal measurements of lesions)
    sentence = sentence.strip('. ')
    return sentence

##############################
# General Cleaning Functions #--------------------------------------------------
##############################
def clean_merged(merged,setname):
    """Fix the labels so there are only two classes and make a binary label
    column for later quantitative eval"""
    #Fix the labels so only 2 classes
    merged['Label'] = merged['Label'].replace('x','h')
    merged['Label'] = merged['Label'].replace('a','s')
     
    #Make binary label column for later quantitative eval
    if setname=='train' or setname=='test':
       merged['BinLabel'] = copy.deepcopy(merged['Label'])
       merged['BinLabel'] = merged['BinLabel'].replace('h',0)
       merged['BinLabel'] = merged['BinLabel'].replace('s',1)
    
    #Ignore the 'Count' column because that column is meaningless seeing as
    #we have merged the FSS and CLS files so each sentence is represented
    #explicitly each time it occurs in the dataset (because of the FSS)
    return merged.drop(labels='Count',axis='columns')

