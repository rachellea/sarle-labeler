#unit_tests.py
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
import shutil
import pandas as pd
import numpy as np

import load
import term_search
from vocab import gr1cm
from vocab import vocabulary_ct
from rules import rule_functions

#Note: this module originally contained over 1,400 lines of unit testing
#code. However, we decided to keep most of this code private, because it
#is based on CT report data that 'looks real' and we do not want to create
#the impression that any real report data was made public through unit tests
#without permission. The CT reports cannot be made public at this time due to
#patient privacy concerns.
#We have made public all unit tests which do not subjectively appear to reveal
#real report data.

############################
# Testing vocabulary_ct.py #----------------------------------------------------
############################
def test_nodulegr1cm_handling():
    x1 = ' 0.2 cm left lower lobe pulmonary nodule series 3 image 33 is newly noted '
    assert gr1cm.nodulegr1cm_handling(x1)==0
    
    x2 = ' 2 mm left upper lobe juxtapleural nodule series 3 image 59 stable '
    assert gr1cm.nodulegr1cm_handling(x2)==0
    
    x3 = ' 2 cm left upper lobe juxtapleural nodule series 3 image 59 stable ' #made up sentence
    assert gr1cm.nodulegr1cm_handling(x3)==1
    
    x4 = ' a few left lower lobe pulmonary nodules are visualized '
    assert gr1cm.nodulegr1cm_handling(x4)==0
    
    x5 = ' again seen in the right lower lobe is a solid pulmonary nodule measuring approximately 1.2 x 1.2 cm series 4 image 340 increased from prior measurement of 0.8 x 0.8 cm '
    assert gr1cm.nodulegr1cm_handling(x5)==1
    
    x6 = 'within the left upper lobe there is a round nodule which measures 2.2 x 1.6 cm which is most likely within a pre existing cavity'
    assert gr1cm.nodulegr1cm_handling(x6)==1
    print('Passed test_nodulegr1cm_handling()')
    
def test_lymphadenopathy_handling():
    x1 = ' 0.9 cm prevascular lymph node is unchanged '
    assert gr1cm.lymphadenopathy_handling(x1)==0
    
    x2 = ' 1 cm low right paratracheal lymph node is nonspecific and may be reactive in nature '
    assert gr1cm.lymphadenopathy_handling(x2)==0
    
    x3 = ' while this may represent a small lymph node a small esophageal diverticulum may have a similar appearance '
    assert gr1cm.lymphadenopathy_handling(x3)==0
    
    x4 = ' no severe change in 1.4 cm right paratracheal lymph node series 3 image 18 '
    assert gr1cm.lymphadenopathy_handling(x4)==1
    
    x5 = ' an enlarged subcarinal lymph node is seen measuring up to 1.3 cm '
    assert gr1cm.lymphadenopathy_handling(x5)==1
    
    x6 = ' stable right precarinal lymph node that measures 1.2 cm in short axis '
    assert gr1cm.lymphadenopathy_handling(x6)==1
    
    x7 = 'severe lymphadenopathy' #made up sentence
    assert gr1cm.lymphadenopathy_handling(x7)==1
    print('Passed test_lymphadenopathy_handling()')

#############################
# Testing rule_functions.py #---------------------------------------------------
#############################
def test_delete_mainword():
    #Example for ' otherwise unremarkable'
    x1 = ' visualized upper abdomen demonstrates calcific atherosclerosis of the aorta otherwise unremarkable '
    _, o1 = rule_functions.delete_mainword(sentence=x1, mainword=' otherwise unremarkable')
    c1 = ' visualized upper abdomen demonstrates calcific atherosclerosis of the aorta '
    assert o1==c1
    
    #Example for ' near complete resolution of'
    x2 = ' near complete resolution of air fluid level in the left upper lobe '
    _, o2 = rule_functions.delete_mainword(sentence=x2, mainword = ' near complete resolution of')
    c2 = ' air fluid level in the left upper lobe '
    assert o2==c2
    
    #Example for ' near resolution of'
    x3 = ' near resolution of a previously seen 5 mm right upper lobe nodule likely reflecting resolving infection or inflammation '
    _, o3 = rule_functions.delete_mainword(sentence=x3, mainword = ' near resolution of')
    c3 = ' a previously seen 5 mm right upper lobe nodule likely reflecting resolving infection or inflammation '
    assert o3==c3
    print('Passed test_delete_mainword()')

def test_delete_part():
    #Example for ' within normal limits'
    x1 = ' main pulmonary artery within normal limits in size '
    _, o1 = rule_functions.delete_part(sentence=x1,delete_part='before',mainword=' within normal limits')
    c1 = ' in size '
    assert o1==c1
    
    #Example for ' normal in'
    x2 = ' the remainder of the airways including the trachea bronchus intermedius right middle and lower lobe bronchi and left upper and lower lobe bronchi appear normal in caliber and are clear '
    _, o2 = rule_functions.delete_part(sentence=x2,delete_part='before',mainword=' normal in')
    c2 = ' caliber and are clear '
    assert o2==c2
    
    #Example for ' normal size'
    x3 = ' there are patent internal iliac arteries and the bilateral external iliac arteries common femoral proximal sfa and profunda are all normal size and caliber without atherosclerotic disease '
    _, o3 = rule_functions.delete_part(sentence=x3,delete_part='before',mainword=' normal size')
    c3 = ' and caliber without atherosclerotic disease '
    assert o3==c3
    
    #Example for ' without'
    x4 = ' there are patent internal iliac arteries and the bilateral external iliac arteries common femoral proximal sfa and profunda are all normal size and caliber without atherosclerotic disease '
    _, o4 = rule_functions.delete_part(sentence=x4,delete_part='after',mainword=' without')
    c4 = ' there are patent internal iliac arteries and the bilateral external iliac arteries common femoral proximal sfa and profunda are all normal size and caliber'
    assert o4==c4
    
    #Example for ' resolution of'
    x5 = ' interval resolution of previously described small groundglass nodules '
    _, o5 = rule_functions.delete_part(sentence=x5,delete_part='after',mainword=' resolution of')
    c5 = ' interval'
    assert o5==c5
    
    #Example for ' removal of'
    x6 = ' interval removal of a surgical drain in the left aspect of the clamshell sternotomy '
    _, o6 = rule_functions.delete_part(sentence=x6,delete_part='after',mainword=' removal of')
    c6 = ' interval'
    assert o6==c6
    
    #Example for ' removed'
    x7 = ' previously noted left pleural pigtail catheter appears to have been removed '
    _, o7 = rule_functions.delete_part(sentence=x7,delete_part='before',mainword=' removed')
    c7 = ' ' #space remains when we delete everything before the word
    assert o7==c7
    
    #Example for ' free of' (made up example)
    x8 = ' free of consolidation or signs of infection'
    _, o8 = rule_functions.delete_part(sentence=x8,delete_part='after',mainword=' free of')
    c8 = '' #no space when we delete everything after the word
    assert o8==c8
    print('Passed test_delete_part()')
    
def test_delete_part_until():
    #Example for ' no '
    x1 = 'otherwise no significant change in findings on ct examination of the chest with partial atelectasis of the right upper lobe and a right hilar mass as well as mediastinal lymphadenopathy and multiple pulmonary nodules'
    _, o1 = rule_functions.delete_part_until(x1, 'after', ' no ', until_hit=['and','change'])
    c1 = 'otherwise change in findings on ct examination of the chest with partial atelectasis of the right upper lobe and a right hilar mass as well as mediastinal lymphadenopathy and multiple pulmonary nodules'
    assert o1==c1
    
    x2 = ' there is a an oblong focus of consolidation within the posterior medial right base on image 89 series 4 adjacent to the pleural effusion this contains no air bronchograms and appears to obliterate some posterior basilar subsegmental bronchi '
    _, o2 = rule_functions.delete_part_until(x2, 'after', ' no ', until_hit=['and','change'])
    c2 = ' there is a an oblong focus of consolidation within the posterior medial right base on image 89 series 4 adjacent to the pleural effusion this contains and appears to obliterate some posterior basilar subsegmental bronchi '
    assert o2==c2
    
    x3 = ' there is no axillary adenopathy and there are scattered mediastinal nodes and a normal size main pulmonary artery with severely enlarged left atrium and left atrial appendage'
    _, o3 = rule_functions.delete_part_until(x3, 'after', ' no ', until_hit=['and','change'])
    c3 = ' there is and there are scattered mediastinal nodes and a normal size main pulmonary artery with severely enlarged left atrium and left atrial appendage'
    assert o3==c3
    
    #Examples made up to test 'before'
    x4 = ' this is a made up sentence no to test the function '
    _, o4 = rule_functions.delete_part_until(x4, 'before', ' test', until_hit=['made','up'])
    c4 = ' this is a made up the function '
    assert o4==c4
    print('Passed test_delete_part_until()')
    
def test_delete_entire_unless_immediate():
    #Example for ' not '
    x1 = ' immediately posterior to the sternomanubrial junction is a small fluid collection with an air fluid level also favored to represent postoperative change although an abscess or phlegmon is not entirely excluded '
    _, o1 = rule_functions.delete_entire_unless_immediate(sentence=x1,mainword=' not',position='after',wrange=2,unless_in=['exclude','change'])
    c1 = ' immediately posterior to the sternomanubrial junction is a small fluid collection with an air fluid level also favored to represent postoperative change although an abscess or phlegmon is not entirely excluded '
    assert o1==c1
    
    x2 = ' the main pulmonary artery is not dilated '
    _, o2 = rule_functions.delete_entire_unless_immediate(sentence=x2,mainword=' not',position='after',wrange=2,unless_in=['exclude','change'])
    c2 = ''
    assert o2==c2
    
    #Example for ' resolved'
    x3 = ' previously described anterior loculated components have resolved '
    _, o3 = rule_functions.delete_entire_unless_immediate(x3,mainword=' resolved',position='before',wrange=1,unless_in=['almost','near','partial','large','essential'])
    c3 = ''
    assert o3==c3
    
    x4 = ' compared to most recent prior examination from january diffuse bilateral consolidative and ground glass opacities are essentially resolved as are bilateral effusions '
    _, o4 = rule_functions.delete_entire_unless_immediate(x4,mainword=' resolved',position='before',wrange=1,unless_in=['almost','near','partial','large','essential'])
    c4 = ' compared to most recent prior examination from january diffuse bilateral consolidative and ground glass opacities are essentially resolved as are bilateral effusions '
    assert o4==c4
    print('Passed test_delete_entire_unless_immediate()')

def test_delete():
    #Example for ' normal'
    x1 = ' the remainder of the airways including the trachea bronchus intermedius right middle and lower lobe bronchi and left upper and lower lobe bronchi appear normal in caliber and are clear '
    _, o1 = rule_functions.delete(x1,' normal')
    assert o1==''
        
    #Example for ' unremarkable'
    x2 = ' the upper abdomen is unremarkable '
    _, o2 = rule_functions.delete(x2,' unremarkable')
    assert o2==''
    
    #Example for ' negative for'
    x3 = ' negative for malignancy ' #made up
    _, o3 = rule_functions.delete(x3, ' negative for')
    assert o3==''
    print('Passed test_delete()')

def test_delete_if_first_word():
    #Example for 'please'
    x1 = 'please refer to the concurrent ct abdomen pelvis report for additional details'
    _, o1 = rule_functions.delete_if_first_word(x1, 'please')
    assert o1 == ''
    _, o2 = rule_functions.delete_if_first_word(' '+x1,'please')
    assert o2 ==  ''
    print('Passed test_delete_if_first_word()')

def test_non_handling():
    x1 = ' 8mm non calcified nodule right lower lobe nodule is unchanged '
    _, o1 = rule_functions.non_handling(x1, 'non')
    c1 =' 8mm nodule right lower lobe nodule is unchanged '
    assert o1==c1
    
    x2 = ' a lytic lesion of the posterior right 6th rib is seen which may now contain a non displaced fracture '
    _, o2 = rule_functions.non_handling(x2, 'non')
    c2 = ' a lytic lesion of the posterior right 6th rib is seen which may now contain a fracture '
    assert o2==c2
    
    x3 = ' 1 cm low right paratracheal lymph node is nonspecific and may be reactive in nature '
    _, o3 = rule_functions.non_handling(x3, 'non')
    c3 = ' 1 cm low right paratracheal lymph node is and may be reactive in nature '
    assert o3==c3
    print('Passed test_non_handling()')

def test_patent_handling():
    x1 = ' tracheobronchial tree is patent '
    _, o1 = rule_functions.patent_handling(x1, ' patent')
    c1 = ' '
    assert o1==c1
    
    x2 = 'patent bronchial anastomoses '
    _, o2 = rule_functions.patent_handling(x2, ' patent')
    c2 = ' '
    assert o2==c2
    
    x3 = ' the bronchial anastomoses are patent and intact and the central bronchi are patent and perhaps slightly dilated '
    _, o3 = rule_functions.patent_handling(x3, ' patent')
    c3 = ' and perhaps slightly dilated '
    assert o3==c3
    
    x4 = ' central airways are patent with some groundglass upper lobe opacities apically that have developed favor radiation changes '
    _, o4 = rule_functions.patent_handling(x4, ' patent')
    c4 = ' with some groundglass upper lobe opacities apically that have developed favor radiation changes '
    assert o4==c4
    
    x5 = ' patent central airways status post bilateral lung transplantation.bilateral chest tubes remains in place '
    _, o5 = rule_functions.patent_handling(x5, ' patent')
    c5 = '  status post bilateral lung transplantation.bilateral chest tubes remains in place '
    assert o5==c5
    
    x6 = ' patent central airways with debris within the trachea '
    _, o6 = rule_functions.patent_handling(x6, ' patent')
    c6 = '  with debris within the trachea '
    assert o6==c6
    print('Passed test_patent_handling()')

def test_clear_handling():
    x1 = ' the right lung remains clear '
    _, o1 = rule_functions.clear_handling(x1, ' clear')
    c1 = ' '
    assert c1==o1
    
    x2 = ' the central airways are clear status post bilateral lung transplantation '
    _, o2 = rule_functions.clear_handling(x2, ' clear')
    c2 = ' status post bilateral lung transplantation '
    assert c2==o2
    
    x3 = ' central airways are clear with normal caliber of the left bronchial anastomosis status post solitary left lung transplant '
    _, o3 = rule_functions.clear_handling(x3,' clear')
    c3 = ' status post solitary left lung transplant '
    assert c3==o3
    print('Passed test_clear_handling()')

def test_subcentimeter_handling():
    #Don't change the sentence if the word 'node' is not present after the word 'subcentimeter'
    x1 = ' enlarged lymph node and subcentimeter nodules in the left lung ' #made up
    _, o1 = rule_functions.subcentimeter_handling(x1, ' subcentimeter')
    c1 = ' enlarged lymph node and subcentimeter nodules in the left lung '
    assert o1==c1
    
    x2 = '1.3 cm pretracheal lymph node unchanged there are a few other subcentimeter lymph nodes which are not changed from prior'
    _, o2 = rule_functions.subcentimeter_handling(x2, ' subcentimeter')
    c2 = '1.3 cm pretracheal lymph node unchanged there are a few others which are not changed from prior'
    assert o2==c2
    
    x3 = '1.5 cm mediastinal lymph node and a subcentimeter lymph node' #made up
    _, o3 = rule_functions.subcentimeter_handling(x3, ' subcentimeter')
    c3 = '1.5 cm mediastinal lymph node and a'
    assert o3==c3
    print('Passed test_subcentimeter_handling()')

if __name__=='__main__':
    test_nodulegr1cm_handling()
    test_lymphadenopathy_handling()
    test_delete_mainword()
    test_delete_part()
    test_delete_part_until()
    test_delete_entire_unless_immediate()
    test_delete()
    test_delete_if_first_word()
    test_non_handling()
    test_patent_handling()
    test_clear_handling()
    test_subcentimeter_handling()
    