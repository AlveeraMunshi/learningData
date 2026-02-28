x <- 10
y <- "Hello"
height <- c(168,177,177,165,178)
height[2]
height[1:3]
id <- 1:5
weight <- c(88,72,85,52,71)
bmi <- weight/(height/100)^2
length(height)
m <- cbind(id, height, weight)
dim(m)

df <- data.frame(m)
names(df)
head(df,3)
summary(df)
df$height
df$bmi <- df$weight/(df$height/100)^2
df$group <- ifelse(df$height < 175, "Short", "Tall")
df[3,3]
df[3,"weight"]
df_cond <- df[df$height >= 170 & df$weight >= 70,]
df_height <- df[,c('id', 'height')]
df_sub <- df[df$height >= 170 & df$weight >= 70,c('id', 'height')]

library(tidyverse)
tib <- as_tibble(m)
tib <- tib %>% 
  mutate(bmi = weight/(height/100)^2,
         group = ifelse(height < 175, "Short", "Tall")) %>% 
  filter(height >= 170 & weight >= 70) %>% 
  select(id, height)
# File path constants
CA_SCHOOLS_CSV <- "CASchools.csv"

df <- read.csv(CA_SCHOOLS_CSV)
ggplot(data = df, aes(x = df$income, y = df$math)) +
  geom_point(color = "blue", alpha = 0.25) + 
  xlab("Income") + 
  ylab("Math Score") + 
  theme_classic()

mean(df$math)
var(df$math)
sd(df$math)
cov(df$math, df$income)
cor(df$math, df$income)

t_stat <- (mean(df$math)-651)/(sd(df$math)/sqrt(length(df$math)))

qnorm(p=0.5, mean=0, sd=1)
qnorm(p=0.975, mean=0, sd=1)
pnorm(q=1.96, mean=0, sd=1)

t.test(df$math, mu=651, alternative = "two.sided", conf.level=0.95)