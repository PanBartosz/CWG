# Workout generator

# EMOM: 4 minutes: 1, 2, 4 exercises
# 	- hard exercises
# EMOM: 6 minutes: 1, 2, 3, 6 exercises
# 	- hard or medium exercises
# EMOM: 8 minutes: 1, 2, 4, 8 exercises
# 	- medium or light exercises
# EMOM: 10 minutes: 1, 2, 5, 10 exercises
# - medium or light exercises

# O(dd) M(inute) E(ven) M(minute): 4 minutes
# - hard exercises
# O(dd) M(inute) E(ven) M(minute): 6 minutes
# 	- one hard one medium exercise
# O(dd) M(inute) E(ven) M(minute): 8 minutes
# 	- two medium exercises
# O(dd) M(inute) E(ven) M(minute): 10 minutes
# 	- one medium and one light exercise

# Humane Burpee Long: 10-1 Ladder + 15 fixed
# Humane Burpee Short: 5-1 Ladder + 15 fixed

# Tabata: 8 rounds 20 second work / 10 seconds rest
# Tabata Modified: 8 rounds 20 second work / 10 seconds rest

# 20-15-10 x 3 exercises
# - three medium exercises

import streamlit as st
import pandas as pd
import numpy as np
from dataclasses import dataclass
import io
from contextlib import redirect_stdout


@dataclass
class Exercise:
    name: str
    implement: str
    weight: int
    difficulty: str
    tabatable: bool
    pattern: list[str]


exercises = pd.read_csv("exercises.csv")
exercises['pattern'] = exercises['pattern'].apply(
    lambda x: [item.strip() for item in x.split(',')] if isinstance(x, str) else [])


def generate_hb(exercises, weight_options, long=False, implements=None):
    eligible = exercises[exercises["active"]]
    if weight_options:
        mask = False  # Start with a False mask
        for implement in weight_options.keys():
            for weight in weight_options[implement]:
                mask |= (eligible['implement'] == implement) & (
                    eligible['weight'] == weight)
        eligible = eligible[mask]
    if implements:
        eligible = eligible[exercises["implement"].isin(implements)]

    eligible = eligible.reindex(np.random.permutation(eligible.index))
    push_exercise = eligible[(eligible["difficulty"] == "medium") & (
        eligible["pattern"].apply(lambda x: "press" in x))].iloc[0]
    squat_exercise = eligible[(eligible["difficulty"] == "medium") & (
        eligible["pattern"].apply(lambda x: "squat" in x))].iloc[0]
    hinge_exercise = eligible[(eligible["difficulty"] == "medium") & (
        eligible["pattern"].apply(lambda x: "hinge" in x))].iloc[0]

    print(f"##### Protocol")
    print(f"*For 5 rounds perform 5-4-3-2-1 reps (descending ladder) of squat and push exercises. After every rung perform 15 reps of hinge exercise.*")
    print(f"##### Selected exercises:")
    print(f" - **Hinge**: {hinge_exercise['implement']} {hinge_exercise['name']} {'x ' + str(int(hinge_exercise['weight'])) + 'kg' if not np.isnan(hinge_exercise['weight']) else ''}")
    print(f" - **Push**: {push_exercise['implement']} {push_exercise['name']} {'x ' + str(int(push_exercise['weight'])) + 'kg' if not np.isnan(push_exercise['weight']) else ''}")
    print(f" - **Squat**: {squat_exercise['implement']} {squat_exercise['name']} {'x ' + str(int(squat_exercise['weight'])) + 'kg' if not np.isnan(squat_exercise['weight']) else ''}")


def generate_tabata(exercises, weight_options, modified=False, implements=None, difficulty=["medium", "hard"]):
    eligible = exercises[exercises["active"]]
    if weight_options:
        mask = False  # Start with a False mask
        for implement in weight_options.keys():
            for weight in weight_options[implement]:
                mask |= (eligible['implement'] == implement) & (
                    eligible['weight'] == weight)
        eligible = eligible[mask]
    if implements:
        eligible = eligible[exercises["implement"].isin(implements)]
    if difficulty:
        eligible = eligible[eligible["difficulty"].isin(difficulty)]
    eligible = eligible.reindex(np.random.permutation(eligible.index))
    eligible = eligible[eligible["tabatable"]]
    eligible = eligible[eligible["difficulty"].isin(difficulty)]
    first_exercise = eligible.iloc[0]

    print(f"##### Protocol")
    print(f"*For rounds perform selected exercise (20 seconds work / 10 seconds rest)*")
    print(f"##### Selected exercises:")
    print(f"Selected exercises:")
    print(f" - {first_exercise['implement']} {first_exercise['name']} {'x ' + str(int(first_exercise['weight'])) + 'kg' if not np.isnan(first_exercise['weight']) else ''}")


def generate_omem(exercises, length, weight_options, overlap=False, implements=None):
    eligible = exercises[exercises["active"]]
    if weight_options:
        mask = False  # Start with a False mask
        for implement in weight_options.keys():
            for weight in weight_options[implement]:
                mask |= (eligible['implement'] == implement) & (
                    eligible['weight'] == weight)
        eligible = eligible[mask]
    if implements:
        eligible = eligible[exercises["implement"].isin(implements)]

    match length:
        case _ if 4 <= length <= 5:
            allowed_difficulties = ["hard"]
        case _ if 6 <= length <= 7:
            allowed_difficulties = ["medium", "hard"]
        case _ if 8 <= length < 10:
            allowed_difficulties = ["medium"]
        case _ if length >= 10:
            allowed_difficulties = ["medium", "easy"]

    used_patterns = []
    eligible = eligible[eligible["difficulty"].isin(allowed_difficulties)]
    eligible = eligible.reindex(np.random.permutation(eligible.index))
    first_exercise = eligible.iloc[0]
    used_patterns += first_exercise['pattern']
    if not overlap:
        eligible = eligible[~eligible["pattern"].apply(
            lambda x: any(item in used_patterns for item in x))]
    eligible = eligible.reindex(np.random.permutation(eligible.index))
    if len(allowed_difficulties) > 1:
        eligible = eligible[eligible["difficulty"]
                            != first_exercise["difficulty"]]
    second_exercise = eligible.iloc[0]
    print(f"##### Protocol")
    print(f"*For {length} minutes perform first exercise on odd numbered round, second exercise on even numbered round*")
    print(f"##### Selected exercises:")
    print(f" - {first_exercise['implement']} {first_exercise['name']} {'x ' + str(int(first_exercise['weight'])) + 'kg' if not np.isnan(first_exercise['weight']) else ''}")
    print(f" - {second_exercise['implement']} {second_exercise['name']} {'x ' + str(int(second_exercise['weight'])) + 'kg' if not np.isnan(second_exercise['weight']) else ''}")


def generate_emom(exercises, length, n_exercises, weight_options, overlap=False, implements=None):
    eligible = exercises[exercises["active"]]
    if weight_options:
        mask = False  # Start with a False mask
        for implement in weight_options.keys():
            for weight in weight_options[implement]:
                mask |= (eligible['implement'] == implement) & (
                    eligible['weight'] == weight)
        eligible = eligible[mask]
    if implements:
        eligible = eligible[exercises["implement"].isin(implements)]

    if length % n_exercises != 0:
        print("Warning: Number of exercises does not divide length in minutes")
    match length:
        case _ if 4 <= length <= 5:
            eligible = eligible[eligible["difficulty"].isin(["hard"])]
        case _ if 6 <= length <= 7:
            eligible = eligible[eligible["difficulty"].isin(
                ["hard", "medium"])]
        case _ if 8 <= length:
            eligible = eligible[eligible["difficulty"].isin(
                ["medium", "easy"])]
        case _:
            raise ValueError("You cannot create EMOM shorter than 4 minutes")

    eligible = eligible.reindex(np.random.permutation(eligible.index))
    selected = []
    used_patterns = []
    for _ in range(n_exercises):
        if not overlap:
            eligible = eligible[~eligible["pattern"].apply(
                lambda x: any(item in used_patterns for item in x))]
        used_patterns += eligible.iloc[0]['pattern']
        selected.append(eligible.iloc[0])
        eligible = eligible.iloc[1:]

    print(f"##### Protocol")
    print(f"*For {length} minutes perform exercises in circuit fashion at the top of every minute (e.g. 0:00, 1:00, and so on)*")
    print(f"##### Selected exercises:")
    for exercise in selected:
        print(
            f" - {exercise['implement']} {exercise['name']} {'x ' + str(int(exercise['weight'])) + 'kg' if not np.isnan(exercise['weight']) else ''}")


st.title("Conditioning workout generator")
exercises_tab, EMOM_tab, OMEM_tab, tabata_tab, hb_tab = st.tabs(
    ["Exercises", "EMOM", "OMEM", "Tabata", "Humane Burpee"])
workout = ""
with exercises_tab:
    f_exercises = st.data_editor(exercises,
                                 column_config={
                                     "difficulty": st.column_config.SelectboxColumn(
                                         options=["hard", "medium", "easy"],
                                         required=True
                                     )
                                 })
with EMOM_tab:
    st.markdown(
        "#### Generate EMOM (Each Minute On Minute) conditioning workout")
    emom_sidebar, emom_main = st.columns([2, 3])
    with emom_sidebar:
        emom_length = st.slider(
            "Length of the workout (in minutes)", 4, 10, 10, key="emom_length")
        emom_n_exercises = st.slider("Number of exercises", 1, 6, 2, key="emom_n_exercises")
        emom_allow_overlaping = st.checkbox("Allow overlaping patterns?", key="emom_allow_overlaping")
        emom_possible_implements = set(list(exercises["implement"]))
        emom_selected_implements = st.multiselect("Select implements",
                                                  options=emom_possible_implements,
                                                  default=emom_possible_implements,
                                                  key="emom_selected_implements")
        weight_options = {}
        for implement in emom_selected_implements:
            if implement != "Bodyweight":
                wts = list(
                    set(exercises[exercises["implement"] == implement]["weight"]))
                weight_options[implement] = st.multiselect(f"Select weights for {implement}",
                                                           options=wts,
                                                           default=wts,
                                                           key=f"emom_wo_{implement}",
                                                           format_func=lambda x: str(
                                                               int(x)) + "kg"
                                                           )
        if st.button("Generate EMOM workout"):
            message = io.StringIO()
            with redirect_stdout(message):
                generate_emom(f_exercises,
                              implements=emom_selected_implements,
                              length=emom_length,
                              n_exercises=emom_n_exercises,
                              overlap=emom_allow_overlaping,
                              weight_options=weight_options)
            workout = message.getvalue()
        with emom_main:
            st.markdown(workout)

with OMEM_tab:
    st.markdown("#### Generate OMEM (Odds Minute Even Minute) conditioning workout")
    omem_sidebar, omem_main = st.columns([2, 3])
    with omem_sidebar:
        omem_length = st.slider(
            "Length of the workout (in minutes)", 4, 10, 10, key = "omem_slider")
        omem_allow_overlaping = st.checkbox("Allow overlaping patterns?")
        omem_possible_implements = set(list(exercises["implement"]))
        omem_selected_implements = st.multiselect("Select implements",
                                                  options=omem_possible_implements,
                                                  default=omem_possible_implements,
                                                  key="omem_selected_implements")
        weight_options = {}
        for implement in omem_selected_implements:
            if implement != "Bodyweight":
                wts = list(
                    set(exercises[exercises["implement"] == implement]["weight"]))
                weight_options[implement] = st.multiselect(f"Select weights for {implement}",
                                                           options=wts,
                                                           default=wts,
                                                           key=f"omem_wo_{implement}",
                                                           format_func=lambda x: str(
                                                               int(x)) + "kg"
                                                           )
        if st.button("Generate OMEM workout"):
            message = io.StringIO()
            with redirect_stdout(message):
                generate_omem(f_exercises,
                              implements=omem_selected_implements,
                              length=omem_length,
                              overlap=omem_allow_overlaping,
                              weight_options=weight_options)
            workout = message.getvalue()
        with omem_main:
            st.markdown(workout)

with tabata_tab:
    st.markdown("#### Generate Tabata (20 second work / 10 seconds rest) conditioning workout")
    tabata_sidebar, tabata_main = st.columns([2, 3])
    with tabata_sidebar:
        tabata_difficulty = st.multiselect("Select difficulty",
                                           options = ["easy", "medium", "hard"],
                                           default = ["medium", "hard"])
        tabata_possible_implements = set(list(exercises["implement"]))
        tabata_selected_implements = st.multiselect("Select implements",
                                                  options=tabata_possible_implements,
                                                  default=tabata_possible_implements,
                                                  key="tabata_selected_implements")
        weight_options = {}
        for implement in tabata_selected_implements:
            if implement != "Bodyweight":
                wts = list(
                    set(exercises[exercises["implement"] == implement]["weight"]))
                weight_options[implement] = st.multiselect(f"Select weights for {implement}",
                                                           options=wts,
                                                           default=wts,
                                                           key=f"tabata_wo_{implement}",
                                                           format_func=lambda x: str(
                                                               int(x)) + "kg"
                                                           )
        if st.button("Generate Tabata workout"):
            message = io.StringIO()
            with redirect_stdout(message):
                generate_tabata(f_exercises,
                              difficulty=tabata_difficulty,
                              implements=tabata_selected_implements,
                              weight_options=weight_options)
            workout = message.getvalue()
        with tabata_main:
            st.markdown(workout)

with hb_tab:
    st.markdown("#### Generate Humane Burpee conditioning workout")
    hb_sidebar, hb_main = st.columns([2, 3])
    with hb_sidebar:
        hb_possible_implements = set(list(exercises["implement"]))
        hb_selected_implements = st.multiselect("Select implements",
                                                  options=hb_possible_implements,
                                                  default=hb_possible_implements,
                                                  key="hb_selected_implements")
        weight_options = {}
        for implement in hb_selected_implements:
            if implement != "Bodyweight":
                wts = list(
                    set(exercises[exercises["implement"] == implement]["weight"]))
                weight_options[implement] = st.multiselect(f"Select weights for {implement}",
                                                           options=wts,
                                                           default=wts,
                                                           key=f"hb_wo_{implement}",
                                                           format_func=lambda x: str(
                                                               int(x)) + "kg"
                                                           )
        if st.button("Generate Humane Burpee workout"):
            message = io.StringIO()
            with redirect_stdout(message):
                generate_hb(f_exercises,
                              implements=hb_selected_implements,
                              weight_options=weight_options)
            workout = message.getvalue()
        with hb_main:
            st.markdown(workout)

