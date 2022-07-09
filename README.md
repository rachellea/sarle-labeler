# SARLE

![SARLE Logo](sarle-labeler-logo.png)

## Description

This is the Python implementation of Sentence Analysis for Radiology 
Label Extraction (SARLE), a method to automatically extract structured 
labels from radiology reports. SARLE achieves an average F-score of 0.976 
(min 0.941, max 1.0) when evaluated on a data set of chest CT reports. 

The SARLE method is described in our [Medical Image Analysis paper](https://doi.org/10.1016/j.media.2020.101857),
which is also available [on arXiv](https://arxiv.org/ftp/arxiv/papers/2002/2002.04752.pdf).

If you find this work useful in your research, please consider citing us:

Draelos R.L., et al. "Machine-Learning-Based Multiple Abnormality Prediction with Large-Scale Chest Computed Tomography Volumes." *Medical Image Analysis* (2020).

## Requirements

The requirements to run SARLE are listed in requirements.txt. 

One of the goals of SARLE is to have minimal dependencies. Only 5 packages are 
required for SARLE-Rules (numpy and pandas for SARLE itself, scikit-learn for
performance metrics, and matplotlib and seaborn for visualization). 
Newer versions of these packages will almost
certainly work. The versions in the requirements.txt file simply represent
one configuration that works for this codebase.

The fasttext package is also needed if you'd like to try the SARLE-Hybrid method,
but as fasttext is only available on Linux or Mac you should delete this
package from requirements.txt if you're on a Windows machine.

## Customization

To deploy SARLE on your own dataset, we recommend using SARLE-Rules rather
than SARLE-Hybrid because:
* you won't need the fasttext dependency;
* you won't need to do the manual sentence labeling fasttext requires;
* SARLE-Rules outperforms SARLE-Hybrid in our experiments.

SARLE presently focuses on chest abnormalities, but does include some abdomen,
pelvis, and general abnormalities. If you would like to customize
SARLE's abnormalities, you can do so by editing the vocabulary files:
* src/vocab/vocabulary_ct.py
* src/vocab/vocabulary_cxr.py

If you would like to customize SARLE's locations, you can do so in
* src/vocab/vocabulary_locations.py

## Usage

To run a demo of SARLE-Rules and SARLE-Hybrid on the public OpenI dataset of
chest x-ray reports, run this command:

`python demo.py`

The required format of the data is demonstrated in the directory data/data_cxr, 
which contains the public OpenI chest x-ray data set in the required format.

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

`python unit_tests.py`

### Logo

The SARLE logo includes Creative Commons icons from the Noun Project: [computer](https://thenounproject.com/term/medical/879529/),
[report](https://thenounproject.com/term/medical/959388/),
and [table](https://thenounproject.com/search/?q=table&i=250445).