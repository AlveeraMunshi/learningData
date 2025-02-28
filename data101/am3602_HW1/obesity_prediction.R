# read csv
df <- read.csv("obesity_prediction.csv")

# fast food consumption vs. obesity levels
table(df$FAVC, df$Obesity)
# The data does not show a strong conclusive link between frequent high-calorie food consumption and obesity levels. While there is some association, it is not definitive enough to confirm causation.

# mean water intake per obesity level
tapply(df$CH2O, df$Obesity, mean)
boxplot(df$CH2O ~ df$Obesity, main="CH2O Levels vs. Obesity Levels", xlab="Obesity Level", ylab="CH2O Levels", cex.axis=0.5, col="lightblue")
# Contrary to expectations, obese individuals tend to drink more water on average compared to those with normal weight. This suggests that while hydration is important, it may not be a primary factor in obesity.

# physical activity
tapply(df$FAF, df$Obesity, summary)
mosaicplot(table(df$FAF, df$Obesity), main="Physical Activity vs. Obesity", xlab="Physical Activity Level", ylab="Obesity Level", cex.axis=0.5, col=rainbow(5))
# While the means of physical activity frequency across obesity levels are similar, the interquartile ranges (IQRs) vary significantly. A boxplot helps in visualizing the spread and identifying outliers in physical activity distribution across different obesity levels.

# obesity levels by mode of transportation
table(df$MTRANS, df$Obesity)
barplot(table(df$MTRANS, df$Obesity), beside=TRUE, col=rainbow(5), legend=rownames(table(df$MTRANS, df$Obesity)), main="Mode of Transportation vs. Obesity Levels", xlab="Mode of Transportation", ylab="Count")
# Most of the data is from automobile and public transport users, with very few individuals primarily using other forms of transport. This makes the conclusion misleading, as the sample sizes for walking and biking are too small to draw definitive insights.

# family history influence on obesity
table(df$family_history, df$Obesity)
mosaicplot(table(df$family_history, df$Obesity), main="Family History vs. Obesity Levels", xlab="Family History of Obesity", ylab="Obesity Level", las=2, color=TRUE)
# A strong correlation exists between family history and obesity, indicating a possible genetic predisposition combined with shared lifestyle habits.

# sleep category vs. obesity levels
table(df$SCC, df$Obesity)
# The data suggests no strong trend between calorie monitoring and obesity levels. Some obese individuals monitor calories while others do not, making it difficult to draw definitive conclusions.

# obesity levels by vegetable consumption
tapply(df$FCVC, df$Obesity, summary)
boxplot(df$FCVC ~ df$Obesity, main="Vegetable Consumption vs. Obesity Levels", xlab="Obesity Level", ylab="Vegetable Consumption", cex.axis=0.5, col="lightblue")
# While the mean vegetable consumption among different obesity levels is similar, the interquartile ranges (IQRs) vary. To better understand this, a boxplot can be used to visualize the spread of vegetable intake across obesity levels.

# Analyze number of main meals vs. obesity levels
tapply(df$NCP, df$Obesity, summary)
boxplot(df$NCP ~ df$Obesity, main="Number of Main Meals vs. Obesity Levels", xlab="Obesity Level", ylab="Number of Main Meals", col="lightgreen", cex.axis=0.7)
# similar mean but very diff IQR, more meals for lower weight and more meals for higher.

