#!/bin/bash
#
# Usage: ./embedConfusionMatrices.sh
#
# A new directory called "timeframes" is created in which all confusion matrices
# are stored. An additional "appendix.tex" is created, which can be used to
# embed all tables into a LaTeX document.

#             13h,   1d,  1.5d,    2d,  2.5d,    3d,    4d,    5d,    6d
timeframes=(46800 86400 129600 172800 216000 259200 345600 432000 518400)
classifiers=("lm" "nb" "svm")
path=../processed/run9/timeframes
latex=${path}/appendix.tex

echo "\subsection{Confusion Matrices for Various Timeframes}" > ${latex}
i=0
for timeframe in "${timeframes[@]}"; do
  echo "\subsubsection{${timeframe}}" >> ${latex}
  mkdir -p ${path}/${timeframe}
    for classifier in "${classifiers[@]}"; do
      cp ~/WikiWho/scripts/processed/run9/${timeframe}/${classifier}_all/confusionMatrix.tex ${path}/${timeframe}/${classifier}.tex
      echo "\input{content/appendix/timeframes/${timeframe}/${classifier}}" >> ${latex}

      # LaTeX will not place more than 18 tables (or floating environments in
      # general) without a \clearpage (e.g. triggered by a \chapter):
      if [ "$((++i % 2))" -eq 0]; then
        echo "\clearpage" >> ${latex}
      fi
  done
done
