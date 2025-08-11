# Understanding Goal-Directed Helping Behavior

### How do people decide the best way to help?

This project examines the reasoning strategies people use when deciding how to help others. Over the past eight months, we analyzed two experiments (E1 and E2) in which participants played a grid-based game and would take turns making moves to advance toward a goal (E1) or play the game alone, individually making moves to complete the goal (E2). This setting introduced collaborative, goal-directed problem-solving scenarios.

Our process involved two stages:

- **Preliminary behavioral analysis** — Using R, we quantified measures of salience, utility, and pragmatism to capture different aspects of participants’ move choices. We compared these measures between experiments to identify behavioral patterns and differences.

- **Computational modeling** — Using Python, we fit participants’ choices to competing models to understand which decision strategies best explained their behavior.

---

## Project Focus

Helping behavior involves multiple cognitive strategies that influence how people choose their actions. Our project focused on understanding three key interpretations of how people undergo decision-making in goal-directed helping tasks:

- **Literal interpretation** — responding directly to the stated goal or instruction without additional inference.

- **Pragmatic reasoning** — integrating contextual and communicative cues to infer the helper’s intended goal more strategically.

- **Salience** — the influence of visual or spatial prominence that makes some moves easier or more attention-grabbing.

Rather than assuming people rely on a single strategy, we aimed to quantify how these factors jointly contribute to move choices, and whether their relative importance changes across different experimental settings.

---

## The Experiments

We analyzed two versions of the grid-based helping game:

- **Experiment 1 (E1)** — Collaborative two-player setup, where a helper was present.

- **Experiment 2 (E2)** — Single-player setup, where the helper was absent.

---

## Stage 1 — Behavioral Measures

Before modeling, we examined several measures:

- **Salience** — how visually prominent or accessible a move was.

- **Utility** — whether a move advanced, hindered, or had no effect on the goal.

- **Pragmatism** — how clearly a move signaled the intended goal to a partner.

We compared these measures across E1 and E2. Notably, E1 tended to have lower salience values (moves less visually accessible), suggesting players sometimes made less obvious moves to communicate intentions, whereas E2 moves were often more salient, suggesting efficiency took priority with the absence of a second player. 

---

## Stage 2 — Modeling

We fit each participant’s move choices to three models:

1. Literal  
2. Pragmatic  
3. Salience + Pragmatic (sal_prag)

Model fits were evaluated using negative log likelihood (NLL), summed across IDs for each specific goal type.

---

## Results

In both experiments, the sal_prag model provided the best overall fit, outperforming the literal and pragmatic models for 3 of the 5 goal types.

This pattern suggests that people’s moves were guided by both visual efficiency (salience) and strategic communicative reasoning (pragmatics), rather than relying on either factor alone.

---

## Tools Used

- **R** — preliminary behavioral analyses, visualization  
- **Python** — computational modeling and simulation  
- **HPC (High-Performance Computing)** — for running large-scale model fits efficiently
