#vocabulary_locations.py
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

#######################
# Lung Location Terms #---------------------------------------------------------
#######################
#Lobes comment: the unbreakable unit is 'left upper' and not 'upper lobe'
#because we do not want to say all lobes are bad in a sentence that has a list,
#e.g. 'atelectasis in the left upper, right middle, and left lower lobes'
ALL_LOBES = ['all lobes', 'all the lobes','all of the lobes']

UPPER_GENERAL = ALL_LOBES + ['apices','upper lobes','superior lobes','biapical',
                             'bilateral upper lobe','bilateral apical']
LEFT_UPPER = UPPER_GENERAL + ['left upper','left superior','left apex',
                              'left apical','left lung apex','superior left lung',
                              'upper left lung']
RIGHT_UPPER = UPPER_GENERAL + ['right upper','right superior','right apex',
                               'right apical','right lung apex','superior right lung',
                               'upper right lung']

MIDDLE_GENERAL = ALL_LOBES + ['middle lobes']
LEFT_MIDDLE = MIDDLE_GENERAL + ['left middle','lingula'] #lingula includes lingular
RIGHT_MIDDLE = MIDDLE_GENERAL + ['right middle','right horizontal fissure',
                                 'right minor fissure']

LOWER_GENERAL = ALL_LOBES + ['bases','lower lobes','inferior lobes','bibasilar',
                 'bilateral lower lobe','bilateral basilar']
LEFT_LOWER = LOWER_GENERAL + ['left lower','left inferior','left base',
                              'left basilar','left lung base','inferior left lung',
                              'lower left lung','left oblique fissure',
                              'left major fissure']
RIGHT_LOWER = LOWER_GENERAL + ['right lower','right inferior','right base',
                               'right basilar','right lung base','inferior right lung',
                               'lower right lung','right oblique fissure',
                               'right major fissure']

#EACH LUNG:
RIGHT_LUNG = ['bilateral']+RIGHT_UPPER+RIGHT_MIDDLE+RIGHT_LOWER
LEFT_LUNG = ['bilateral']+LEFT_UPPER+LEFT_MIDDLE+LEFT_LOWER

#GENERAL:
LUNG_GENERAL = ['lung','lobe','pulmonary','lingula','pleura','basilar','apical',
                'fissure','fissural'] #fissural captures fissural and perifissural
                #I think I don't need to add 'apex' in here because 'apex' could
                #be referring to a different organ. 'right apex' is already in RUL
                #and 'apex of the right lung' would be caught by 'lung'

#EITHER LUNG:
LUNG_TERMS = RIGHT_LUNG+LEFT_LUNG+LUNG_GENERAL

#EXCLUDE_NONLUNG is for locations: specifically, non-lung locations
EXCLUDE_NONLUNG = ['liver','hepatic','thyroid','caudate','quadrate','pulmonary artery',
           'pulmonary vein','kidney','renal','nephr','gyne','spleen','splenic',
           'humer',' rib','breast','quadrant']
    #quadrant is needed to exclude e.g. 'left upper quadrant' (of the abdomen)
    #'gyne' to exclude 'bilateral gynecomastia'; nephr for 'bilateral nephrolithiasis'

#LOCATIONS:
LUNG_LOCATION_TERMS = {'left_upper':{'Any':LEFT_UPPER,'Term1':['left'],'Term2':['apical'],'Exclude':EXCLUDE_NONLUNG},
        'left_mid':{'Any':LEFT_MIDDLE, 'Exclude':EXCLUDE_NONLUNG},
        'left_lower':{'Any':LEFT_LOWER, 'Term1':['left'], 'Term2':['basilar'], 'Exclude':EXCLUDE_NONLUNG},
        'right_upper':{'Any':RIGHT_UPPER,'Term1':['right'],'Term2':['apical'],'Exclude':EXCLUDE_NONLUNG},
        'right_mid':{'Any':RIGHT_MIDDLE, 'Exclude':EXCLUDE_NONLUNG},
        'right_lower':{'Any':RIGHT_LOWER, 'Term1':['right'],'Term2':['basilar'],'Exclude':EXCLUDE_NONLUNG},
        'right_lung':{'Any':RIGHT_LUNG,'Term1':['right'],'Term2':LUNG_GENERAL,'Exclude':EXCLUDE_NONLUNG}, 
        'left_lung':{'Any':LEFT_LUNG,'Term1':['left'],'Term2':LUNG_GENERAL,'Exclude':EXCLUDE_NONLUNG},
        'lung':{'Any':LUNG_TERMS,'Exclude':EXCLUDE_NONLUNG},
        'airways':{'Any':['trache','bronchi','mainstem','bronchus','central airway',' carina'],'Exclude':EXCLUDE_NONLUNG}
        #trache = trachea, tracheostomy. 'bronchi' = bronchi, bronchioles
    }

########################
# Heart Location Terms #--------------------------------------------------------
########################
HEART_LOCATION_TERMS = {'heart':{'Any':['heart','cardiac','cardio','atrium',
                'atria','ventric','coronary','pericardi','epicardi',' lad ',
                'mitral','bicuspid','aortic valv','aortic annul',
                'aortic_prosthe','tricuspid','pulmonary valv',
                ' cabg ','sternotomy','bypass']}, #ventric = ventricle, ventricular. ' lad ' is for the left anterior descending artery
            'mitral_valve':{'Any':['mitral','bicuspid']}, #mitral valve, valvular, annulus, annular, prosthe
            'aortic_valve':{'Any':['aortic valv','aortic annul','aortic prosthe']}, #valve, valvular. annulus, annular. don't want confusion with the aorta (vessel)
            'tricuspid_valve':{'Any':['tricuspid']},
            'pulmonary_valve':{'Any':['pulmonary valv']}
    }

###############################
# Great Vessel Location Terms #-------------------------------------------------
###############################
GREAT_VESSEL_LOCATION_TERMS = {
        'aorta':{'Any':['aorta','aortic',' arch ']},
                #sometimes aortic arch is just called 'the arch'.
                #Unfortunately this will overlap with aortic valve since
                #both are often mentioned in the same sentence with the same pathology, e.g. calcification.
        'svc':{'Any':['superior vena cava','svc']},
        'ivc':{'Any':['inferior vena cava','ivc']},
        'pulmonary_artery':{'Any':['pulmonary arter']},
        'pulmonary_vein':{'Any':['pulmonary vein']}
    }

########################
# Other Location Terms #--------------------------------------------------------
########################
GENERIC_LOCATION_TERMS = {
    #Generic relative locations
        'right':{'Any':['right','bilateral']},
        'left':{'Any':['left','bilateral']},
        'anterior':{'Any':['anterior']},
        'posterior':{'Any':['posterior']},
        'superior':{'Any':['superior']},
        'inferior':{'Any':['inferior']},
        'medial':{'Any':['medial']},
        'lateral':{'Any':['lateral']},
        'interstitial':{'Any':['interstitial']},
        'subpleural':{'Any':['subpleural']},
        'centrilobular':{'Any':['centrilobular']},
    #Structures
        'thyroid':{'Any':['thyroid']},
        'breast':{'Any':['breast','mastect']},
        'axilla':{'Any':['axilla']}, #axilla, axillary
        'chest_wall':{'Any':['chest wall']},
        'rib':{'Any':['rib']}, #rib, ribs
        'spine':{'Any':['spine','spinal','vertebr',
                        'c1','c2','c3','c4','c5','c6','c7',
                        't1','t2','t3','t4','t5','t6','t7','t8','t9','t10','t11','t12',
                        'l1','l2','l3','l4','l5',
                        's1','s2','s3','s4','s5']}, #e.g. vertebral compression fracture
        'bone':{'Any':['bone','osseous']},
        'mediastinum':{'Any':['mediastin','precarinal','subcarinal']}, #mediastinum, mediastinal
        'diaphragm':{'Any':['hiatus','hiatal','bochdalek','morgagni']}, #mainly for diaphragmatic hernias
        'hilum':{'Any':['hilum','hila']}, #hilar, hila (plural of hilum)
        'abdomen':{'Any':['abdomen','abdominal']},
        'esophagus':{'Any':['esophag']}, #esophageal, esophagus, paraesophageal
        'stomach':{'Any':['stomach','gastro','gastric']},
        'intestine':{'Any':['colon','intestin','duoden','jejun','ileum']}, #colon, colonic, intestine, intestinal
        'liver':{'Any':['liver','hepatic','caudate','quadrate','hepatis']}, #porta hepatis
        'gallbladder':{'Any':['gallbladder','gallstone',' chole']}, #cholecystic, cholelithiasis
        'kidney':{'Any':['kidney',' renal','nephr']}, #space in front of renal to avoid confusion with 'adrenal'. nephrolithiasis
        'adrenal_gland':{'Any':['adrenal','suprarenal']},
        'spleen':{'Any':['spleen','splenic']},
        'pancreas':{'Any':['pancrea']} #pancreas, pancreatic
    }

#TODO in the future, specify exactly which pathology is allowed with exactly
#which locations, for the GENERIC_LOCATION_TERMS (e.g. you cannot have a
#breast_implant located in the thyroid)

#TODO perhaps include a "generic vascular" location (vascular, venous, arterial, etc.)

#TODO perhaps group abdominal organs into 'abdomen' category