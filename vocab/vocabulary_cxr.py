#vocabulary_cxr.py
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

from . import vocabulary_locations as loc

########################
# Lung Pathology Terms #--------------------------------------------------------
########################
LUNG_PATHOLOGY = {
         'airspace_disease':{'Any':['airspace disease','copd'], 'Term1':['airspace','air-space']+loc.LUNG_TERMS, 'Term2':['disease']},
         'atelectasis':{'Any':['atelectasis', 'atelectases', 'atelectatic'], 'Term1':loc.LUNG_TERMS,'Term2':['collapse']},
         'blister':{'Any':['blister','bullae','bullous']},
         'bronchiectasis':{'Any':['bronchiectas']}, #bronchiectases, bronchiectasis
         'bronchiolitis':{'Any':['bronchiolitis']},
         'bronchitis':{'Any':['bronchitis']},
         'consolidation':{'Any':['consolidation']},
         'costophrenic_blunting':{'Any':[], 'Term1':['costophrenic'], 'Term2':['blunt', 'obscured']}, #blunt, blunting, obscured
         'cystic_fibrosis':{'Any':['cystic fibrosis']},
         'emphysema':{'Any':['emphysem']}, #emphysema, emphysematous
         'hyperdistention':{'Any':['hyperdisten','hyperexpan','hyperaer','hyperinfl']}, #hyperdistention, hyperdistended, etc.
         'hyperlucent':{'Any':['hyperluc']}, #hyperlucent, hyperlucency
         'hypoinflation':{'Any':['hypoinflat','hypovol','hypoventila','low lung volume','low volume'], 'Term1':['low'], 'Term2':['volume']}, #hypoinflation, hypoinflated, hypovolemia, hypovolemic
         'infiltrate':{'Any':['infiltrat']}, #infiltrate, infiltrates, infiltration
         'interstitial_lung_disease':{'Any':['interstitial disease','interstitial lung disease'], 'Term1':['interstit'], 'Term2':['disease']+loc.LUNG_TERMS}, #interstitial, interstitium
         'lucency_lung':{'Any':[], 'Term1':[' lucency '], 'Term2':loc.LUNG_TERMS},
         'lung_blood_vessels':{'Any':[], 'Term1':['blood','vessel'], 'Term2':['prominent']},
         'lung_markings':{'Any':['bronchovascular crowd'], 'Term1':['mark ','marks','marking'], 'Term2':loc.LUNG_TERMS},
         'lung_misc':{'Any':[], 'Term1':['obscured','azygous','prominent','small','tortuous'],'Term2':['thorax','trachea']+loc.LUNG_TERMS},
         'pleural_effusion':{'Any':['effusion','pleural fluid'], 'Term1':['pleura'], 'Term2':['fluid'], 'Exclude':['pericardial']},
         'pleura_abnormal':{'Any':[], 'Term1':['thick','blunted','abnormal'], 'Term2':['pleura']},
         'pneumonectomy':{'Any':['pneumonectomy','lobectomy']},
         'pneumoperitoneum':{'Any':['pneumoperitoneum']},
         'pneumonia':{'Any':['pneumonia','pneumoniae']},
         'pneumothorax':{'Any':['pneumothorax','hydropneumothorax','hemopneumothorax']},
         'pulmonary_congestion':{'Any':['pulmonary congestion'], 'Term1':['congestion','prominen'], 'Term2':loc.LUNG_TERMS+['vascular','vasculature']},
         'sulcus_blunting':{'Any':[], 'Term1':['sulcus'], 'Term2':['blunt', 'obscured']},
         'tuberculosis':{'Any':['tubercul']}, #tuberculous, tuberculosis, tuberculoses
         'volume_loss':{'Any':[], 'Term1':['volume'], 'Term2':['loss']}
         }

LUNG_ALLOWED_PATH = (['airspace_disease','atelectasis','blister','bronchiectasis',
         'bronchiolitis','bronchitis','consolidation','costophrenic_blunting',
         'cystic_fibrosis','emphysema','hyperdistention','hyperlucent',
         'hypoinflation','infiltrate','interstitial_lung_disease',
         'lucency_lung','lung_blood_vessels','lung_markings','lung_misc',
         'pleural_effusion','pleura_abnormal','pneumonectomy','pneumoperitoneum',
         'pneumonia','pneumothorax','pulmonary_congestion','sulcus_blunting',
         'tuberculosis','volume_loss']
         +['calcinosis','cavitation','cyst','density','edema','fibrosis',
           'granuloma','mass','nodule','opacity','scarring'])

#########################
# Heart Pathology Terms #-------------------------------------------------------
#########################
HEART_TERMS = ['cardiac','heart','ventricle','atria','atrium']
HEART_PATHOLOGY = {'cardiomegaly':{'Any':['cardiomegaly'], 'Term1':['enlarge', 'large', 'increase','prominent'], 'Term2':HEART_TERMS},
         'cardiac_shadow':{'Any':[], 'Term1':['irregular','obscure'], 'Term2':['cardiac shadow','cardiac silhouette']},
         'heart_failure':{'Any':['heart failure'], 'Term1':['failure'], 'Term2':HEART_TERMS},
         'heart_misc':{'Any':[], 'Term1':['prominent','obscured','small'], 'Term2':HEART_TERMS},
         'pericardial_effusion':{'Any':['pericardial effusion'], 'Term1':['pericardi'], 'Term2':['effusion','fluid']}
    }

HEART_ALLOWED_PATH = ['cardiomegaly','cardiac_shadow','heart_failure',
                      'heart_misc','pericardial_effusion',
                      'atherosclerosis','calcinosis','device','epicardial_fat']

#############################
# Great Vessel Allowed Path #---------------------------------------------------
#############################
GREAT_VESSEL_ALLOWED_PATH = ['aortic_aneurysm','aorta_shape','atherosclerosis','calcinosis','catheter']

###########################
# Generic Pathology Terms #-----------------------------------------------------
###########################
BONE_TERMS = ['humerus','bone','shoulder','rib','clavicle']

GENERIC_PATHOLOGY = {'abdomen_enlarged':{'Any':[],'Term1':['abdomen','abdominal'],'Term2':['large']}, #large, enlarged
         'adipose_tissue':{'Any':['adipose']},
         'aortic_aneurysm':{'Any':[], 'Term1':['aneurysm'], 'Term2':['aort'] }, #aorta, aortic
         'aorta_shape':{'Any':[], 'Term1':['tortuous','obscured','prominent','enlarged','ectasia','unfolding'], 'Term2':['aorta']}, #tortuous, tortuosity
         'arthritis':{'Any':['arthritis','arthritic']},
         'atherosclerosis':{'Any':['atherosclerosis','atherosclerotic']},
         'breast_implant':{'Any':[], 'Term1':['implant'], 'Term2':['breast']},
         'calcinosis':{'Any':['calcifi','calcinosis','calcium'], 'Exclude':['granuloma']}, #calcifications, calcified
         'catheter':{'Any':['catheter','picc']},
         'cavitation':{'Any':['cavitation','cavity']},
         'cholelithiasis':{'Any':['cholelithiasis','gallstone'], 'Term1':['stone'], 'Term2':['gallbladder']},
         'colonic_interposition':{'Any':[], 'Term1':['colonic','colon'], 'Term2':['interpos']}, #interposition, interposed
         'contrast_media':{'Any':['contrast media']},
         'cyst':{'Any':[' cyst ']},
         'deformity':{'Any':['deform'], 'Term1':['scaphoid'], 'Term2':['abdomen']}, #deformity, deformities, deformed
         'degenerative_bone':{'Any':[],'Term1':['degenerat'],'Term2':BONE_TERMS},
         'degenerative_spine':{'Any':[], 'Term1':['degenerat'], 'Term2':['spine','vertebr']}, #vertebrae, vertebra
         'density':{'Any':['density','densities']},
         'device':{'Any':['device','pacemaker','icd','monitor','prosthetic','valve','leads','stimulator','ekg','generator']},
         'diaphragm':{'Any':['diaphrag','eventration']}, #diaphragm, diaphragmatic
         'edema':{'Any':['edema']},
         'epicardial_fat':{'Any':[], 'Term1':['epicardial'],'Term2':['fat']},
         'fibrosis':{'Any':['fibrosis','fibrotic','fibroses']},
         'foreign':{'Any':['foreign body']},
         'fracture':{'Any':['fracture'], 'Term1':['broken'],'Term2':BONE_TERMS},
         'funnel_chest':{'Any':['funnel']},
         'granuloma':{'Any':['granuloma']}, #granuloma, granulomatous
         'hemothorax':{'Any':['hemothorax']},
         'hernia':{'Any':['hernia']},
         'hilum_issue':{'Any':[],'Term1':['prominent','enlarged','lymph node'], 'Term2':['hilum','hilar']},
         'hyperostosis':{'Any':['hyperost']},
         'hypertension':{'Any':['hypertension']},
         'instruments':{'Any':['instrument','clip']}, #instrument, instrumentation
         'kyphosis':{'Any':['kyphosis']},
         'lucency_other':{'Any':[], 'Term1':[' lucency '], 'Term2':['clavicle','diaphragm','ventricle','humerus','mediastinum','retrocardiac','rib','round','thorax']},
         'lymph_nodes_enlarged':{'Any':[], 'Term1':['large'], 'Term2':['lymph','node']},
         'mass':{'Any':['mass']},
         'mastectomy':{'Any':['mastectomy']},
         'mediastinum':{'Any':['mediastin']}, #mediastinum, mediastinal
         'metabolic_bone_disease':{'Any':['metabolic bone disease',
                                'osteoporo', #osteoporosis, osteoporotic
                                'osteomalacia','osteodystroph', #osteodystrophy, osteodystrophic
                                'osteopeni'], #osteopenic, osteopenia
                                   'Term1':['metabolic'],'Term2':BONE_TERMS},
         'nipple_shadow':{'Any':[], 'Term1':['nipple'], 'Term2':['shadow']},
         'nodule':{'Any':['nodule']}, #adding 'nodular' actually makes F-score worse
         'opacity':{'Any':['opacit','opacification']}, #opacity, opacities
         'osteophyte':{'Any':['osteophyte']},
         'pectus_carinatum':{'Any':['carinatum']},
         'pulmonary_artery':{'Any':[], 'Term1':['pulmonary artery'], 'Term2':['enlarged','large','prominent']},
         'rib_issue':{'Any':[],'Term1':['degen','prominent','large','expans','lesion'], 'Term2':['rib']},
         'sarcoidosis':{'Any':['sarcoid']},
         'scarring':{'Any':['cicatrix','scar']}, #scar, scarring
         'sclerosis':{'Any':['scleros','sclerotic']}, #sclerosis, scleroses
         'scoliosis':{'Any':['scoliosis'],'Term1':['spine','spinal'],'Term2':['curvature','curve']},
         'shift':{'Any':[' shift ']},
         'shoulder_issue':{'Any':[], 'Term1':['shoulder','humerus'], 'Term2':['dislocat','degen','prominent']},
         'spine_dislocation':{'Any':[],'Term1':['dislocat'],'Term2':['spine','vertebr']},
         'spinal_fusion':{'Any':[], 'Term1':['spine','spinal','verteb'], 'Term2':['fusion','fused']},
         'spondylosis':{'Any':['spondylosis']},
         'stent':{'Any':['stent']},
         'sutures':{'Any':['suture']},
         'technical_unsatisfactory':{'Any':['limited','body habitus','rotation','rotated',
                                            'underpenetr','technical','image quality','unsatisfactory']},
         'thickening':{'Any':['thicken']},#thickened, thickening
         'tube':{'Any':[' tube ']} #space to distinguish from tuberculosis
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
