# WikiWho Scripts
These scripts are intended to postprocess the results of `WikiWho.py`.
Classifiers can be run on the data, including a 4-gram language model with Kneser-Ney smoothing, a multinomial naïve Bayes classifier and a support vector machine.
The latter two use RapidMiner.
The scripts also contain some plotting options (see the `dataAnalysis` and `postprocessing` directories).
Classifier performance is stored as LaTeX tables containing recall, precision, F1 score, accuracy and AUC.

The classifications are full text classifications without stop word removal.
Additionally, function words classifications are done.
The list of function words is taken from that compiled by [Leah Gilner and Franc Morales](http://www.sequencepublishing.com/academic.html).

## Requirements
The language model scripts require the
* [Generalised Language Modeling Toolkit](https://github.com/renepickhardt/generalized-language-modeling-toolkit).
* They were successfully tested using [revision cebbff8](https://github.com/renepickhardt/generalized-language-modeling-toolkit/tree/cebbff8a740d4afd97316239a4259f2e4840f566).

The SVM and NB classifier use
* [Rapidminer 5.3.015](https://github.com/rapidminer/rapidminer-5).
* [Parallel Processing Extension 5.3.000](https://marketplace.rapidminer.com/UpdateServer/faces/product_details.xhtml?productId=rmx_parallel)
* [Text Processing Extension 5.3.002](https://marketplace.rapidminer.com/UpdateServer/faces/product_details.xhtml?productId=rmx_text)

It is advised to run all Python scripts using Python 3 although some are compatible with Python 2 as well.
The scripts contain information about their dependencies. These are:
* [NumPy](http://www.numpy.org/)
* [Matplotlib](http://matplotlib.org/)
* [MediaWiki Utilities 0.4.18](https://github.com/mediawiki-utilities/python-mediawiki-utilities)

To execute all full text classifiers on different timeframes, run `classify.sh`.
The results will be stored in `processed/run9` containing LaTeX tables as well as raw classifier data.
Calling the classification toolchain with a seconds parameter, e.g. `classify.sh 86400`, will run classifications for a single timeframe.
Passing a third parameter will make all classifications use the sliding window approach instead of the independent posts approach.
The latter is the default.
When using the sliding window approach, linear sampling should be used in RapidMiner.
For the independent posts approach, use stratified sampling.
This has not been automated; please refer to `dataPreparation/createRapidMinerFiles.sh`.
