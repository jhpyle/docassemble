from docassemble.base.util import (
    set_knn_machine_learner,
    set_machine_learning_entry,
    set_random_forest_machine_learner,
    set_svm_machine_learner,
)
from docassemble.webapp.ml.machinelearning import (
    SimpleTextMachineLearner,
    MachineLearningEntry,
    RandomForestMachineLearner,
    SVMMachineLearner,
)

set_knn_machine_learner(SimpleTextMachineLearner)
set_machine_learning_entry(MachineLearningEntry)
set_random_forest_machine_learner(RandomForestMachineLearner)
set_svm_machine_learner(SVMMachineLearner)
