##sentence_rules.py
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
import pandas as pd

import load
import evaluation
from rules import rules_ct
from rules import rules_cxr

##############################
# Class to Run Rules on Data #--------------------------------------------------
##############################
class ApplyRules(object):
    """Apply a rule-based method to extract 'sick' parts of radiology report
    sentences"""
    def __init__(self, dataset, rules_to_use):
        """Variables:
        <dataset>: either 'duke_ct' or 'openi_cxr'
        <rules_to_use>: either 'duke_ct', 'cxr_amb_pos', or
            'cxr_amb_neg'
        """
        self.dataset = dataset
        print('rules_to_use = ',rules_to_use)
        
        if rules_to_use == 'duke_ct':
            self.rules_order = rules_ct.RULES_ORDER_CT
            self.rules_def = rules_ct.RULES_DEF_CT
        elif rules_to_use == 'cxr_amb_pos':
            self.rules_order = rules_cxr.RULES_ORDER_CXR_AMBPOS
            self.rules_def = rules_cxr.RULES_DEF_CXR_AMBPOS
        elif rules_to_use == 'cxr_amb_neg':
            self.rules_order = rules_cxr.RULES_ORDER_CXR_AMBNEG
            self.rules_def = rules_cxr.RULES_DEF_CXR_AMBNEG
        
    def run_all(self):
        print('Running sentence_rules')
        self._prepare_data()
        self._run_rules()
    
    # Data Handling #-----------------------------------------------------------
    def _prepare_data(self):
        self.train_merged, self.test_merged, self.predict_merged = load.load_merged_with_style(self.dataset, 'trainall_testall')
    
    # Rules #-------------------------------------------------------------------
    def _run_rules(self):
        """Run the rules to separate healthy and sick parts of sentences"""
        self.train_merged = ApplyRules.apply_all_rules(self.train_merged, self.rules_order, self.rules_def)
        self.test_merged = ApplyRules.apply_all_rules(self.test_merged, self.rules_order, self.rules_def)
        if self.dataset == 'duke_ct':
            self.predict_merged = ApplyRules.apply_all_rules(self.predict_merged, self.rules_order, self.rules_def)
        
        self.train_merged = self._extract_predictions(self.train_merged)
        self.test_merged = self._extract_predictions(self.test_merged)
        if self.dataset == 'duke_ct':
            self.predict_merged = self._extract_predictions(self.predict_merged)
    
    @staticmethod
    def apply_all_rules(merged, rules_order, rules_def):
        merged = merged.rename(columns={'Sentence':'OriginalSentence'})
        #pad with spaces. important to ensure terms at beginning of words work
        merged['OriginalSentence'] = [' '+x+' ' for x in merged['OriginalSentence'].values.tolist()]
        merged['Sentence']=merged['OriginalSentence'].values.tolist() #will contain modified version of sentence acceptable for term search
        merged['PredLabelConservative']=1 #assume sick unless marked healthy
        for idx in merged.index.values.tolist():
            sent = merged.at[idx,'OriginalSentence']
            for mainword in rules_order:
                func = rules_def[mainword]['function']
                kwargs = rules_def[mainword]
                modified, sent = func(sentence=sent,mainword=mainword,**kwargs)
                if modified:
                    merged.at[idx,'PredLabelConservative']=0
                    merged.at[idx,'Sentence'] = sent
        return merged
    
    def _extract_predictions(self, merged):
        """Report overall performance and save binary labels, predicted
        labels, and predicted probabilities in <merged>"""
        
        #Note that some outputs of some rules will produce empty sentences that
        #are not the empty string, e.g. ' ' or '   '. We need to turn these into
        #the empty string so that we can produce our labels based on assuming
        #that a healthy sentence is the empty string.
        #Note that ' '.join(' '.split()) produces the empty string.
        merged['Sentence'] = [' '.join(x.split()) for x in merged['Sentence'].values.tolist()]
        
        #Actual PredLabel should be healthy only if there is NOTHING left in the
        #Sentence column because then it means every component of the sentence
        #was deemed healthy. If any part is remaining, that part should be
        #treated as sick. 
        merged['PredLabel'] = 1
        for idx in merged.index.values.tolist():
            if merged.at[idx,'Sentence']=='':
                merged.at[idx,'PredLabel'] = 0
        
        #Rules are not probabilistic so the PredProb column is equal to the
        #PredLabel column. PredProb column is accessed in the eval functions.
        merged['PredProb'] = merged['PredLabel'].values.tolist()
        return merged
        