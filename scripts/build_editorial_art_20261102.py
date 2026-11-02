"""Render exact editorial diagrams; no photographs or performance data implied."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

root=Path(__file__).resolve().parents[1]
font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
bold='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
for slug,title,subtitle,labels in [
    ('streaming-ai-accessibility-status-contract','LET PEOPLE SET THE PACE.','A review framework for streaming AI',('STATUS','CONTROL','RECOVERY')),
    ('static-site-migration-conversion-contract','SHIP THE WHOLE JOURNEY.','A review framework for static site migration',('PAGE','ENDPOINT','DELIVERY')),
]:
    im=Image.new('RGB',(1600,900),'#f6f6f2')
    d=ImageDraw.Draw(im)
    d.rectangle((64,65,82,95),fill='#065dff')
    d.text((101,60),'INTERFACE REPORT  /  PRODUCT SYSTEMS',font=ImageFont.truetype(bold,25),fill='#080a0d')
    d.text((64,195),title,font=ImageFont.truetype(bold,60),fill='#080a0d')
    d.text((64,290),subtitle,font=ImageFont.truetype(font,30),fill='#586377')
    for i,label in enumerate(labels):
        x=64+i*500
        d.rounded_rectangle((x,425,x+465,680),radius=24,fill='#065dff' if i==1 else '#e8f0ff')
        color='white' if i==1 else '#065dff'
        d.text((x+32,460),f'0{i+1}',font=ImageFont.truetype(font,30),fill=color)
        d.text((x+32,570),label,font=ImageFont.truetype(bold,40),fill=color)
    d.text((64,790),'ORIGINAL EDITORIAL FRAMEWORK  /  NOVEMBER 2026',font=ImageFont.truetype(font,23),fill='#586377')
    im.save(root/'assets'/f'{slug}.png',optimize=True)
