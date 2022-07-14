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

from src import evaluation
from src.rules import rules_ct, rules_cxr

##############################
# Class to Run Rules on Data #--------------------------------------------------
##############################
class ApplyRules(object):
    """Apply a rule-based method to extract 'sick' parts of radiology report
    sentences"""
    def __init__(self, data, setname, rules_to_use):
        """Variables:
        <data>: dataset, as described in demo.py and run_sarle.py
        <setname>: either 'train' or 'test' or 'predict'
        <rules_to_use>: either 'duke_ct_rules', 'cxr_amb_pos_rules', or
            'cxr_amb_neg_rules'
        """
        self.data = data
        self.setname = setname
        assert self.setname in ['train','test','predict']
                
        if rules_to_use=='duke_ct_rules':
            self.rules_order = rules_ct.RULES_ORDER_CT
            self.rules_def = rules_ct.RULES_DEF_CT
        elif rules_to_use=='cxr_amb_pos_rules':
            self.rules_order = rules_cxr.RULES_ORDER_CXR_AMBPOS
            self.rules_def = rules_cxr.RULES_DEF_CXR_AMBPOS
        elif rules_to_use=='cxr_amb_neg_rules':
            self.rules_order = rules_cxr.RULES_ORDER_CXR_AMBNEG
            self.rules_def = rules_cxr.RULES_DEF_CXR_AMBNEG
    
        #Run rules to separate healthy and sick phrases.
        if not self.data.empty:
            self._apply_all_rules()
            self._extract_predictions()
        
        self.data_processed = self.data
    
    def _apply_all_rules(self):
        self.data = self.data.rename(columns={'Sentence':'OriginalSentence'})
        #pad with spaces. important to ensure terms at beginning of words work
        self.data['OriginalSentence'] = [' '+x+' ' for x in self.data['OriginalSentence'].values.tolist()]
        self.data['Sentence']=self.data['OriginalSentence'].values.tolist() #will contain modified version of sentence acceptable for term search
        self.data['PredLabelConservative']=1 #assume sick unless marked healthy
        for idx in self.data.index.values.tolist():
            sent = self.data.at[idx,'OriginalSentence']
            for mainword in self.rules_order:
                func = self.rules_def[mainword]['function']
                kwargs = self.rules_def[mainword]
                modified, sent = func(sentence=sent,mainword=mainword,**kwargs)
                if modified:
                    self.data.at[idx,'PredLabelConservative']=0
                    self.data.at[idx,'Sentence'] = sent
    
    def _extract_predictions(self):
        """Report overall performance and put binary labels, predicted
        labels, and predicted probabilities into <self.data>"""
        #Note that some outputs of some rules will produce empty sentences that
        #are not the empty string, e.g. ' ' or '   '. We need to turn these into
        #the empty string so that we can produce our labels based on assuming
        #that a healthy sentence is the empty string.
        #Note that ' '.join(' '.split()) produces the empty string.
        self.data['Sentence'] = [' '.join(x.split()) for x in self.data['Sentence'].values.tolist()]
        
        #Actual PredLabel should be healthy only if there is NOTHING left in the
        #Sentence column because then it means every component of the sentence
        #was deemed healthy. If any part is remaining, that part should be
        #treated as sick. 
        self.data['PredLabel'] = 1
        for idx in self.data.index.values.tolist():
            if self.data.at[idx,'Sentence']=='':
                self.data.at[idx,'PredLabel'] = 0
        
        #Rules are not probabilistic so the PredProb column is equal to the
        #PredLabel column. PredProb column is accessed in the eval functions.
        self.data['PredProb'] = self.data['PredLabel'].values.tolist()
        
        #Report performance
        #This is within a 'try' block because it will only work if sentence
        #level ground truth is provided for all sentences, which may not
        #be the case for all datasets.
        try:
            evaluation.report_sentence_level_eval(self.data, self.setname, 'Rules')
                