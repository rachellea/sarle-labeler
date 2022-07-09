#gr1cm.py
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

"""Rules for abnormalities that are defined based on being > 1 cm in size
and therefore require searching the sentences for mm and cm measurements"""

def lymphadenopathy_handling(sentence): #Done with testing
    """Return 1 if lymphadenopathy is present in the sentence else return 0."""
    if 'adenopathy' in sentence: #adenopathy, lymphadenopathy
        return 1
    if ' node' not in sentence and ' nodal' not in sentence:
        return 0
    if 'large' in sentence: #note that you already know 'node' or 'nodal' is present
        #e.g. 'enlarged lymph node,' 'enlarged prevascular lymph node'
        #'mild mediastinal nodal enlargement'
        return 1
    
    #If you're still in this function, now try to find a measurement
    return measures_gr_1_cm(senthalved=sentence.split('node'))

def nodulegr1cm_handling(sentence): #Done with testing
    """Return 1 if a nodule greater than 1 cm is present"""
    if 'nodul' not in sentence:
        return 0
    return measures_gr_1_cm(senthalved=sentence.split('nodul'))

def measures_gr_1_cm(senthalved):
    """Return 1 if the object in the sentence fragment measures greater than
    1 cm else return 0"""
    size = 0.0
    try:
        if 'cm' in senthalved[0]: #e.g. '1.5 cm paratracheal lymph node'
            size = float(senthalved[0].split('cm')[0].split()[-1])
        elif 'mm' in senthalved[0]:
            size = float(senthalved[0].split('mm')[0].split()[-1])/10
        #Check the second half of the sentence AFTER you've checked the first half
        #so that you correctly handle both these kinds of sentences:
        #'0.8 cm pretracheal lymph node which previously measured 0.6 cm' (you'll catch
        #the current measurement instead of the previous one)
        #'stable right precarinal lymph node that measures 1.2 cm in short axis' (you'll
        #catch the measurement)
        elif 'cm' in senthalved[1] and 'measur' in senthalved[1]: #e.g. 'lymph node measuring up to 1.3 cm'
            size = float(senthalved[1].split('cm')[0].split()[-1])
        elif 'mm' in senthalved[1] and 'measur' in senthalved[1]:
            size = float(senthalved[1].split('mm')[0].split()[-1])/10
    except: #weird situation, e.g. the word that comes before cm or mm isn't a number
        size = 0.0
    if size > 1.0:
        return 1
    else:
        return 0
    
    