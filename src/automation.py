#!/usr/bin/env python3
"""Pipeline reproducible para Shorts de fútbol. Sin publicación pública automática.

Pipeline:
  OPENAI_API_KEY -> investigación web + guión -> validación editorial mínima
  HEYGEN_API_KEY -> voz Emiliano (una solicitud)
  Python + FFmpeg -> video 9:16 sin marca de agua -> subtítulos -> MP4
  YouTube API (opcional) -> borrador PRIVADO

En modo demo no llama APIs externas y genera un teaser silencioso.
"""
from __future__ import annotations
import argparse
import copy
import datetime as dt
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_VOICE = '70bc24b8126c446c8cf50fc1a01eb834'  # Emiliano (HeyGen)
OFFICIAL_DOMAINS = {
    'uefa.com','fifa.com','fifatrainingcentre.com','premierleague.com',
    'laliga.com','legaseriea.it','bundesliga.com','ligue1.com','efl.com',
    'thefa.com','psg.fr','realmadrid.com','fcbarcelona.com','manutd.com',
    'liverpoolfc.com','arsenal.com','mancity.com','acmilan.com','inter.it',
    'juventus.com','bvb.de','fcbayern.com','villarrealcf.es',
}
CONCEPTS = {'intro','presion','transicion','balon_parado','rebote','tercer_hombre','bloque','comparacion','cierre'}

class PipelineError(RuntimeError): pass

def json_obj(raw:str)->dict:
    """Extrae JSON sin ejecutar texto o código arbitrario del modelo."""
    raw=raw.strip()
    if raw.startswith('```'):
        raw=re.sub(r'^```(?:json)?\s*','',raw)
        raw=re.sub(r'\s*```$','',raw)
    start=raw.find('{');end=raw.rfind('}')
    if start<0 or end<=start: raise PipelineError('La investigación no devolvió JSON válido')
    try: return json.loads(raw[start:end+1])
    except json.JSONDecodeError as e: raise PipelineError('JSON mal formado en la investigación') from e

def official(url:str)->bool:
    try:
        p=urlparse(url)
        if p.scheme!='https':return False
        host=p.netloc.lower().split(':')[0].removeprefix('www.')
        return any(host==d or host.endswith('.'+d) for d in OFFICIAL_DOMAINS)
    except (TypeError,ValueError):return False

def verify_brief(d:dict)->None:
    """Puerta automática MINIMA: URLs válidas y trazabilidad. NO sustituye verificación humana."""
    if not isinstance(d,dict):raise PipelineError('Datos incorrectos')
    items=d.get('candidates',[])
    if not isinstance(items,list) or len(items)!=5:raise PipelineError('Se necesitan exactamente cinco ideas investigadas')
    sel=d.get('selected')
    if not isinstance(sel,dict):raise PipelineError('Falta tema seleccionado')
    urls=sel.get('sources',[])
    if len(set(urls))<2 or not any(official(x) for x in urls):
        raise PipelineError('Se requieren 2 fuentes diferentes y al menos una fuente oficial')
    if not isinstance(sel.get('voice_script'),str) or not 250<=len(sel['voice_script'])<=1400:
        raise PipelineError('Guion fuera del rango para un Short')
    scenes=sel.get('scenes')
    if not isinstance(scenes,list) or not 5<=len(scenes)<=9:
        raise PipelineError('Se requieren entre cinco y nueve escenas')
    for i,sc in enumerate(scenes):
        if sc.get('concept') not in CONCEPTS: raise PipelineError(f'Concepto inválido en escena {i+1}')
        for k in ('headline','caption','insight'):
            if not isinstance(sc.get(k),str) or not sc[k].strip():raise PipelineError(f'Falta {k} de escena {i+1}')
            if len(sc[k])>90:raise PipelineError(f'Texto demasiado largo en escena {i+1}: {k}')
    if sel.get('positions_are_verified') is True:
        raise PipelineError('La producción automatizada no acepta coordenadas de partido exactas autodeclaradas')
    if not isinstance(sel.get('verification_notes'),str) or not sel['verification_notes'].strip():
        raise PipelineError('Faltan advertencias de verificación')

SYSTEM_PROMPT = '''Eres editor de análisis táctico periodístico en español de México. Debes producir EXACTAMENTE cinco ideas recientes cubriendo las cinco grandes ligas europeas, UCL, y cuando exista una historia relevante, segundas divisiones. Investiga en la web fuentes primarias/oficiales y fuentes adicionales; no inventes partidos, horarios, entrenadores, marcadores, frases, números, flechas ni xG. Prefiere una idea reciente con datos verificados y potencial didáctico. Habla con lenguaje mexicano relajado, serio y cercano, sin gritos ni sensacionalismo. Cada pieza debe explicar un solo mecanismo (presión, balón parado, pérdida, rebote, bloque, transición), y reconocer límites de evidencia. IMPORTANTE: NO has tenido acceso automático al tracking de los jugadores ni a la grabación completa, así que jamás afirmes coordenadas exactas ni reconstrucciones. No dependas de metraje con derechos de TV, música sin licencia o logos de tercero.
Devuelve SOLO un objeto JSON válido con esta forma exacta:
{ "candidates": [ {"title":"...", "competition":"...", "reason":"...", "source_urls":["https://...","https://..."]} x5 ], "selected": { "title":"...", "match":"...", "date":"YYYY-MM-DD", "score":"...", "voice_script":"texto completo 550-1000 caracteres, español natural", "sources":["https://...","https://..."], "verification_notes":"qué falta comprobar con video completo", "positions_are_verified":false, "scenes":[{"concept":"intro|presion|transicion|balon_parado|rebote|tercer_hombre|bloque|comparacion|cierre", "headline":"<25 caracteres", "caption":"<55 caracteres", "insight":"<50 caracteres", "label":"MINUTO / IDEA"} x6-8] } }
El guion debe ser autocontenido y describir con fidelidad cada hecho. Esquematiza movimientos como HIPÓTESIS didáctica, no como secuencia exacta de un partido. Si no encuentras hechos verificables, devuelve un mensaje de error válido en vez de inventar, no avances al video.'''

def research()->dict:
    if not os.getenv('OPENAI_API_KEY'):
        raise PipelineError('Falta OPENAI_API_KEY. No hay investigación automática verificable.')
    try: from openai import OpenAI
    except ImportError as e: raise PipelineError('Instala requirements.txt') from e
    # Un solo ciclo de investigación con búsqueda web.
    client=OpenAI()
    result=client.responses.create(
       model=os.getenv('OPENAI_MODEL','gpt-5.4-mini'),
       tools=[{'type':'web_search'}],
       tool_choice='required',
       instructions=SYSTEM_PROMPT,
       input=(f'Investiga hoy, {dt.datetime.now(dt.timezone.utc).date().isoformat()}, cinco temas de fútbol europeo y selecciona el que más merezca un Short de 45-75 segundos. Solo JSON.'),
    )
    data=json_obj(result.output_text)
    verify_brief(data)
    return data

def demo_brief()->dict:
    base=ROOT/'examples'/'psg_borrador.json'
    return json.loads(base.read_text(encoding='utf8'))

# No se venden posiciones ficticias como reales: los diagramas siempre son ilustrativos.
ATTACK=[[0.50,0.83,'5'],[0.26,0.70,'3'],[0.76,0.70,'2'],[0.46,0.62,'8'],[0.25,0.46,'11'],[0.78,0.43,'7'],[0.52,0.34,'9']]
DEFENSE=[[0.24,0.26,'4'],[0.42,0.26,'5'],[0.60,0.26,'6'],[0.78,0.26,'2'],[0.28,0.40,'11'],[0.45,0.40,'8'],[0.61,0.40,'6'],[0.78,0.40,'7']]

def scene_diagram(concept):
    a=copy.deepcopy(ATTACK);d=copy.deepcopy(DEFENSE)
    arrows=[];focus=[];ball=(0.50,0.83)
    if concept=='presion':
        a[3][:2]=[0.49,0.47];a[6][:2]=[0.55,0.27]
        arrows=[{'from':[0.52,0.34],'to':[0.55,0.27],'kind':'run'},
                {'from':[0.48,0.55],'to':[0.55,0.37],'kind':'run'}]
        focus=['8','9']; ball=(0.55,0.35)
    elif concept in ('transicion','tercer_hombre'):
        a[5][:2]=[0.87,0.30];a[3][:2]=[0.52,0.55]
        arrows=[{'from':[0.50,0.83],'to':[0.52,0.55],'kind':'pass'},
                {'from':[0.52,0.55],'to':[0.87,0.30],'kind':'pass'}]
        focus=['7','8'];ball=(0.52,0.55)
    elif concept=='balon_parado':
        ball=(0.12,0.12)
        arrows=[{'from':[0.12,0.12],'to':[0.50,0.25],'kind':'pass'}];focus=['9']
    elif concept=='rebote':
        ball=(0.55,0.25)
        arrows=[{'from':[0.56,0.45],'to':[0.55,0.25],'kind':'pass'}];focus=['9']
    elif concept=='bloque':focus=['8']
    elif concept in ('comparacion','cierre'):
        focus=['8','9'];arrows=[{'from':[0.5,0.83],'to':[0.46,0.62],'kind':'pass'}]
    return {'attack':a,'defense':d,'arrows':arrows,'focus':focus,'ball':ball}

def audio_length(file:Path)->float:
    x=subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=noprint_wrappers=1:nokey=1',str(file)],text=True)
    return float(x.strip())

def plan_story(data:dict,audio_seconds:float|None=None)->dict:
    s=data['selected']
    # Audio measurement (when present) determines the total timeline; no voice time stretching.
    count=len(s['scenes'])
    total=audio_seconds if audio_seconds is not None else max(18,min(75,len(s['voice_script'])/14.5))
    total=max(8,float(total))
    weights=[1.0 for _ in s['scenes']]
    weights[0]=0.9;weights[-1]=0.85
    z=sum(weights)
    scenes=[]
    for i,sc in enumerate(s['scenes']):
        concept=sc['concept']; base=scene_diagram(concept)
        scenes.append({**base,'duration':total*weights[i]/z,'label':sc.get('label',concept.upper()),
                       'headline':sc['headline'].upper(), 'caption':sc['caption'].upper(),
                       'insight':sc['insight'].upper()})
    return {
      'project_name':'LABORATORIO TÁCTICO',
      'video_title':s['title'][:32].upper(),
      'format':'shorts_9_16',
      'verified_match':False,  # no tracking o video completo verificado por humanos
      'sources':s['sources'],
      'narration':s['voice_script'],
      'disclaimer':'ILUSTRACIÓN · POSICIONES NO EXACTAS',
      'teams':{'attack':'AZUL · ATAQUE','defense':'AMARILLO · DEFENSA'},
      'scenes':scenes,
    }

def get_audio(text:str,out:Path)->dict:
    """Una sola solicitud al servicio de voz, si el usuario configura pago y token."""
    if not os.getenv('HEYGEN_API_KEY'):raise PipelineError('Falta HEYGEN_API_KEY para usar a Emiliano')
    if os.getenv('GENERACION_PAGADA_AUTORIZADA')!='SI':
        raise PipelineError('Producción detenida: GENERACION_PAGADA_AUTORIZADA no es SI')
    import requests
    # Emiliano usa el motor predeterminado de su voz. No sustituir sin autorización.
    url=os.getenv('HEYGEN_TTS_URL','https://api.heygen.com/v1/audio/text_to_speech')
    payload={'text':text,'voice_id':os.getenv('HEYGEN_VOICE_ID',DEFAULT_VOICE),'speed':1.0}
    resp=requests.post(url,headers={'X-Api-Key':os.environ['HEYGEN_API_KEY']},json=payload,timeout=180)
    if not resp.ok:raise PipelineError(f'Error de voz HeyGen ({resp.status_code}): revisar cuenta/voz/plan')
    value=resp.json()
    blob=value.get('data',value)
    audio_url=blob.get('audio_url') or blob.get('audioUrl') or blob.get('url')
    if not audio_url:raise PipelineError('La API de voz no proporcionó URL de audio; no se rehace la solicitud')
    u=urlparse(audio_url)
    if u.scheme!='https':raise PipelineError('Enlace de audio no HTTPS')
    voice=requests.get(audio_url,timeout=90)
    voice.raise_for_status()
    out.write_bytes(voice.content)
    return {'duration':audio_length(out),'word_timestamps':blob.get('word_timestamps')}

def timecode_srt(v:float)->str:
    n=int(round(v*1000));h=n//3600000;m=(n//60000)%60;s=(n//1000)%60;ms=n%1000
    return f'{h:02}:{m:02}:{s:02},{ms:03}'

def make_subtitles(text:str,seconds:float,out:Path):
    """SRT por grupos de palabras, con tiempos estimados (no alineación acústica)."""
    # El tiempo estimado no se presenta como alineación exacta.
    words=text.split();blocks=[words[i:i+6] for i in range(0,len(words),6)]
    lens=[max(1,sum(len(w) for w in b)) for b in blocks]
    total=sum(lens); at=0.; lines=[]
    for i,(w,n) in enumerate(zip(blocks,lens),1):
        end=seconds if i==len(blocks) else at+seconds*n/total
        end=max(at+0.12,end)
        lines += [str(i),f'{timecode_srt(at)} --> {timecode_srt(end)}',' '.join(w),'']
        at=end
    out.write_text('\n'.join(lines),encoding='utf8')

def run_render(story_path:Path,video:Path,audio:Path|None,size:str,fps:int):
    cmd=[sys.executable,str(ROOT/'src'/'render.py'),'--project',str(story_path),
       '--output',str(video),'--size',size,'--fps',str(fps)]
    if audio:cmd+=['--voice',str(audio)]
    subprocess.run(cmd,check=True)

def mux_subs(video:Path,subtitle:Path):
    """Subtítulos incrustados si FFmpeg incluye libass, sin marcas de agua."""
    tmp=video.with_name(video.stem+'_subtitled.mp4')
    cmd=['ffmpeg','-y','-v','error','-i',str(video),'-vf',f"subtitles={subtitle}:force_style='FontName=DejaVu Sans,FontSize=17,PrimaryColour=&H00FFFFFF,OutlineColour=&H00112538,BorderStyle=1,Outline=2,Shadow=0,Alignment=2,MarginV=220'",
         '-c:v','libx264','-preset','veryfast','-crf','21','-c:a','copy','-movflags','+faststart',str(tmp)]
    subprocess.run(cmd,check=True)
    tmp.replace(video)

def main()->int:
    p=argparse.ArgumentParser(description='Pipeline Shorts automatizado sin marca de agua')
    p.add_argument('--mode',choices=['demo','full'],default='demo')
    p.add_argument('--size',default=None)
    p.add_argument('--fps',type=int,default=30)
    p.add_argument('--voice-file',type=Path,default=None)
    p.add_argument('--output-dir',type=Path,default=ROOT/'output')
    p.add_argument('--skip-subtitles',action='store_true')
    p.add_argument('--youtube-private',action='store_true',help='Subir solo como privado si hay OAuth configurado')
    opts=p.parse_args()
    od=opts.output_dir;od.mkdir(parents=True,exist_ok=True)
    if opts.mode=='full':
        if os.getenv('GENERACION_PAGADA_AUTORIZADA')!='SI':
            raise PipelineError('Falta autorización de gasto recurrente (GENERACION_PAGADA_AUTORIZADA=SI). Se evita cargo.')
        data=research()
        verify_brief(data)
    else:
        data=demo_brief();verify_brief(data)
    (od/'investigacion_5_ideas.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8')
    selected=data['selected']
    narration=selected['voice_script']
    (od/'narracion.txt').write_text(narration,encoding='utf8')
    sound=opts.voice_file
    if sound is None and opts.mode=='full':
        sound=od/'emiliano.wav'
        get_audio(narration,sound)
    if sound and not sound.exists():raise PipelineError(f'No existe audio: {sound}')
    duration=audio_length(sound) if sound else None
    story=plan_story(data,duration)
    story_path=od/'story.json';story_path.write_text(json.dumps(story,ensure_ascii=False,indent=2),encoding='utf8')
    (od/'FUENTES_Y_REVISION.txt').write_text('TÍTULO: '+selected['title']+'\n\nFUENTES:\n'+'\n'.join(selected['sources'])+'\n\nPENDIENTE VERIFICAR:\n'+selected['verification_notes']+'\n\nAVISO: las pizarras son ejemplos didácticos; no reproducciones exactas.\n',encoding='utf8')
    size=opts.size or ('1080x1920' if opts.mode=='full' else '360x640')
    video=od/'short_sin_marca.mp4'
    run_render(story_path,video,sound,size,opts.fps)
    if sound:
        subs=od/'subtitulos.srt';make_subtitles(narration,duration,subs)
        if not opts.skip_subtitles:mux_subs(video,subs)
    (od/'descripcion_youtube.txt').write_text(f"{selected['title']}\n\n¿Tú cómo lo viste?\n\nFuentes:\n"+'\n'.join(selected['sources'])+"\n\nGráficos ilustrativos. Las posiciones no representan tracking real.\n#Futbol #Tactica #Shorts\n",encoding='utf8')
    if opts.youtube_private:
        subprocess.run([sys.executable,str(ROOT/'src'/'upload_private_youtube.py'),str(video),str(od/'descripcion_youtube.txt')],check=True)
    print(f'OK: {video} | {audio_length(sound) if sound else "sin voz"} | renderizado sin marca de agua')
    return 0

if __name__=='__main__':
    try:sys.exit(main())
    except PipelineError as exc:
        print('DETENIDO CON SEGURIDAD:',exc,file=sys.stderr)
        sys.exit(2)
