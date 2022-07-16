#demo.py
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

import pandas as pd

from src import run_sarle, load

def sarle_demo(train_data, test_data, predict_data, dataset_descriptor):
    """Demo the SARLE-Rules and SARLE-Hybrid methods with ambiguities=='pos'."""
    run_sarle.generate_labels(train_data, test_data, predict_data, 
                            dataset_descriptor, sarle_variant='rules', 
                            ambiguities='pos', run_locdis_checks=True)
    
    run_sarle.generate_labels(train_data, test_data, predict_data,
                            dataset_descriptor, sarle_variant='hybrid', 
                            ambiguities='pos', run_locdis_checks=True)


def load_fake_data():
    #For legacy reasons, the 'Label' and 'BinLabel' columns are redundant 
    #with 'h'=0 and 's'=1. They contain the same information but are 
    #unfortunately both used in the code.
    #You can easily generate one column from the other programatically.
    #TODO: eliminate use of the 'Label' column in the future.
    #The 'Section' column is also there for legacy reasons. You can populate this
    #entirely with the string 'Findings' or entirely with the string 
    #'Impression' if you don't want to use this column.
    train_data = pd.DataFrame(
        [['s','There is a nodule in the right upper lobe.','report1.txt','Findings','1'],
        ['s','There is cardiomegaly without pericardial effusion.','report1.txt','Findings','1'],
        ['h','The lungs are clear.','report2.txt','Findings','0'],
        ['h','The heart is normal in size.','report2.txt','Findings','0'],
        ['s','An opacity in the left lower lobe is favored to represent atelectasis vs consolidation.','report3.txt','Findings','1']],
        columns = ['Label', 'Sentence', 'Filename', 'Section', 'BinLabel'])
    train_data['BinLabel'] = train_data['BinLabel'].astype(int)

    test_data = pd.DataFrame(
        [['s','Scattered nodules bilaterally.','report4.txt','Findings','1'],
        ['s','There is a right pleural effusion.','report4.txt','Findings','1'],
        ['h','There are no lung abnormalities.','report5.txt','Findings','0']],
        columns = ['Label', 'Sentence', 'Filename', 'Section', 'BinLabel'])
    test_data['BinLabel'] = test_data['BinLabel'].astype(int)
    
    #As mentioned in the README, it's okay not to have any predict data. We'll
    #demo that case here, with an empty df for the predict set.
    predict_data = pd.DataFrame()

    return train_data, test_data, predict_data


if __name__=='__main__':
    # #OpenI demo
    # train_data, test_data, predict_data = load.load_merged_with_style('openi_cxr', 'trainall_testall')
    # sarle_demo(train_data, test_data, predict_data, 'openi_cxr')

    # #Fake data demo
    # train_data, test_data, predict_data = load_fake_data()
    # sarle_demo(train_data, test_data, predict_data, 'fakedata')


    #TEMP DUKE
    train_data, test_data, predict_data = load.load_merged_with_style('duke_ct_2019_09_25', 'trainall_testall')
    run_sarle.generate_labels(train_data, test_data, predict_data,
                            dataset_descriptor='duke_ct_2019_09_25', sarle_variant='rules', 
                            ambiguities='pos', run_locdis_checks=True)
    
    