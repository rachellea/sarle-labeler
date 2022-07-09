#test_gr1cm.py
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

from src.vocab import gr1cm

class TestGreaterThanOneCentimeter(unittest.TestCase):
    def test_nodulegr1cm_handling(self):
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
        
    def test_lymphadenopathy_handling(self):
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

if __name__=='__main__':
    unittest.main()