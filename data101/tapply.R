moody<-read.csv("https://raw.githubusercontent.com/dev7796/data101_tutorial/main/files/dataset/moody2022.csv")

print(moody)

#Tapply is used to apply a function (e.g., mean, min, max) to subsets of a vector, grouped by a factor or combination of factors.

# Calculate the mean score for each Grade
tapply_result <- tapply(moody$Score, moody$Grade, mean) # numerical data, grouped by category, function to be applied

# Print the result
print(tapply_result)

# Subset the data for Seniors
seniors <- subset(moody, Seniority == "Senior")

# Use tapply to find the maximum GPA for each Grade in the subset
tapply_result <- tapply(seniors$GPA, seniors$Grade, max)

# Print the result
print(tapply_result)

# Extra basic queries
colnames(moody)
summary(moody)
unique(moody$Seniority)
min(moody[moody$Grade=='A',]$Score)
max(moody[moody$Grade=='B',]$Score)

# tapply for categorization
tapply(moody[moody$Grade=='A',]$Score, moody[moody$Grade=='A',]$Major, min)

# cut function
moody$ScoreIntervals<-cut(moody$Score,breaks=c(0,60,80,90,100),labels=c("Low","Medium",'Good', "Excellent"))
table(moody$ScoreIntervals)

moody$ScoreIntervals<-cut(moody$Score,breaks=c(0,60,80,90,100),labels=c('Low','Medium','Good', 'Excellent'))
table(moody$ScoreIntervals, moody$Grade)