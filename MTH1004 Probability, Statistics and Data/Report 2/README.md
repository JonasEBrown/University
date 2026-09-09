Atlantic Hurricane and ENSO Analysis (1870-2024)
================================================

My Role
-------

I developed statistical models to analyse hurricane frequency patterns and their relationship with ENSO (El Niño-Southern Oscillation) index, including predictive modeling for future hurricane activity.

### Key Contributions:

- **Developed the Statistical Modelling Framework**<br>
  - Created a comprehensive R analysis to compare Poisson and Negative Binomial distributions for modeling hurricane counts. Including parameter estimation, goodness-of-fit evaluation, and visualisation components.
<br><br>
- **Implemented ENSO Impact Analysis**<br>
Developed methods to stratify and compare hurricane frequencies between positive and negative ENSO conditions, including:
  - Confidence interval estimation for each ENSO phase.
  - Incidence Rate Ratio calculation.
  - Statistical significance testing (Z-test implementation).
<br><br>
- **Prediction System Development**<br>
Built a probabilistic forecasting system that:
  - Generates prediction intervals for future hurricane counts.
  - Calculates probability of extreme events (≥3 hurricanes).
  - Incorporates expert climate probabilities (25% positive ENSO).
<br><br>
- **Numerical Stability and Validation**<br>
Implemented robust parameter estimation using Method of Moments and verified results through:
  - Standard error calculations for all estimates.
  - Model comparison metrics (variance-to-mean ratio).
  - Visual goodness-of-fit assessments.
<br><br>
- **Data Visualisation**<br>
Created publication-quality visualisations including:
  - Observed vs. modelled hurricane frequency distributions.
<br><br>
<p align="center">
    <img src="./figures/Hurricane Counts - Observed vs Model Predictions.png" width=350px>
</p>

Key Findings
------------
- Negative Binomial model `(μ=1.79, r=7.73)` better fits hurricane data than Poisson.
- Negative ENSO years have `62%` higher hurricane rates `(IRR=1.62, p<0.001)`.
- 2025 prediction: `90%` prediction interval between 0 and 4 hurricanes, `P(≥3)=27.12%`.

Lecturer Feedback
-----------------

> "Suitable model choices and good assessment of fit. Comment on the iid assumption."

> "Point estimates and intervals for positive and negative indexes were correctly computed, but you should also compute these for the difference in means. You should also quote the general form of your interval."

> "Good calculations for % and prediction interval. Consider the proportion of years with different numbers of hurricanes when assessing whether results are reasonable."

> "Excellent presentation - would benefit from a more detailed conclusion e.g. talk about whether you thought the model captured the data relationship correctly."
