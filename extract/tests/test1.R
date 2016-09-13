# test1 r-script for metaextract demo
#####################################

library("RColorBrewer")
library('dplyr')
library(ggplot2)
library('definitivelyUnknownPackage')
library('minqa')
library('PBSmapping')

#Trying some seperation lines:
# ###################################
#************************
# ~~~~~~~~~~~~~~~~~~~~~~~~ ~~~~~~~~~~~~ ~~~~~~~~~~
# ---------------------------------
#+++++++++++++++++++++++++++++++

# chunk: random string
set.seed(42)
random <- lapply(1:100, function(x) sample(1:12,size=10))
anotherstr <- paste(sample(LETTERS, 16), collapse = "")
anotherstr
# umlaut ö ä ü ß
l <- nchar(anotherstr)
l

# some plot
p <- ggplot(morley, aes(Expt)) + geom_density(adjust = 1/5)
p
print('done')