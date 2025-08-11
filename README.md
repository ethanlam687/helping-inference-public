# Understanding Goal-Directed Helping Behavior

### How do people decide the *best way* to help?

This project explores the decision-making strategies people use when helping others in different contexts. Over the past eight months, we’ve analyzed two experiments (E1 and E2) where participants observed situations and chose how to act in order to help someone achieve a goal.  

We then used computational modeling to understand **what kind of reasoning people relied on** — whether they acted based on:
- **Literal interpretation** of instructions  
- **Pragmatic reasoning**, where they considered the broader communicative context  
- **Salience**, where they were drawn to the most noticeable or prominent cues  

---

## Project Summary

When someone needs help, our minds can process the request in different ways.  
For example:
- If a friend says “pass me the blue cup,” you might literally hand them the nearest blue cup (**literal**).
- But if you notice that they’re making tea and their kettle is right next to a different blue cup, you might think they mean something else (**pragmatic**).
- Or you might simply grab whatever object stands out the most in the scene (**salience**).

We wanted to measure *how much each of these strategies explains human behavior*, and whether it changes across different task settings.

---

## The Experiments

We analyzed **two experiments**:
- **Experiment 1 (E1)** — Collaborative game--the presence of a helper  
- **Experiment 2 (E2)** — Single player game--absence of the helper

Participants’ choices were fit to three models:
1. **Literal model**
2. **Pragmatic model**
3. **Salience + Pragmatic model (sal_prag)**

We then compared the **negative log likelihood (NLL)** of each model fit

---

## Results

Across both experiments:
- E2 participants consistently had **lower NLL values** than E1 for all models.
- This suggests that **E2 participants might be relying more on salience** when making decisions (in the absence of the helper, the single players may make more visually accessible and efficient moves at the sacrifice of greater strategic signalling).
- The salience-pragmatic model often outperformed the others, showing that people don’t rely on *just* one strategy, rather incorporating both visual efficiency cues and pragmatically strategic thinking.
---

## 🛠 Tools We Used

- **R** (data analysis, visualization)
- **Python** (modeling)  
- **HPC (High-Performance Computing)** for processing large datasets

