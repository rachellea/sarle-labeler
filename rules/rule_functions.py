#rule_functions.py
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

def delete_mainword(sentence, mainword, **kwargs): #Done with testing
    if mainword not in sentence:
        return False, sentence
    return True, sentence.replace(mainword,'')

def delete_part(sentence, delete_part, mainword, **kwargs): #Done with testing
    """Delete all words in the sentence coming either <delete_part>='before'
    or <delete_part>='after'"""
    if mainword not in sentence:
        return False, sentence
    senthalved = sentence.split(mainword)
    if delete_part == 'after':
        return True, senthalved[0]
    if delete_part == 'before':
        #if the word occurs more than once then we want to make sure we delete
        #everything before the LAST occurrence
        return True, senthalved[-1]

def delete_part_until(sentence, delete_part, mainword, until_hit, **kwargs): #Done with testing
    """Delete all words in the sentence coming either <delete_part>='before'
    or <delete_part>='after' the <mainword> until you hit any words in the
    list <until_hit>"""
    if mainword not in sentence:
        return False, sentence
    senthalved = sentence.split(mainword)
    if delete_part == 'after':
        keep = senthalved[0] #defintely keep before
        dregs = senthalved[1] #you may keep some of 'after'
        idx = len(dregs)
        for u in until_hit:
            d = dregs.find(u)
            if d < idx and d!=-1:
                idx = d
        keep2 = dregs[idx:]
        return True, keep+' '+keep2
    if delete_part == 'before':
        keep = senthalved[1]
        dregs = senthalved[0]
        idx = 0
        for u in until_hit:
            d = dregs.find(u)+len(u) #len(u) because we don't want to delete u
            if d > idx and d!=-1:
                idx = d
        keep2 = dregs[0:idx]
        return True, keep2+keep #don't need a space because one will already be included

def delete_entire_unless_immediate(sentence, mainword, position, wrange, unless_in, **kwargs): #Done with testing
    """Delete entire sentence if <mainword> is present, unless any of the words
    in the list <unless_in> are present within <wrange> of position=='before' or
    position=='after' the mainword in which case keep the entire sentence."""
    if mainword not in sentence:
        return False, sentence
    if position == 'after':
        if sentence.split()[-1]==mainword.strip(): #mainword is the last word so sentence can't be saved (no words after)
            return True, '' 
        possible_save_words = ' '.join(sentence.split(mainword)[1].split()[0:wrange])
    elif position == 'before':
        if sentence.split()[0]==mainword.strip(): #mainword is the first word so sentence can't be saved (no words before)
            return True, ''
        possible_save_words = ' '.join(sentence.split(mainword)[0].split()[-1*wrange:])
    #Check if any word in unless_in is a root of possible_save_word        
    saved = False
    for u in unless_in:
        if u in possible_save_words:
            saved = True    
    if saved:
        return False, sentence
    else:
        return True, ''

def delete(sentence, mainword, **kwargs): #Done with testing
    """Delete entire sentence if <mainword> is present"""
    if mainword not in sentence:
        return False, sentence
    else:
        return True, ''

def delete_if_first_word(sentence, mainword, **kwargs): #Done with testing
    """Delete entire sentence if exactly <mainword> is the first word"""
    if mainword not in sentence: #e.g. if sentence=='' due to prior processing
        return False, sentence
    if mainword == sentence.split()[0]:
        return True, ''
    else:
        return False, sentence

def delete_one_before_mainword(sentence, mainword, **kwargs):
    """Delete every word starting from (and including) one word before
    <mainword>. Used in ambiguity detection e.g. 'there is scarring vs
    atelectasis' -->mainword 'vs' --> 'there is' (delete both scarring and
    atelectasis)"""
    if mainword in sentence:
        s = sentence.split(mainword)[0].split()
        return True, (' ').join(s[0:-1])
    else:
        return False, sentence

def non_handling(sentence, mainword, **kwargs): #Done with testing
    """Delete any word that starts with 'non' or delete any word that comes
    immediately after the standalone word 'non'. Prevents the term search
    from making mistakes on words like noncalcified, nontuberculous,
    noninfectious, etc."""
    if 'non' not in sentence:
        return False, sentence
    else:
        sentlist = sentence.split()
        if ' non ' in sentence: #i.e., standalone word ' non '
            idx = sentlist.index('non')
            return True, ' '+' '.join(sentlist[0:idx]+sentlist[idx+2:])+' '
        else: #non is prefixing another word
            for word in sentlist:
                if 'non' in word:
                    sentlist.remove(word)
            return True, ' '+' '.join(sentlist)+' '

def patent_handling(sentence, mainword, **kwargs): #Done with testing
    """Function for handling the word 'patent' """
    assert mainword==' patent'
    if 'patent' not in sentence:
        return False, sentence
    sentlist = sentence.split()
    if sentlist[0]=='patent':
        return delete_part_until(sentence, delete_part = 'after',mainword = 'patent', until_hit = ['status','with'])
    else: #patent is at the middle or the end of the sentence
        return delete_part(sentence, delete_part = 'before',mainword = 'patent')

def clear_handling(sentence, mainword, **kwargs): #Done with testing
    """Function for handling the word 'clear' """
    assert mainword==' clear'
    if ' clear' not in sentence:
        return False, sentence
    changed1, sentence = delete_part(sentence, delete_part='before',mainword=mainword)
    sentence = ' clear '+sentence #must keep word 'clear' at the beginning of the fragment so that the next step can work
    changed2, sentence = delete_part_until(sentence, delete_part='after',mainword=mainword,until_hit=['status'])
    return (changed1 or changed2), sentence

def subcentimeter_handling(sentence, mainword, **kwargs): #Done with testing
    """Example:
    'a few scattered subcentimeter lymph nodes are visualized not
    significantly changed from prior' --> 'a few scattered are visualized not
    significantly changed from prior'
    """
    assert mainword==' subcentimeter'
    if mainword not in sentence:
        return False, sentence
    if 'node' in ' '.join(sentence.split(mainword)[1:]):
        pre_idx = sentence.rfind(' subcentimeter')
        pre = sentence[0:pre_idx]
        post_idx = sentence.rfind('node')+len('node')
        post = sentence[post_idx:]
        sentence = pre+post
        return True, sentence
    else:
        return False, sentence