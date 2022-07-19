#install.packages("sessioninfo", repos = "http://cran.us.r-project.org")
#install.packages("here", repos = "http://cran.us.r-project.org")
#install.packages("dplyr", repos = "http://cran.us.r-project.org")
#install.packages("rjson", repos = "http://cran.us.r-project.org")
library(knitr)
library(sessioninfo)
library(here)
library(dplyr)
library("rjson")
sessioninfo::session_info()

data=read.csv("data.csv", sep = ",")

sample=select(data, papertitle, figure, why_excluded)
kable(sample)

summary(na.omit(data$why_excluded))

summary(na.omit(data$rmd_codelines))

sd(na.omit(data$rmd_codelines))

summary(na.omit(data$runall1))

sd(na.omit(data$runall1))

summary(na.omit(data$runall2))

sd(na.omit(data$runall2))

summary(na.omit(data$data))

summary(na.omit(data$format))

summary(na.omit(data$codelines))

sd(na.omit(data$codelines))

summary(na.omit(data$runfigure1))

sd(na.omit(data$runfigure1))

nrow(data[which(data$runfigure1<6),])

nrow(data[which(data$runfigure1>60),])

summary(na.omit(data$runfigure2))

sd(na.omit(data$runfigure2))

summary(na.omit(data$required_changes))

codelines <- fromJSON(file = "codelines.json")
codeblocks=c()
for(i in 1:length(codelines)) {
  codeblocks[i]=length(codelines[[i]]$lines)
}
summary(codeblocks)

sd(codeblocks)

parameterData=read.csv("parameters.csv", sep = ",")
summary(na.omit(parameterData$identifiedParameterFrom))

summary(na.omit(parameterData$identifiedOptionsFrom))

summary(na.omit(data$why_excluded))

summary(na.omit(parameterData$uiWidget))

summary(na.omit(parameterData$parameterType))

summary(na.omit(data$data))

summary(na.omit(data$format))