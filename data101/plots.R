moody<-read.csv("https://raw.githubusercontent.com/dev7796/data101_tutorial/main/files/dataset/moody2020b.csv") #web load
plot(moody$participation,moody$score,ylab="score",xlab="participation",main=" Participation vs Score",col="red")

colors<- c('red','blue','cyan','yellow','green') # Assigning different colors to bars

#lets make a table for the grades of students and counts of students for each Grade. 

t<-table(moody$Grade)

#once we have the table lets create a barplot for it.

barplot(t,xlab="Grade",ylab="Number of Students",col=colors, 
        main="Barplot for student grade distribution",border="black")

#Suppose you want to find the distribution of students score per Grade. We use box plot for getting that. 
boxplot(Score~Grade,data=moody,xlab="Grade",ylab="Score", main="Boxplot of grade vs score",col=colors,border="black")

# the circles represent outliers.

#suppose you want to find numbers of students with a particular grade based on their texting habits. Use Mosiac-plot.

mosaicplot(moody$grade~moody$texting,xlab = 'Grade',ylab = 'Texting habit', main = "Mosiac of grade vs texing habit in class",col=colors,border="black")