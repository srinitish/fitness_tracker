"""
LangGraph pipeline — 4 nodes: metrics → diet → workout → summary
API key comes from config.py (never from UI)
"""
import json, re
from typing import TypedDict
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from prompts import DIET_PROMPT, WORKOUT_PROMPT, SUMMARY_PROMPT
from config import GROQ_API_KEY, GROQ_MODEL


# ── Shared state ──────────────────────────────────────────────────────────────
class State(TypedDict):
    age: int
    weight: float
    height: float
    days: int
    goal: str
    # computed
    bmi: float
    calories: int
    profile: str
    diet: dict
    workout: dict
    summary: str


# ── Helpers ───────────────────────────────────────────────────────────────────
def _llm():
    return ChatGroq(
        groq_api_key=GROQ_API_KEY,
        model_name=GROQ_MODEL,
        temperature=0.7,
        max_tokens=4096,
    )

def _parse_json(text: str) -> dict:
    # Strip accidental markdown code fences
    text = re.sub(r"```json|```", "", text.strip()).strip()
    try:
        return json.loads(text)
    except Exception:
        return {"parse_error": text}


# ── Node 1: Calculate metrics ─────────────────────────────────────────────────
def calc_metrics(state: State) -> State:
    w  = state["weight"]
    hm = state["height"] / 100
    a  = state["age"]
    g  = state["goal"]

    bmi  = round(w / hm ** 2, 1)
    bmr  = 10 * w + 6.25 * state["height"] - 5 * a
    tdee = bmr * 1.55

    cal = (int(tdee - 500) if g == "Weight Loss"  else
           int(tdee + 400) if g == "Weight Gain"  else
           int(tdee + 250) if g == "Muscle Gain"  else
           int(tdee))

    profile = (f"Age {a} | {w}kg | {state['height']}cm | "
               f"BMI {bmi} | Goal: {g} | Target: {cal} kcal/day")

    return {**state, "bmi": bmi, "calories": cal, "profile": profile}


# ── Node 2: Generate diet ─────────────────────────────────────────────────────
def gen_diet(state: State) -> State:
    prompt = DIET_PROMPT.format(
        age=state["age"], weight=state["weight"],
        height=state["height"], goal=state["goal"],
        calories=state["calories"],
    )
    resp = _llm().invoke([HumanMessage(content=prompt)])
    return {**state, "diet": _parse_json(resp.content)}


# ── Node 3: Generate workout ──────────────────────────────────────────────────
def gen_workout(state: State) -> State:
    prompt = WORKOUT_PROMPT.format(
        age=state["age"], weight=state["weight"],
        goal=state["goal"], days=state["days"],
    )
    resp = _llm().invoke([HumanMessage(content=prompt)])
    return {**state, "workout": _parse_json(resp.content)}


# ── Node 4: Generate summary ──────────────────────────────────────────────────
def gen_summary(state: State) -> State:
    prompt = SUMMARY_PROMPT.format(
        profile=state["profile"],
        diet_overview=state["diet"].get("overview", ""),
        workout_overview=state["workout"].get("overview", ""),
    )
    resp = _llm().invoke([HumanMessage(content=prompt)])
    return {**state, "summary": resp.content}


# ── Build & run ───────────────────────────────────────────────────────────────
def build_graph():
    g = StateGraph(State)
    g.add_node("calc_metrics", calc_metrics)
    g.add_node("gen_diet",     gen_diet)
    g.add_node("gen_workout",  gen_workout)
    g.add_node("gen_summary",  gen_summary)
    g.set_entry_point("calc_metrics")
    g.add_edge("calc_metrics", "gen_diet")
    g.add_edge("gen_diet",     "gen_workout")
    g.add_edge("gen_workout",  "gen_summary")
    g.add_edge("gen_summary",  END)
    return g.compile()


def run(age, weight, height, days, goal) -> State:
    return build_graph().invoke({
        "age": age, "weight": weight, "height": height,
        "days": days, "goal": goal,
        "bmi": 0.0, "calories": 0, "profile": "",
        "diet": {}, "workout": {}, "summary": "",
    })
