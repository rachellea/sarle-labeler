#test_term_search.py
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
import shutil
import unittest
import pandas as pd
import numpy as np

from src import term_search
from src.vocab import vocabulary_ct, vocabulary_locations

from tests import equality_checks as eqc

####################################
# Global Variables Used in Testing #--------------------------------------------
####################################
#for testing obtain_sarle_labels and obtain_sarle_complex_labels
sarle_x = [['000013_CTAAEJ','Findings','findings visualized thyroid within normal limitsleft anterior chest wall pacer with the leads terminating along the left lateral ventricle and right ventricle'],
        ['000013_CTAAEJ','Findings','there is a metallic density likely related to intra aortic balloon pump seen in the descending thoracic aorta'],
        ['000013_CTAAEJ','Findings','the heart is borderline enlarged heart with a prosthetic aortic valve and mitral valve seen as well as aortic calcifications'],
        ['000013_CTAAEJ','Findings','there are multiple scattered adjacent lymph nodes with the largest on the right paratracheal region measuring 2.0 cm series 4 image 25'],
        ['000013_CTAAEJ','Findings','there is diffuse bilateral predominately upper lobe and to less extent bilateral lower lobe nodular groundglass and consolidative opacities which are new from 12 27 %year'],
        ['000013_CTAAEJ','Findings','bilateral moderate volume pleural effusions are slightly increased and there are associated areas of bilateral lower lobe rounded atelectasis'],
        ['000013_CTAAEJ','Findings','multilevel thoracolumbar degenerative changes without suspicious osseous lesions identified'],
        ['000013_CTAAEJ','Impression','new diffuse bilateral upper lobe predominant nodular groundglass opacities in the setting of hemoptysis may represent pulmonary hemorrhage though worsening pulmonary edema or infection may have similar appearance'],
        ['000013_CTAAEJ','Impression','interval increase in moderate bilateral pleural effusions'],
        ['000013_CTAAEJ','Impression','there is by basilar rounded atelectasis'],
        ['000013_CTAAEJ','Impression','metallic density in the descending thoracic aorta likely represents intra aortic balloon pump'],
        
        ['000022_CTAAES','Findings','lungs there is extensive parenchymal opacification including all lobes'],
        ['000022_CTAAES','Findings','abnormal bronchi within these areas'],
        ['000022_CTAAES','Findings','pleura moderate right effusion unchanged mediastinum limited visualization without iv contrast'],
        ['000022_CTAAES','Findings','mediastinal lymph node prominence aortic arch is on the right side congenital variant of normal'],
        ['000022_CTAAES','Impression','extensive right sided parenchymal opacity unchanged prior outside study december 21 %year'],
        ['000022_CTAAES','Impression','overall appearance compatible with chronic change'],
        ['000022_CTAAES','Impression','this may all be related to prior radiation treatment'],
        ['000022_CTAAES','Impression','underlying residual or recurrent neoplasm needs to be considered'],
        ['000022_CTAAES','Impression','moderate right pleural effusion about the same'],
        ['000022_CTAAES','Impression','mediastinal lymph node prominence as on prior studies'],
        
        ['000038_CTAAFI','Findings','swan ganz ganz catheter with tip in the right pulmonary artery'],
        ['000038_CTAAFI','Findings','right arm picc with tip in the lower svc'],
        ['000038_CTAAFI','Findings','mild cardiomegaly with biatrial enlargement left greater than right'],
        ['000038_CTAAFI','Findings','multiple small mediastinal lymph nodes are present the largest measuring 9 mm in short axis series 2 image 22 anterior to the lower trachea'],
        ['000038_CTAAFI','Findings','a few partially calcified lymph nodes within the left axilla may represent sequelae from prior granulomatous disease versus prior treated disease'],
        ['000038_CTAAFI','Findings','tiny punctate calcifications about the pancreatic head and tail may be within small vessels'],
        ['000038_CTAAFI','Findings','additional calcification within the spleen series 2 image 60 likely sequela of prior granulomatous infection'],
        ['000038_CTAAFI','Findings','small focus of ill defined sclerosis within the anterolateral right seventh rib series 2 image 41'],
        ['000038_CTAAFI','Findings','old healing fracture of the posterolateral left seventh rib series 2 image 34'],
        ['000038_CTAAFI','Findings','partial resection of the anterior left fifth rib'],
        ['000038_CTAAFI','Findings','reticular groundglass pleural based opacities with intralobular septal thickening primarily centered within the left upper lobe about the prior resection site but to a lesser degree within the left lower lobe right middle lobe and right lower lobe'],
        ['000038_CTAAFI','Findings','these have the appearance suggestive of posttreatment postradiation changes rather than metastatic disease'],
        ['000038_CTAAFI','Findings','there is associated pleural thickening at the resection site along the anterolateral left chest wall'],
        ['000038_CTAAFI','Findings','additional pleural thickening is seen along the bilateral fissures left greater than right'],
        ['000038_CTAAFI','Findings','pleural thickening along the right major fissure with a few areas of small nodular thickening series 3 image 221 and minor fissure series 3 image 292 percent and may represent scarring or a small intrafissural lymph node'],
        ['000038_CTAAFI','Findings','semisolid 3 mm nodule seen within the central left upper lobe series 3 image 145'],
        ['000038_CTAAFI','Findings','additional tiny 1 2 mm semisolid nodules within the left upper lobe series 3 image 133 183 204 and left lower lobe series 3 image 230'],
        ['000038_CTAAFI','Impression','postoperative changes of the anterolateral left fifth rib for history of prior ewing s sarcoma metastasis'],
        ['000038_CTAAFI','Impression','peripheral reticular groundglass opacities in both lungs left greater than right are favored to represent posttreatment changes'],
        ['000038_CTAAFI','Impression','a few small 1 3 mm pulmonary nodules within the left lung'],
        ['000038_CTAAFI','Impression','these are indeterminate and too small to characterize'],
        ['000038_CTAAFI','Impression','comparison with prior studies would be helpful'],
        ['000038_CTAAFI','Impression','several prominent but not pathologically enlarged mediastinal lymph nodes'],
        ['000038_CTAAFI','Impression','these may be reactive although metastatic disease is not excluded'],
        ['000038_CTAAFI','Impression','5 old healing left seventh rib fracture'],
        ['000038_CTAAFI','Impression','the preliminary report critical or emergent communication was reviewed prior to this dictation and there are no substantial differences between the preliminary results and the impressions in this final report'],
        
        ['fabricated1','Findings','there is a tumor in the right lung'],
        ['fabricated1','Findings','there is pneumonia'],
        ['fabricated1','Findings','the central airways are clogged'],
        
        ['fabricated2','Findings','something about the pancreas'],
        ['fabricated2','Findings','something about thyroid lobe enlarged'],
        ['fabricated2','Findings','moderate cardiomegaly'],
            
        ['008266_CTAKMI','Findings','biapical pleural parenchymal scarring'],
        ['008266_CTAKMI','Findings','right upper lobe pulmonary nodule is decreased in size compared to the prior examination particularly the surrounding groundglass component'],
        ['008266_CTAKMI','Findings','overall the nodule now measures 3 mm series 3 image 82'],
        ['008266_CTAKMI','Findings','multiple other pulmonary nodules are unchanged in size when compared to the prior examination'],
        ['008266_CTAKMI','Findings','the largest nodule is within the right lower lobe measuring 7 mm series 3 image 282'],
        ['008266_CTAKMI','Findings','moderate sized hiatal hernia'],
        ['008266_CTAKMI','Findings','degenerative changes of thoracic spine'],
        ['008266_CTAKMI','Impression','impression multiple bilateral pulmonary nodules are again visualized throughout the lungs'],
        ['008266_CTAKMI','Impression','the index right upper lobe semisolid nodule is decreased in size when compared to the prior examination particularly the groundglass component'],
        ['008266_CTAKMI','Impression','other pulmonary nodules are unchanged when compared to the prior'],
        
        ['008271_CTAKML','Findings','there are extensive vascular calcifications throughout the thoracic aorta and coronary arteries'],
        ['008271_CTAKML','Findings','there is a stent in the right coronary artery'],
        ['008271_CTAKML','Findings','the patient is status post partial left upper lobe resection'],
        ['008271_CTAKML','Findings','there is emphysema'],
        ['008271_CTAKML','Findings','there is stable post radiation change in the right paramediastinum and right upper lobe'],
        ['008271_CTAKML','Findings','there is an unchanged 6 mm left lower lobe pulmonary nodule likely present on the exam from %year'],
        ['008271_CTAKML','Findings','there is an unchanged 5 mm right upper lobe nodule series 3 image 270'],
        ['008271_CTAKML','Findings','there is an unchanged 4 mm left lower lobe nodule series 3 image 280'],
        ['008271_CTAKML','Impression','impression stable postradiation change without evidence of progressive malignancy'],
        ['008271_CTAKML','Impression','stable left lung pulmonary nodules'],
        
        ['008295_CTAKNG','Findings','there is consolidative opacity of the paramedian left upper lobe and lingula in keeping with findings of prior radiograph'],
        ['008295_CTAKNG','Findings','there is additional diffuse groundglass opacity of the inferior right middle right lower lingula and left lower lobes'],
        ['008295_CTAKNG','Findings','limited noncontrast examination of the upper abdomen reveals a fluid attenuation simple cyst of the superior pole the right kidney'],
        ['008295_CTAKNG','Impression','impression masslike opacity of the paramedian left upper lobe and lingula in keeping with findings of prior radiographs with diffuse superimposed groundglass pulmonary opacity this constellation of findings highly concerning for multifocal adenocarcinoma given persistence from prior examinations'],
        
        ['010512_CTANCR','Findings','there are there is moderate coronary arterial calcification in the visualized lad'],
        ['010512_CTANCR','Findings','mild scattered mural calcification within the thoracic aorta is noted'],
        ['010512_CTANCR','Findings','scattered calcified nodules in the lungs likely secondary to prior granulomatous disease'],
        ['010512_CTANCR','Findings','there is a hypodense partially calcified mass in the area of the portal confluence caudate lobe which may correspond with given history of known hcc'],
        ['010512_CTANCR','Impression','partially visualized hypodense partially calcified mass in the area of the portal confluence caudate lobe likely corresponds to given history of hcc'],
        
        ['fabricated3','Findings','the left lung is full of nodules']]
    
#########
# Tests #-----------------------------------------------------------------------
#########
class TestTermSearch(unittest.TestCase):
    def test_term_search_different_setname(self):
        #if setname is test, it'll be compared to ground truth, so don't run that one
        #if setname is train, the ground truth BinLabel will be used to choose sick sentences
        #if setname is predict, the predicted PredLabel will be used to choose sick sentences
        #Results dir
        results_dir = 'testing_delthis'
        if not os.path.exists(results_dir):
            os.mkdir(results_dir)
            
        fake_merged =  pd.DataFrame([[1,'pneumonia','AAFF','Findings',0,0.5,1],
            [2,'cardiomegaly','AAFF','Findings',1,0.5,0]],
             columns=['Count','Sentence','Filename','Section','PredLabel','PredProb','BinLabel'])
        
        #Check term search with setname train
        m = term_search.RadLabel(data=fake_merged, setname='train',
                                 dataset_descriptor='duke_ct_2019_09_25',
                                 results_dir=results_dir,
                                 run_locdis_checks=True,
                                 save_output_files=False)
        output = m.out_bin
        AAFF_df = ground_truth_helper(output, key='AAFF',include_list = [['pneumonia','lung']])
        assert eqc.dfs_equal(AAFF_df,output['AAFF'])
        
        #Check term search with setname predict
        #need to set testing=True so that it doesn't try to sort the output by
        #accession numbers (since AAFF is a fake accession number)
        m = term_search.RadLabel(data=fake_merged, setname='predict', 
                                 dataset_descriptor='duke_ct_2019_09_25',
                                 results_dir=results_dir, 
                                 run_locdis_checks=True,
                                 save_output_files=False)
        output = m.out_bin
        AAFF_df = ground_truth_helper(output, key='AAFF',include_list = [['cardiomegaly','heart']])
        assert eqc.dfs_equal(AAFF_df,output['AAFF'])
        shutil.rmtree(results_dir)
        print('Passed test_term_search_different_setname()')
    
    def test_term_search_overall(self):
        #Make fake input data
        #The critical columns are Sentence, PredLabel, and BinLabel
        fake_merged = pd.DataFrame(
            #AA11 has normal liver, normal lungs:
            [[3,'the liver is normal','AA11','Findings',0,0.01,0], #normal liver
            [1,'the lungs are clear','AA11','Findings',0,0.05,0], #normal lungs
            #AA11 has abnormal heart and great vessels:
            [2,'the heart is severely enlarged','AA11','Findings',1,0.9,1], #cardiomegaly, heart
            [6,'the aortic arch is atherosclerotic','AA11','Impression',1,0.66,1], #atherosclerosis, aorta
            [2,'severe coronary artery disease','AA11','Impression',1,0.88,1], #coronary artery disease, heart
            
            #PericardialEffusionBug:
            #I have commented out the pericardial effusion line below because on my new
            #computer this is causing some VERY weird behavior wherein the 'Exclude' code
            #of the term_search does not appear to work properly and pericardial
            #effusion leads to pleural effusion being marked present when it really
            #shouldn't due to the word 'pericardial' being in 'Exclude' for
            #the pleural effusion label. But then if I put in debugging print statements
            #within the logic for the Exclude part of the term search, it will
            #randomly start working again which makes NO sense.
            #[1,'small pericardial effusion','AA11','Findings',1,0.59,1], #pericardial effusion, heart
            
            [11,'ivc filter in place','AA11','Findings',1,0.87,1], #other_disease, ivc
            #AA11 has sentences that will be filtered out because they include 'removal of' and 'resolved':
            [2,'removal of left chest tube in the interval','AA11','Impression',1,0.03,1], #normal
            [3,'pneumonia has resolved','AA11','Impression',0,0.1,0], #normal
            #Test abnormalities that should be filtered out for the wrong location or the wrong pathology:
            #for lung_path, for heart_loc or generic_loc: delete
            [2,'bronchiectasis in the ventricle','AA11','Impression',1,0.9,1], #bronchiectasis, lung (not ventricle)
            [3,'reticular opacity in the atrium','AA11','Impression',1,0.99,1], #opacity, lung AND reticular, lung (not atrium)
            [4,'honeycombing in the esophagus','AA11','Impression',1,0.87,1], #honeycombing, lung (not esophagus)
            #for heart_path, for lung_loc or generic_loc: delete
            [4,'pericardial thickening in the right upper lobe','AA11','Impression',1,0.67,1], #pericardial_thickening, heart (not RUL)
            [6,'pacemaker in the adrenal gland','AA11','Findings',1,0.78,1], #pacemaker_or_defib, heart (not adrenal gland)
            #for vessel_loc, for forbidden path: delete
            [2,'opacity in the svc','AA11','Impression',1,0.87,1], #deleted
                    
            #AA22 has normal aorta, normal lingula, and normal kidneys:
            [4,'the aorta is normal','AA22','Findings',0,0.2,0], #normal aorta
            [2,'the lingula is normal','AA22','Findings',0,0.03,0], #normal left middle lobe (lingula)
            [3,'the kidneys are healthy','AA22','Findings',0,0.02,0], #normal kidneys
            #AA22 has abnormal lungs:
            [9,'groundglass opacity in the right middle lobe','AA22','Findings',1,0.99,1], #groundglass, right_mid AND opacity, right_mid
            [10,'severe right airspace disease','AA22','Findings',1,0.97,1], #airspace_disease, right_lung
            [2,'bronchiolitis on the left side','AA22','Findings',1,0.89,1], #bronchiolitis, left_lung
            [8,'severe emphysema in the right middle lobe','AA22','Findings',1,0.92,1], #emphysema, right_mid
            [3,'left pneumothorax','AA22','Findings',1,0.91,1], #pneumothorax, left_lung
            [1,'mucous plugging in the bronchi','AA22','Findings',1,0.93,1], #mucous_plugging, airways
            [2,'tuberculous lesion in the lingula','AA22','Findings',1,0.94,1], #tuberculosis, left_mid AND lesion, left_mid
            [1,'septal thickening near the right upper lobe','AA22','Findings',1,0.96,1], #septal_thickening, right_upper
            [5,'right pleural thickening','AA22','Findings',1,0.76,1], #pleural_thickening, right_lung
            [4,'nodule and opacity in the right lower lobe','AA22','Findings',1,0.99,1], #nodule, right_lower AND opacity, right_lower
            
            #AA33 has various abnormalities
            [1,'linear atelectasis','AA33','Findings',1,0.99,1], #bandlike_or_linear, lung AND atelectasis, lung
            [1,'tree-in-bud opacity in the lung','AA33','Findings',1,0.99,1], #tree_in_bud, lung AND opacity, lung
            [1,'bronchial wall thickening on the left','AA33','Findings',1,0.99,1], #bronchial_wall_thickening, left_lung
            [1,'severe bronchitis','AA33','Findings',1,0.99,1], #bronchitis, lung
            [1,'bilateral hemothoraces','AA33','Findings',1,0.99,1], #hemothorax, right_lung AND hemothorax, left_lung
            [1,'interstitial lung disease is present','AA33','Findings',1,0.99,1], #interstitial_lung_disease, lung AND airspace_disease, lung
            [1,'the left upper lobe has been surgically resected with residual scarring','AA33','Findings',1,0.99,1], #lung_resection, left_upper AND postsurgical, left_upper AND scarring, left_upper
            [1,'pleural fluid and pneumonia have worsened','AA33','Findings',1,0.99,1], #pleural_effusion, lung AND pneumonia, lung
            [1,'edema in the left lower lobe','AA33','Findings',1,0.99,1], #pulmonary_edema, left_lower
            [1,'mitral valve replacement is visible','AA33','Findings',1,0.99,1], #heart_valve_replacement, heart
            [1,'severe left-sided ventricular failure','AA33','Findings',1,0.99,1], #heart_failure, heart
            [1,'4 cm aneurysmal dilation in the svc','AA33','Findings',1,0.99,1], #aneurysm, svc AND dilation_or_ectasia, svc
            [1,'breast implant on the right and a mastectomy on the left','AA33','Findings',1,0.99,1], #breast_implant, breast AND breast_surgery, breast
            [1,'calcified metastasis in the liver','AA33','Findings',1,0.99,1], #calcification, liver AND cancer, liver
            [1,'the pulmonary artery has been catheterized','AA33','Findings',1,0.99,1], #catheter_or_port, pulmonary_artery
            [1,'cavitary lesion in the right lung','AA33','Findings',1,0.99,1], #cavitation, right_lung AND lesion, right_lung
            [1,'gallbladder clips visible','AA33','Findings',1,0.99,1], #clip, gallbladder
            [1,'stent in the pulmonary vein','AA33','Findings',1,0.99,1], #stent, pulmonary_vein
            [1,'severe congestion and consolidation in the lungs','AA33','Findings',1,0.99,1], #congestion, lung AND consolidation, lung
            [1,'metallic density in the heart likely an intra-aortic balloon pump','AA33','Findings',1,0.99,1], #density, heart (no density, aorta because of loc dis cleanup)
            [1,'debris and secretions visible in the trachea','AA33','Findings',1,0.99,1], #debris, airways AND secretion, airways
            [1,'severe lung fibrosis is apparent','AA33','Findings',1,0.99,1], #fibrosis, lung
            [1,'cysts in the kidneys','AA33','Findings',1,0.99,1], #cyst, kidney
            [1,'soft tissue and stranding along the left anterior chest wall','AA33','Findings',1,0.99,1], #soft_tissue, chest_wall
            [1,'lucency in the left breast next to a granuloma','AA33','Findings',1,0.99,1], #lucency, breast AND granuloma, breast
            [1,'mass in the axilla with suture visible','AA33','Findings',1,0.99,1], #mass, axilla AND suture, axilla
            [1,'mediastinal and hilar lymphadenopathy','AA33','Findings',1,0.99,1], #lymphadenopathy, mediastinum AND lymphadenopathy, hilum
            [1,'small hiatal hernia','AA33','Findings',1,0.99,1], #hernia, diaphragm
            [1,'status post liver transplant','AA33','Findings',1,0.99,1], #postsurgical, liver AND transplant, liver
            [1,'staples in the abdomen','AA33','Findings',1,0.99,1], #staple, abdomen
            [1,'pleural plaques','AA33','Findings',1,0.99,1], #plaque, lung
            [1,'there is a nasogastric tube in the patulous esophagus with its tip in the stomach','AA33','Findings',1,0.99,1], #gi_tube, esophagus AND gi_tube, stomach
            [1,'fatty infiltrates in the pancreas','AA33','Findings',1,0.99,1], #infiltrate, pancreas
            [1,'thyroid nodularity has worsened','AA33','Findings',1,0.99,1], #nodule, thyroid
            [1,'bilateral rib fractures','AA33','Findings',1,0.99,1], #fracture, rib
            [1,'distention of the intestines','AA33','Findings',1,0.99,1], #distention, intestine
            [1,'nodule in the adrenal gland','AA33','Findings',1,0.99,1], #nodule, adrenal_gland
            [1,'degenerative changes in the thoracic spine','AA33','Findings',1,0.99,1], #arthritis, spine
            [1,'hardware and deformity in the cervical spine','AA33','Findings',1,0.99,1], #hardware, spine AND deformity, spine
            [1,'severe air trapping noted','AA33','Findings',1,0.99,1], #air_trapping, lung
            [1,'it appears that the nodules have not changed in size','AA33','Findings',1,0.99,1]], #nodule, other_location -> won't be marked because other nodules have been specified.
            columns=['Count','Sentence','Filename','Section','PredLabel','PredProb','BinLabel'])
        
        #Results dir
        results_dir = 'testing_delthis'
        if not os.path.exists(results_dir):
            os.mkdir(results_dir)
            
        #Run term search
        m = term_search.RadLabel(data=fake_merged, setname='train',
                                 dataset_descriptor='duke_ct_2019_09_25',
                                 results_dir=results_dir, 
                                 run_locdis_checks=True,
                                 save_output_files=False)
        output = m.out_bin #dictionary. keys are filenames, values are pandas dataframes with pathology as index and location as columns
        
        #Ground truth
        AA11_gt_include_list = [['cardiomegaly','heart'],
            ['atherosclerosis','aorta'],
            ['coronary_artery_disease','heart'],
            #['pericardial_effusion','heart'], #see comment PericardialEffusionBug above
            ['other_disease','ivc'],
            ['bronchiectasis','lung'],
            ['bronchiectasis','airways'], #because 'bronchi' is in the 'airways' location definition
            ['opacity','lung'],
            ['reticulation','lung'],
            ['honeycombing','lung'],
            ['pericardial_thickening','heart'],
            ['pacemaker_or_defib','heart']]
        AA22_gt_include_list = [['groundglass','right_mid'],
            ['groundglass','right_lung'], #because of right_mid
            ['groundglass','lung'], #because of right_mid
            
            ['opacity','right_mid'],
            ['opacity','right_lung'], #because of right_mid
            ['opacity','lung'], #because of right_mid
            
            ['airspace_disease','right_lung'],
            ['airspace_disease','lung'], #because of right_lung
            
            ['bronchiolitis','left_lung'],
            ['bronchiolitis','lung'], #because of left_lung
            ['bronchiolitis','airways'], #because 'bronchi' is in the 'airways' location definition
            
            ['emphysema','right_mid'],
            ['emphysema','right_lung'], #because of right_mid
            ['emphysema','lung'], #because of right_mid
            
            ['pneumothorax','left_lung'],
            ['pneumothorax','lung'], #because of left_lung
            
            ['mucous_plugging','airways'],
            ['mucous_plugging','lung'], #because it's lung-specific pathology
            
            ['tuberculosis','left_mid'],
            ['tuberculosis','left_lung'], #because of left_mid
            ['tuberculosis','lung'], #because of left_mid
            
            ['lesion','left_mid'],
            ['lesion','left_lung'], #because of left_mid
            ['lesion','lung'], #because of left_mid
            
            ['septal_thickening','right_upper'],
            ['septal_thickening','right_lung'], #because of right_upper
            ['septal_thickening','lung'], #because of right_upper
            
            ['pleural_thickening','right_lung'],
            ['pleural_thickening','lung'], #because of right_lung
            
            ['nodule','right_lower'],
            ['nodule','right_lung'], #because of right_lower
            ['nodule','lung'], #becasue of right_lower
            
            ['opacity','right_lower'],
            ['opacity','right_lung'], #because of right_lower
            ['opacity','lung'] #because of right_lower
            ]
        AA33_gt_include_list = [['bandlike_or_linear','lung'],
            ['atelectasis','lung'],
            ['tree_in_bud','lung'],
            ['opacity','lung'],
            
            ['bronchial_wall_thickening','left_lung'],
            ['bronchial_wall_thickening','lung'], #because of left_lung
            ['bronchial_wall_thickening','airways'], #because of bronchi
            
            ['bronchitis','lung'],
            ['bronchitis','airways'], #because of bronchi
            
            ['hemothorax','right_lung'],
            ['hemothorax','left_lung'],
            ['hemothorax','lung'],
            
            ['interstitial_lung_disease','lung'],
            ['airspace_disease','lung'],
            
            ['lung_resection','left_upper'],
            ['lung_resection','left_lung'], #because of left_upper
            ['lung_resection','lung'], #because of left_upper
            ['postsurgical','left_upper'],
            ['postsurgical','left_lung'], #because of left_upper
            ['postsurgical','lung'], #because of left_upper
            ['scarring','left_upper'],
            ['scarring','left_lung'], #because of left_upper
            ['scarring','lung'], #because of left_upper
            
            ['pleural_effusion','lung'],
            ['pneumonia','lung'],
            
            ['pulmonary_edema','left_lower'],
            ['pulmonary_edema','left_lung'], #because of left_lower
            ['pulmonary_edema','lung'], #because of left_lower
            
            ['heart_valve_replacement','heart'],
            ['heart_failure','heart'],
            ['aneurysm','svc'],
            ['dilation_or_ectasia','svc'],
            ['breast_implant','breast'],
            ['breast_surgery','breast'],
            ['calcification','liver'],
            ['catheter_or_port','pulmonary_artery'],
            ['cancer','liver'],
            
            ['cavitation','right_lung'],
            ['cavitation','lung'], #because of right_lung
            
            ['lesion','right_lung'],
            ['lesion','lung'], #because of right_lung
            
            ['clip','gallbladder'],
            ['stent','pulmonary_vein'],
            ['congestion','lung'],
            ['consolidation','lung'],
            ['density','heart'],
            ['debris','airways'],
            ['secretion','airways'],
            ['fibrosis','lung'],
            ['cyst','kidney'],
            ['soft_tissue','chest_wall'],
            ['lucency','breast'],
            ['granuloma','breast'],
            ['mass','axilla'],
            ['suture','axilla'],
            ['lymphadenopathy','mediastinum'],
            ['lymphadenopathy','hilum'],
            ['hernia','diaphragm'],
            ['postsurgical','liver'],
            ['transplant','liver'],
            ['staple','abdomen'],
            ['plaque','lung'],
            ['gi_tube','esophagus'],
            ['gi_tube','stomach'],
            ['infiltrate','pancreas'],
            ['nodule','thyroid'],
            ['fracture','rib'],
            ['distention','intestine'],
            ['nodule','adrenal_gland'],
            ['arthritis','spine'],
            ['hardware','spine'],
            ['deformity','spine'],
            ['air_trapping','lung']]
        AA11_df = ground_truth_helper(output, key='AA11',include_list = AA11_gt_include_list)
        AA22_df = ground_truth_helper(output, key='AA22',include_list = AA22_gt_include_list)
        AA33_df = ground_truth_helper(output, key='AA33',include_list = AA33_gt_include_list)
        
        #Verify correctness
        #I have updated the term search since I first wrote this test, which is why
        #I have to specify which diseases and locations to check (i.e. which ones
        #were available when I first wrote the test and which are still available
        #in the current term search):
        common_idx = ['bandlike_or_linear', 'bronchial_wall_thickening', 
            'groundglass', 'honeycombing', 'reticulation', 'tree_in_bud', 
            'airspace_disease', 'air_trapping', 'atelectasis', 'bronchiectasis', 
            'bronchiolitis', 'bronchitis', 'emphysema', 'hemothorax', 
            'interstitial_lung_disease', 'lung_resection', 'mucous_plugging', 
            'pleural_effusion', 'pleural_thickening', 'pneumonia', 'pneumothorax', 
            'pulmonary_edema', 'septal_thickening', 'tuberculosis', 'cardiomegaly', 
            'coronary_artery_disease', 'heart_failure', 'heart_valve_replacement', 
            'pacemaker_or_defib', 'pericardial_effusion', 'pericardial_thickening', 
            'arthritis', 'atherosclerosis', 'aneurysm', 'breast_implant', 
            'breast_surgery', 'calcification', 'cancer', 'catheter_or_port', 
            'cavitation', 'clip', 'congestion', 'consolidation', 'cyst', 'debris', 
            'deformity', 'density', 'dilation_or_ectasia', 'distention', 'fibrosis', 
            'fracture', 'granuloma', 'hardware', 'hernia', 'infiltrate', 'lesion', 
            'lucency', 'lymphadenopathy', 'mass', 'nodule', 'opacity', 'plaque', 
            'postsurgical', 'scarring', 'secretion', 'soft_tissue', 'staple', 
            'stent', 'suture', 'transplant', 'other_disease']

        common_col = ['left_upper', 'left_mid', 'left_lower', 'right_upper', 
            'right_mid', 'right_lower', 'right_lung', 'left_lung', 'lung', 
            'airways','heart', 'aorta', 'svc', 'ivc', 'pulmonary_artery',
            'pulmonary_vein', 'thyroid', 'breast', 'axilla',
            'chest_wall', 'rib', 'spine', 'mediastinum', 'diaphragm',
            'hilum', 'abdomen', 'esophagus', 'stomach', 'intestine', 'liver',
            'gallbladder', 'kidney', 'adrenal_gland', 'spleen', 'pancreas',
            'other_location']
        for disease in common_idx:
            for location in common_col:
                assert output['AA11'].at[disease,location] == AA11_df.at[disease,location] 
                assert output['AA22'].at[disease,location] == AA22_df.at[disease,location]
                assert output['AA33'].at[disease,location] == AA33_df.at[disease,location]
        assert sorted(list(output.keys()))==['AA11','AA22','AA33']
        shutil.rmtree(results_dir)
        print('Passed test_term_search_overall()')
    
    def test_label_for_keyterm_and_sentence(self):
        termdict = vocabulary_locations.LUNG_LOCATION_TERMS
        tests = [('there is a tumor in the left upper lobe','left_upper',True),
            ('atelectasis in the superior left lung','left_upper',True),
            ('the left lung apex looks bad','left_upper',True),
            ('the apices of both lungs have opacities','left_upper',True),
            ('the right upper lobe looks awful','left_upper',False),
            ('a nodule is visible in the right lower lobe','right_lower',True),
            ('a nodule can be seen in the right inferior lobe','right_lower',True),
            ('there is a gorilla in the left lung base','left_lower',True),
            ('basilar atelectasis on the right','right_lower',True),
            ('there is bibasilar atelectasis','right_lower',True),
            ('there is bibasilar atelectasis','left_lower',True),
            ('there is bibasilar atelectasis','left_mid',False),
            ('there are bilateral monkeys in the lungs','right_lung',True),
            ('there are bilateral polka dots everywhere','left_lung',True),
            ('the pleura are full of nodules','lung',True),
            ('there is a tumor in the left upper lobe','lung',True),
            ('bibasilar cancer everywhere','lung',True),
            ('the lingula is sick','lung',True),
            ('the lingula is sick','left_mid',True),
            ('the right middle lobe pneumonia','right_mid',True),
            ('the right lung is bad but so is the hepatic lobe','lung',False),
            ('the right upper lobe has cancer and so does the liver','lung',False)]
        for tup in tests:
            sentence = tup[0]
            keyterm = tup[1]
            answer = tup[2]
            assert answer==term_search.RadLabel.label_for_keyterm_and_sentence(keyterm, sentence, termdict)
        print('Passed test_label_for_keyterm_and_sentence()')
    
    def test_label_for_right_and_left_from_diseases(self):
        lung_path_dict = vocabulary_ct.LUNG_PATHOLOGY
        #order of answers is right, left, lung
        tests = [('there is copd in the right lung',[1,0,1]),
            ('left lung and right lower lobe air-space disease',[1,1,1]),
            ('right upper lobe and lingula pneumonia',[1,1,1]),
            ('there is atelectasis in the right lung and the left lung base',[1,1,1]),
            ('the right lower lobe is collapsed',[1,0,1]),
            ('blister in the lingula',[0,1,1]),
            ('there are nodules in the liver',[0,0,0]),
            ('there is a mass in the pancreas',[0,0,0]),
            ('there is left bronchiectasis',[0,1,1]),
            ('right bronchiolitis present',[1,0,1]),
            ('left and right tuberculous lesions',[1,1,1])]
        for tup in tests:
            sentence = tup[0]
            answer = tup[1]
            assert answer == [x for x in term_search.RadLabel.label_for_right_and_left_from_diseases(sentence, lung_path_dict)]
        print('Passed test_label_for_right_and_left_from_diseases')
    
    def test_obtain_sarle_labels_and_missingness(self):
        global sarle_x
        merged = pd.DataFrame(sarle_x,columns=['Filename','Section','Sentence'])
        merged['Label'] = 's'
        merged['BinLabel'] = 1
        x = term_search.RadLabel(data = merged, setname='train',
                                 dataset_descriptor='duke_ct_2019_09_25',
                                 results_dir='', 
                                 run_locdis_checks=True,
                                 save_output_files=True) #in this case we do want to save the output files so we can check them
        
        #Check correctness of everything
        used_files = ['000013_CTAAEJ', '000022_CTAAES','000038_CTAAFI','008266_CTAKMI',
                     '008271_CTAKML','008295_CTAKNG','010512_CTANCR','fabricated1',
                     'fabricated2','fabricated3']
        
        #Check that count labels are correct
        columns = ['left_upper','left_mid','left_lower','right_upper',
                       'right_mid','right_lower','right_lung','left_lung','lung']
        output_count = pd.DataFrame(np.zeros((len(used_files),len(columns))),
                                    index = used_files, columns = columns)
        for filename in used_files:
            df = x.out_bin[filename]
            for location in columns:
                loc_count = np.sum(df.loc[:,location].values)
                output_count.at[filename,location] = loc_count
        output = output_count.apply(lambda x: [0 if y == 0 else 1 for y in x])
        correct = pd.DataFrame(
            [[1,0,1,1,0,1,1,1,1],
            [1,1,1,1,1,1,1,1,1],
            [1,0,1,0,1,1,1,1,1],
            [1,0,0,1,0,1,1,1,1],
            [1,0,1,1,0,0,1,1,1],
            [1,1,1,0,1,1,1,1,1],
            [0,0,0,0,0,0,0,0,1],
            [0,0,0,0,0,0,1,0,1],
            [0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,1,1]],
            columns = columns,
            index = used_files)
        assert eqc.dfs_equal(output,correct)
        
        #Check that missingness is correct
        output_miss = pd.read_csv('imgtrain_notetrain_Missingness.csv',header=0,index_col=0)
        correct_miss = pd.DataFrame([[1,1,1],
                        [1,1,1],
                        [1,1,1],
                        [1,1,1],
                        [1,1,1],
                        [1,1,1],
                        [1,1,0],
                        [1,0,1],
                        [1,1,1],
                        [0,1,1]],columns = ['left_lobes_all','right_lobes_all','lungs_right_left'],
                               index = used_files)
        assert eqc.dfs_equal(output_miss, correct_miss)
    
        #Clean up
        os.remove('imgtrain_notetrain_BinaryLabels.pkl')
        os.remove('imgtrain_notetrain_DiseaseBinaryLabels.csv')
        os.remove('imgtrain_notetrain_Missingness.csv')
        os.remove('imgtrain_notetrain_Merged.csv')
        os.remove('train_other_location_sentences.txt')
        os.remove('train_other_disease_sentences.txt')
        print('Passed test_obtain_sarle_labels_and_missingness()')

###########
# Helpers #---------------------------------------------------------------------
###########
def ground_truth_helper(output, key, include_list):
    """Create ground truth for the function test_term_search_overall().
    Variables:
    <output> is a dictionary of pandas dataframes of the correct output;
        the dfs will be used to initialize the rows and columns.
    <key> is one of the keys in the dictionary <output>, e.g. 'AA11'
    <include_list> is a list of lists specifying which row/col pairs are
        equal to 1."""
    out_df = pd.DataFrame(np.zeros(output[key].shape),
                                   columns = output[key].columns.values.tolist(),
                                   index = output[key].index.values.tolist())
    for sublist in include_list:
        path = sublist[0]
        loc = sublist[1]
        out_df.at[path,loc] = 1
    return out_df

if __name__=='__main__':
    unittest.main()