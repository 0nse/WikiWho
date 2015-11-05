#!/bin/bash
#
# Usage: ./confusionMatrix.sh 5000 3000 2000 9000
#
# with $1 being true negatives
#      $2 false negatives
#      $3 false positives
#      $4 true negatives

# set this directory as current working directory:
cd "$(dirname "$0")"

function createLaTeXTable {
  trueNegatives=$1
  falseNegatives=$2
  falsePositives=$3
  truePositives=$4

  negativePrecision=`calc "${trueNegatives}. / (${trueNegatives} + ${falseNegatives})"`
  positivePrecision=`calc "${truePositives}. / (${truePositives} + ${falsePositives})"`

  positiveRecall=`calc "${truePositives}. / (${truePositives} + ${falseNegatives})"`
  negativeRecall=`calc "${trueNegatives}. / (${trueNegatives} + ${falsePositives})"`

  accuracy=`calc "(${trueNegatives}. + ${truePositives}) / (${trueNegatives} + ${falseNegatives} + ${falsePositives} + ${truePositives})"`

  auc_opt=`processAUCOutput optimistic`
  auc_pess=`processAUCOutput pessimistic`
  auc=`processAUCOutput AUC`

  echo "\begin{tabular}
  \begin{table}{ | c | c  c  c |}
    \hline
    & \textbf{True negative} & \textbf{True positive} & \textbf{Precision (\%)}
    \\\\\hline
    \textbf{Predicted negative}  & ${trueNegatives} & ${falseNegatives} & \multicolumn{1}{|c}{${negativePrecision}}\\\\
    \textbf{Predicted positive}  & ${falsePositives} & ${truePositives} & \multicolumn{1}{|c}{${positivePrecision}} \\\\\hline
    \textbf{Recall (\%)}         & ${negativeRecall} & ${positiveRecall} & \\\\
    \textbf{Accuracy (\%)}       & ${accuracy} & & \\\\
    \textbf{AUC (optimistic)}    & ${auc_opt} & & \\\\
    \textbf{AUC}                 & ${auc} & & \\\\
    \textbf{AUC (pessimistic)}   & ${auc_pess} & & \\\\\hline
  \end{table}
  \label{t:confusionMatrix_${RANDOM}} % give it a meaningful name; we use a pseudorandom number to prevent naming clashes
  \caption{The confusion matrix of the language model considering [all words|only function words]. Contributions made XXX days before a blocking was issued, were assumed to have been of disruptive nature.} % TODO choose between all or just function words and insert the days
\end{tabular}" > confusionMatrix.tex
}

function calc {
  # Use python for calculations and round to 2 decimal places.
  # The multiplication with 100 is used for percentages.
  echo `python -c "print(round(${1} * 100, 2))"`
}

function processAUCOutput {
  # $1 can be of type "AUC", "optimistic" or "pessimistic"'
  output=`../../venv/bin/python3 ../AUC/AUC.py $1 --dir ../AUC/. | tail -n 1`
  # Remove leading "AUC:	":
  echo ${output:5}
}

# Run LaTeX table creation function with all arguments passed:
createLaTeXTable $@
