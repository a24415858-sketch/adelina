"""Create a 9:16 affirmation film using the selected female voice and generated artwork.
Run: .venv/bin/python scripts/make_muladhara_video.py
The audio is slowed without pitch shifting; existing pauses are gently extended.
"""
from pathlib import Path
import subprocess, wave, math, json
import numpy as np
from PIL import Image, ImageOps, ImageDraw, ImageFont
import imageio_ffmpeg

ROOT=Path(__file__).resolve().parents[1]
ASSETS=ROOT/'assets/muladhara'
TMP=ROOT/'.cache/muladhara'
TMP.mkdir(parents=True,exist_ok=True)
OUT=ROOT/'videos/Муладхара — моя опора.mp4'
OUT.parent.mkdir(exist_ok=True)
FF=imageio_ffmpeg.get_ffmpeg_exe()
FPS=24
RATE=24000

def run(args):
    subprocess.run([FF,'-hide_banner','-loglevel','error','-y',*map(str,args)],check=True)

parts=[]
part_lengths=[]
for i in range(1,4):
    wav=TMP/f'part-{i}.wav'
    run(['-i',ASSETS/f'voice-0{i}.mp3','-af','atempo=0.88,highpass=f=65,alimiter=limit=0.94:level=false',
         '-ar',RATE,'-ac',1,wav])
    with wave.open(str(wav)) as f:
        samples=np.frombuffer(f.readframes(f.getnframes()),dtype='<i2').copy()
    # Extend natural pauses, never cut voiced speech. Analyze 20 ms RMS windows.
    size=int(.02*RATE)
    blocks=len(samples)//size
    rms=np.sqrt(np.mean((samples[:blocks*size].reshape(-1,size).astype(float)/32768)**2,axis=1))
    quiet=rms<.003
    edges=np.diff(np.r_[False,quiet,False].astype(int))
    starts=np.flatnonzero(edges==1); ends=np.flatnonzero(edges==-1)
    cuts=[int((a+b)/2)*size for a,b in zip(starts,ends) if b-a>=14 and a>12 and b<blocks-12]
    chunks=[];previous=0
    for cut in cuts:
        chunks.extend([samples[previous:cut],np.zeros(int(.35*RATE),dtype='<i2')]);previous=cut
    chunks.append(samples[previous:])
    expanded=np.concatenate(chunks)
    # A short lead-in and breathing room between paragraphs/groups.
    lead=2.0 if i==1 else .7
    tail=3.0 if i==3 else 1.5
    final=np.concatenate([np.zeros(int(lead*RATE),dtype='<i2'),expanded,np.zeros(int(tail*RATE),dtype='<i2')])
    parts.append(final);part_lengths.append(len(final)/RATE)

samples=np.concatenate(parts)
audio=TMP/'narration.wav'
with wave.open(str(audio),'wb') as f:
    f.setnchannels(1);f.setsampwidth(2);f.setframerate(RATE);f.writeframes(samples.astype('<i2').tobytes())
DURATION=len(samples)/RATE
print(f'Voice ready: {DURATION:.2f} seconds, groups {part_lengths}',flush=True)

# Two complementary images per narration group. Captions are thematic, not subtitles.
scenes=[
 ('earth.jpg',['Муладхара'], 'МОЯ ЗЕМЛЯ · МОЯ СИЛА · МОЯ ОПОРА'),
 ('woman.jpg',['Я укоренена','в этом мире'], 'ДОВЕРИЕ К ЖИЗНИ'),
 ('mountain.jpg',['Я разрешаю себе','получать'], 'ДОСТАТОК · СТАБИЛЬНОСТЬ'),
 ('earth.jpg',['Моя опора —','внутри меня'], 'ТЕЛО — МОЙ ДОМ'),
 ('woman.jpg',['Я выбираю себя'], 'МОЙ ПУТЬ · МОЁ БЛАГОПОЛУЧИЕ'),
 ('bloom.jpg',['Я сильна.','Я наполнена жизнью.'], 'Я УКОРЕНЕНА'),
]
font_path=ROOT/'assets/CormorantGaramond.ttf'
body_path='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
# Match scene changes to narration groups, keeping two-second cross dissolves.
boundaries=[0,part_lengths[0]/2,part_lengths[0],part_lengths[0]+part_lengths[1]/2,
            sum(part_lengths[:2]),sum(part_lengths[:2])+part_lengths[2]/2,DURATION]
transition=2.0
lengths=[]
for idx,(image,lines,kicker) in enumerate(scenes):
    duration=boundaries[idx+1]-boundaries[idx]+(transition if idx<5 else 0)
    frames=math.ceil(duration*FPS)
    lengths.append(frames/FPS)
    im=ImageOps.fit(Image.open(ASSETS/image).convert('RGB'),(1080,1920),centering=(.5,.5)).convert('RGBA')
    # A smooth dark vignette behind type; avoid hard rectangular title cards.
    y=np.linspace(0,1,1920)
    alpha=np.clip((y-.48)/.48,0,1)*165
    overlay=np.zeros((1920,1080,4),dtype='uint8');overlay[:,:,:3]=[27,15,14];overlay[:,:,3]=alpha[:,None].astype('uint8')
    im=Image.alpha_composite(im,Image.fromarray(overlay))
    draw=ImageDraw.Draw(im)
    font=ImageFont.truetype(str(font_path),88 if idx!=5 else 79)
    small=ImageFont.truetype(body_path,22)
    # Generous lower safe area for social-video controls.
    line_top=1440 if len(lines)>1 else 1480
    for n,line in enumerate(lines):
        draw.text((540,line_top+n*98),line,font=font,fill='#FFF4E3',anchor='mt',stroke_width=0)
    draw.line((470,line_top-40,610,line_top-40),fill='#E6BD94',width=2)
    draw.text((540,1695),kicker,font=small,fill='#F5DDC3',anchor='mt')
    png=TMP/f'scene-{idx}.png';im.convert('RGB').save(png)
    # Slow camera move, four percent over each shot, always centered.
    zoom=f"1.0+0.04*on/{max(frames-1,1)}" if idx%2==0 else f"1.04-0.04*on/{max(frames-1,1)}"
    vf=f"scale=1440:2560,zoompan=z='{zoom}':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d={frames}:s=720x1280:fps={FPS},setsar=1"
    run(['-i',png,'-vf',vf,'-frames:v',frames,'-an','-c:v','libx264','-preset','fast','-crf',22,'-pix_fmt','yuv420p','-threads',2,TMP/f'clip-{idx}.mp4'])
    print(f'Scene {idx+1}/6 rendered ({duration:.1f}s)',flush=True)

inputs=[]
for i in range(6):inputs+=['-i',TMP/f'clip-{i}.mp4']
inputs+=['-i',audio]
filters=[f'[{i}:v]settb=AVTB,setpts=PTS-STARTPTS[v{i}]' for i in range(6)]
last='v0';elapsed=lengths[0]
for i in range(1,6):
    offset=elapsed-transition
    filters.append(f'[{last}][v{i}]xfade=transition=fade:duration={transition}:offset={offset:.6f}[mix{i}]')
    elapsed+=lengths[i]-transition;last=f'mix{i}'
filters.append(f'[{last}]fade=t=in:st=0:d=1.5,fade=t=out:st={DURATION-2:.4f}:d=2[video]')
run([*inputs,'-filter_complex_threads',1,'-filter_complex',';'.join(filters),'-map','[video]','-map','6:a',
     '-af','loudnorm=I=-18:TP=-2:LRA=9,afade=t=in:d=0.5',
     '-t',f'{DURATION:.4f}','-c:v','libx264','-preset','fast','-crf',24,'-pix_fmt','yuv420p',
     '-r',FPS,'-c:a','aac','-b:a','128k','-ar','48000','-movflags','+faststart','-threads',2,
     '-metadata','title=Муладхара — моя земля, моя сила, моя опора',OUT])
(TMP/'timing.json').write_text(json.dumps({'duration':DURATION,'parts':part_lengths,'boundaries':boundaries},indent=2))
print(f'DONE: {OUT} ({OUT.stat().st_size/1024/1024:.1f} MB)',flush=True)
