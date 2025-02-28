# Clear workspace and set seed for reproducibility
rm(list = ls())
set.seed(1)  # Ensures consistent random sampling for reproducibility across runs

# Load Required Libraries
library(ggplot2)      # For data visualization (e.g., barplot)
library(rpart)        # For building decision trees
library(rpart.plot)   # For visualizing decision trees
library(randomForest) # For building random forest models
library(caret)        # For cross-validation and model training with tuning

# Load the training dataset
train <- read.csv("/Users/alveeramunshi/Documents/GitHub/learningData/data101/predictionchallenge2/Prediction2025-2Train.csv")
# Loads training data containing features like Groom_Age, Bride_MB, Outcome, etc.

# Marriages Outcomes
barplot(table(train$Outcome), 
        col = c("red", "green"), 
        main = "Marriage Outcome Dist", 
        ylab = "Count")
# Visualizes the count of marriage outcomes (Success/Failure) with a barplot; red = Failure, green = Success
# Comment: Success > Fail indicates class imbalance, which might affect model performance

# MBTI Outcomes
mbti_outcome_table <- table(train$Groom_MB, train$Bride_MB, train$Outcome)
mosaicplot(mbti_outcome_table, 
           color = c("red", "green"), 
           main = "Marriage Outcome by MBTI", 
           las = 2,  # Rotates axis labels for readability
           cex.axis = 0.8,  # Scales axis text size
           xlab = "Groom MBTI", ylab = "Bride MBTI")
# Creates a mosaic plot to explore how Groom and Bride MBTI types correlate with Outcome

# Convert Variables to Factors
train$Groom_MB  <- as.factor(train$Groom_MB)  # Myers-Briggs type for groom, categorical
train$Bride_MB  <- as.factor(train$Bride_MB)  # Myers-Briggs type for bride, categorical
train$Groom_Edu <- as.factor(train$Groom_Edu) # Education level of groom, categorical
train$Bride_Edu <- as.factor(train$Bride_Edu) # Education level of bride, categorical
train$Outcome   <- as.factor(train$Outcome)   # Target variable (Success/Failure), categorical

# Feature Engineering on Train
# AgeDiff: Difference in age between groom and bride. Positive means groom is older, negative means bride is older.
train$AgeDiff <- train$Groom_Age - train$Bride_Age  # Captures directional age gap

# sameEdu: Binary indicator of whether groom and bride have the same education level. Could signal compatibility or shared values.
train$sameEdu <- as.factor(ifelse(train$Groom_Edu == train$Bride_Edu, "Yes", "No"))  # Yes/No for education match

# age_rule: Categorical rule based on age difference. Assumes large positive differences favor success, large negative favor failure.
train$age_rule <- as.factor(ifelse(train$AgeDiff >= 7, "Success", 
                                   ifelse(train$AgeDiff <= -7, "Failure", "Neutral")))
# Creates a heuristic-based feature from AgeDiff with thresholds at ±7

# totalAge: Sum of groom and bride ages. Captures combined maturity or lifecycle stage, potentially affecting outcome.
train$totalAge <- train$Groom_Age + train$Bride_Age  # Combined age as a proxy for couple’s life stage

# eduLevelDiff: Numeric difference in education levels. Assumes education is ordinal (e.g., 1 = HS, 2 = Bachelor’s). Measures relative disparity.
train$eduLevelDiff <- as.numeric(train$Groom_Edu) - as.numeric(train$Bride_Edu)  # Numeric gap in education levels

# mbMatch: Binary indicator of whether groom and bride share the same Myers-Briggs type. Personality alignment might influence outcome.
train$mbMatch <- as.factor(ifelse(train$Groom_MB == train$Bride_MB, "Yes", "No"))  # Yes/No for exact MBTI match

# ageEduInteract: Interaction term between age difference and education match (numeric version of sameEdu). Tests if age gap effects depend on education similarity.
train$ageEduInteract <- train$AgeDiff * as.numeric(train$sameEdu)  # Multiplies AgeDiff by sameEdu (1 = No, 2 = Yes)

# MBTI similarity: Breaks down MBTI into components (E/I, N/S, T/F, J/P) and counts matches
train$Groom_EI <- substr(train$Groom_MB, 1, 1)  # Extraversion/Introversion for groom
train$Groom_NS <- substr(train$Groom_MB, 2, 2)  # Intuition/Sensing for groom
train$Groom_TF <- substr(train$Groom_MB, 3, 3)  # Thinking/Feeling for groom
train$Groom_JP <- substr(train$Groom_MB, 4, 4)  # Judging/Perceiving for groom
train$Bride_EI <- substr(train$Bride_MB, 1, 1)  # Same for bride
train$Bride_NS <- substr(train$Bride_MB, 2, 2)
train$Bride_TF <- substr(train$Bride_MB, 3, 3)
train$Bride_JP <- substr(train$Bride_MB, 4, 4)
train$EI_match <- ifelse(train$Groom_EI == train$Bride_EI, 1, 0)  # 1 if match, 0 if not
train$NS_match <- ifelse(train$Groom_NS == train$Bride_NS, 1, 0)
train$TF_match <- ifelse(train$Groom_TF == train$Bride_TF, 1, 0)
train$JP_match <- ifelse(train$Groom_JP == train$Bride_JP, 1, 0)
train$MBTI_similarity <- train$EI_match + train$NS_match + train$TF_match + train$JP_match  # Total number of MBTI component matches (0-4)

# AgeMBTIInteract: Interaction term between age difference and MBTI similarity. Tests combined effect on outcome.
train$AgeMBTIInteract <- train$AgeDiff * train$MBTI_similarity

# New Feature: AgeDiffSquared - Captures non-linear effects of age difference
train$AgeDiffSquared <- train$AgeDiff^2  # Squared term to model parabolic relationships

# New Feature: TotalAgeEduInteract - Interaction between total age and education difference
train$TotalAgeEduInteract <- train$totalAge * train$eduLevelDiff  # Combines maturity with educational disparity

# Define cross-validation control (5-fold CV)
cv_control <- trainControl(method = "cv", number = 5, classProbs = TRUE, summaryFunction = twoClassSummary)
# Sets up 5-fold cross-validation, optimizing for ROC (suitable for binary classification)

# Build and Cross-Validate Decision Tree Model with tuning
fit_tree_cv <- train(Outcome ~ Groom_MB + Bride_MB + Groom_Edu + Bride_Edu +
                       Groom_Age + Bride_Age + AgeDiff + sameEdu + age_rule +
                       totalAge + eduLevelDiff + mbMatch + ageEduInteract +
                       EI_match + NS_match + TF_match + JP_match + MBTI_similarity + 
                       AgeMBTIInteract + AgeDiffSquared + TotalAgeEduInteract,
                     data = train,
                     method = "rpart",  # Decision tree algorithm
                     trControl = cv_control,
                     tuneGrid = expand.grid(cp = seq(0.000001, 0.0001, by = 0.00001)), # Tunes complexity parameter for pruning
                     control = rpart.control(minsplit = 2, maxdepth = 30), # Allows fine splits and deep trees
                     metric = "ROC")  # Optimizes for area under ROC curve
print("Decision Tree Cross-Validation Results:")
print(fit_tree_cv)  # Displays CV results, including best cp value
fit_tree <- fit_tree_cv$finalModel  # Extracts the final tuned decision tree
rpart.plot(fit_tree, extra = 104, fallen.leaves = TRUE)  # Plots the tree with class labels and probabilities

# Training accuracy for Decision Tree
train_pred_tree <- predict(fit_tree_cv, train)  # Predicts on training data using tuned model
tree_accuracy <- mean(train_pred_tree == train$Outcome)  # Computes proportion of correct predictions
print(paste("Decision Tree Training Accuracy:", round(tree_accuracy * 100, 2), "%"))

# Build and Cross-Validate Random Forest Model
fit_rf_cv <- train(Outcome ~ Groom_MB + Bride_MB + Groom_Edu + Bride_Edu +
                     Groom_Age + Bride_Age + AgeDiff + sameEdu + age_rule +
                     totalAge + eduLevelDiff + mbMatch + ageEduInteract +
                     EI_match + NS_match + TF_match + JP_match + MBTI_similarity + 
                     AgeMBTIInteract + AgeDiffSquared + TotalAgeEduInteract,
                   data = train,
                   method = "rf",  # Random forest algorithm
                   trControl = cv_control,
                   tuneLength = 5,  # Tests 5 mtry values (number of variables sampled at each split)
                   ntree = 500,  # Builds 500 trees
                   metric = "ROC")
print("Random Forest Cross-Validation Results:")
print(fit_rf_cv)  # Shows CV results and best mtry
fit_rf <- fit_rf_cv$finalModel  # Extracts the final random forest model

# Training accuracy for Random Forest
train_pred_rf <- predict(fit_rf_cv, train)  # Predicts on training data
rf_accuracy <- mean(train_pred_rf == train$Outcome)  # Computes training accuracy
print(paste("Random Forest Training Accuracy:", round(rf_accuracy * 100, 2), "%"))

# Feature importance
varImp(fit_rf_cv)  # Displays importance of each feature in the random forest model

# Load and preprocess the test dataset
test <- read.csv("/Users/alveeramunshi/Documents/GitHub/learningData/data101/predictionchallenge2/Prediction2025-2TestStud.csv")
# Loads test data for prediction

# Apply the same feature engineering as train
test$AgeDiff <- test$Groom_Age - test$Bride_Age  # Age difference for test
test$sameEdu <- as.factor(ifelse(test$Groom_Edu == test$Bride_Edu, "Yes", "No"))  # Education match
test$age_rule <- as.factor(ifelse(test$AgeDiff >= 7, "Success", 
                                  ifelse(test$AgeDiff <= -7, "Failure", "Neutral")))  # Age-based rule
test$totalAge <- test$Groom_Age + test$Bride_Age  # Total age
test$eduLevelDiff <- as.numeric(test$Groom_Edu) - as.numeric(test$Bride_Edu)  # Education level difference
test$mbMatch <- as.factor(ifelse(test$Groom_MB == test$Bride_MB, "Yes", "No"))  # MBTI match
test$ageEduInteract <- test$AgeDiff * as.numeric(test$sameEdu)  # Age-education interaction

# MBTI similarity for test
test$Groom_EI <- substr(test$Groom_MB, 1, 1)
test$Groom_NS <- substr(test$Groom_MB, 2, 2)
test$Groom_TF <- substr(test$Groom_MB, 3, 3)
test$Groom_JP <- substr(test$Groom_MB, 4, 4)
test$Bride_EI <- substr(test$Bride_MB, 1, 1)
test$Bride_NS <- substr(test$Bride_MB, 2, 2)
test$Bride_TF <- substr(test$Bride_MB, 3, 3)
test$Bride_JP <- substr(test$Bride_MB, 4, 4)
test$EI_match <- ifelse(test$Groom_EI == test$Bride_EI, 1, 0)
test$NS_match <- ifelse(test$Groom_NS == test$Bride_NS, 1, 0)
test$TF_match <- ifelse(test$Groom_TF == test$Bride_TF, 1, 0)
test$JP_match <- ifelse(test$Groom_JP == test$Bride_JP, 1, 0)
test$MBTI_similarity <- test$EI_match + test$NS_match + test$TF_match + test$JP_match

# New interaction term for test
test$AgeMBTIInteract <- test$AgeDiff * test$MBTI_similarity

# New features for test
test$AgeDiffSquared <- test$AgeDiff^2  # Squared age difference
test$TotalAgeEduInteract <- test$totalAge * test$eduLevelDiff  # Total age and education interaction

# Convert categorical variables to factors in test
test$Groom_MB  <- as.factor(test$Groom_MB)
test$Bride_MB  <- as.factor(test$Bride_MB)
test$Groom_Edu <- as.factor(test$Groom_Edu)
test$Bride_Edu <- as.factor(test$Bride_Edu)

# Load submission csv
submission <- read.csv("/Users/alveeramunshi/Documents/GitHub/learningData/data101/predictionchallenge2/Prediction2025-2submission.csv")
# Loads pre-existing submission file with ID and Outcome columns

# Predict on test dataset using Random Forest, assigning to submission$Outcome
submission$Outcome <- predict(fit_rf, data = test, type = "class")
# Uses the random forest model to predict Outcomes for test data; assigns to submission file

# Save Submission File
write.csv(submission, "/Users/alveeramunshi/Documents/GitHub/learningData/data101/predictionchallenge2/Prediction2025-2submission.csv", row.names = FALSE)
print("Submission file created successfully.")
# Writes the updated submission file with predictions