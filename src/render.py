#!/usr/bin/env python3
"""Generador 9:16 de pizarras tácticas animadas. Dependencias: Pillow y ffmpeg.

Ejemplos:
  python render.py --project story.json --output salida.mp4 --size 720x1280
  python render.py --project story.json --output final.mp4 --size 1080x1920 --voice narracion.mp3
"""
import argparse, json, math, subprocess, shutil, os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

BG=(9,16,30); BG2=(14,29,42); WHITE=(244,248,249); MUTED=(160,177,192)
BLUE=(86,213,246); GOLD=(255,189,88); MINT=(191,252,143); RED=(255,114,117)
FONT_BOLD = [
    '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
    '/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf',
    'C:/Windows/Fonts/arialbd.ttf',
    '/System/Library/Fonts/Supplemental/Arial Bold.ttf',
    'DejaVuSans-Bold.ttf', 'arialbd.ttf'
]
FONT_NORMAL = [
    '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
    '/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf',
    'C:/Windows/Fonts/arial.ttf',
    '/System/Library/Fonts/Supplemental/Arial.ttf',
    'DejaVuSans.ttf', 'arial.ttf'
]

def font(size, bold=True):
    for path in (FONT_BOLD if bold else FONT_NORMAL):
        try: return ImageFont.truetype(path,max(10,int(size)))
        except OSError: pass
    raise RuntimeError('Falta una fuente TrueType (DejaVuSans o Arial). Instala una fuente de sistema.')

def ease(v):
    x=max(0,min(1,v)); return x*x*(3-2*x)

def lerp(a,b,t): return a+(b-a)*t

def rgbmix(a,b,t): return tuple(int(lerp(x,y,t)) for x,y in zip(a,b))

def centertext(draw,xy,txt,f,fill,anchor='mm'):
    draw.text(xy,txt,font=f,fill=fill,anchor=anchor,stroke_width=0)

def rounded(draw, rect, radius, fill, outline=None, width=1):
    draw.rounded_rectangle(tuple(int(v) for v in rect),radius=int(radius),fill=fill,outline=outline,width=width)

def line_arrow(draw, p1, p2, color, width, progress, dashed=False):
    progress=ease(progress)
    ax,ay=p1; bx,by=p2
    x2=lerp(ax,bx,progress); y2=lerp(ay,by,progress)
    if dashed:
      n=12
      for i in range(n):
        s0=i/n;s1=min(1,(i+.58)/n)
        if s0>progress:break
        s1=min(s1,progress)
        draw.line((lerp(ax,bx,s0),lerp(ay,by,s0),lerp(ax,bx,s1),lerp(ay,by,s1)),fill=color,width=width)
    else: draw.line((ax,ay,x2,y2),fill=color,width=width,joint='curve')
    if progress>.17:
      ang=math.atan2(by-ay,bx-ax)
      al=max(9,width*3.0)
      l=(x2-al*math.cos(ang-.44),y2-al*math.sin(ang-.44))
      r=(x2-al*math.cos(ang+.44),y2-al*math.sin(ang+.44))
      draw.polygon([(x2,y2),l,r],fill=color)


def render_frame(story,t,W,H):
    scale=W/720.0
    def S(x):return int(x*scale)
    def f(size):return font(S(size))
    im=Image.new('RGB',(W,H),BG)
    draw=ImageDraw.Draw(im)
    # subtle background strips
    for i in range(0,W,S(36)):
      draw.line((i,0,i,H),fill=(12,23,37),width=1)
    draw.rounded_rectangle((S(30),S(32),W-S(30),S(74)),radius=S(16),fill=(20,38,50))
    draw.ellipse((S(46),S(49),S(56),S(59)),fill=MINT)
    draw.text((S(66),S(54)),story.get('project_name','LABORATORIO TÁCTICO'),font=f(16),fill=WHITE,anchor='lm')
    draw.text((W-S(49),S(54)),'09:16   /   LAB',font=f(11),fill=MUTED,anchor='rm')
    # stage determination
    elapsed=0; idx=0
    scenes=story['scenes']
    for j,s in enumerate(scenes):
      if t < elapsed+s['duration'] or j==len(scenes)-1:idx=j;break
      elapsed+=s['duration']
    scene=scenes[idx]
    local=t-elapsed
    duration=scene['duration']
    entry=ease(min(1,local/0.5))
    head=scene['headline']
    def fitfont(msg, start, bound):
      size=start
      while size>10 and draw.textbbox((0,0),msg,font=f(size))[2]>bound:
        size-=1
      return f(size)
    draw.text((S(39),S(126)),story['video_title'],font=fitfont(story['video_title'],24,W-S(78)),fill=MUTED,anchor='lm')
    draw.text((S(38),S(200)),head,font=fitfont(head,41,W-S(80)),fill=WHITE,anchor='lm')
    draw.text((S(40),S(259)),scene['label'],font=fitfont(scene['label'],17,W-S(80)),fill=MINT,anchor='lm')
    # bottom of clip progress + series marker
    track=(S(40),S(310),W-S(40),S(316))
    rounded(draw,track,S(3),(47,67,82))
    total=sum(z['duration'] for z in scenes)
    rounded(draw,(track[0],track[1],max(track[0]+S(6),track[0]+int((track[2]-track[0])*min(t/total,1))),track[3]),S(3),MINT)
    pitch=(S(52),S(343),W-S(52),S(1040))
    px,py,pr,pb=pitch
    pw,ph=pr-px,pb-py
    rounded(draw,(px-S(6),py-S(6),pr+S(6),pb+S(6)),S(20),(26,51,64))
    rounded(draw,pitch,S(14),(18,73,65))
    for n in range(10):
       if n%2==0:
         y1=py+int(n*ph/10);y2=py+int((n+1)*ph/10)
         draw.rectangle((px+S(2),y1,pr-S(2),y2),fill=(18,80,71))
    lc=(161,210,193);lw=max(2,S(2))
    mx=int((px+pr)/2);my=int((py+pb)/2)
    draw.rectangle((px+S(24),py+S(22),pr-S(24),pb-S(22)),outline=lc,width=lw)
    draw.line((px+S(24),my,pr-S(24),my),fill=lc,width=lw)
    R=S(75)
    draw.ellipse((mx-R,my-R,mx+R,my+R),outline=lc,width=lw)
    draw.ellipse((mx-S(4),my-S(4),mx+S(4),my+S(4)),fill=lc)
    draw.rectangle((mx-S(118),py+S(22),mx+S(118),py+S(116)),outline=lc,width=lw)
    draw.rectangle((mx-S(118),pb-S(116),mx+S(118),pb-S(22)),outline=lc,width=lw)
    draw.rectangle((mx-S(56),py+S(22),mx+S(56),py+S(50)),outline=lc,width=lw)
    draw.rectangle((mx-S(56),pb-S(50),mx+S(56),pb-S(22)),outline=lc,width=lw)
    def pp(pos):return (px+int(pos[0]*pw),py+int(pos[1]*ph))
    prev=scenes[max(0,idx-1)]
    # look up previous position by jersey number
    def roster_map(sc, key): return {str(p[2]):p[:2] for p in sc[key]}
    def interpolate_positions(key):
      old=roster_map(prev,key);new=roster_map(scene,key)
      blend=ease(min(1,local/1.3)) if idx else 1
      return {k:(lerp(old.get(k,v)[0],v[0],blend),lerp(old.get(k,v)[1],v[1],blend)) for k,v in new.items()}
    a=interpolate_positions('attack');d=interpolate_positions('defense')
    # shade focus zone, oriented around current highlighted attacking players
    for num in scene.get('focus',[]):
      if num in a:
         x,y=pp(a[num]);rad=S(36)
         draw.ellipse((x-rad,y-rad,x+rad,y+rad),outline=MINT,width=S(2))
    # passes and runs
    for ar in scene.get('arrows',[]):
      typ=ar['kind'];color=MINT if typ=='pass' else (128,239,255) if typ=='run' else RED
      line_arrow(draw,pp(ar['from']),pp(ar['to']),color,S(5),max(0,min(1,(local-.5)/1.8)),dashed=(typ!='pass'))
    # player markers
    def marker(pos, number, color):
      x,y=pp(pos);r=S(17)
      draw.ellipse((x-r-S(2),y-r-S(2),x+r+S(2),y+r+S(2)),fill=(7,24,34))
      draw.ellipse((x-r,y-r,x+r,y+r),fill=color,outline=WHITE,width=max(1,S(1)))
      centertext(draw,(x,y+S(1)),number,f(15),(6,19,28))
    for num,pos in d.items():marker(pos,num,GOLD)
    for num,pos in a.items():marker(pos,num,BLUE)
    # ball slides from last scene to target during scene entry
    if scene.get('ball'):
      pstart=prev.get('ball',scene['ball']);pend=scene['ball'];tt=ease(min(1,local/1.5))
      bx,by=pp((lerp(pstart[0],pend[0],tt),lerp(pstart[1],pend[1],tt)))
      rad=S(8);draw.ellipse((bx-rad,by-rad,bx+rad,by+rad),fill=WHITE,outline=BG,width=max(1,S(2)))
    # icon labels directly under pitch
    draw.ellipse((S(42),S(1065),S(57),S(1080)),fill=BLUE)
    draw.text((S(64),S(1074)),story['teams']['attack'],font=f(12),fill=MUTED,anchor='lm')
    draw.ellipse((S(388),S(1065),S(403),S(1080)),fill=GOLD)
    draw.text((S(410),S(1074)),story['teams']['defense'],font=f(12),fill=MUTED,anchor='lm')
    # caption card
    rounded(draw,(S(36),S(1110),W-S(36),S(1204)),S(18),(20,37,52))
    draw.rounded_rectangle((S(36),S(1110),S(41),S(1204)),radius=S(2),fill=MINT)
    draw.text((S(58),S(1138)),scene['insight'],font=fitfont(scene['insight'],14,W-S(100)),fill=MINT,anchor='lm')
    # split long allcaps caption into lines
    caption=scene['caption'];cfont=f(18)
    maxw=W-S(110);words=caption.split(); lines=[];cur=''
    for word in words:
      cand=(cur+' '+word).strip()
      if draw.textbbox((0,0),cand,font=cfont)[2] > maxw and cur:
        lines.append(cur);cur=word
      else:cur=cand
    if cur:lines.append(cur)
    for k,v in enumerate(lines[:2]):draw.text((S(58),S(1170+k*22)),v,font=cfont,fill=WHITE,anchor='lm')
    draw.text((S(40),S(1238)),story.get('disclaimer',''),font=fitfont(story.get('disclaimer',''),10,W-S(115)),fill=(129,147,158),anchor='lm')
    draw.text((W-S(40),S(1238)),f'{idx+1:02}/{len(scenes):02}',font=f(12),fill=MUTED,anchor='rm')
    return im

def main():
  ap=argparse.ArgumentParser()
  ap.add_argument('--project',default='story.json')
  ap.add_argument('--output',default='output/demo.mp4')
  ap.add_argument('--size',default='720x1280')
  ap.add_argument('--fps',type=int,default=24)
  ap.add_argument('--voice',default=None,help='Archivo MP3/WAV opcional de la narración IA')
  ap.add_argument('--keep-silent',action='store_true')
  ap.add_argument('--for-publication',action='store_true',help='Rechaza videos sin fuentes ni validación')
  a=ap.parse_args()
  if shutil.which('ffmpeg') is None: raise SystemExit('Falta ffmpeg en PATH')
  W,H=map(int,a.size.split('x'))
  if W/H!=9/16: raise SystemExit('Solo proporción 9:16; ej. 720x1280 o 1080x1920')
  with open(a.project,encoding='utf8') as fp: story=json.load(fp)
  if a.for_publication and (not story.get('verified_match') or not story.get('sources')):
    raise SystemExit('Faltan fuentes y validación. No se permite exportación marcada para publicación.')
  total=sum(x['duration'] for x in story['scenes'])
  frames=int(round(total*a.fps))
  dst=Path(a.output).resolve();dst.parent.mkdir(parents=True,exist_ok=True)
  silent=dst.with_name(dst.stem+'_silent.mp4') if a.voice else dst
  cmd=['ffmpeg','-y','-v','error','-f','rawvideo','-pixel_format','rgb24','-video_size',f'{W}x{H}','-framerate',str(a.fps),'-i','-','-an','-c:v','libx264','-preset','veryfast','-crf','22','-pix_fmt','yuv420p','-movflags','+faststart',str(silent)]
  proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
  try:
    for i in range(frames):
      proc.stdin.write(render_frame(story,i/a.fps,W,H).tobytes())
    proc.stdin.close()
    err=proc.stderr.read();rc=proc.wait()
    if rc: raise RuntimeError(err.decode('utf8','replace'))
  finally:
    if proc.poll() is None:proc.kill()
  if a.voice:
    # Keep the speaker's speed unchanged; don't trim words or force a faster voice.
    audio=Path(a.voice).resolve()
    if not audio.exists():raise FileNotFoundError(audio)
    # Preserve the full speech and video; do not speed up, crop, or truncate narration.
    probe=['ffprobe','-v','error','-show_entries','format=duration','-of','default=noprint_wrappers=1:nokey=1',str(audio)]
    voice_seconds=float(subprocess.check_output(probe,text=True).strip())
    target=max(total,voice_seconds)
    extra=max(1.0,voice_seconds-total+1)
    cmd=['ffmpeg','-y','-v','error','-i',str(silent),'-i',str(audio),
         '-filter_complex',f'[0:v]tpad=stop_mode=clone:stop_duration={extra:.3f}[v];[1:a]apad[a]',
         '-map','[v]','-map','[a]','-t',f'{target:.3f}',
         '-c:v','libx264','-preset','veryfast','-crf','22','-c:a','aac','-b:a','192k',
         '-ar','48000','-pix_fmt','yuv420p','-movflags','+faststart',str(dst)]
    subprocess.run(cmd,check=True)
    if not a.keep_silent:silent.unlink()
  print(f'OK {dst} | {total:.1f}s de animación | {W}x{H} | {a.fps} fps')

if __name__=='__main__':main()