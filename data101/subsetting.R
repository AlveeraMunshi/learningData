# set path
setwd("/Users/alveeramunshi/Documents/GitHub/learningData")

# Create DataFrame
df <- data.frame(
  id = c(10,11,12,13,14,15,16,17),
  name = c('sai','ram','deepika','sahithi','kumar','scott','Don','Lin'),
  gender = c('M','M',NA,'F','M','M','M','F'),
  dob = as.Date(c('1990-10-02','1981-3-24','1987-6-14','1985-8-16',
                  '1995-03-02','1991-6-21','1986-3-24','1990-8-26')),
  state = c('CA','NY',NA,NA,'DC','DW','AZ','PH'),
  row.names=c('r1','r2','r3','r4','r5','r6','r7','r8')
)
df

# subset of one row
subset(df, rownames(df) == 'r1')

# subset of multiple rows
subset(df, rownames(df) %in% c('r1','r2','r3'))

# subset by one condition
subset(df, gender=='M')

# subset by multiple conditions using vector
subset(df, state %in% c('CA','DC'))

# subset by multiple conditions using OR
subset(df, gender=='M' | state == 'PH')

# subset by multiple conditions using AND
subset(df, gender=='M' & state %in% c('CA','NY'))

# subset columns after filter conditions
subset(df,gender=='M',select='id')

# subset multiple columns by name after filter conditions
subset(df,gender=='M',select=c('id','name','gender'))

#subset multiple columns by index
subset(df,gender=='M',select=c(1,2,3))

moody<-read.csv("https://raw.githubusercontent.com/dev7796/data101_tutorial/main/files/dataset/moody2022.csv")
#Subset of rows
moody_psychology<-subset(moody, Major== 'Psychology')
nrow(moody) # number of rows in og
nrow(moody_psychology) # number of rows in subset

#Alternate way to subset.
moody[moody$Major=="Psychology", ]
moody[moody$Major!="Psychology", ]
moody[moody$Score >80, ]
moody[moody$Score >80 & moody$Grade == 'B', ]

colnames(moody)
#subset of columns
moody3<-subset(moody, select = -c(1))
ncol(moody3)
# You can see the number of columns has been reduced by 1, due to sub-setting without column 1
ncol(moody3)