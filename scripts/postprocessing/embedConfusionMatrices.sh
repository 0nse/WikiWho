#!/bin/bash
#
# Usage: ./embedConfusionMatrices.sh
#
# A new directory called "timeframes" is created in which all confusion matrices
# are stored. An additional "appendix.tex" is created, which can be used to
# embed all tables into a LaTeX document.

# set this directory as current working directory:
cd "$(dirname "$0")"

#             13h,   1d,  1.5d,    2d,  2.5d,    3d,    4d,    5d,    6d
timeframes=(46800 86400 129600 172800 216000 259200 345600 432000 518400)
classifiers=("lm" "nb" "svm")
path=../processed/timeframes
mkdir -p ${path}
latex=${path}/appendix.tex

echo "% For this tex file to compile, you will need to import the package extraplaceins." > ${latex}
echo "% Using it as \usepackage[section,subsection]{extraplaceins} is recommended." >> ${latex}
echo "%" >> ${latex}
echo "% Download extraplaceins: http://lexfridman.com/files/research/extraplaceins.sty" >> ${latex}
echo "%" >> ${latex}
echo "\section{Confusion Matrices for Various Timeframes}" >> ${latex}
i=0
for timeframe in "${timeframes[@]}"; do
  echo "\subsection{${timeframe}}" >> ${latex}
  mkdir -p ${path}/${timeframe}
    for classifier in "${classifiers[@]}"; do
      cp ../processed/run9/${timeframe}/${classifier}_all/confusionMatrix.tex ${path}/${timeframe}/${classifier}.tex
      echo "\input{content/appendix/timeframes/${timeframe}/${classifier}}" >> ${latex}

      # LaTeX will not place more than 18 tables (or floating environments in
      # general). One can use a \clearpage or like we do in this case, a
      # \FloatBarrier. The later is from the placeins package.
      if [ "$((++i % 3))" -eq 0 ]; then
        echo "\FloatBarrier" >> ${latex}
      fi
  done
done
