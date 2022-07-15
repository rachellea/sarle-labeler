#run_sarle.py
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
import datetime
import pandas as pd

from . import load, sentence_rules, sentence_classifier, term_search, visualizations

def generate_labels(train_data_raw, test_data_raw, predict_data_raw,
                    dataset_descriptor, sarle_variant, ambiguities,
                    run_locdis_checks):
    """Generate a matrix of abnormality x location labels for each
    free-text radiology report in the dataset.
    
    Variables:
    <dataset_descriptor> is any of ['duke_ct_2019_09_25','duke_ct_2020_03_17','openi_cxr'].
        Note that for demo purposes only 'openi_cxr' is publicly available.
    <sarle_variant> is either 'hybrid' or 'rules'.
        If 'hybrid' then a Fasttext sentence classifier will be used to filter
        out normal sentences and keep only abnormal sentences.
        If 'rules' then a rule-based method will be used to filter out normal
        phrases and keep only abnormal phrases. Different rules will be applied
        depending on whether the data set is Duke CT or OpenI.
        'rules' outperforms 'hybrid' on the Duke CT dataset.
    <ambiguities> is either 'pos' or 'neg' which determines whether
        ambiguous findings are kept in the sentences (and thus marked positive) 
        or deleted from the sentences (and thus marked negative).
    <run_locdis_checks> is either True or False. If True then run sanity
        checks based on allowed abnormality x location combos."""
    #Run sanity checks and set up results dirs
    setup = [sarle_variant, dataset_descriptor, ambiguities, run_locdis_checks]
    sanity_check_configuration(*setup)
    results_dir, sent_class_dir, term_search_dir = configure_results_dirs(*setup)
    
    #Deep copy of data to enable loading data once in demo.py and then using
    #it repeatedly. The data gets modified by SARLE so this deep copy is
    #necessary if running SARLE multiple times on the same data.
    train_data = copy.deepcopy(train_data_raw)
    test_data = copy.deepcopy(test_data_raw)
    predict_data = copy.deepcopy(predict_data_raw)

    #Step 1: Sentence/Phrase Classification
    if sarle_variant == 'hybrid': #Sentence Classifier, Fasttext approach
        m = sentence_classifier.ClassifySentences(train_data, test_data, predict_data, sent_class_dir, ambiguities)
        m.run_all()
        train_data = m.train_data
        test_data = m.test_data
        predict_data = m.predict_data
    
    elif sarle_variant == 'rules': #Rule-based approach
        rules_to_use = decide_rules_to_use(dataset_descriptor, ambiguities)
        train_data = sentence_rules.ApplyRules(train_data, 'train', rules_to_use).data_processed
        test_data = sentence_rules.ApplyRules(test_data, 'test', rules_to_use).data_processed
        predict_data = sentence_rules.ApplyRules(predict_data, 'predict', rules_to_use).data_processed
    
    #Step 2: Term Search
    term_search.RadLabel(train_data, 'train', dataset_descriptor, term_search_dir, run_locdis_checks)
    term_search.RadLabel(test_data, 'test', dataset_descriptor, term_search_dir, run_locdis_checks)
    term_search.RadLabel(predict_data, 'predict', dataset_descriptor, term_search_dir, run_locdis_checks)
    
    if ((dataset_descriptor in ['duke_ct_2019_09_25','duke_ct_2020_03_17']) and (not predict_data.empty)):
        load.combine_imgtrain_files(term_search_dir)
    print('Done')


def generate_visualizations(dataset_descriptor, results_dir):
    """Make visualizations that summarize the extracted labels"""
    assert dataset_descriptor == 'duke_ct', 'Visualizations only tested for dataset_descriptor = duke_ct'
    
    #Set up results directories for visualizations
    viz_dir = os.path.join(results_dir, '2_visualizations')
    if not os.path.isdir(viz_dir):
        os.mkdir(viz_dir)
    for setname in ['imgtrain', 'imgvalid', 'imgtest']:
        viz_dir_setname = os.path.join(viz_dir,setname)
        if not os.path.isdir(viz_dir_setname):
            os.mkdir(viz_dir_setname)
    
    #Sentence Histograms for the notetrain set only
    visualizations.RepeatedSentenceHistograms(dataset_descriptor, os.path.join(viz_dir,'imgtrain'))
    
    #Other visualizations:
    for setname in ['imgtrain', 'imgvalid', 'imgtest']:
        viz_dir_setname = os.path.join(viz_dir,setname)
        #Location x Disease Summary:
        missing = pd.read_csv(os.path.join(term_search_dir, setname+'_Missingness.csv'), header=0, index_col = 0)
        out_bin = pickle.load(open(os.path.join(term_search_dir, setname+'_BinaryLabels.pkl'), 'rb'))
        visualizations.LocationDiseaseSummary(setname, term_search_dir, viz_dir_setname, out_bin, missing)
        
        #Abnormalities per CT Summary
        visualizations.AbnormalitiesPerCTHistograms(setname, term_search_dir, viz_dir_setname)
        
        #Abnormality Label Correlations
        visualizations.AbnormalityLabelCorrelations(setname, term_search_dir, viz_dir_setname)


def sanity_check_configuration(sarle_variant, dataset_descriptor, ambiguities, 
                               run_locdis_checks):
    """Sanity check the requested configuration"""
    assert sarle_variant in ['hybrid','rules']
    
    if dataset_descriptor in ['duke_ct_2019_09_25','openi_cxr']:
        print(dataset_descriptor,'report-level ground truth is available, '\
                                  'so SARLE\'s performance will be calculated')
    elif dataset_descriptor=='duke_ct_2020_03_17':
        print(dataset_descriptor,'does not have report-level ground truth '\
                         'available, so SARLE\'s performance will not be '\
                         'calculated')
    else:
        print(dataset_descriptor,'Note that if you would like SARLE\'s test '\
                        'set performance to be calculated on this data set '\
                        'you must provide report-level abnormality ground '\
                        'truth on the test set') 
    
    assert ambiguities in ['pos','neg']
    if ambiguities=='neg':
        assert dataset_descriptor=='openi_cxr','Error: Currently ambiguities=neg '\
                         'is only supported for the openi_cxr dataset: see '\
                         'run_sarle.decide_rules_to_use() to change this.'

    assert isinstance(run_locdis_checks, bool)
    
    if dataset_descriptor in ['duke_ct_2019_09_25','duke_ct_2020_03_17']:
        assert ambiguities == 'pos', 'ambiguities=negative with Duke data is '\
                        'not allowed. Duke CT ground truth assumes all '\
                        'ambiguous findings are positive.'


def configure_results_dirs(sarle_variant, dataset_descriptor, ambiguities,
                           run_locdis_checks):
    """Create and return the paths to results directories"""
    if not os.path.isdir('results'):
        os.mkdir('results')
    
    results_dir = os.path.join('results',datetime.datetime.today().strftime('%Y-%m-%d')
                               +'_'+dataset_descriptor+'_'+sarle_variant+'_amb'+ambiguities
                               +'_locdis'+str(run_locdis_checks))
    if not os.path.isdir(results_dir):
        os.mkdir(results_dir)
    print('Results in',results_dir)

    if sarle_variant=='hybrid':
        sent_class_dir = os.path.join(results_dir, '0_sentences')
        if not os.path.isdir(sent_class_dir):
            os.mkdir(sent_class_dir)
    else:
        sent_class_dir = ''
    
    term_search_dir = os.path.join(results_dir, '1_term_search')
    if not os.path.isdir(term_search_dir):
        os.mkdir(term_search_dir)

    return results_dir, sent_class_dir, term_search_dir


def decide_rules_to_use(dataset_descriptor, ambiguities):
    if dataset_descriptor=='openi_cxr':
        if ambiguities=='pos':
            return 'cxr_amb_pos_rules'
        elif ambiguities=='neg': 
            #then ambiguity filter will be applied to delete ambiguous
            #findings so that they are not identified by the term search
            #and thus marked negative
            return 'cxr_amb_neg_rules'
    elif dataset_descriptor in ['duke_ct_2019_09_25','duke_ct_2020_03_17']:
        return 'duke_ct_rules'
    else:
        print('For',dataset_descriptor,'defaulting to duke_ct_rules')
        return 'duke_ct_rules'

