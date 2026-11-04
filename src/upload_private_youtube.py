#!/usr/bin/env python3
"""Sube MP4 a YouTube como PRIVADO, nunca pública por defecto."""
import os,sys
from pathlib import Path

def main():
    expected=('YOUTUBE_CLIENT_ID','YOUTUBE_CLIENT_SECRET','YOUTUBE_REFRESH_TOKEN')
    missing=[x for x in expected if not os.getenv(x)]
    if missing:raise SystemExit('Subida privada omitida: faltan '+', '.join(missing))
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    from google.auth.transport.requests import Request
    credentials=Credentials(token=None,refresh_token=os.getenv('YOUTUBE_REFRESH_TOKEN'),
      token_uri='https://oauth2.googleapis.com/token',client_id=os.environ['YOUTUBE_CLIENT_ID'],
      client_secret=os.environ['YOUTUBE_CLIENT_SECRET'],scopes=['https://www.googleapis.com/auth/youtube.upload'])
    credentials.refresh(Request())
    api=build('youtube','v3',credentials=credentials,cache_discovery=False)
    video=Path(sys.argv[1]);description=Path(sys.argv[2]).read_text(encoding='utf8')
    title=description.splitlines()[0][:100]
    req=api.videos().insert(part='snippet,status',body={
      'snippet':{'title':title,'description':description,'categoryId':'17','defaultLanguage':'es'},
      'status':{'privacyStatus':'private','selfDeclaredMadeForKids':False}
    },media_body=MediaFileUpload(str(video),mimetype='video/mp4',resumable=True))
    result=None
    while result is None:
       status,result=req.next_chunk()
    print('Subida privada completada (YouTube ID):',result.get('id','sin-id'))
if __name__=='__main__':main()