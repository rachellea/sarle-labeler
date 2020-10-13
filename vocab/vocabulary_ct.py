#vocabulary_ct.py
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

import copy
from . import vocabulary_locations as loc

########################
# Lung Pathology Terms #--------------------------------------------------------
########################
#This lung pathology consists of findings that can ONLY be found in the lungs
#by its very nature, e.g. pneumonia is by definition ONLY a lung disease. It is
#critical that LUNG_PATHOLOGY contains only lung-specific pathology because
#the presence of any of these pathological findings is used to assume that
#the location of the lungs is abnormal. (That is why you won't find 'nodule'
#in this list, and instead you'll find 'nodule' in the GENERIC_PATHOLOGY
#section. The presence of 'nodule' does NOT necessarily imply a lung abnormality,
#as the nodule may be in the liver, for example.)
LUNG_PATHOLOGY = {
            #Lung textures (e.g. for opacities and nodules, e.g. groundglass nodule, groundglass opacity)
            'bandlike_or_linear':{'Any':['bandlike','band like','band-like','linear']},
            'groundglass':{'Any':['groundglass','ground glass','ground-glass']},
            'honeycombing':{'Any':['honeycomb']},
            'reticulation':{'Any':['reticula']}, #reticular, reticulated, reticulation
            'tree_in_bud':{'Any':['tree-in-bud','tree in bud']},
            #Diseases and abnormalities:
            'airspace_disease':{'Any':['airspace disease','copd','chronic obstructive'],
                'Term1':['airspace','air-space','airway']+loc.LUNG_TERMS,'Term2':['disease']}, #airways disease
            'air_trapping':{'Any':['air trapping']},
            'aspiration':{'Any':['aspirat']}, #aspiration
            'atelectasis':{'Any':['atelecta'], #atelectasis, atelectases, atelctatic
                'Term1':loc.LUNG_TERMS,'Term2':['collapse']},
            'bronchial_wall_thickening':{'Any':['bronchial wall thicken'],'Term1':['bronch'],'Term2':['thicken']}, #bronchial thickening
            'bronchiectasis':{'Any':['bronchiecta']}, #iectases, iectasis, iectatic
            'bronchiolectasis':{'Any':['bronchiolecta']},
            'bronchiolitis':{'Any':['bronchiolitis']},
            'bronchitis':{'Any':['bronchitis']},
            'emphysema':{'Any':['emphysem','blister','bulla','bullous']}, #emphysema, emphysematous, bulla, bullae
            'hemothorax':{'Any':['hemothora','hemopneumothora']}, #thorax, thoraces
            'interstitial_lung_disease':{'Any':['interstitial lung disease','interstitial disease',
                    'interstitial pneumonia',' uip ',' ild ','fibrosis',' ipf ',' nsip ',
                    'interstitial pneumonitis','hypersensitivity pneumonitis','organizing pneumonia',
                    'sarcoidosis'],'Exclude':loc.EXCLUDE_NONLUNG}, #Exclude non-lung terms because we don't want to pick up on liver fibrosis or heart fibrosis
            'lung_resection':{'Any':['pneumonectomy','lobectomy','bronchial stump'],
                'Term1':['resect'], 'Term2':loc.LUNG_TERMS},
                #resection, resected (e.g. 'wedge resection of the lower lobe')
            'mucous_plugging':{'Any':['mucous plug','mucus plug']}, #mucous plug(s), plugging
            'pleural_effusion':{'Any':['effusion','pleural effusion','pleural fluid','basilar fluid','lower lobe fluid','fissural fluid'], #groundtruth #DO NOT DELETE PLEURAL EFFUSION
                'Term1':['pleura'], 'Term2':['fluid'],'Exclude':['pericardial']},
            'pleural_thickening':{'Any':['pleural thick'], 'Term1':['pleura'], 'Term2':['thicken']},
            'pneumonia':{'Any':['pneumonia','pneumoniae']}, #pneumonia, pneumoniae. Can't do 'pneumoni' because that also hits 'pneumonitis'
            'pneumonitis':{'Any':['pneumonitis']},
            'pneumothorax':{'Any':['pneumothora']}, #pneumothorax, pneumothoraces, hydropneumothorax
            'pulmonary_edema':{'Any':['edema']},
            'septal_thickening':{'Any':['septal thickening']},
            'tuberculosis':{'Any':['tubercul']} #tuberculous, tuberculosis, tuberculoses. nontuberculous excluded with sentence rules for 'non'
    }

#Subset of GENERIC_PATHOLOGY that is allowed in the lung:
LUNG_ALLOWED_PATH = ['calcification','cancer','catheter_or_port','cavitation',
    'clip','congestion','consolidation','cyst','debris','density','fibrosis',
    'granuloma','infection','infiltrate','inflammation','lesion','lucency',
    'lymphadenopathy','mass','nodule','nodulegr1cm','opacity','plaque',
    'postsurgical','scarring','scattered_calc','scattered_nod','secretion',
    'soft_tissue','staple','stent','suture','transplant','chest_tube',
    'tracheal_tube']

#########################
# Heart Pathology Terms #-------------------------------------------------------
#########################
#HEART_PATHOLOGY includes pathology that by definition can only be found in
#the heart. It is crtiical that HEART_PATHOLOGY contains only heart-specific
#pathology because the presence of any of these pathological findings is used
#to assume that the location of the heart is abnormal.
HEART_PATHOLOGY = {'cabg':{'Any':[' cabg ','bypass']}, #coronary artery bypass graft/grafting/grafts/surgery, bypass grafting, coronary bypass
        'cardiomegaly':{'Any':['cardiomegaly'],'Term1':['large', 'increase','prominent',' dilat'],
                        'Term2':['cardiac','heart','ventric','atria','atrium']},
        'coronary_artery_disease':{'Any':['coronary artery','coronary arterial'],
                'Term1':['coronary'],'Term2':['disease','calci','atheroscl']},
                #coronary artery disease/calcium. if coronary arteries are mentioned in a sick sentence, they're sick!
        'heart_failure':{'Any':['heart failure'],
                'Term1':['failure'],'Term2':['cardiac','heart','ventric','atria','atrium']},
        'heart_valve_replacement':{'Any':['valve replacement'],
                'Term1':['aortic','mitral','tricupsid','pulmonary','bicuspid','pulmonic'],
                'Term2':['replacement','prosthe','replaced']}, #prosthesis, prosthetic
        'pacemaker_or_defib':{'Any':['pacemaker',' pacer ','pacing device','leads',' icd ','defibr']},
        'pericardial_effusion':{'Any':['pericardial effusion','pericardial fluid'], #groundtruth
            'Term1':['pericardi'], 'Term2':['fluid','effusion']},
        'pericardial_thickening':{'Any':['pericardial thicken'], 'Term1':['pericardi'], 'Term2':['thicken']},
        'sternotomy':{'Any':['sternotomy']}
    }

#Subset of GENERIC_PATHOLOGY that is allowed in the heart
HEART_ALLOWED_PATH = ['atherosclerosis','calcification','catheter_or_port','clip',
                      'congestion','density','fibrosis','plaque','postsurgical',
                      'scarring','scattered_calc','staple','stent','suture','transplant']

#############################
# Great Vessel Allowed Path #---------------------------------------------------
#############################
#Subset of GENERIC_PATHOLOGY that is allowed in the great vessels
GREAT_VESSEL_ALLOWED_PATH = ['atherosclerosis','aneurysm','calcification',
                             'catheter_or_port','clip','dilation_or_ectasia',
                             'plaque','postsurgical','scarring','scattered_calc',
                             'stent','staple','suture']

###########################
# Generic Pathology Terms #-----------------------------------------------------
###########################
GENERIC_PATHOLOGY = {
        'arthritis':{'Any':['arthritis','arthritic','degenerative']},
        'atherosclerosis':{'Any':['atheroscler']}, #osis, otic
        'aneurysm':{'Any':['aneurysm']}, #aneurysm, aneurysmal
        'breast_implant':{'Any':[], 'Term1':['implant','prosthesis','prostheses'], 'Term2':['breast']},
        'breast_surgery':{'Any':['mastectomy','lumpectomy']},
        'calcification':{'Any':['calcifi','calcium']}, #calcification, calcified. Deliberately excludes 'calculus'. noncalcified excluded with sentence rules for 'non'
        'cancer':{'Any':['cancer','metasta','tumor','malignan','carcinoma','neoplas',
                         'sarcoma','blastoma','cytoma','melanoma','lymphoma','mesothelioma',
                         'myeloma','mycetoma']},
            #cancer, cancerous, metastasis, metastases, metastatic,
            #malignancy, malignant, carcinoma, carcinomatous, carcinomatosis, neoplasm, neoplastic
            #myxofibrosarcoma, liposarcoma, neuroblastoma, plasmocytoma
        'catheter_or_port':{'Any':['catheter',' cath ','picc','venous line',' port ']},
            #port needs spaces around it so it doesn't catch 'portion'
            #don't use 'tip' because that will get the tips of gj tubes etc.
        'cavitation':{'Any':['cavitation','cavitary','cavity']},
        'clip':{'Any':['clip']},
        'congestion':{'Any':['congest']},
        'consolidation':{'Any':['consolid']},
            #consolidation, consolidative #groundtruth (DO NOT DELETE GENERIC CONSOLIDATION)
        'cyst':{'Any':[' cyst ',' cysts ',' cystic '], 'Exclude':['cystic fibrosis']}, #cyst, cystic
        'debris':{'Any':['debris']}, #esp. in airways
        'deformity':{'Any':['deform']}, #deformity, deformed, deformation
        'density':{'Any':['density','densities']},
        'dilation_or_ectasia':{'Any':[' dilat','ectasia',' ectatic ']},
            #diverse category for different structures, e.g. ectatic aorta, dilated ventricle. dilation, dilated, dilatation.
            #need spaces around ectatic to avoid confusion with atelectatic.
        'distention':{'Any':['disten']}, #e.g. distended stomach. distended, distention.
        'fibrosis':{'Any':['fibrosis','fibrotic','fibroses','fibrosing']},
        'fracture':{'Any':['fracture']}, #fracture, fractures, fractured
        'granuloma':{'Any':['granuloma']}, #granuloma, granulomatous. Not to be confused with 'granulation' which is different
        'hardware':{'Any':['hardware']}, #e.g. spinal hardware
        'hernia':{'Any':['hernia']},
        'infection':{'Any':['infect']}, #infection, infected, infective. noninfectious excluded with sentence rules for 'non'
        'infiltrate':{'Any':['infiltrat']}, #infiltrate, infiltrates, infiltration (can be in lungs, pancreas, liver, etc.)
        'inflammation':{'Any':['inflam']}, #inflammation, inflammatory, inflamed
        'lesion':{'Any':['lesion']}, #lesion(s)
        'lucency':{'Any':['lucency','lucencies']},
        'lymphadenopathy':{'Any':['adenopathy']}, #Note: there is a special function below that captures things like '2.5 cm node'
        'mass':{'Any':['mass']}, #mass, masses #groundtruth (DO NOT DELETE GENERIC MASS)
        'nodule':{'Any':['nodul']}, #nodule, nodular, nodularity #groundtruth (DO NOT DELETE GENERIC NODULE)
        'nodulegr1cm':{'Any':[]}, #Note: there is a special function to compute this label
        'opacity':{'Any':['opaci']}, #opacity, opacities, opacification #groundtruth (DO NOT DELETE GENERIC OPACITY)
        'plaque':{'Any':['plaque']}, #note that pleural plaque and vessel (atherosclerotic) plaque are not the same
        'postsurgical':{'Any':['surgical','status post','surgery','postoperative', 'post operative']},
            #postsurgical findings/changes, 'post surgical', prior surgery
        'scarring':{'Any':['scar']}, #scar, scarring, scarred
        'scattered_calc':{'Any':[],'Term1':['scatter'],'Term2':['calcifi']},
        'scattered_nod':{'Any':[],'Term1':['scatter'],'Term2':['nodul','node']}, #e.g. scattered nodules, scattered nodes
        'secretion':{'Any':['secretion','secrete']}, #esp in airways
        'soft_tissue':{'Any':['soft tissue']},#e.g. 'soft tissue nodule' in the lungs, e.g. 'soft tissue in the mediastinum'
        'staple':{'Any':['staple','stapling']}, #staple(s)
        'stent':{'Any':[' stent']}, #need space in front of stent to distinguish it from 'consistent'
        'suture':{'Any':['suture']},
        'transplant':{'Any':['transplant']}, #diverse category: lung transplant, heart transplant, liver transplant, etc
        #Tubes
        'chest_tube':{'Any':['chest tube']},
        'tracheal_tube':{'Any':['tracheal tube','tracheostomy tube']},
        'gi_tube':{'Any':['nasogastric tube','ng tube','gastrojejunostomy tube',
                          'gastric tube','esophageal tube','gj tube',
                          'enteric tube','feeding tube','gastrostomy tube']}
    }


#############
# Functions #-------------------------------------------------------------------
#############
def return_lung_terms():
    return loc.LUNG_LOCATION_TERMS, LUNG_PATHOLOGY

def return_heart_terms():
    return HEART_PATHOLOGY

def return_generic_terms():
    return GENERIC_PATHOLOGY
