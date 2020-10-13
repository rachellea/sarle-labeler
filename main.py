#main.py
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
import numpy as np

#from sentence_classifier import ClassifySentences
from sentence_rules import *
import term_search
import visualizations

def run_SARLE_Rules_demo():
    #SARLE-Rules
    #Apply rule-based methods. There are 3 options: 'duke_ct' applies the rules
    #developed for CT scans to the CXR data, just for demo purposes since the
    #CT data could not be made public. 'cxr_amb_neg' applies the rules
    #developed for chest x-rays that consider ambiguous findings negative.
    #'cxr_amb_pos' applies the rules developed for chest x-rays that consider
    #ambiguous findings positive.
    #Here we'll just apply all the rule based methods in sequence,
    #to demo all of them:
    for rules_to_use in ['duke_ct', 'cxr_amb_neg', 'cxr_amb_pos']:
        generate_labels(method='rules',rules_to_use=rules_to_use)

def run_SARLE_Hybrid_demo():
    #SARLE-Hybrid
    #Apply hybrid approach where the Fasttext classifier is used to distinguish
    #normal and abnormal sentences before the term search.
    #Note that Fasttext is only available on Linux.
    generate_labels(method='hybrid', rules_to_use='')
    
def generate_labels(method, rules_to_use):
    """Generate labels for the radiology reports using the specified <method>, either
        'hybrid' for a Fasttext sentence classifier followed by the term search, or
        'rules' for a rule-based phrase classifier followed by the term search"""
    assert method in ['hybrid','rules']
    assert rules_to_use in ['duke_ct', 'cxr_amb_neg', 'cxr_amb_pos','']
    if method=='hybrid': assert rules_to_use==''
    
    #Note that to run on CT data, dataset = 'duke_ct'. However CT data is
    #not public, so 'openi_cxr' is the only dataset option here.
    dataset = 'openi_cxr'
    
    #For the openi_cxr data set, there is no 'predict set'
    run_predict=False
    #For the Duke CT data, the predict set consists of the many thousands of
    #reports on which we need to apply the labeler to get a volume ground truth.
    
    #Make results directory
    if not os.path.isdir('results'):
        os.mkdir('results')
    if len(rules_to_use)>0:
        results_dir = os.path.join('results',datetime.datetime.today().strftime('%Y-%m-%d')+'_'+dataset+'_'+method+'_'+rules_to_use)
    else:
        results_dir = os.path.join('results',datetime.datetime.today().strftime('%Y-%m-%d')+'_'+dataset+'_'+method)
    if not os.path.isdir(results_dir):
        os.mkdir(results_dir)
    
    #Extracting Abnormal Sentences (Fasttext) or Abnormal Phrases (Rules):
    if method == 'hybrid': #Sentence Classifier, Fasttext approach
        sent_class_dir = os.path.join(results_dir, '0_sentences')
        if not os.path.isdir(sent_class_dir):
            os.mkdir(sent_class_dir)
        #Safra Fasttext 
        #First, just get results to report (but not to use downstream):
        ClassifySentences(dataset,sent_class_dir,'trainfilt_testfilt').run_all()
        ClassifySentences(dataset,sent_class_dir,'trainall_testfilt').run_all()
        #Now get results to report AND use downstream:
        m = ClassifySentences(dataset,sent_class_dir,'trainall_testall')
        m.run_all()
    elif method == 'rules': #Rule-based approach
        m = ApplyRules(dataset, rules_to_use)
        m.run_all()
    
    #Term Search
    term_search_dir = os.path.join(results_dir, '1_term_search')
    if not os.path.isdir(term_search_dir):
        os.mkdir(term_search_dir)
    term_search.RadLabel(dataset, term_search_dir, 'train', m.train_merged)
    term_search.RadLabel(dataset, term_search_dir, 'test', m.test_merged)
    if run_predict:
        term_search.RadLabel(dataset, term_search_dir, 'predict', m.predict_merged)
    if dataset == 'duke_ct' and run_predict is True:
        term_search.combine_imgtrain_files(term_search_dir)
    
    #Visualizations
    generate_visualizations(dataset, results_dir)
    print('Done')

def generate_visualizations(dataset, results_dir):
    """Make visualizations that summarize the extracted labels"""
    #Results dirs for visualizations
    viz_dir = os.path.join(results_dir, '2_visualizations')
    if not os.path.isdir(viz_dir):
        os.mkdir(viz_dir)
    #Sentence Histograms for the notetrain set only
    visualizations.RepeatedSentenceHistograms(dataset, viz_dir)
    
if __name__=='__main__':
    run_SARLE_Rules_demo()
    #run_SARLE_Hybrid_demo()
  