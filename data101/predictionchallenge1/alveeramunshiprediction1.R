# Load the training, test, and submission datasets
train <- read.csv("/Users/alveeramunshi/Documents/GitHub/learningData/data101/predictionchallenge1/Prediction20251Train.csv")
submission <- read.csv("/Users/alveeramunshi/Documents/GitHub/learningData/data101/predictionchallenge1/submission2025-1.csv")
test <- read.csv("/Users/alveeramunshi/Documents/GitHub/learningData/data101/predictionchallenge1/Prediction20251TestStudents.csv")

# box splot dist across grades
boxplot(train$Score ~ train$Grade, 
        main="Boxplot of Scores by Grade", 
        xlab="Grade", 
        ylab="Score", 
        col="lightblue", 
        border="black")

boxplot(train$Participation ~ train$Grade, 
        main="Boxplot of Scores by Grade", 
        xlab="Grade", 
        ylab="Score", 
        col="lightblue", 
        border="black")

# Senior data
seniors_data <- subset(train, Seniority == "Senior")
boxplot(Score ~ Grade, data = seniors_data,
        main="Boxplot of Scores for Seniors",
        xlab="Grade",
        ylab="Score",
        col="lightblue",
        border="black")

boxplot(Participation ~ Grade, data = seniors_data,
        main="Boxplot of Participation for Seniors",
        xlab="Participation",
        ylab="Score",
        col="lightblue",
        border="black")

# Assign default grade "F" to all students
decision <- rep("F", nrow(train))

# Assign grades based on score thresholds
decision[train$Score > 60] <- "C"  # Score > 62 is assigned "C"
decision[train$Score > 75] <- "B"  # Score > 82 is assigned "B"
decision[train$Score > 92] <- "A"  # Score > 92 is assigned "A"

# Assign default grade "F" to all students
decision <- rep("F", nrow(train))

# Assign grades based on score thresholds
decision[train$Score > 60] <- "C"  
decision[train$Score > 75] <- "B"  
decision[train$Score > 92] <- "A"

# Assign higher grades with good participation
decision[train$Score > 82 & train$Participation > 0.50] <- "B"
decision[train$Score > 88 & train$Participation > 0.50] <- "A"

# Lower participation bar for Business Majors
decision[train$Major == "Business" & train$Participation > 0.20 & train$Score > 90] <- "A"
decision[train$Major == "Business" & train$Participation > 0.50 & train$Score > 75 & train$Score < 90] <- "B"

# Participation < 0.20 receive grades of "F".
decision[train$Participation < 0.20] <- "F"

# Low scores and low participation are also F for non business
decision[train$Score < 75 & train$Participation < 0.25 & train$Major != "Business"] <- "F"

# If students are in A and B ranges and their participation is between 0.20 and 0.50, bump the grade down to a C.
decision[train$Score >= 70 & train$Participation < 0.50 & train$Participation >= 0.20] <- "C"

# Bump up seniors
decision[train$Seniority == "Senior" & train$Score > 0.75 & train$Score < 0.89] <- "B"

# Final grade assignments
train$Predicted_Grade <- decision

# Predict grades on test dataset using the same logic
test_decision <- rep("F", nrow(test))
test_decision[test$Score > 60] <- "C"  
test_decision[test$Score > 75] <- "B"  
test_decision[test$Score > 92] <- "A"
test_decision[test$Score > 82 & test$Participation > 0.50] <- "B"
test_decision[test$Score > 88 & test$Participation > 0.50] <- "A"
test_decision[test$Major == "Business" & test$Participation > 0.20 & test$Score > 90] <- "A"
test_decision[test$Major == "Business" & test$Participation > 0.50 & test$Score > 75 & test$Score < 90] <- "B"
test_decision[test$Participation < 0.20] <- "F"
test_decision[test$Score < 75 & test$Participation < 0.25 & test$Major != "Business"] <- "F"
test_decision[test$Score >= 70 & test$Participation < 0.50 & test$Participation >= 0.20] <- "C"
test_decision[test$Seniority == "Senior" & test$Score > 0.75 & test$Score < 0.90] <- "B"

# Add predictions to the test
test$Predicted_Grade <- test_decision

# Identify instances where the model's decision does not match the actual grade
misclassified <- subset(train, decision != train$Grade)
print("Misclassified instances:")
print(misclassified)

# Calculate and print the accuracy of the model on training data
accuracy <- mean(decision == train$Grade)
print(paste("Revised Training Accuracy:", accuracy))

# Submission
submission$Grade <- test_decision
write.csv(submission, "/Users/alveeramunshi/Documents/GitHub/learningData/data101/predictionchallenge1/submission2025-1.csv", row.names = FALSE)


