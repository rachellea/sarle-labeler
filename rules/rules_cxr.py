#rules_cxr.py
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

from . import rule_functions as fxn

###################################
# Specific Rules for Chest X-Rays #---------------------------------------------
###################################
RULES_ORDER_CXR_AMBPOS = [' not ',' no ',' absent ',' unobserved ',' unremarkable ',
               ' within normal limits ', ' normal ',' without ',' free of ', ' negative for ',
               ' clear of ',' clearing of ',' without evidence of ',' resolution of ', ' removal of ',
               ' removed ']

RULES_DEF_CXR_AMBPOS = {' not ':{'function':fxn.delete},
    ' no ':{'function':fxn.delete},
    ' absent ':{'function':fxn.delete},
    ' unobserved ':{'function':fxn.delete},
    ' unremarkable ':{'function':fxn.delete},
    ' within normal limits ':{'function':fxn.delete},
    ' normal ':{'function':fxn.delete},
    ' without ':{'function':fxn.delete},
    ' free of ':{'function':fxn.delete},
    ' negative for ':{'function':fxn.delete},
    ' clear of ':{'function':fxn.delete},
    ' clearing of ':{'function':fxn.delete},
    ' without evidence of ':{'function':fxn.delete},
    ' resolution of ':{'function':fxn.delete},
    ' removal of ':{'function':fxn.delete},
    ' removed ':{'function':fxn.delete}}

AMB_ORDER =['not excluded','cannot be excluded','versus','vs',' or ','andor',
            'concerning for','concern for','suspicious for', 'suspected',
            'probab','may','suggest','could be','question','cannot exclude',
            'ill-defined','ill defined','poorly-defined','poorly defined',
            'differential','vague','perhaps','possibly','possible']

AMB_DEF = {'not excluded':{'function':fxn.delete},
           'cannot be excluded':{'function':fxn.delete},
           'versus':{'function':fxn.delete_one_before_mainword},
           'vs':{'function':fxn.delete_one_before_mainword},
           ' or ':{'function':fxn.delete_one_before_mainword},
           'andor':{'function':fxn.delete_one_before_mainword},
           'concerning for':{'function':fxn.delete_part,'delete_part':'after'},
           'concern for':{'function':fxn.delete_part,'delete_part':'after'},
           'suspicious for':{'function':fxn.delete_part,'delete_part':'after'},
            'suspected':{'function':fxn.delete_part,'delete_part':'after'},
            'probab':{'function':fxn.delete_part,'delete_part':'after'},
            'may':{'function':fxn.delete_part,'delete_part':'after'},
            'suggest':{'function':fxn.delete_part,'delete_part':'after'},
            'could be':{'function':fxn.delete_part,'delete_part':'after'},
            'question':{'function':fxn.delete_part,'delete_part':'after'},
            'cannot exclude':{'function':fxn.delete_part,'delete_part':'after'},
            'ill-defined':{'function':fxn.delete_part,'delete_part':'after'},
            'ill defined':{'function':fxn.delete_part,'delete_part':'after'},
            'poorly-defined':{'function':fxn.delete_part,'delete_part':'after'},
            'poorly defined':{'function':fxn.delete_part,'delete_part':'after'},
            'differential':{'function':fxn.delete_part,'delete_part':'after'},
            'vague':{'function':fxn.delete_part,'delete_part':'after'},
            'perhaps':{'function':fxn.delete_part,'delete_part':'after'},
            'possibly':{'function':fxn.delete_part,'delete_part':'after'},
            'possible':{'function':fxn.delete_part,'delete_part':'after'}}

RULES_ORDER_CXR_AMBNEG = RULES_ORDER_CXR_AMBPOS + AMB_ORDER

RULES_DEF_CXR_AMBNEG = {}
for dictionary in [RULES_DEF_CXR_AMBPOS, AMB_DEF]:
    for key in list(dictionary.keys()):
        RULES_DEF_CXR_AMBNEG[key] = dictionary[key]