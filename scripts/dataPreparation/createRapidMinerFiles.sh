#!/bin/bash
#
# Usage: ./createRapidMinerFiles.sh
#
# Dependencies: RapidMiner5 installed under ~/RapidMiner
#
# Generates all relevant RapidMiner files (data and processes) for full text SVM
# and LM. SOC would put the XML snippets into separate files but this is merely
# a quick and dirty solution.
#
# If an input parameter is given, it will be used instead of iterating over all
# timeframes.
#
# Databases will be stored in ~/RapidMiner/repository/data/timeframes -- make
# sure, you have run classify_lm.sh beforehand.
# Processes will be stored in ~/RapidMiner/repository/processes
#
# Please note that you should use stratified sampling for tests using the
# independent posts approach and linear sampling for tests using the sliding
# window approach. If you want this script to be fully automatic, you can pass a
# a sliding window variable and change the code below appropriately.

# set this directory as current working directory:
cd "$(dirname "$0")"

source ../helpers.sh
# Reduce the array to the input parameter if any:
timeframes=(`returnTimeFrames "$1"`)

fileNames=(blocked notBlocked)
classifiers=(svm_all nb_all)

# This part gets a bit hackish but so is the whole script.
if [ "${#timeframes[@]}" -eq 1 ]; then
  # If we only provide one timeframe, we want to iterate twice over it. Once
  # with full text classification and the second time only considering
  # function words.
  timeframes=(${timeframes} ${timeframes})
  classifiers=("${classifiers[0]}" "${classifiers[1]}" svm_fw nb_fw)
  echo "[I] Files for full text and function words classification will be created."
fi

repositoryPath=~/RapidMiner/repository
storePath=${repositoryPath}/processes/store
timeframePath=${repositoryPath}/processes/timeframes
mkdir ${storePath}

# Create the properties file:
echo '<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<!DOCTYPE properties SYSTEM "http://java.sun.com/dtd/properties.dtd">
<properties>
<comment>Properties of repository entry store</comment>
<entry key="owner">0nse</entry>
</properties>' > ${storePath}/store.properties

for timeframe in "${timeframes[@]}"; do
  # create directory for storing the RM data container:
  mkdir -p ${repositoryPath}/data/timeframes/${timeframe}

  for fileName in "${fileNames[@]}"; do
    contributionsPath=~/WikiWho/scripts/processed/run9/${timeframe}/${fileName}

    # remove <BOP> and <EOP> for processing with RM:
    sed -r 's/<BOP> (.*) <EOP>/\1/g' ${contributionsPath}.txt > ${contributionsPath}_tmp.txt

    echo '<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<process version="5.3.015">
  <context>
    <input/>
    <output/>
    <macros/>
  </context>
  <operator activated="true" class="process" compatibility="5.3.015" expanded="true" name="Process">
    <parameter key="logverbosity" value="init"/>
    <parameter key="random_seed" value="2001"/>
    <parameter key="send_mail" value="never"/>
    <parameter key="notification_email" value=""/>
    <parameter key="process_duration_for_mail" value="30"/>
    <parameter key="encoding" value="SYSTEM"/>
    <parameter key="parallelize_main_process" value="false"/>
    <process expanded="true">
      <operator activated="true" class="read_csv" compatibility="5.3.015" expanded="true" height="60" name="Read CSV" width="90" x="112" y="120">
        <parameter key="csv_file" value="'${contributionsPath}'_tmp.txt"/>
        <parameter key="column_separators" value=";"/>
        <parameter key="trim_lines" value="false"/>
        <parameter key="use_quotes" value="true"/>
        <parameter key="quotes_character" value="&quot;"/>
        <parameter key="escape_character" value="\"/>
        <parameter key="skip_comments" value="false"/>
        <parameter key="comment_characters" value="#"/>
        <parameter key="parse_numbers" value="true"/>
        <parameter key="decimal_character" value="."/>
        <parameter key="grouped_digits" value="false"/>
        <parameter key="grouping_character" value=","/>
        <parameter key="date_format" value=""/>
        <parameter key="first_row_as_names" value="false"/>
        <list key="annotations"/>
        <parameter key="time_zone" value="SYSTEM"/>
        <parameter key="locale" value="English (United States)"/>
        <parameter key="encoding" value="UTF-8"/>
        <list key="data_set_meta_data_information">
          <parameter key="0" value="PostContent.true.text.attribute"/>
        </list>
        <parameter key="read_not_matching_values_as_missings" value="true"/>
        <parameter key="datamanagement" value="double_array"/>
      </operator>
      <operator activated="true" class="store" compatibility="5.3.015" expanded="true" height="60" name="Store" width="90" x="313" y="120">
        <parameter key="repository_entry" value="//Local Repository/data/timeframes/'${timeframe}'/'${fileName}'"/>
      </operator>
      <connect from_op="Read CSV" from_port="output" to_op="Store" to_port="input"/>
      <portSpacing port="source_input 1" spacing="0"/>
      <portSpacing port="sink_result 1" spacing="0"/>
    </process>
  </operator>
</process>' > ${storePath}/store.rmp
    ~/RapidMiner/scripts/rapidminer '//Local Repository/processes/store/store'
    # remove the temporary file. Inplace editing (sed -i) is not of interest so
    # that the input files remain usable for further LM analysation.
    rm ${contributionsPath}_tmp.txt
  done

  # create directory for the RM processes:
  mkdir -p ${timeframePath}/${timeframe}

  for classifier in "${classifiers[@]}"; do
    classifierPath=${timeframePath}/${timeframe}/${classifier}
    echo "[I] Creating process files for ${classifier}"
    # create properties file for the classifiers:
    echo '<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<!DOCTYPE properties SYSTEM "http://java.sun.com/dtd/properties.dtd">
<properties>
<comment>Properties of repository entry '${classifier}'</comment>
<entry key="owner">0nse</entry>
</properties>' > ${classifierPath}.properties

    echo '<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<process version="5.3.015">
  <context>
    <input/>
    <output/>
    <macros/>
  </context>
  <operator activated="true" class="process" compatibility="5.3.015" expanded="true" name="Process">
    <parameter key="logverbosity" value="init"/>
    <parameter key="logfile" value="rm_svm.log"/>
    <parameter key="resultfile" value="rm_svm_results.log"/>
    <parameter key="random_seed" value="2001"/>
    <parameter key="send_mail" value="never"/>
    <parameter key="notification_email" value=""/>
    <parameter key="process_duration_for_mail" value="30"/>
    <parameter key="encoding" value="SYSTEM"/>
    <parameter key="parallelize_main_process" value="false"/>
    <process expanded="true">
      <operator activated="true" class="retrieve" compatibility="5.3.015" expanded="true" height="60" name="Retrieve blocked" width="90" x="45" y="345">
        <parameter key="repository_entry" value="../../../data/timeframes/'${timeframe}'/blocked"/>
      </operator>
      <operator activated="true" class="generate_attributes" compatibility="5.3.015" expanded="true" height="76" name="True=wasBlocked" width="90" x="179" y="345">
        <list key="function_descriptions">
          <parameter key="wasBlocked" value="1==1"/>
        </list>
        <parameter key="use_standard_constants" value="true"/>
        <parameter key="keep_all" value="true"/>
      </operator>
      <operator activated="true" class="retrieve" compatibility="5.3.015" expanded="true" height="60" name="Retrieve notBlocked" width="90" x="45" y="480">
        <parameter key="repository_entry" value="../../../data/timeframes/'${timeframe}'/notBlocked"/>
      </operator>
      <operator activated="true" class="generate_attributes" compatibility="5.3.015" expanded="true" height="76" name="False=wasBlocked" width="90" x="179" y="480">
        <list key="function_descriptions">
          <parameter key="wasBlocked" value="1!=1"/>
        </list>
        <parameter key="use_standard_constants" value="true"/>
        <parameter key="keep_all" value="true"/>
      </operator>
      <operator activated="true" class="union" compatibility="5.3.015" expanded="true" height="76" name="Union" width="90" x="313" y="390"/>
      <operator activated="true" class="set_role" compatibility="5.3.015" expanded="true" height="76" name="Label wasBlocked" width="90" x="179" y="30">
        <parameter key="attribute_name" value="wasBlocked"/>
        <parameter key="target_role" value="label"/>
        <list key="set_additional_roles"/>
      </operator>
      <operator activated="true" class="discretize_by_user_specification" compatibility="5.3.015" expanded="true" height="94" name="Separate data by label" width="90" x="313" y="30">
        <parameter key="return_preprocessing_model" value="false"/>
        <parameter key="create_view" value="false"/>
        <parameter key="attribute_filter_type" value="single"/>
        <parameter key="attribute" value="wasBlocked"/>
        <parameter key="attributes" value=""/>
        <parameter key="use_except_expression" value="false"/>
        <parameter key="value_type" value="numeric"/>
        <parameter key="use_value_type_exception" value="false"/>
        <parameter key="except_value_type" value="real"/>
        <parameter key="block_type" value="value_series"/>
        <parameter key="use_block_type_exception" value="false"/>
        <parameter key="except_block_type" value="value_series_end"/>
        <parameter key="invert_selection" value="false"/>
        <parameter key="include_special_attributes" value="true"/>
        <parameter key="attribute_type" value="nominal"/>
        <list key="classes">
          <parameter key="False" value="0.1"/>
          <parameter key="True" value="Infinity"/>
        </list>
      </operator>
      <operator activated="true" class="text:process_document_from_data" compatibility="5.3.002" expanded="true" height="76" name="Post: Tokenise, split" width="90" x="447" y="30">
        <parameter key="create_word_vector" value="true"/>
        <parameter key="vector_creation" value="TF-IDF"/>
        <parameter key="add_meta_information" value="true"/>
        <parameter key="keep_text" value="false"/>
        <parameter key="prune_method" value="none"/>
        <parameter key="prune_below_percent" value="3.0"/>
        <parameter key="prune_above_percent" value="30.0"/>
        <parameter key="prune_below_rank" value="0.05"/>
        <parameter key="prune_above_rank" value="0.95"/>
        <parameter key="datamanagement" value="double_sparse_array"/>
        <parameter key="select_attributes_and_weights" value="false"/>
        <list key="specify_weights"/>
        <parameter key="parallelize_vector_creation" value="false"/>
        <process expanded="true">
          <operator activated="true" class="text:tokenize" compatibility="5.3.002" expanded="true" height="60" name="Tokenize to words" width="90" x="179" y="30">
            <parameter key="mode" value="non letters"/>
            <parameter key="characters" value=".:"/>
            <parameter key="language" value="English"/>
            <parameter key="max_token_length" value="3"/>
          </operator>
          <operator activated="true" class="text:stem_snowball" compatibility="5.3.002" expanded="true" height="60" name="Stem (Snowball)" width="90" x="380" y="30">
            <parameter key="language" value="English"/>
          </operator>' > ${classifierPath}.rmp
    ##################
    # Function words #
    ##################
    if [[ "${classifier}" = *"_fw" ]]; then
      echo '<operator activated="true" class="text:filter_tokens_by_content" compatibility="5.3.002" expanded="true" height="60" name="Filter (I/You, Function Words)" width="90" x="581" y="30">
              <parameter key="condition" value="matches"/>
              <parameter key="regular_expression" value="i|a|aboard|about|above|absent|according|accordingly|across|after|against|ahead|albeit|all|along|alongside|although|amid|amidst|among|amongst|an|and|another|anti|any|anybody|anyone|anything|around|as|aside|astraddle|astride|at|away|bar|barring|be|because|before|behind|below|beneath|beside|besides|between|beyond|bit|both|but|by|can|certain|circa|concerning|consequently|considering|could|dare|deal|despite|down|during|each|either|enough|every|everybody|everyone|everything|except|excepting|excluding|failing|few|fewer|following|for|four|from|given|great|had|he|heaps|hence|her|hers|herself|him|himself|his|however|if|in|including|inside|instead|into|it|its|itself|less|like|little|loads|lots|many|may|me|might|mine|minus|more|most|much|must|my|myself|near|neither|nevertheless|no|nobody|none|nor|nothing|notwithstanding|of|off|on|once|one|onto|or|other|ought|our|ours|ourselves|out|outside|over|past|pending|per|plenty|plus|regarding|respecting|round|save|saving|several|shall|she|should|since|so|some|somebody|someone|something|such|than|that|the|their|theirs|them|themselves|then|thence|therefore|these|they|this|those|though|three|through|throughout|thru|thus|till|to|toward|towards|two|under|underneath|unless|unlike|until|unto|up|upon|us|various|versus|via|wanting|we|what|whatever|when|whence|whenever|where|whereas|wherever|whether|which|whichever|while|whilst|who|whoever|whom|whomever|whose|will|with|within|without|would|yet|you|your|yours|yourself|yourselves"/>
            </operator>
            <connect from_op="Tokenize to words" from_port="document" to_op="Filter (I/You, Function Words)" to_port="document"/>
            <connect from_op="Filter (I/You, Function Words)" from_port="document" to_op="Stem (Snowball)" to_port="document"/>
            <connect from_op="Stem (Snowball)" from_port="document" to_port="document 1"/>' >> ${classifierPath}.rmp
    else
       echo '<connect from_op="Tokenize to words" from_port="document" to_op="Stem (Snowball)" to_port="document"/>
             <connect from_op="Stem (Snowball)" from_port="document" to_port="document 1"/>' >> ${classifierPath}.rmp
    fi
    echo '<connect from_port="document" to_op="Tokenize to words" to_port="document"/>
          <portSpacing port="source_document" spacing="0"/>
          <portSpacing port="sink_document 1" spacing="0"/>
          <portSpacing port="sink_document 2" spacing="0"/>
        </process>
      </operator>
      <operator activated="true" class="parallel:x_validation_parallel" compatibility="5.3.000" expanded="true" height="112" name="X-Validation" width="90" x="581" y="30">
        <parameter key="create_complete_model" value="false"/>
        <parameter key="average_performances_only" value="true"/>
        <parameter key="leave_one_out" value="false"/>
        <parameter key="number_of_validations" value="10"/>
<!-- USE LINEAR SAMPLING FOR TESTS USING THE SLIDING WINDOW APPROACH
        <parameter key="sampling_type" value="linear sampling"/> -->
<!-- USE STRATIFIED SAMPLING FOR TESTS USING THE INDEPENT POSTS APPROACH -->
        <parameter key="sampling_type" value="stratified sampling"/>
        <parameter key="use_local_random_seed" value="true"/>
        <parameter key="local_random_seed" value="3055"/>
        <parameter key="number_of_threads" value="4"/>
        <parameter key="parallelize_training" value="true"/>
        <parameter key="parallelize_testing" value="true"/>
        <process expanded="true">' >> ${classifierPath}.rmp
    ####################
    # Switch operators #
    ####################
    if [[ "${classifier}" = "nb_"* ]]; then # NB
      echo '          <operator activated="true" class="naive_bayes" compatibility="5.3.015" expanded="true" height="76" name="Naive Bayes" width="90" x="112" y="255">
            <parameter key="laplace_correction" value="true"/>
          </operator>
          <connect from_port="training" to_op="Naive Bayes" to_port="training set"/>
          <connect from_op="Naive Bayes" from_port="model" to_port="model"/>' >> ${classifierPath}.rmp
    else # SVM
      echo '          <operator activated="true" class="support_vector_machine" compatibility="5.3.015" expanded="true" height="112" name="SVM" width="90" x="112" y="30">
            <parameter key="kernel_type" value="dot"/>
            <parameter key="kernel_gamma" value="1.0"/>
            <parameter key="kernel_sigma1" value="1.0"/>
            <parameter key="kernel_sigma2" value="0.0"/>
            <parameter key="kernel_sigma3" value="2.0"/>
            <parameter key="kernel_shift" value="1.0"/>
            <parameter key="kernel_degree" value="2.0"/>
            <parameter key="kernel_a" value="1.0"/>
            <parameter key="kernel_b" value="0.0"/>
            <parameter key="kernel_cache" value="200"/>
            <parameter key="C" value="0.0"/>
            <parameter key="convergence_epsilon" value="0.001"/>
            <parameter key="max_iterations" value="100000"/>
            <parameter key="scale" value="true"/>
            <parameter key="calculate_weights" value="true"/>
            <parameter key="return_optimization_performance" value="true"/>
            <parameter key="L_pos" value="1.0"/>
            <parameter key="L_neg" value="1.0"/>
            <parameter key="epsilon" value="0.0"/>
            <parameter key="epsilon_plus" value="0.0"/>
            <parameter key="epsilon_minus" value="0.0"/>
            <parameter key="balance_cost" value="false"/>
            <parameter key="quadratic_loss_pos" value="false"/>
            <parameter key="quadratic_loss_neg" value="false"/>
            <parameter key="estimate_performance" value="false"/>
          </operator>
          <connect from_port="training" to_op="SVM" to_port="training set"/>
          <connect from_op="SVM" from_port="model" to_port="model"/>' >> ${classifierPath}.rmp
    fi
    ######################
    # Performance output #
    ######################
    echo '          <portSpacing port="source_training" spacing="0"/>
          <portSpacing port="sink_model" spacing="0"/>
          <portSpacing port="sink_through 1" spacing="0"/>
        </process>
        <process expanded="true">
          <operator activated="true" class="apply_model" compatibility="5.3.015" expanded="true" height="76" name="Apply Model" width="90" x="45" y="30">
            <list key="application_parameters"/>
            <parameter key="create_view" value="false"/>
          </operator>
          <operator activated="true" class="write_model" compatibility="5.3.015" expanded="true" height="60" name="Write Model" width="90" x="380" y="75">
            <parameter key="model_file" value="'${classifier}'_model.mod"/>
            <parameter key="overwrite_existing_file" value="true"/>
            <parameter key="output_type" value="XML Zipped"/>
          </operator>
          <operator activated="true" class="multiply" compatibility="5.3.015" expanded="true" height="94" name="Multiply" width="90" x="112" y="165"/>
          <operator activated="true" class="performance" compatibility="5.3.015" expanded="true" height="76" name="Performance" width="90" x="179" y="30">
            <parameter key="use_example_weights" value="true"/>
          </operator>
          <operator activated="true" class="performance_binominal_classification" compatibility="5.3.015" expanded="true" height="76" name="Performance (3)" width="90" x="246" y="165">
            <parameter key="main_criterion" value="first"/>
            <parameter key="accuracy" value="false"/>
            <parameter key="classification_error" value="false"/>
            <parameter key="kappa" value="false"/>
            <parameter key="AUC (optimistic)" value="true"/>
            <parameter key="AUC" value="true"/>
            <parameter key="AUC (pessimistic)" value="true"/>
            <parameter key="precision" value="false"/>
            <parameter key="recall" value="false"/>
            <parameter key="lift" value="false"/>
            <parameter key="fallout" value="false"/>
            <parameter key="f_measure" value="true"/>
            <parameter key="false_positive" value="false"/>
            <parameter key="false_negative" value="false"/>
            <parameter key="true_positive" value="false"/>
            <parameter key="true_negative" value="false"/>
            <parameter key="sensitivity" value="false"/>
            <parameter key="specificity" value="false"/>
            <parameter key="youden" value="false"/>
            <parameter key="positive_predictive_value" value="false"/>
            <parameter key="negative_predictive_value" value="false"/>
            <parameter key="psep" value="false"/>
            <parameter key="skip_undefined_labels" value="true"/>
            <parameter key="use_example_weights" value="true"/>
          </operator>
          <operator activated="true" class="write_performance" compatibility="5.3.015" expanded="true" height="60" name="Write Performance (2)" width="90" x="380" y="165">
            <parameter key="performance_file" value="'${classifier}'_auc.per"/>
          </operator>
          <connect from_port="model" to_op="Apply Model" to_port="model"/>
          <connect from_port="test set" to_op="Apply Model" to_port="unlabelled data"/>
          <connect from_op="Apply Model" from_port="labelled data" to_op="Multiply" to_port="input"/>
          <connect from_op="Apply Model" from_port="model" to_op="Write Model" to_port="input"/>
          <connect from_op="Multiply" from_port="output 1" to_op="Performance (3)" to_port="labelled data"/>
          <connect from_op="Multiply" from_port="output 2" to_op="Performance" to_port="labelled data"/>
          <connect from_op="Performance" from_port="performance" to_port="averagable 1"/>
          <connect from_op="Performance (3)" from_port="performance" to_op="Write Performance (2)" to_port="input"/>
          <portSpacing port="source_model" spacing="0"/>
          <portSpacing port="source_test set" spacing="0"/>
          <portSpacing port="source_through 1" spacing="0"/>
          <portSpacing port="sink_averagable 1" spacing="0"/>
          <portSpacing port="sink_averagable 2" spacing="0"/>
        </process>
      </operator>
      <operator activated="true" class="write_performance" compatibility="5.3.015" expanded="true" height="60" name="Write Performance" width="90" x="581" y="210">
        <parameter key="performance_file" value="'${classifier}'_performance"/>
      </operator>
      <connect from_op="Retrieve blocked" from_port="output" to_op="True=wasBlocked" to_port="example set input"/>
      <connect from_op="True=wasBlocked" from_port="example set output" to_op="Union" to_port="example set 1"/>
      <connect from_op="Retrieve notBlocked" from_port="output" to_op="False=wasBlocked" to_port="example set input"/>
      <connect from_op="False=wasBlocked" from_port="example set output" to_op="Union" to_port="example set 2"/>
      <connect from_op="Union" from_port="union" to_op="Label wasBlocked" to_port="example set input"/>
      <connect from_op="Label wasBlocked" from_port="example set output" to_op="Separate data by label" to_port="example set input"/>
      <connect from_op="Separate data by label" from_port="example set output" to_op="Post: Tokenise, split" to_port="example set"/>
      <connect from_op="Post: Tokenise, split" from_port="example set" to_op="X-Validation" to_port="training"/>
      <connect from_op="X-Validation" from_port="model" to_port="result 1"/>
      <connect from_op="X-Validation" from_port="averagable 1" to_op="Write Performance" to_port="input"/>
      <connect from_op="Write Performance" from_port="through" to_port="result 2"/>
      <portSpacing port="source_input 1" spacing="0"/>
      <portSpacing port="sink_result 1" spacing="0"/>
      <portSpacing port="sink_result 2" spacing="0"/>
      <portSpacing port="sink_result 3" spacing="0"/>
    </process>
  </operator>
</process>' >> ${classifierPath}.rmp
  done
done
# it's just a temporary helper, so remove it again:
rm -r ${storePath}
