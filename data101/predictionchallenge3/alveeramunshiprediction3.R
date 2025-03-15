# Load required libraries
library(dplyr)
library(randomForest)
library(caret)
library(e1071)

# Read data
location <- read.csv("/Users/alveeramunshi/Documents/GitHub/learningData/data101/predictionchallenge3/Location.csv")
training <- read.csv("/Users/alveeramunshi/Documents/GitHub/learningData/data101/predictionchallenge3/Prediction3Train.csv")
testing <- read.csv("/Users/alveeramunshi/Documents/GitHub/learningData/data101/predictionchallenge3/Prediction3Students.csv")

# Feature engineering function
engineer_features <- function(df, location_df) {
  df <- merge(df, location_df, by = "University", all.x = TRUE)
  df$Major_Encoded <- as.numeric(as.factor(df$Major))
  df$State_Encoded <- as.numeric(as.factor(df$State))
  df$University_Encoded <- as.numeric(as.factor(df$University))
  df$GPA_Major <- as.numeric(df$GPA) * df$Major_Encoded
  df$GPA_State <- as.numeric(df$GPA) * df$State_Encoded
  df$High_GPA <- ifelse(df$GPA >= 3.0, 1, 0)
  df$GPA_Squared <- df$GPA^2
  df$GPA_Bin <- as.numeric(cut(df$GPA, breaks = c(0, 2.0, 2.5, 3.0, 3.5, 4.0), 
                               labels = c(1, 2, 3, 4, 5), include.lowest = TRUE))
  df$Uni_State <- as.numeric(as.factor(paste(df$University, df$State, sep="_")))
  
  if ("Hired" %in% names(df)) {
    major_gpa <- df %>% group_by(Major) %>% summarise(Major_Avg_GPA = mean(GPA, na.rm = TRUE))
    state_gpa <- df %>% group_by(State) %>% summarise(State_Avg_GPA = mean(GPA, na.rm = TRUE))
    df <- merge(df, major_gpa, by = "Major", all.x = TRUE)
    df <- merge(df, state_gpa, by = "State", all.x = TRUE)
  }
  
  if (!"Hired" %in% names(df)) {
    train_major_gpa <- training %>% engineer_features(location) %>% 
      group_by(Major) %>% summarise(Major_Avg_GPA = mean(GPA, na.rm = TRUE))
    train_state_gpa <- training %>% engineer_features(location) %>% 
      group_by(State) %>% summarise(State_Avg_GPA = mean(GPA, na.rm = TRUE))
    df <- merge(df, train_major_gpa, by = "Major", all.x = TRUE)
    df <- merge(df, train_state_gpa, by = "State", all.x = TRUE)
    df$Major_Avg_GPA[is.na(df$Major_Avg_GPA)] <- mean(training$GPA, na.rm = TRUE)
    df$State_Avg_GPA[is.na(df$State_Avg_GPA)] <- mean(training$GPA, na.rm = TRUE)
  }
  
  df$GPA_vs_Major <- df$GPA - df$Major_Avg_GPA
  
  return(df)
}

# Prepare training data
train_data <- engineer_features(training, location)

# Prepare features and target
features <- c("GPA", "Major_Encoded", "State_Encoded", "University_Encoded", 
              "GPA_Major", "GPA_State", "High_GPA", "GPA_Squared", "GPA_Bin",
              "Uni_State", "Major_Avg_GPA", "State_Avg_GPA", "GPA_vs_Major")
X <- train_data[, features]
y <- as.factor(train_data$Hired)

# Create train/validation split
set.seed(42)
trainIndex <- createDataPartition(y, p = .8, list = FALSE)
X_train <- X[trainIndex, ]
X_val <- X[-trainIndex, ]
y_train <- y[trainIndex]
y_val <- y[-trainIndex]

# Hyperparameter tuning with cross-validation
rf_control <- trainControl(method = "cv", number = 5, search = "grid")
rf_grid <- expand.grid(mtry = c(2, 4, 6, 8))

rf_model <- train(
  x = X_train,
  y = y_train,
  method = "rf",
  trControl = rf_control,
  tuneGrid = rf_grid,
  ntree = 200,
  maxdepth = 15,
  nodesize = 3
)

# Train SVM for stacking
svm_model <- svm(x = X_train, y = y_train, probability = TRUE)

# Get predictions for stacking
rf_train_pred <- predict(rf_model, X_train)
rf_val_pred <- predict(rf_model, X_val)
svm_train_pred <- predict(svm_model, X_train)
svm_val_pred <- predict(svm_model, X_val)

# Create stacking dataset (ensure factors match y levels)
stack_train <- data.frame(RF_Pred = rf_train_pred, SVM_Pred = svm_train_pred)
stack_val <- data.frame(RF_Pred = rf_val_pred, SVM_Pred = svm_val_pred)

# Train meta-model
meta_model <- glm(y_train ~ ., data = stack_train, family = "binomial")

# Calculate training accuracy
train_meta_pred <- predict(meta_model, stack_train, type = "response")
train_meta_pred_class <- ifelse(train_meta_pred > 0.5, 1, 0)  # Directly to 0/1
train_confusion <- table(train_meta_pred_class, as.numeric(y_train) - 1)
train_accuracy <- sum(diag(train_confusion)) / sum(train_confusion)
cat(sprintf("Training Accuracy: %.4f\n", train_accuracy))

# Calculate validation accuracy
val_meta_pred <- predict(meta_model, stack_val, type = "response")
val_meta_pred_class <- ifelse(val_meta_pred > 0.5, 1, 0)  # Directly to 0/1
val_confusion <- table(val_meta_pred_class, as.numeric(y_val) - 1)
val_accuracy <- sum(diag(val_confusion)) / sum(val_confusion)
cat(sprintf("Validation Accuracy: %.4f\n", val_accuracy))

# Feature importance from RF
print("\nFeature Importance from Random Forest:")
varImp(rf_model)

# Prepare test data
test_data <- engineer_features(testing, location)
X_test <- test_data[, features]

# Get test predictions for stacking
rf_test_pred <- predict(rf_model, X_test)
svm_test_pred <- predict(svm_model, X_test)
stack_test <- data.frame(RF_Pred = rf_test_pred, SVM_Pred = svm_test_pred)

# Final predictions
test_meta_pred <- predict(meta_model, stack_test, type = "response")
test_preds <- ifelse(test_meta_pred > 0.5, 1, 0)  # Directly to 0/1

# Create submission file
submission <- data.frame(
  ID = test_data$ID,
  Hired = test_preds  # No need to subtract 1 anymore
)

# Write submission file
write.csv(submission, "/Users/alveeramunshi/Documents/GitHub/learningData/data101/predictionchallenge3/submission.csv", 
          row.names = FALSE)
cat("\nSubmission file created successfully!\n")

# Display first few predictions
cat("\nFirst 5 predictions:\n")
print(head(submission, 5))