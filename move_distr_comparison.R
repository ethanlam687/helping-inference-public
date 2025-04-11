library(tidyverse)

e1 <- read_csv("~/Downloads/final_tracker (1).csv")
e2 <- read_csv("~/Downloads/final_tracker (2).csv")

e1_architects <- e1 %>%
  filter(role == "architect") %>%
  mutate(experiment = "E1")

e2 <- e2 %>%
  mutate(experiment = "E2")

combined <- bind_rows(e1_architects, e2)
#view(combined)

combined <- combined %>%
  mutate(
    move_utility = case_when(
      move_utility == 1 ~ "useful",
      move_utility == 0 ~ "inconsequential",
      move_utility == -1 ~ "harmful"
    ),
    move_type = case_when(
      move_utility == "useful" ~ "Useful",
      move_utility == "inconsequential" ~ "Inconsequential",
      move_utility == "harmful" ~ "Harmful"
    )
  )

move_summary <- combined %>%
  group_by(experiment, move_utility) %>%
  summarise(count = n(), .groups = 'drop') %>%
  pivot_wider(names_from = move_utility, values_from = count, values_fill = 0) %>%
  rename(
    harmful = `harmful`,
    inconsequential = `inconsequential`,
    useful = `useful`
  ) %>%
  mutate(total_moves = harmful + inconsequential + useful)

print(move_summary)


# average number of moves per participant, grouped by move type
avg_moves_by_player <- combined %>%
  group_by(experiment, ID, anonID, move_type) %>%
  summarise(count = n(), .groups = 'drop') %>%
  pivot_wider(names_from = move_type, values_from = count, values_fill = 0) %>%
  mutate(total_moves = Useful + Inconsequential + Harmful)

view(avg_moves_by_player)

# summary statistics: mean and SD of total moves by move type per player
avg_moves_summary <- avg_moves_by_player %>%
  group_by(experiment) %>%
  summarise(
    mean_Useful = mean(Useful),
    sd_Useful = sd(Useful),
    mean_Inconsequential = mean(Inconsequential),
    sd_Inconsequential = sd(Inconsequential),
    mean_Harmful = mean(Harmful),
    sd_Harmful = sd(Harmful),
    mean_total_moves = mean(total_moves),
    sd_total_moves = sd(total_moves)
  )


#create a bar plot to visualize avg_moves_summary
ggplot(avg_moves_summary, aes(x = experiment)) +
  geom_bar(aes(y = mean_Useful), stat = "identity", fill = "blue", alpha = 0.5) +
  geom_errorbar(aes(ymin = mean_Useful - sd_Useful, ymax = mean_Useful + sd_Useful), width = 0.2) +
  labs(title = "Average Useful Moves per Player by Experiment",
       x = "Experiment", y = "Average Useful Moves per Player") +
  theme_minimal()

ggplot(avg_moves_summary, aes(x = experiment)) +
  geom_bar(aes(y = mean_Harmful), stat = "identity", fill = "red", alpha = 0.5) +
  geom_errorbar(aes(ymin = mean_Harmful - sd_Harmful, ymax = mean_Harmful + sd_Harmful), width = 0.2) +
  labs(title = "Average Harmful Moves per Player by Experiment",
       x = "Experiment", y = "Average Harmful Moves per Player") +
  theme_minimal()

ggplot(avg_moves_summary, aes(x = experiment)) +
  geom_bar(aes(y = mean_Inconsequential), stat = "identity", fill = "green", alpha = 0.5) +
  geom_errorbar(aes(ymin = mean_Inconsequential - sd_Inconsequential, ymax = mean_Inconsequential + sd_Inconsequential), width = 0.2) +
  labs(title = "Average Inconsequential Moves per Player by Experiment",
       x = "Experiment", y = "Average Inconsequential Moves per Player") +
  theme_minimal()