# SARLE

![SARLE Logo](sarle-labeler-logo.png)

## Description

This is the Python implementation of Sentence Analysis for Radiology 
Label Extraction (SARLE), a method to automatically extract structured 
labels from radiology reports. SARLE achieves an average F-score of 0.976 
(min 0.941, max 1.0) when evaluated on the RAD-ChestCT dataset of chest CT 
reports. 

The SARLE method is described in our [Medical Image Analysis paper](https://doi.org/10.1016/j.media.2020.101857),
which is also available [on arXiv](https://arxiv.org/ftp/arxiv/papers/2002/2002.04752.pdf).

If you find this work useful in your research, please consider citing us:

Draelos, Rachel Lea, David Dov, Maciej A. Mazurowski, Joseph Y. Lo, 
Ricardo Henao, Geoffrey D. Rubin, and Lawrence Carin. 
"Machine-learning-based multiple abnormality prediction with large-scale chest computed tomography volumes."
*Medical Image Analysis* 67 (2021): 101857.

## Requirements

The requirements to run SARLE are listed in requirements.txt. 

One of the goals of SARLE is to have minimal dependencies. 

To run all the code in this repository, only 6 packages are required:
* numpy and pandas for SARLE data handling
* scikit-learn for performance metrics
* matplotlib and seaborn for visualizations
* fasttext for SARLE-Hybrid

Newer versions of these packages will almost
certainly work. The versions in the requirements.txt file simply represent
one configuration that works for this codebase.

SARLE-Rules can run on any operating system (Linux, Mac, Windows, etc.)

SARLE-Hybrid can only run on Linux or Mac, as the fasttext package is not
available for Windows.

## Usage

To run a demo of SARLE-Rules and SARLE-Hybrid on the public OpenI dataset of
chest x-ray reports, run this command:

`python demo.py`

## Deploying SARLE on your own dataset

### Choice of SARLE sub-method
To deploy SARLE on your own dataset, we recommend using SARLE-Rules rather
than SARLE-Hybrid because:
* you won't need the fasttext dependency;
* you won't need to do the manual sentence labeling fasttext requires;
* SARLE-Rules outperforms SARLE-Hybrid in our experiments.

### Required data format
demo.py includes a demo on real data and fake data.
* real data: SARLE is demonstrated on the OpenI dataset of chest x-ray reports.
* fake data: SARLE is demonstrated on some tiny handcrafted dataframes of
  fake data, to demonstrate the data format.

train_data 
* In SARLE-Hybrid, the train_data is used to train the sentence classifier.
  In order to train a sentence classifier, the sentences in the train_data
  must be labeled with 1 (abnormal) or 0 (normal) if they describe abnormal
  or normal radiologic findings, respectively. If you do not want to spend
  time manually labeling sentences, just use SARLE-Rules.
* In SARLE-Rules, the train_data was used by a human to create the rules.
  When running SARLE, the rules that were created will get applied to the 
  train_data, because if we have the end goal of computer vision classifier 
  training, we still need to have labels for our note train_data set. For 
  SARLE-Rules, train_data does not need any manual sentence labels.
* If you just want to quickly try out SARLE-Rules on a sample of your own 
  data and look at the output, you can put your sample data in as the 
  train_data in the fake data demo.

test_data
* The test_data is used to calculate SARLE's performance predicting abnormality
  labels.
* To calculate SARLE's performance on your own dataset, the reports in the 
  test_data set must be manually labeled with report-level abnormality
  ground truth. 
* To see an example of the required abnormality ground truth format, you can
  look at the output of load.load_ground_truth('openi_cxr').
* You can see an example of ground truth being used in performance
  calculations in the function eval_on_report_level_ground_truth() in 
  evaluation.py.

predict_data
* The predict_data is optional. It consists of additional radiology reports
  on which we might want to deploy SARLE to obtain abnormality x location labels,
  e.g. as part of creating a large dataset to train a computer vision classifier.
* predict_data does not need to be manually labeled in any way. It does not
  need to have binary sentence labels and it does not need to have report-level
  abnormality labels either.
* It is OK not to have a predict_set. If you don't have a predict_set then you
  must set the predict_set to pd.DataFrame() (an empty dataframe).

### Customization of the phrase classification step of SARLE-Rules
If you would like to customize the normal/abnormal phrase classification step
of SARLE-Rules, you can edit the rules in:
* src/rules/rules_ct.py
* src/rules/rules_cxr.py

### Customization of the abnormalities and locations
SARLE presently focuses on chest abnormalities, but does include some abdomen,
pelvis, and general abnormalities. If you would like to customize
SARLE's abnormalities, you can do so by editing the vocabulary files:
* src/vocab/vocabulary_ct.py
* src/vocab/vocabulary_cxr.py

If you would like to customize SARLE's locations, you can do so in
* src/vocab/vocabulary_locations.py

## Locations and Abnormalities

[An earlier version of this repository](https://github.com/rachellea/sarle-labeler/tree/8cdb3d494b46df2bc820592e14c9c8e23d08fa07)
contains the original SARLE which produces predictions of abnormalities only.

The current version of this repository is a more advanced version of SARLE
that produces predictions for both abnormalities and their locations. As far
as we are aware, SARLE is the only radiology label extraction software to
produce both abnormality and location predictions. For each radiology report,
an abnormality x location matrix is produced specifying every abnormality
identified and its location (e.g. nodule/right upper lobe of the lung,
mass/left lower lobe of the lung, nodule/liver). Location identification is
done in a rule-based manner.

## Tests

To run the unit tests, run this command:

`python -m unittest discover`

## Logo

The SARLE logo includes Creative Commons icons from the Noun Project: [computer](https://thenounproject.com/term/medical/879529/),
[report](https://thenounproject.com/term/medical/959388/),
and [table](https://thenounproject.com/search/?q=table&i=250445).