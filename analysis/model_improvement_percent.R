library(dplyr)
library(tidyr)
e1_model_results <- read_csv("../data/e1/all_model_results.csv") 

# Filter to just literal and sal_prag models
comparison_data <- e1_model_results %>%
  filter(model %in% c("literal", "sal_prag")) %>%
  select(ID, goal_type, model, NLL)

# Spread to wide format: one row per subject x goal_type, with NLLs for both models
wide_nll <- comparison_data %>%
  pivot_wider(names_from = model, values_from = NLL)

# Calculate percent improvement
improvement_data <- wide_nll %>%
  mutate(
    percent_improvement = (literal - sal_prag) / literal * 100
  )

# Summarize across subjects per goal_type
summary_improvement <- improvement_data %>%
  group_by(goal_type) %>%
  summarise(
    mean_improvement = mean(percent_improvement, na.rm = TRUE),
    sd_improvement = sd(percent_improvement, na.rm = TRUE),
    se_improvement = sd_improvement / sqrt(n()),
    .groups = "drop"
  )

print(summary_improvement)

library(ggplot2)

ggplot(summary_improvement, aes(x = goal_type, y = mean_improvement)) +
  geom_bar(stat = "identity", width = 0.6, fill = "steelblue") +
  geom_errorbar(aes(ymin = mean_improvement - se_improvement,
                    ymax = mean_improvement + se_improvement),
                width = 0.2) +
  labs(
    title = "Percent Improvement of sal_prag over literal Model by Goal Type",
    x = "Goal Type",
    y = "Mean % Improvement in NLL"
  ) +
  theme_minimal()

# For each goal_type, perform a paired t-test
library(dplyr)
library(tidyr)
library(purrr)
library(broom)

# Prepare wide format data again
wide_nll <- e1_model_results %>%
  filter(model %in% c("literal", "sal_prag")) %>%
  select(ID, goal_type, model, NLL) %>%
  pivot_wider(names_from = model, values_from = NLL)

# Paired t-test per goal_type
t_test_results <- wide_nll %>%
  group_by(goal_type) %>%
  summarise(
    t_test = list(t.test(literal, sal_prag, paired = TRUE)),
    .groups = "drop"
  ) %>%
  mutate(tidy_result = map(t_test, tidy)) %>%
  unnest(tidy_result) %>%
  select(goal_type, estimate, statistic, p.value, conf.low, conf.high)

print(t_test_results)


