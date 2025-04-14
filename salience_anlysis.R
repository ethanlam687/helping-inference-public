library(tidyverse)

exp1_data <- read_csv("~/Downloads/final_first_moves.csv")
exp2_data <- read_csv("~/Downloads/first_moves (1).csv")

# convert flat grid index to (row, col)
row_col <- function(index) {
  row <- index %/% 18   
  col <- index %% 18
  return(c(row, col))
}

# grid center defined at 44
center_coords <- row_col(44)

# compute stepwise and euclidean salience
compute_saliences <- function(move_string) {
  start_index <- as.integer(str_split(str_remove_all(move_string, "[()]"), ",")[[1]][1])
  start_coords <- row_col(start_index)
  
  stepwise <- abs(start_coords[1] - center_coords[1]) + abs(start_coords[2] - center_coords[2])
  euclidean <- sqrt((start_coords[1] - center_coords[1])^2 + (start_coords[2] - center_coords[2])^2)
  
  return(list(stepwise = stepwise, euclidean = euclidean))
}


exp1_data <- exp1_data %>%
  mutate(
    salience_values = map(first_move, compute_saliences),
    stepwise_salience = map_dbl(salience_values, "stepwise"),
    euclidean_salience = map_dbl(salience_values, "euclidean"),
    experiment = "exp1"
  ) %>%
  select(-salience_values) 


exp2_data <- exp2_data %>%
  mutate(
    salience_values = map(first_move, compute_saliences),
    stepwise_salience = map_dbl(salience_values, "stepwise"),
    euclidean_salience = map_dbl(salience_values, "euclidean"),
    experiment = "exp2"
  ) %>%
  select(-salience_values)

combined <- bind_rows(exp1_data, exp2_data)

# Summary statistics
combined %>%
  group_by(experiment) %>%
  summarise(
    mean_stepwise = mean(stepwise_salience),
    mean_euclidean = mean(euclidean_salience),
    sd_stepwise = sd(stepwise_salience),
    sd_euclidean = sd(euclidean_salience),
    n = n()
  )

# stepwise salience comparison
ggplot(combined, aes(x = experiment, y = stepwise_salience, fill = experiment)) +
  geom_boxplot(alpha = 0.7) +
  labs(
    title = "Stepwise Salience by Experiment",
    y = "Stepwise Distance from Center"
  ) +
  theme_minimal()

# euclidean salience comparison
ggplot(combined, aes(x = experiment, y = euclidean_salience, fill = experiment)) +
  geom_boxplot(alpha = 0.7) +
  labs(
    title = "Euclidean Salience by Experiment",
    y = "Euclidean Distance from Center"
  ) +
  theme_minimal()


t.test(stepwise_salience ~ experiment, data = combined)
t.test(euclidean_salience ~ experiment, data = combined)

# COMPARISON TO RANDOMLY SAMPLED SALIENCE

# generate N random saliences
sample_random_salience <- function(n = 1000) {
  random_indices <- sample(0:107, n, replace = TRUE)  
  saliences <- map(random_indices, ~{
    coords <- row_col(.x)
    stepwise <- abs(coords[1] - center_coords[1]) + abs(coords[2] - center_coords[2])
    euclidean <- sqrt((coords[1] - center_coords[1])^2 + (coords[2] - center_coords[2])^2)
    c(stepwise = stepwise, euclidean = euclidean)
  })
  
  df <- bind_rows(saliences)
  summarise(df,
            expected_stepwise = mean(stepwise),
            expected_euclidean = mean(euclidean))
}

# mutate df
combined <- combined %>%
  rowwise() %>%
  mutate(random_baseline = list(sample_random_salience(n = 1000))) %>%
  unnest_wider(random_baseline)

# difference from expected
combined <- combined %>%
  mutate(
    stepwise_diff = stepwise_salience - expected_stepwise,
    euclidean_diff = euclidean_salience - expected_euclidean
  )

# Plotting the differences
ggplot(combined, aes(x = experiment, y = stepwise_diff, fill = experiment)) +
  geom_boxplot(alpha = 0.7) +
  labs(
    title = "Stepwise Salience Difference from Expected",
    y = "Difference from Expected Stepwise Salience"
  ) +
  theme_minimal()
