#!/bin/bash
#
# Usage: ./confusionMatrix.sh "3 days" "SVM" 5000 3000 2000 9000
#
# with $1 being the timeframe in words for the LaTeX table caption
#      $2 the classifier name for LaTeX table caption
#      $3 true positives
#      $4 false positives
#      $5 false negatives
#      $6 true positives
# optional parameters are
#      $7 optimistic AUC
#      $8 AUC
#      $9 pessimistic AUC
# If an optional parameter is provided, the calculation from the provided first
# variables is skipped. This is important for classifiers other than the LM.

# set this directory as current working directory:
cd "$(dirname "$0")"

function createLaTeXTable {
  timeframeMnemonic=$1
  classifier=$2
  truePositives=$3
  falsePositives=$4
  falseNegatives=$5
  trueNegatives=$6
  auc_opt=$7
  auc=$8
  auc_pess=$9

  negativePrecision=`calc "${trueNegatives}. / (${trueNegatives} + ${falseNegatives})"`
  positivePrecision=`calc "${truePositives}. / (${truePositives} + ${falsePositives})"`

  positiveRecall=`calc "${truePositives}. / (${truePositives} + ${falseNegatives})"`
  negativeRecall=`calc "${trueNegatives}. / (${trueNegatives} + ${falsePositives})"`

  accuracy=`calc "(${trueNegatives}. + ${truePositives}) / (${trueNegatives} + ${falseNegatives} + ${falsePositives} + ${truePositives})"`

  # We use 0.02 as calc will multiply by 100, assuming it is not already a
  # percentage:
  positiveF1=`calc "0.02 * (${positivePrecision} * ${positiveRecall}) / (${positivePrecision} + ${positiveRecall})"`
  negativeF1=`calc "0.02 * (${negativePrecision} * ${negativeRecall}) / (${negativePrecision} + ${negativeRecall})"`

  # Calculate the AUC if not provided. Needed for LM. In any case, round:
  if [ -z "${auc_opt}" ];  then auc_opt=`processAUCOutput optimistic`; fi
  auc_opt=`round3DecimalPlaces ${auc_opt}`
  if [ -z "${auc}" ];      then auc=`processAUCOutput AUC`; fi
  auc=`round3DecimalPlaces ${auc}`
  if [ -z "${auc_pess}" ]; then auc_pess=`processAUCOutput pessimistic`; fi
  auc_pess=`round3DecimalPlaces ${auc_pess}`

  # using !htbp may seem a bit harsh but otherwise you either have the choice of
  # all sections appearing after each other and then all floats or two floats on
  # one page, one float on the next page, a single section on an otherwise empty
  # page and then floats again.
  echo "\begin{table}[!htbp]
  \begin{tabular}{c | c  c  c}
    \cline{2-4}
    & \textbf{True positive} & \textbf{True negative} & \multicolumn{1}{|c}{\textbf{Precision (\%)}}
    \\\\\hline
    \textbf{Predicted positive}  & ${truePositives} & ${falsePositives} & \multicolumn{1}{|c}{${positivePrecision}} \\\\
    \textbf{Predicted negative}  & ${falseNegatives} & ${trueNegatives} & \multicolumn{1}{|c}{${negativePrecision}} \\\\\hline
    \textbf{Recall (\%)}         & ${positiveRecall} & ${negativeRecall} & \multicolumn{1}{|c}{} \\\\
    \textbf{F1 score (\%)}       & ${positiveF1} & ${negativeF1} & \multicolumn{1}{|c}{} \\\\\cline{1-3}
    \textbf{Accuracy (\%)}       & ${accuracy} & & \\\\
    \textbf{AUC (optimistic)}    & ${auc_opt} & & \\\\
    \textbf{AUC}                 & ${auc} & & \\\\
    \textbf{AUC (pessimistic)}   & ${auc_pess} & &
  \end{tabular}
  \label{t:confusionMatrix_${RANDOM}} % give it a meaningful name; we use a pseudorandom number to prevent naming clashes
  \caption{The confusion matrix built from the full text ${classifier} predictions. Contributions made ${timeframeMnemonic} before a blocking was issued, were assumed to have been of disruptive nature.}
\end{table}" > confusionMatrix.tex
}

function calc {
  # Use python for calculations and round to 2 decimal places.
  # The multiplication with 100 is used for percentages.
  echo `python -c "print(round(${1} * 100, 2))"`
}

function round3DecimalPlaces {
  echo `python -c "print(round(${1}, 3))"`
}

function processAUCOutput {
  # $1 can be of type "AUC", "optimistic" or "pessimistic"'
  output=`../../venv/bin/python3 ../AUC/AUC.py $1 --dir ../AUC/. | tail -n 1`
  # Remove leading "AUC:	":
  echo ${output:5}
}

# Run LaTeX table creation function with all arguments passed:
createLaTeXTable "$@"
