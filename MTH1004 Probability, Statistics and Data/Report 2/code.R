# R code to calculate the estimates
load("MTH1004T2CW2024.RData")
mean_hurricanes <- mean(Hurricanes$Number)
se_hurricanes <- sqrt(mean_hurricanes/nrow(Hurricanes))
variance_hurricanes <- var(Hurricanes$Number)


# Positive ENSO years
pos <- Hurricanes[Hurricanes$ENSO > 0,]
mean_pos <- mean(pos$Number)
ci_pos <- mean_pos + c(-1,1)*1.96*sqrt(mean_pos/nrow(pos))

# Negative ENSO years
neg <- Hurricanes[Hurricanes$ENSO < -0.00001,] # I had to use this number instead of 0, I was getting weird overlap.
mean_neg <- mean(neg$Number)
ci_neg <- mean_neg + c(-1,1)*1.96*sqrt(mean_neg/nrow(neg))

# Prediction Intervals

mu <- 1.79; theta <- 7.73
p_0 <- dnbinom(0, size = theta, mu = mu)  # ≈0.1999
p_1 <- dnbinom(1, size = theta, mu = mu)  # ≈0.2905
p_2 <- dnbinom(2, size = theta, mu = mu)  # ≈0.2384
P_geq3 <- 1 - (p_0 + p_1 + p_2)          # ≈0.2712

# Part 3b.

mu_pos <- 1.29; theta <- 7.73
p0_pos <- dnbinom(0, size = theta, mu = mu_pos)  # ≈0.3033
p1_pos <- dnbinom(1, size = theta, mu = mu_pos)  # ≈0.3353
p2_pos <- dnbinom(2, size = theta, mu = mu_pos)  # ≈0.2093
P_geq3_pos <- 1 - (p0_pos + p1_pos + p2_pos)    # ≈0.1521

mu_neg <- 2.09
p0_neg <- dnbinom(0, size = theta, mu = mu_neg)  # ≈0.1573
p1_neg <- dnbinom(1, size = theta, mu = mu_neg)  # ≈0.2587
p2_neg <- dnbinom(2, size = theta, mu = mu_neg)  # ≈0.2403
P_geq3_neg <- 1 - (p0_neg + p1_neg + p2_neg)    # ≈0.3437

# ENSO being positive is 0.25

P_ENSO_pos <- 0.25
P_3_or_more <- (P_geq3_pos*P_ENSO_pos)+(P_geq3_neg*(1-P_ENSO_pos))

########### PLOTS ########### 

# Observed vs. Fitted Counts #

# Prepare data
plot_data <- data.frame(
  Counts = 0:7,
  Observed = as.numeric(table(factor(Hurricanes$Number, levels = 0:7))),
  Poisson = dpois(0:7, lambda = 1.79) * nrow(Hurricanes),
  NegativeBinomial = dnbinom(0:7, size = 7.73, mu = 1.79) * nrow(Hurricanes)
)

# Plot
ggplot(plot_data, aes(x = Counts)) +
  geom_bar(aes(y = Observed, fill = "Observed Data"), 
           stat = "identity", alpha = 0.7, width = 0.6) +
  geom_line(aes(y = Poisson, color = "Poisson Model"), 
            linewidth = 1.2, linetype = "dashed", group = 1) +
  geom_point(aes(y = Poisson, color = "Poisson Model"), size = 3) +
  geom_line(aes(y = NegativeBinomial, color = "NB Model"), 
            linewidth = 1.2, group = 1) +
  geom_point(aes(y = NegativeBinomial, color = "NB Model"), size = 3) +
  scale_fill_manual(name = "", values = c("Observed Data" = "gray70")) +
  scale_color_manual(name = "Model", 
                     values = c("Poisson Model" = "#E41A1C", "NB Model" = "#377EB8")) +
  labs(
    title = "Hurricane Counts: Observed vs. Model Predictions",
    subtitle = "Negative Binomial better captures overdispersion than Poisson.",
    x = "Number of Hurricanes per Year", 
    y = "Frequency (Number of Years)",
    caption = "Data: 1870–2024 | Poisson (λ=1.79) vs. NB (μ=1.79, θ=7.73)"
  ) +
  theme_minimal(base_size = 14) +
  theme(
    legend.position = "top",
    plot.title = element_text(face = "bold"),
    plot.subtitle = element_text(color = "gray40")
  ) +
  annotate("text", x = 5, y = 25, 
           label = "NB fits extremes (≥4) better", color = "#377EB8", size = 5)