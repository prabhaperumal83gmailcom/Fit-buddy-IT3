import json
from fastapi import APIRouter,Request,Form
from fastapi.responses import HTMLResponse
from sqlalchemy import select
from .database import SessionLocal,UserPlan
from .schemas import FitnessInput,WorkoutPlan
from .ai import gemini
router=APIRouter()
@router.get('/',response_class=HTMLResponse)
def home(request:Request): return request.app.state.templates.TemplateResponse('index.html',{'request':request})
@router.post('/generate-workout',response_class=HTMLResponse)
def generate(request:Request,name:str=Form(...),age:int=Form(...),weight:float=Form(...),goal:str=Form(...),intensity:str=Form(...)):
    d=FitnessInput(name=name,age=age,weight=weight,goal=goal,intensity=intensity)
    plan=gemini.generate_workout(d.name,d.age,d.weight,d.goal,d.intensity); tip=gemini.nutrition_tip(d.goal)
    with SessionLocal() as db:
        row=UserPlan(name=d.name,age=d.age,weight=d.weight,goal=d.goal,intensity=d.intensity,plan_json=plan.model_dump_json(),nutrition_tip=tip); db.add(row); db.commit(); db.refresh(row); pid=row.id
    return request.app.state.templates.TemplateResponse('result.html',{'request':request,'plan':plan,'nutrition_tip':tip,'plan_id':pid,'message':None})
@router.post('/submit-feedback',response_class=HTMLResponse)
def feedback(request:Request,plan_id:int=Form(...),feedback:str=Form(...)):
    with SessionLocal() as db:
        row=db.get(UserPlan,plan_id)
        if not row: return request.app.state.templates.TemplateResponse('error.html',{'request':request,'error':'Plan not found.'},status_code=404)
        revised=gemini.update_workout(WorkoutPlan.model_validate(json.loads(row.plan_json)),feedback); row.plan_json=revised.model_dump_json(); row.feedback=feedback; row.nutrition_tip=gemini.nutrition_tip(row.goal); db.commit(); tip=row.nutrition_tip
    return request.app.state.templates.TemplateResponse('result.html',{'request':request,'plan':revised,'nutrition_tip':tip,'plan_id':plan_id,'message':'Plan updated successfully.'})
@router.get('/view-all-users',response_class=HTMLResponse)
def users(request:Request):
    with SessionLocal() as db:
        rows=db.scalars(select(UserPlan).order_by(UserPlan.created_at.desc())).all(); data=[{'id':r.id,'name':r.name,'age':r.age,'weight':r.weight,'goal':r.goal,'intensity':r.intensity,'created_at':r.created_at.strftime('%Y-%m-%d %H:%M')} for r in rows]
    return request.app.state.templates.TemplateResponse('all_users.html',{'request':request,'users':data})
@router.get('/health')
def health(): return {'status':'ok'}
