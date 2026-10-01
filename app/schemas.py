from pydantic import BaseModel, Field
class FitnessInput(BaseModel):
    name:str=Field(min_length=1,max_length=120)
    age:int=Field(ge=13,le=100)
    weight:float=Field(gt=20,le=400)
    goal:str=Field(min_length=2,max_length=80)
    intensity:str=Field(min_length=2,max_length=40)
class WorkoutDay(BaseModel):
    day:str; focus:str; warmup:list[str]=[]; exercises:list[str]=[]; cooldown:list[str]=[]; recovery:str=''
class WorkoutPlan(BaseModel):
    title:str; summary:str; safety_note:str; days:list[WorkoutDay]
