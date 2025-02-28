# get and set path
getwd() 
setwd("/Users/alveeramunshi/Documents/GitHub/learningData")

# read and save csv
moody <- read.csv("moody2022.csv")

# first 6 lines
head(moody)

# Return row 1
moody[1, ]

# Return column 5
moody[, 5]

# Rows 1:5 and column 2
moody[1:5, 2]

# Give me rows 1-3 and columns 2 and 4 of moody
moody[1:3, c(2:4)]

# Give me rows 1-3 and columns 2 and 4 of moody (wrong)
moody[1:3, 2:4]

#lets make a table for the grades of students and counts of students for each Grade. 
grades <- table(moody$Grade)

#Joint distribution of grade and major
table(moody$Grade, moody$Major)

#Lets look at the mean of score column.
mean(moody$Score)

#Lets look at the length of the grade column 
length(moody$Grade)

#lets look at the maximum value of the score in the score column
max(moody$Score)

#Lets look at the minimum value of score in the score column.
min(moody$Score)

# examples of vectors
id <- c(10,11,12,13)
name <- c('sai','ram','deepika','sahithi')
dob <- as.Date(c('1990-10-02','1981-3-24','1987-6-14','1985-8-16'))

# Types of Vectors
typeof(id)
#[1] "double"

typeof(name)
#[1] "character"

typeof(dob)
#[1] "double"

# Create Named Vector
x <- c(C1='A',C2='B',C3='C')

# Create Vector using vector()
x <- vector(mode='logical',length=5)

# Create Character Vector
x <- character(5)

# Create Vector From List
li <- list('A','B','C')
v <- unlist(li)

# Create Vector of Zeros
v <- integer(6)

# Create Vector of Specified length
v <- character(5)

# Create Numeric Vector with 0 to 10 Values
v <- seq(1, 10)
v <- 1:10

# Create Vector using vector()
x <- vector(mode='logical',length=5)