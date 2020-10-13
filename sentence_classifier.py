#sentence_classifier.py
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
import fasttext
import numpy as np
import pandas as pd

import load
import evaluation

class ClassifySentences(object):
    """Train (training set), evaluate (test set), and use (predict set)
    a Fasttext model that classifies individual radiology report sentences as
    'sick' or 'healthy'"""
    def __init__(self, dataset, results_dir, style):
        """Variables:
        <dataset>: either 'duke_ct' or 'openi_cxr'
        <results_dir>: path to directory in which results will be saved
        <style>:
            'trainall_testall': train on all training sentences and test on
                all test sentences. This is the variant needed for the overall
                task of predicting note-level labels.
            'trainfilt_testfilt': train on only unique sentences in the training
                set, and train on only unique sentences in the test set.
                There is no overlap between training set and test set
                sentences. Sentences that would overlap are assigned to the
                training set.
            'trainall_testfilt': train on all training sentences, and test on
                only unique sentences in the test set. Sentences that would
                overlap are assigned to the training set."""
        self.dataset = dataset
        self.results_dir = results_dir
        self.style = style #affects function _save_fasttext_splits(), and what files get saved
        assert self.style in ['trainall_testall','trainfilt_testfilt','trainall_testfilt']
        print('Running sentence_classifier with style',self.style)
        
    def run_all(self):
        self._prepare_data()
        self._run_fasttext_model()
    
    # Data Handling #-----------------------------------------------------------
    def _prepare_data(self):
        """Save the fasttext input files to disk and save the corresponding
        filename order as self.data_set_filename_order"""
        #create self.train_merged, self.test_merged, self.predict_merged
        #and clean them up based on the style
        self.train_merged, self.test_merged, self.predict_merged = load.load_merged_with_style(self.dataset, self.style)
        
        #Save the fasttext files:
        self._save_fasttext_split('train',self.train_merged)
        self._save_fasttext_split('test',self.test_merged)
    
    def _save_fasttext_split(self, setname, merged):
        """Create the file fasttext_<name>_set.txt in <self.results_dir>
        for the data set specified by <setname>, containing the sentence and
        label data formatted for fasttext: the file has no header, and each line
        contains a label (either '__label__s' or '__label__h') followed by a
        sentence."""
        assert setname=='train' or setname=='test' or setname=='predict'
        data_set = []
        for index in merged.index.values.tolist():
            sentence = merged.at[index,'Sentence']
            label = '__label__'+merged.at[index,'Label']
            data_set.append([label,sentence])
        np.savetxt(os.path.join(self.results_dir,'fasttext_'+setname+'_set.txt'), np.array(data_set), fmt='%s')
    
    # Fasttext Model #----------------------------------------------------------
    def _run_fasttext_model(self):
        """Use the prepared train and test data to run the fasttext model"""
        model = fasttext.train_unsupervised(os.path.join(self.results_dir,'fasttext_train_set.txt'), model='skipgram')
        model.save_model(os.path.join(self.results_dir,'skipgram_model.bin'))
        self.classifier = fasttext.train_supervised(os.path.join(self.results_dir, 'fasttext_train_set.txt'))
        self.classifier.save_model(os.path.join(self.results_dir,'classifier.bin'))
        result = self.classifier.test(os.path.join(self.results_dir, 'fasttext_test_set.txt'))
        #result is a tuple (N, precision, recall)
        print('(N, P@1, R@1)=',result)
        self.train_merged = self._get_preds_and_perf('train',self.train_merged)
        self.test_merged = self._get_preds_and_perf('test',self.test_merged)
        if self.dataset == 'duke_ct':
            self.predict_merged = self._get_preds_and_perf('predict',self.predict_merged)
        self._clean_up()
    
    def _get_preds_and_perf(self, setname, merged):
        """Report overall performance and save binary labels, predicted
        labels, and predicted probabilities in <merged>"""
        #Make predictions
        print('*** '+setname+' ***')
        merged = self._extract_predictions(merged)
        
        #Report performance
        evaluation.report_sentence_level_eval(merged, setname, 'Fasttext')
        return merged
        
    def _extract_predictions(self, merged):
        """Return <merged> with the predicted labels and probabilities added"""
        sentences = merged['Sentence'].values.tolist()
        preds_h_or_s = self.classifier.predict(sentences)
        predicted_labels = [x[0].replace('__label__','') for x in preds_h_or_s[0]]
        predicted_probs = [x[0] for x in preds_h_or_s[1]]
        
        #Now flip the predicted probs for the healthy because we want to
        #output the probability that the sentence is sick.
        #Also binarize the predicted labels to 1 and 0 from s and h
        predicted_labels_final = []
        predicted_probs_final = []
        for index in range(len(sentences)):
            if predicted_labels[index] == 's':
                predicted_labels_final.append(1)
                predicted_probs_final.append(predicted_probs[index])
            elif predicted_labels[index] == 'h':
                predicted_labels_final.append(0)
                #one minus, because we want this to report the probability of being
                #sick (which is the opposite of the probability of being healthy)
                predicted_probs_final.append(1 - predicted_probs[index])
            else:
                assert False
        merged['PredLabel'] = predicted_labels_final
        merged['PredProb'] = predicted_probs_final
        return merged
    
    def _clean_up(self):
        if self.style in ['trainfilt_testfilt','trainall_testfilt']:
            os.remove(os.path.join(self.results_dir,'skipgram_model.bin'))
            os.remove(os.path.join(self.results_dir,'classifier.bin'))
            os.remove(os.path.join(self.results_dir,'fasttext_train_set.txt'))
            os.remove(os.path.join(self.results_dir,'fasttext_test_set.txt'))                  
    