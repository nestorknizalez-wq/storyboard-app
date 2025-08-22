from pydantic import BaseModel
from typing import List, Literal

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
    return f"{scene}, {estetica and estilo_map[estetica]}, lighting: {luz_map[luz]}, shot: {shot}, lens: {lens}, rule of thirds, realistic textures --ar 9:16"

def veo_json(duration, movimiento, shot_type, lens, lighting, action, transition):
    lighting_map = {"calida":"warm cinematic","natural":"natural daylight","fria":"cool","golden":"golden hour","interior":"soft interior"}
    motion_map = {"estatico":"static","paneos":"slow pan","tracking":"tracking","dinamico":"orbit"}
    clean_lens = lens.split()[0].replace("–","").replace("f/1.8","")
    return {
        "resolution":"1080x1920",
        "duration":duration,
        "camera_motion": motion_map[movimiento],
        "shot_type": shot_type,
        "lens": clean_lens,
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
    if "detalle" in plano:
        return "macro"
    if "cenital" in plano:
        return "overhead"
    if "contrapicado" in plano or "picado" in plano:
        return "low angle"
    return "medium"

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
        frames.append({
            "orden": i+1,
            "beat": beats[i],
            "duracion_s": durations[i],
            "camara": {"plano": plano, "lente": lens, "movimiento": a.movimiento},
            "accion": actions[i],
            "transicion": trans,
            "prompt_mj": mj_prompt(scene, a.estetica, a.luz, plano, lens),
            "prompt_video": veo_json(durations[i], a.movimiento,
                                     shot_type_from_plano(plano),
                                     lens, a.luz, actions[i], trans)
        })
    resumen = f"Vídeo {a.duracion}s 9:16, estética {a.estetica}, luz {a.luz}, ritmo {a.ritmo}. CTA: {a.cta}. Idea: {idea}"
    return {"resumen": resumen, "frames": frames}
