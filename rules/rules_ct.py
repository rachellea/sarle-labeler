#rules_ct.py
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

#####################################
# Specific Rules for Chest CT Scans #-------------------------------------------
#####################################
RULES_ORDER_CT = [' no ',' not ',' within normal limits',' normal in',
               ' normal size',' normal',' otherwise unremarkable',' unremarkable',
               ' without',' patent',' resolved',' near complete resolution of',' near resolution of',
               ' resolution of',' clear',' removal of',' removed',' free of',' negative for',
               
               ' nondilated',' nonenlarged','please',' standard',' subcentimeter',
               ' follow up',' nondiagnostic',' reconstructed','recommend','consider',
               'correlate','discuss','discussed','fleischner','screening','non',
               
               'evaluate for','evaluation for','were performed','were likewise performed',
               'was performed','was likewise performed','were obtained','was obtained',
               'were reconstructed','were acquired','awaiting',
               'lung apices to bases without contrast as per ordering physician',
               'was performed from the lower neck to the adrenal glands',
               'procedure routine ct scan of the chest','protocol chest ct wo protocol',
               'ct chest','chest ct',' risk ']

RULES_DEF_CT = {#Stage 1 Rules:
         ' no ':{'function':fxn.delete_part_until,'delete_part':'after','until_hit':['and','change']},
         ' not ':{'function':fxn.delete_entire_unless_immediate,
                 'position':'after','wrange':2,'unless_in':['exclude','change']}, #not with spaces on both sides to avoid 'noted'
         ' within normal limits':{'function':fxn.delete_part,'delete_part':'before'},
         ' normal in':{'function':fxn.delete_part,'delete_part':'before'},
         ' normal size':{'function':fxn.delete_part,'delete_part':'before'},
         ' normal':{'function':fxn.delete},
         ' otherwise unremarkable':{'function':fxn.delete_mainword},
         ' unremarkable':{'function':fxn.delete},
         ' without':{'function':fxn.delete_part,'delete_part':'after'},
         ' patent':{'function':fxn.patent_handling},
         ' resolved':{'function':fxn.delete_entire_unless_immediate,
                      'position':'before','wrange':1,'unless_in':['almost','near','partial','large','essential']},
         #Don't want to delete sentences that say 'near complete resolution of' or 'near resolution of'
         #so we delete those phrases before we do the general 'resolution of' deletion part
         ' near complete resolution of':{'function':fxn.delete_mainword},
         ' near resolution of':{'function':fxn.delete_mainword},
         ' resolution of':{'function':fxn.delete_part,'delete_part':'after'},
         ' clear':{'function':fxn.clear_handling},
         ' removal of':{'function':fxn.delete_part,'delete_part':'after'},
         ' removed':{'function':fxn.delete_part,'delete_part':'before'},
         ' free of':{'function':fxn.delete_part,'delete_part':'after'},
         ' negative for':{'function':fxn.delete},
         
         #Stage 2 Rules:
         ' nondilated':{'function':fxn.delete},
         ' nonenlarged':{'function':fxn.delete},
         'please':{'function':fxn.delete_if_first_word},
         ' standard':{'function':fxn.delete_part_until,'delete_part':'after','until_hit':['with']},
         ' subcentimeter':{'function':fxn.subcentimeter_handling},
         ' follow up':{'function':fxn.delete},
         ' nondiagnostic':{'function':fxn.delete},
         ' reconstructed':{'function':fxn.delete},
         'recommend':{'function':fxn.delete_if_first_word},
         'consider':{'function':fxn.delete_if_first_word},
         'correlate':{'function':fxn.delete_if_first_word},
         'discuss':{'function':fxn.delete_if_first_word},
         'discussed':{'function':fxn.delete_if_first_word},
         'fleischner':{'function':fxn.delete},
         'screening':{'function':fxn.delete},
         'non':{'function':fxn.non_handling},
         
         #Stage 3 Rules (mostly dealing with sentences that appear at the
         #beginning of CT reports, since these sentences are now included)
         'evaluate for':{'function':fxn.delete_part,'delete_part':'after'},
         'evaluation for':{'function':fxn.delete_part,'delete_part':'after'},
         'were performed':{'function':fxn.delete},
         'were likewise performed':{'function':fxn.delete},
         'was performed':{'function':fxn.delete},
         'was likewise performed':{'function':fxn.delete},
         'were obtained':{'function':fxn.delete},
         'was obtained':{'function':fxn.delete},
         'were reconstructed':{'function':fxn.delete},
         'were acquired':{'function':fxn.delete},
         'awaiting':{'function':fxn.delete},
         'lung apices to bases without contrast as per ordering physician':{'function':fxn.delete_mainword},
         'was performed from the lower neck to the adrenal glands':{'function':fxn.delete_mainword},
         'procedure routine ct scan of the chest':{'function':fxn.delete_mainword},
         'protocol chest ct wo protocol':{'function':fxn.delete_mainword},
         'ct chest':{'function':fxn.delete_mainword},
         'chest ct':{'function':fxn.delete_mainword},
         ' risk ':{'function':fxn.delete_part,'delete_part':'after'}
         }
