library(tidyverse)
library(plyr)

manydogs = read_delim("manydogs_data.csv", delim=",") # Read the csv in using read_delim.

# ============================================================================================================================================== #



                                                                    ## Part 1: Introduction ##



# ============================================================================================================================================== #

# 1. How many dogs are in the data set?

totalDogs = nrow(manydogs)
sprintf("There are %s dogs in the data set.", totalDogs)

# There are 455 dogs in the data set.

# ============================================================================================================================================== #

# 2. Describe the study and comment on how representative the dogs in the study may be
# among all dogs on the planet. Provide a reference for your answer. (No coding.)

# C-BARQ (Canine Behavioural Assessment and Research Questionnaire) developed by Yuying Hsu and James Serpell in 2003[1] got 
# 'guardians' recruited via existing databases and also social media outreaches to complete a survey answering basic environment and 
# demographic information alongside an assessment. This consisted of a "short series of object-choice warm-ups … followed by two 
# experimental pointing conditions" being "ostensive and non-ostensive".

# Looking at section "2.4 Sampling, sample and data collection", you can see that there is narrow age range (4.40 ± 3.1 years) and that a 
# large majority of the data (around 90.2%) are dogs living in private homes.[2] This means the data is skewed towards younger dogs, 
# which could prove bene cial for identi cation of issues in Working Dogs at early ages. However, a broader understanding of dog’s 
# behaviour could have been achieved by collecting data from more of a variety of ages and environments. 

# The study initially contained 704 dogs of which 235 were excluded (leaving 469) because “they did not complete the behavioural 
# testing”.[2] This is an extremely small sample size meaning a large amount of dogs outside the ranges of the average age, sex, and 
# environment will not be represented by the data. However, currently there are “approximately 50,000 pet dogs” in the C-BARQ 
# database comprising of “more than 300 species”.[1] This means that C-BARQ is now extremely accurate for a huge range of ages, sexes, 
# and environments.

# [1]: ManyDogs Project, Espinosa, J., Hare, E., Alberghina, D., Valverde, B.M.P., and Stevens,
# J.R. (2024). Data from the ManyDogs 1. Journal of Open Psychology Data, 12:7, pp. 1-26.
# DOI: https://doi.org/10.5334/jopd.109.

# [2]: C-BARQ, Serpell, J., University of Pennsylvania (2024) About the C-BARQ. Canine Behavioral Assessment & Research Questionnaire.
# DOI: https://vetapps.vet.upenn.edu/cbarq/about.cfm.

# ============================================================================================================================================== #

# 3. Describe the dogs in the study using suitable summary statistics based on the following
# columns: age, sex, and owned status. (Drop any relevant missing data, if applicable,
# but report how many observations were omitted.)

averageAge = mean(manydogs$age, na.rm=TRUE) # Find the mean of the age of all the dogs.
ageNACount = sum(is.na(manydogs$age)) # Count the number of removed entries.

ownedStatusTypes = unique(manydogs$owned_status) # Get the unique values of the types of environments. ("Private home", etc.)
averageOwnedStatus = ownedStatusTypes[ # Index the max number's index in the ownedStatusTypes table to get the environment it corresponds to.
  which.max( # Find the max number in the table and return the index.
    tabulate( # Compact all the data into a count of each number.
      match( # Essentially, match each value in ownedStatusTypes to a value in the data set, allocating a number 1-length(ownedStatusTypes) to each value.
        manydogs$owned_status, # Read what this all does from bottom to top ↑.
        ownedStatusTypes
      )
    )
  )
]

averageSex = c("Female", "Male")[ # Works the same as the above, but instead of "sexTypes" replace with just a collection of the two possibilities.
  which.max(
    tabulate(
      match(
        manydogs$environment,
        c("Female", "Male")
      )
    )
  )
]

sprintf("Average age: %.2f years old (%i entries removed).", averageAge, ageNACount)
sprintf("%s -> %s | Average sex: %s.", paste(count(manydogs$sex)$x, collapse=":"), paste(count(manydogs$sex)$freq, collapse=":"), averageSex)
sprintf("Average environment: %s.", averageOwnedStatus)

# ============================================================================================================================================== #



                                                                    ## Part 2: C-BARQ Scores ##



# ============================================================================================================================================== #

# 1. What do the letters in C-BARQ stand for? Who invented this measure and when?
# Provide a reference for your answer. (No coding.)

# C-BARQ: Canine Behavioral Assessment and Research Questionnaire.
# "developed by Yuying Hsu and James Serpell in 2003" [2]

# ============================================================================================================================================== #

# 2. Create a new column in the data set called cbarq which is the sum of the individual CBARQ scores: cbarq_train1, cbarq_train2, cbarq_train3, cbarq_train4, cbarq_train5,
# cbarq_train6, cbarq_train7, and cbarq_train8. What range of C-BARQ scores are
# possible? How should we interpret the C-BARQ score? For example, if dog A has a
# higher C-BARQ score than dog B, what does that mean?

manydogs = manydogs %>%
  mutate(
    cbarq=rowSums(
      manydogs[, c('cbarq_train1', 'cbarq_train2', 'cbarq_train3', 
                          'cbarq_train4', 'cbarq_train5', 'cbarq_train6', 
                          'cbarq_train7', 'cbarq_train8')
      ],
      #na.rm=TRUE
    )
  )
manydogs

# C-BARQ uses a scale (0-4) to measure the prominence of behavioral problems in dogs. The lower the number, the least displayed
# the problem is: 0 being none/never and 5 being extreme/always. This means that higher scores indicate a more misbehaved dog.

# ============================================================================================================================================== #

# 3. Using cbarq, how many dogs in the study, if any, are missing C-BARQ scores?

manydogs = manydogs %>%
  mutate(
    hasNA=rowSums(
      is.na(manydogs)[, c('cbarq_train1', 'cbarq_train2', 'cbarq_train3', 
                          'cbarq_train4', 'cbarq_train5', 'cbarq_train6', 
                          'cbarq_train7', 'cbarq_train8')
                      ]
    )
  )
totalNA = sum(manydogs$hasNA) # 147 dogs have missing data for at least one scale.
sprintf("Total dogs missing at least one test score: %s.", totalNA)

# ============================================================================================================================================== #

# 4. Create a box plot of cbarq and save your graph as a file using ggsave(). Comment on
# the shape of the distribution of C-BARQ scores including a discussion of the outliers, if
# applicable.

plot_theme = theme(
  plot.title = element_text(size=15, hjust=0.5),
  plot.subtitle = element_text(size=10, hjust=0.5),
  axis.title = element_text(size=12),
  axis.text = element_text(size=12),
  strip.text = element_text(size=12)
) # Quickly set up a variable for our styles.

manydogs %>%
  ggplot(mapping=aes(x=age, y=sex)) + # Map to age and sex.
  scale_x_continuous(breaks=seq(0, 22, 2)) + # Make the plot display numbers in 2's between 0 and 22.
  geom_boxplot() + # Display a boxplot.
  labs(
    x='Age',
    y='Sex',
    title='Age variance in the sex of dogs'
  ) + # Add labels to the axis and title.
  plot_theme
ggsave('box-plot.jpg') # Save to file.

# From the boxplots (le ), we can see that the ages of both sexes are distributed somewhat similarly and average is just under 4. This means that the results will 
# be much more accurate when determining the behaviour of dogs between the ages of 2 and 6 in either sex. 

# ============================================================================================================================================== #

# 5. Use suitable summary statistics to describe the distribution of cbarq, connecting your
# explanation with your box plot from question (4), the range of possible C-BARQ scores,
# and any other information you deem relevant. (Drop any relevant missing data, if
# applicable, but report how many observations were omitted.)

manydogs %>%
  ggplot(mapping=aes(x=cbarq)) + # Map to cbarq scores.
  facet_grid(rows=vars(sex)) + # Add to grid (for male and female).
  scale_x_continuous(breaks=seq(0,30, 2)) + # Make the plot display numbers in 2's between 0 and 32 (the max C-BARQ score for 8 tests).
  scale_y_continuous(breaks=seq(0, 40, 4)) + # Display age range in 4's.
  geom_histogram(bins=22) + # Display a histogram.
  labs(
    x='C-BARQ',
    y='Total of dogs',
    title='C-BARQ score variance between sexes'
  ) + # Add labels to the axes and title.
  plot_theme
ggsave('histogram.jpg') # Save to file.
  
#From the histograms (right), we can see that there is more variance in the C-BARQ score for female dogs (top) and that they received a higher score on 
# average, suggesting that the behaviour of female dogs is more desirable overall. 

# ============================================================================================================================================== #



                                                                ## Part 3: Exploring further ##



# ============================================================================================================================================== #

# 1. Is there any evidence that cbarq scores differ substantially by age and/or sex? Use a
# suitable data visualisation and sample correlation calculations to support your answer.
# (Drop any relevant missing data, if applicable, but report how many observations were
# omitted. Save your visualisation using ggsave().)

# Already done in P2.4 and P2.5

