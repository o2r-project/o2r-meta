# test1 r-script for metaextract demo
#####################################

library("RColorBrewer")
library('dplyr')
library(ggplot2)
library('definitivelyUnknownPackage')
library('minqa')
library('PBSmapping')


# chunk: random string
set.seed(42)
anotherstr <- paste(sample(LETTERS, 16), collapse = "")
anotherstr
l <- nchar(anotherstr)
l

# some plot
p <- ggplot(morley, aes(Expt)) + geom_density(adjust = 1/5)
p
print('done')