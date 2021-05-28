# Hypernymy Directionality

Code for the experiments in: "More than just Frequency? Demasking Unsupervised Hypernymy Prediction Methods." Thomas Bott, Dominik Schlechtweg and Sabine Schulte im Walde. Accepted to appear in *Findings of ACL 2021*

---

## Required packages

- pickle (to save and load files)
- docopt (for command line interface)
- tqdm (for processing bars)
- sklearn (for classification)
- graphviz (for drawing trees)
- numpy
- tabulate (for creating tables)

They can be installed by running: ```pip install -r requirements.txt``` in the terminal. Pickle should already be contained in the python standard library.

---

## Usage notes

The scripts should be run with python3. Each script contains a usage pattern, which indicates how to use it. Further information about the arguments and options can be obtained with the -h (--help) option.
For successfull usage, it is recommended to execute the scripts in the following order:

### 1. Create distributional semantic space(s) (*scripts/dsm_creation/*)

- ``dsm_creation.py``
- ``dsm_combine.py``

### 2. Calculate row sums (*scripts/dsm_creation/*)

- ``rowSums.py``

### 3. Read data set(s) (*scripts/dataset_processing/*)

- ``read_dataset.py``

### 4. Filter data set(s) (*scripts/dataset_processing/*)

- ``filter_dataset.py``

### 5. Optionally create subsets of data set(s) (*scripts/dataset_processing/*)

- ``freqDiff_freqBias.py``

### 6. For SLQS, calculate Positive Local Mutual Information scores (*scripts/dsm_creation/*)

- ``plmi.py``

### 7. Calculate unsupervised hypernymy measures (*scripts/measures/*)

- ``weedsPrec.py``
- ``invCL.py``
- ``slqsRow.py``
- ``slqs.py``

### 8. Evaluate measures, unsupervised and supervised (*scripts/evaluation/*)

- ``evaluation.py``
- ``classification.py``

---

## Corpora

<https://wacky.sslmit.unibo.it/doku.php>

### SdeWaC

Gertrud Faaß and Kerstin Eckart. 2013. SdeWaC – A Corpus of Parsable Sentences from the Web. In Proceedings of the International Conference of the German Society for Computational Linguistics and Language Technology, pages 61–68, Darmstadt, Germany.

### PukWaC

Adriano Ferraresi, Eros Zanchetta, Marco Baroni, and Silvia Bernardini. In- troducing and evaluating ukwac, a very large web-derived corpus of english. In Proceedings of the 4th Web as Corpus Workshop (WAC-4) Can we beat Google, pages 47–54, 2008

---

## Data sets

### GermaNet Version 11

<https://uni-tuebingen.de/en/142806>

Birgit Hamp and Helmut Feldweg. Germanet - a lexical-semantic net for german. In Automatic information extraction and building of lexical semantic resources for NLP applications, pages 9–15, 1997

### WordNet Version 3

<https://wordnet.princeton.edu>

Christiane Fellbaum. Wordnet. The encyclopedia of applied linguistics, 1998

### BLESS, EVALution, Lenci/Benotto, Weeds

Can be obtained from: <https://github.com/vered1986/UnsupervisedHypernymy>

Marco Baroni and Alessandro Lenci. How we blessed distributional semantic evaluation. In Proceedings of the GEMS 2011 Workshop on GEometrical Models of Natural Language Semantics, pages 1–10. Association for Computational Linguistics, 2011

Enrico Santus, Frances Yung, Alessandro Lenci, and Chu-Ren Huang. Evalution 1.0: an evolving semantic dataset for training and evaluation of distributional semantic models. In Proceedings of the 4th Workshop on Linked Data in Linguistics: Resources and Applications, pages 64–69, 2015

Alessandro Lenci and Giulia Benotto. Identifying hypernyms in distribu- tional semantic spaces. In * SEM 2012: The First Joint Conference on Lexical and Computational Semantics–Volume 1: Proceedings of the main conference and the shared task, and Volume 2: Proceedings of the Sixth International Workshop on Semantic Evaluation (SemEval 2012), pages 75–79, 2012

Julie Weeds, Daoud Clarke, Jeremy Reffin, David Weir, and Bill Keller. Learning to distinguish hypernyms and co-hyponyms. In Proceedings of COLING 2014, the 25th International Conference on Computational Linguistics: Technical Papers, pages 2249–2259. Dublin City University and Association for Computational Linguistics, 2014
