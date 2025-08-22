
from pydantic import BaseModel
from typing import List, Literal
import re

class Answers(BaseModel):
    objetivo: Literal["ventas","leads","branding","lanzamiento","test"]
    publico: str
    estetica: Literal["cinematografica","iphone","urbana","minimal","deportiva","cozy"]
    duracion: int  # 15, 18, 20
    movimiento: Literal["estatico","paneos","tracking","dinamico"]
    dialogo: Literal["no_visual","vo","on_cam"]
    ritmo: Literal["clasico","producto","emocional","ugc"]
    luz: Literal["calida","natural","fria","golden","interior"]
    restricciones: str
    cta: str

def split_frames(total:int=18, n:int=6)->List[int]:
    base = total//n
    frames = [base]*n
    for i in range(total - sum(frames)):
        frames[i]+=1
    return frames

def mj_prompt(scene, estetica, luz, shot, lens):
    estilo_map = {
        "cinematografica":"editorial, cinematic, soft shadows, depth of field",
        "iphone":"natural handheld look, realistic, slight motion blur",
        "urbana":"urban vibrant, neon accents, gritty",
        "minimal":"clean minimal, negative space, soft light",
        "deportiva":"dynamic energy, crisp detail, motion emphasis",
        "cozy":"warm cozy home, wood textures, soft bokeh"
    }
    luz_map = {
        "calida":"warm cinematic light",
        "natural":"natural daylight",
        "fria":"cool studio light",
        "golden":"golden hour glow",
        "interior":"soft interior practicals"
    }
    return f"{scene}, {estilo_map[estetica]}, lighting: {luz_map[luz]}, shot: {shot}, lens: {lens}, rule of thirds, realistic textures --ar 9:16"

def normalize_lens(lens:str)->str:
    clean = lens.replace('–','-').lower()
    digits = re.findall(r'\d+', clean)
    if digits:
        return f"{digits[0]}mm"
    return "35mm"

def veo_json(duration, movimiento, shot_type, lens, lighting, action, transition):
    lighting_map = {"calida":"warm cinematic","natural":"natural daylight","fria":"cool","golden":"golden hour","interior":"soft interior"}
    motion_map = {"estatico":"static","paneos":"slow pan","tracking":"tracking","dinamico":"orbit"}
    return {
        "resolution":"1080x1920",
        "duration":duration,
        "camera_motion": motion_map[movimiento],
        "shot_type": shot_type,
        "lens": normalize_lens(lens),
        "lighting": lighting_map[lighting],
        "action": action,
        "transition_out": transition
    }

def shot_type_from_plano(plano:str)->str:
    if "general" in plano:
        return "wide"
    if "medio" in plano:
        return "medium"
    if "primer plano" in plano:
        return "closeup"
    if "detalle" in plano or "macro" in plano:
        return "macro"
    if "cenital" in plano:
        return "overhead"
    if "contrapicado" in plano or "picado" in plano:
        return "low angle"
    return "medium"

def prompt_critic(prompt:str)->dict:
    issues = []
    score = 100
    if "--ar 9:16" not in prompt:
        issues.append("Añade '--ar 9:16' para vertical.")
        score -= 12
    if "lighting" not in prompt and "light" not in prompt:
        issues.append("Especifica la iluminación (lighting: warm cinematic/natural/etc.).")
        score -= 10
    if "shot:" not in prompt:
        issues.append("Incluye 'shot: [wide/medium/closeup/macro]' para composición.")
        score -= 10
    if "lens:" not in prompt:
        issues.append("Incluye 'lens: [14mm/35mm/85mm]' para consistencia óptica.")
        score -= 10
    if "rule of thirds" not in prompt:
        issues.append("Añade 'rule of thirds' para una composición base sólida.")
        score -= 5
    if "realistic textures" not in prompt:
        issues.append("Añade 'realistic textures' para detalle y coherencia.")
        score -= 3
    if len(prompt) < 80:
        issues.append("El prompt es muy corto; añade entorno y acción concreta.")
        score -= 10
    if len(prompt) > 380:
        issues.append("Demasiado largo; reduce descriptores que no aportan.")
        score -= 5

    rewrite = prompt
    tail = []
    if "--ar 9:16" not in rewrite:
        tail.append("--ar 9:16")
    if "rule of thirds" not in rewrite:
        tail.append("rule of thirds")
    if tail:
        rewrite = f"{rewrite}, " + ", ".join(tail)
    return {"score": max(0,min(100,score)), "issues": issues, "rewrite": rewrite}

def generate_storyboard(idea:str, a:Answers):
    beats = ["Hook","Contexto/Producto","Problema/Emoción","Solución/Detalle","Benefit/Prueba","CTA/Packshot"]
    durations = split_frames(a.duracion, 6)
    shots = [
        ("plano general","14–35mm","corte"),
        ("plano medio","35–50mm","corte"),
        ("primer plano","50–85mm","corte"),
        ("detalle","macro/85mm","corte"),
        ("contrapicado","24–35mm","corte"),
        ("narrativo","35–50mm f/1.8","fade")
    ]
    actions = [
        "presenta el ambiente y el protagonista",
        "producto en manos o uso real",
        "reacción/emoción cercana",
        "detalle de textura/beneficio clave",
        "beneficio social o status del producto",
        f"logo + texto en pantalla: {a.cta}"
    ]
    frames=[]
    for i in range(6):
        plano, lens, trans = shots[i]
        scene = f"{beats[i]} · {actions[i]}"
        mj = mj_prompt(scene, a.estetica, a.luz, plano, lens)
        critique = prompt_critic(mj)
        frames.append({
            "orden": i+1,
            "beat": beats[i],
            "duracion_s": durations[i],
            "camara": {"plano": plano, "lente": lens, "movimiento": a.movimiento},
            "accion": actions[i],
            "transicion": trans,
            "prompt_mj": mj,
            "critic": critique,
            "prompt_video": veo_json(durations[i], a.movimiento,
                                     shot_type_from_plano(plano),
                                     lens, a.luz, actions[i], trans)
        })
    resumen = f"Vídeo {a.duracion}s 9:16, estética {a.estetica}, luz {a.luz}, ritmo {a.ritmo}. CTA: {a.cta}. Idea: {idea}"
    return {"resumen": resumen, "frames": frames}
