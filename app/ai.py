import json,time
from typing import Any
from google import genai
from google.genai import types
from .config import settings
from .schemas import WorkoutPlan

SYSTEM='''You are FitBuddy, a responsible fitness-planning assistant. Create practical fitness guidance. Do not diagnose conditions or prescribe treatment. Avoid extreme dieting or dangerous exercises. Return only valid JSON matching the requested schema.'''

def plan_schema():
    return {'type':'object','properties':{'title':{'type':'string'},'summary':{'type':'string'},'safety_note':{'type':'string'},'days':{'type':'array','items':{'type':'object','properties':{'day':{'type':'string'},'focus':{'type':'string'},'warmup':{'type':'array','items':{'type':'string'}},'exercises':{'type':'array','items':{'type':'string'}},'cooldown':{'type':'array','items':{'type':'string'}},'recovery':{'type':'string'}},'required':['day','focus','warmup','exercises','cooldown','recovery']}}},'required':['title','summary','safety_note','days']}

class GeminiService:
    def __init__(self): self.client=genai.Client(api_key=settings.gemini_api_key) if settings.gemini_api_key else None
    def _json(self,prompt,schema):
        if not self.client: raise RuntimeError('GEMINI_API_KEY is not configured.')
        last=None
        for model in [settings.gemini_model,*settings.fallback_models]:
            for attempt in range(3):
                try:
                    r=self.client.models.generate_content(model=model,contents=prompt,config=types.GenerateContentConfig(system_instruction=SYSTEM,temperature=.4,response_mime_type='application/json',response_schema=schema))
                    return json.loads((r.text or '').strip())
                except Exception as e:
                    last=e; msg=str(e).lower()
                    transient=any(x in msg for x in ('503','unavailable','429','rate limit','500','502','504'))
                    if transient and attempt<2: time.sleep(2**attempt); continue
                    break
        raise RuntimeError(f'Gemini request failed after retries: {last}')
    def generate_workout(self,name,age,weight,goal,intensity):
        try:
            d=self._json(f'''Create a personalized exactly 7-day workout plan. Name:{name}; Age:{age}; Weight kg:{weight}; Goal:{goal}; Intensity:{intensity}. Include warmup, exercises, cooldown and recovery for every day.''',plan_schema())
            return WorkoutPlan.model_validate(d)
        except Exception:
            return self.offline(name,goal,intensity)
    def update_workout(self,original,feedback):
        try:
            d=self._json(f'Revise this 7-day plan according to feedback. Plan:{original.model_dump_json()} Feedback:{feedback}',plan_schema())
            return WorkoutPlan.model_validate(d)
        except Exception:
            x=original.model_copy(deep=True); x.summary += f' Revised according to feedback: {feedback}'; return x
    def nutrition_tip(self,goal):
        try:
            d=self._json(f'Give one concise practical nutrition and recovery tip for goal {goal}. No medical treatment or extreme dieting.',{'type':'object','properties':{'tip':{'type':'string'}},'required':['tip']})
            return str(d.get('tip','')).strip() or self.offline_tip(goal)
        except Exception: return self.offline_tip(goal)
    @staticmethod
    def offline_tip(goal): return f'For {goal}, prioritize balanced meals, adequate protein, vegetables, whole-food carbohydrates, healthy fats, water and consistent sleep.'
    @staticmethod
    def offline(name,goal,intensity):
        data=[('Day 1','Full Body',['Squats 3x10','Incline push-ups 3x8-12','Glute bridges 3x12','Plank 3x20-30 sec']),('Day 2','Cardio & Mobility',['20-30 min brisk walk','Hip mobility 2x8','Shoulder mobility 2x8']),('Day 3','Upper Body',['Rows 3x10','Push-ups 3x8-12','Shoulder raises 2x12','Dead bug 3x8/side']),('Day 4','Recovery',['20 min easy walk','Light stretching 10 min']),('Day 5','Lower Body',['Squats 3x10','Reverse lunges 3x8/side','Hip hinge 3x10','Calf raises 3x15']),('Day 6','Cardio',['25-35 min moderate walk/cycle','Core circuit 2 rounds']),('Day 7','Rest',['Rest, easy mobility or relaxed walk'])]
        return WorkoutPlan(title=f"{name}'s 7-Day FitBuddy Plan",summary=f'A {intensity.lower()} weekly plan for {goal}.',safety_note='Stop for unusual pain, dizziness, chest pain or significant shortness of breath and seek appropriate professional advice.',days=[{'day':d,'focus':f,'warmup':['5-10 min easy movement'],'exercises':e,'cooldown':['5 min easy movement','Gentle stretching'],'recovery':'Hydrate and prioritize sleep.'} for d,f,e in data])
gemini=GeminiService()
