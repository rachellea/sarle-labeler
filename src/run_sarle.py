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
import pickle
import datetime
import pandas as pd
from types import SimpleNamespace

from . import load, sentence_rules, sentence_classifier, term_search, visualizations

def generate_labels(sarle_variant, dataset, run_predict, ambiguities,
                    run_locdis_checks):
    """Generate a matrix of abnormality x location labels for each
    free-text radiology report in the dataset.
    
    Variables:
    <sarle_variant> is either 'hybrid' or 'rules'.
        If 'hybrid' then a Fasttext sentence classifier will be used to filter
        out normal sentences and keep only abnormal sentences.
        If 'rules' then a rule-based method will be used to filter out normal
        phrases and keep only abnormal phrases. Different rules will be applied
        depending on whether the data set is Duke CT or OpenI.
        'rules' outperforms 'hybrid' on the Duke CT dataset.
    <dataset> is any of ['duke_ct_2019_09_25','duke_ct_2020_03_17','openi_cxr'].
        Note that for demo purposes only 'openi_cxr' is publicly available.
    <run_predict> is True in order to make predictions on the predict set of
        the Duke CT data. Warning: this step takes a long time, so if you only
        want to calculate the test set performance then set run_predict to 
        False.
    <ambiguities> is either 'pos' or 'neg' which determines whether
        ambiguous findings are kept in the sentences (and thus marked positive) 
        or deleted from the sentences (and thus marked negative).
    <run_locdis_checks> is either True or False. If True then run sanity
        checks based on allowed abnormality x location combos."""
    #Run sanity checks and set up results dirs
    setup = [sarle_variant, dataset, run_predict, ambiguities, run_locdis_checks]
    sanity_check_configuration(*setup)
    results_dir, sent_class_dir, term_search_dir = configure_results_dirs(*setup)
    
    #Step 1: Sentence/Phrase Classification
    if sarle_variant == 'hybrid': #Sentence Classifier, Fasttext approach
        #First, just get results to report (but not to use downstream):
        sentence_classifier.ClassifySentences(dataset,sent_class_dir,'trainfilt_testfilt',run_predict,ambiguities).run_all()
        sentence_classifier.ClassifySentences(dataset,sent_class_dir,'trainall_testfilt',run_predict,ambiguities).run_all()
        #Now get results to report AND use downstream:
        m = sentence_classifier.ClassifySentences(dataset,sent_class_dir,'trainall_testall',run_predict,ambiguities)
        m.run_all()
    elif sarle_variant == 'rules': #Rule-based approach
        rules_to_use = decide_rules_to_use(dataset, ambiguities)
        m = sentence_rules.ApplyRules(dataset, rules_to_use)
        m.run_all()
        
    #Step 2: Term Search
    term_search.RadLabel(dataset, term_search_dir, 'train', m.train_merged, run_locdis_checks)
    term_search.RadLabel(dataset, term_search_dir, 'test', m.test_merged, run_locdis_checks)
    if run_predict:
        term_search.RadLabel(dataset, term_search_dir, 'predict', m.predict_merged, run_locdis_checks)
    if ((dataset in ['duke_ct_2019_09_25','duke_ct_2020_03_17']) and (run_predict is True)):
        term_search.combine_imgtrain_files(term_search_dir)
    print('Done')


def generate_visualizations(dataset, results_dir):
    """Make visualizations that summarize the extracted labels"""
    assert dataset == 'duke_ct', 'Visualizations only tested for dataset = duke_ct'
    
    #Set up results directories for visualizations
    viz_dir = os.path.join(results_dir, '2_visualizations')
    if not os.path.isdir(viz_dir):
        os.mkdir(viz_dir)
    for setname in ['imgtrain', 'imgvalid', 'imgtest']:
        viz_dir_setname = os.path.join(viz_dir,setname)
        if not os.path.isdir(viz_dir_setname):
            os.mkdir(viz_dir_setname)
    
    #Sentence Histograms for the notetrain set only
    visualizations.RepeatedSentenceHistograms(dataset, os.path.join(viz_dir,'imgtrain'))
    
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


def sanity_check_configuration(sarle_variant, dataset, run_predict, 
                               ambiguities, run_locdis_checks):
    """Sanity check the requested configuration"""
    assert sarle_variant in ['hybrid','rules']
    assert dataset in ['duke_ct_2019_09_25','duke_ct_2020_03_17','openi_cxr']
    assert isinstance(run_predict,bool)
    assert ambiguities in ['pos','neg']
    if ambiguities == 'neg':
        #currently, setting ambiguous findings negative is only supported for
        #the OpenI dataset. In practice the ambiguity filter is implemented
        #using rules, which are applied either (a) after the base rules
        #to remove normal phrases in the case of sarle_variant='rules' or 
        #(b) after the Fasttext step to remove normal sentences in the case
        #of sarle_variant='hybrid'
        assert dataset=='openi_cxr'
    assert isinstance(run_locdis_checks,bool)
    if dataset in ['duke_ct_2019_09_25','duke_ct_2020_03_17']:
        assert ambiguities == 'pos', '''ambiguities=negative with Duke data is 
                                        not allowed. Duke CT ground truth 
                                        assumes all ambiguous findings 
                                        are positive.'''
    if dataset=='openi_cxr':
        assert run_predict == False, '''run_predict must be False for openi_cxr 
                                        data because there is no predict set'''


def configure_results_dirs(sarle_variant, dataset, run_predict, ambiguities,
                           run_locdis_checks):
    """Create and return the paths to results directories"""
    if not os.path.isdir('results'):
        os.mkdir('results')
    
    results_dir = os.path.join('results',datetime.datetime.today().strftime('%Y-%m-%d')
                               +'_'+dataset+'_'+sarle_variant+'_amb'+ambiguities
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


def decide_rules_to_use(dataset, ambiguities):
    if dataset=='openi_cxr':
        if ambiguities=='pos':
            return 'cxr_amb_pos_rules'
        elif ambiguities=='neg':
            return 'cxr_amb_neg_rules'
    elif dataset in ['duke_ct_2019_09_25','duke_ct_2020_03_17']:
        return 'duke_ct_rules'
