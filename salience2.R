# analysis.R
library(tidyverse)
library(jsonlite)

# ———————————————————————————————————————————————————————————————————————
# 1) Load & clean the two first‐move datasets
#    (treat IDs and goals as characters so binds and joins will align)
exp1_data <- read_csv("data/e1/final_first_moves.csv",
                      col_types = cols(ID = col_character(),
                                       goal = col_character())) %>%
  mutate(experiment = "E1")

exp2_data <- read_csv("data/e2/first_moves.csv",
                      col_types = cols(importId = col_character(),
                                       goal     = col_character())) %>%
  rename(ID = importId) %>%
  mutate(experiment = "E2")

# ———————————————————————————————————————————————————————————————————————
# 2) Compute observed salience of first moves
row_col <- function(i, n=18) c(i %/% n, i %% n)
center_coords <- row_col(44)

compute_saliences <- function(move_string) {
  idx <- as.integer(str_remove_all(move_string, "[()]") %>% str_split(",", simplify=TRUE))[1]
  rc  <- row_col(idx)
  list(
    stepwise  = abs(rc[1]-center_coords[1]) + abs(rc[2]-center_coords[2]),
    euclidean = sqrt((rc[1]-center_coords[1])^2 + (rc[2]-center_coords[2])^2)
  )
}

# actually reassign:
exp1_data <- exp1_data %>%
  mutate(
    tmp = map(first_move, compute_saliences),
    stepwise_salience  = map_dbl(tmp, "stepwise"),
    euclidean_salience = map_dbl(tmp, "euclidean")
  ) %>% select(-tmp)

exp2_data <- exp2_data %>%
  mutate(
    tmp = map(first_move, compute_saliences),
    stepwise_salience  = map_dbl(tmp, "stepwise"),
    euclidean_salience = map_dbl(tmp, "euclidean")
  ) %>% select(-tmp)

# 3) Combine & do your usual t‑tests / plots
combined <- bind_rows(exp1_data, exp2_data)
print(combined %>% group_by(experiment) %>% 
        summarise(
          mean_step = mean(stepwise_salience),
          mean_euc  = mean(euclidean_salience)
        ))
# (…any further analysis on combined…)

# ———————————————————————————————————————————————————————————————————————
# 4) Now for EXP2 only: load the “legal moves” and sample baselines
move_df <- read_csv("data/e2/final_move_df.csv",
                    col_types = cols(importId = col_character(),
                                     goal     = col_character(),
                                     config   = col_character())) %>%
  select(-ID) %>%
  rename(ID = importId) %>%
  mutate(
    # parse the Python list-of-strings into an R character vector
    config_json = str_replace_all(config, "'", '"'),
    config_vec  = map(config_json, ~ fromJSON(.x)),
    origin_inds = map(config_vec, ~ which(.x != "white") - 1)
  ) %>%
  select(ID, goal, origin_inds)

# join onto exp2_data
exp2_data <- exp2_data %>%
  left_join(move_df, by = c("ID","goal"))

# sanity‑check
exp2_data %>% 
  mutate(n_possible = map_int(origin_inds, length)) %>%
  count(n_possible) %>%
  print()

# sampler
sample_random_salience_poss <- function(poss, n=1000) {
  if (length(poss) < 1) return(tibble(
    expected_stepwise  = NA_real_,
    expected_euclidean = NA_real_
  ))
  sampled <- sample(poss, n, replace=TRUE)
  sals <- map_dfr(sampled, ~{
    rc <- row_col(.x); 
    tibble(
      stepwise  = abs(rc[1]-center_coords[1]) + abs(rc[2]-center_coords[2]),
      euclid    = sqrt((rc[1]-center_coords[1])^2 + (rc[2]-center_coords[2])^2)
    )
  })
  summarise(sals,
            expected_stepwise  = mean(stepwise),
            expected_euclidean = mean(euclid))
}

# compute baseline_all
exp2_data <- exp2_data %>%
  rowwise() %>%
  mutate(baseline_all = list(sample_random_salience_poss(origin_inds))) %>%
  unnest_wider(baseline_all)

# peek
print(exp2_data)

%>% 
        select(ID, goal, expected_stepwise, expected_euclidean) %>% 
        head())

exp2_data <- exp2_data %>%
  # 1) compute the difference between observed and random‐baseline
  mutate(
    step_diff = stepwise_salience - expected_stepwise,
    euc_diff  = euclidean_salience - expected_euclidean
  )

# 2) Print a quick summary of those differences:
print(
  exp2_data %>%
    summarise(
      mean_step_diff = mean(step_diff, na.rm = TRUE),
      sd_step_diff   = sd(step_diff,   na.rm = TRUE),
      mean_euc_diff  = mean(euc_diff,  na.rm = TRUE),
      sd_euc_diff    = sd(euc_diff,    na.rm = TRUE)
    )
)

# 3) Visualize: are observed moves systematically closer or farther?
library(ggplot2)

ggplot(exp2_data, aes(x = step_diff)) +
  geom_histogram(bins = 30, fill = "steelblue", alpha = 0.7) +
  labs(
    title    = "Distribution of Stepwise Salience Difference\n(observed − expected)",
    x        = "Stepwise Difference",
    y        = "Count"
  ) +
  theme_minimal()

ggplot(exp2_data, aes(x = euc_diff)) +
  geom_histogram(bins = 30, fill = "darkorange", alpha = 0.7) +
  labs(
    title    = "Distribution of Euclidean Salience Difference\n(observed − expected)",
    x        = "Euclidean Difference",
    y        = "Count"
  ) +
  theme_minimal()

