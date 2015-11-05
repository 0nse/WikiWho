#!/bin/bash
function process {
  seconds=$1
  path=processed/run9/${seconds}
  mkdir -p ${path}/{lm,svm,nb}

  dataPreparation/separate.sh ../processed/run9/deletionRevisions.csv ${seconds}
  # start language model on data:
  lm/evaluate_posts.sh
  # move data files:
  mv data/{blocked,notBlocked,notBlocked_full}.txt ${path}/
  # move LM output:
  mv data/output_{n,}b.csv ${path}/lm/
  # move LM log:
  mv data/evaluation.log ${path}/lm/
  # move LM confusion matrix:
  mv postprocessing/confusionMatrix.tex ${path}/lm/
  # move LM AUC data:
  mv AUC/auc*.png ${path}/lm/
}

# 13h
process(46800)
# 1)
process(86400)
# 1.5)
process(129600)
# 2)
process(172800)
# 2.5)
process(216000)
# 3)
process(259200)
# 4)
process(345600)
# 5)
process(432000)
# 6)
process(518400)
