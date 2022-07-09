#test_load.py
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

import unittest
import pandas as pd

from src import load

class TestLoad(unittest.TestCase):
    def test_load_expand_by_indication(self):
        s = ('rpt ct chest wo contrast w 3d mips protocol date %date facility'+
            ' duh chest ct without contrast indication 401.9 unspecified essential'+
            ' hypertension 272.4 other and unspecified hyperlipidemia 424.1 aortic'+
            ' valve disorders 414.00 coronary atherosclerosis of unspecified type of'+
            ' vessel native or graft 428.22 chronic systolic heart failure 453.40'+
            ' acute venous embolism and thrombosis of unspecified deep vessels of'+
            ' lower extremity 416.8 other chronic pulmonary heart diseases 585.9'+
            ' chronic kidney diseas comparison none available protocol volumetric'+
            ' non contrast chest ct was performed from the lower neck through the'+
            ' adrenal glands')
        x = pd.DataFrame([['s','There is a nodule in the upper lobe','12345','Findings'],
                          ['s',s,'5678','Findings'],
                          ['h','There is no pneumonia','494949','Impression']],
            columns=['Label','Sentence','Filename','Section'])
        output = load.expand_by_indication(x)
        correct = pd.DataFrame(
            [['s','There is a nodule in the upper lobe','12345','Findings'],
            ['h','There is no pneumonia','494949','Impression'],
            ['s','unspecified essential hypertension','5678','Findings'],
            ['s','other and unspecified hyperlipidemia','5678','Findings'],
            ['s','aortic valve disorders','5678','Findings'],
            ['s','coronary atherosclerosis of unspecified type of vessel native or graft','5678','Findings'],
            ['s','chronic systolic heart failure','5678','Findings'],
            ['s','acute venous embolism and thrombosis of unspecified deep vessels of lower extremity','5678','Findings'],
            ['s','other chronic pulmonary heart diseases','5678','Findings'],
            ['s','chronic kidney diseas','5678','Findings'],
            ['s','none available','5678','Findings'],
            ['s','volumetric non contrast chest ct was performed from the lower neck through the adrenal glands','5678','Findings']],
            columns=['Label','Sentence','Filename','Section'])
        assert output.equals(correct)
        print('Passed test_load_expand_by_indication()')

if __name__=='__main__':
    unittest.main()