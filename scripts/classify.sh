#!/bin/bash
function process {
  seconds=$1
  classifier=$2
  path=processed/run9/${seconds}
  mkdir -p ${path}/{{lm,nb,svm}_{all,fw}}

  dataPreparation/separate.sh ../../processed/run9/deletionRevisions.csv ${seconds}
  # start language model on data:
  ${classifier}/evaluate_posts.sh
  # move data files:
  mv data/{blocked,notBlocked,notBlocked_full}.txt ${path}/
  # move LM output:
  mv data/output_{n,}b.csv ${path}/${classifier}/
  # move LM log:
  mv data/evaluation.log ${path}/${classifier}/
  # move LM confusion matrix:
  mv postprocessing/confusionMatrix.tex ${path}/${classifier}/
  # move LM AUC data:
  mv AUC/auc*.png ${path}/${classifier}/
}

#             13h,    1d,   1.5d,     2d,   2.5d,     3d,     4d,     5d,     6d
timeframes=(46800, 86400, 129600, 172800, 216000, 259200, 345600, 432000, 518400)

for timeframe in "${timeframes[@]}"; do
  process ${timeframe} lm_all
done
