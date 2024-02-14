from typing import Union, Annotated

from fastapi import FastAPI, File, UploadFile

import uuid, asyncio, time, shutil, psycopg2

from datetime import datetime

from fastapi.responses import FileResponse

from fastapi.concurrency import run_in_threadpool


app = FastAPI()

def connect_bd():
    try:
        conn = psycopg2.connect(dbname='SLON', user='postgres', password='postgres', host='db-pg')
#        cursor = conn.cursor()
        return conn
    except: 
        return {"message": "Can`t establish connection to database"}




@app.get("/find/{filename}")
def find_file(filename: Union[str, None] = None):
    conn = connect_bd()
    with conn.cursor() as curs:
            curs.execute("SELECT FILE_UUID, FILENAME, UPLOAD_DATE FROM file_doc WHERE FILENAME LIKE %s", ('%'+ filename+ '%',))
            rows=curs.fetchall()
            if len(rows) >0:
                curs.close()
                return rows
            else:
                curs.close()
                return {"message": "File not found"}



@app.get("/download/{UUID}")
def find_file(UUID: Union[str, None] = None):
    conn = connect_bd()
    with conn.cursor() as curs:
            curs.execute("SELECT COUNT(*) FROM file_doc WHERE FILE_UUID LIKE %s", (UUID,))
            result=curs.fetchone()[0]
            if result == 1:
                curs.close()
                return FileResponse(path='/files/'+ UUID, media_type='application/octet-stream')
            elif result > 1:
                curs.close()
                return {"message": "More than one file has this uuid. Error"}
            else:
                curs.close()
                return {"message": "File not found"}





@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    conn = connect_bd()
    try:
        file_uuid = str(uuid.uuid4())
        f = await run_in_threadpool(open,'/files/'+ file_uuid, 'wb+')
        await run_in_threadpool(shutil.copyfileobj, file.file, f)
    except Exception:
        return {"message": "There was an error uploading the file"}
    finally:
        date=str(datetime.now())
        with conn.cursor() as curs:
            curs.execute("INSERT INTO file_doc (FILE_UUID, FILENAME, UPLOAD_DATE) VALUES (%s, %s, %s)", (file_uuid, file.filename, date))
        conn.commit()
        curs.close()
        if 'f' in locals(): await run_in_threadpool(f.close)
        await file.close()
    return {"message": f"Successfuly uploaded {file.filename} as "+ file_uuid}



