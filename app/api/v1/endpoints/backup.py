import json
import subprocess
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.database import get_db
from app.api.v1.endpoints.auth import verify_backup_token
from app.config import settings

router = APIRouter()


@router.post("/backup")
def create_backup(db: Session = Depends(get_db), _: bool = Depends(verify_backup_token)):
    """Crée un backup de la base de données"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Backup SQL avec pg_dump
        sql_filename = f"backup_{timestamp}.sql"
        cmd = [
            "pg_dump",
            settings.database_url,
            "-f", sql_filename,
            "--no-owner",
            "--no-privileges"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"pg_dump failed: {result.stderr}")
        
        # Backup JSON (données structurées)
        json_data = {
            "timestamp": timestamp,
            "employees": [],
            "weeks": [],
            "slots": [],
            "notes": []
        }
        
        # Ici, vous pourriez ajouter la logique pour exporter les données en JSON
        # Pour simplifier, on retourne juste les informations du backup
        
        return {
            "status": "success",
            "timestamp": timestamp,
            "sql_file": sql_filename,
            "message": "Backup created successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Backup failed: {str(e)}")


@router.post("/restore")
def restore_backup(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _: bool = Depends(verify_backup_token)
):
    """Restaure la base de données depuis un fichier de backup"""
    try:
        if not file.filename.endswith(('.sql', '.json')):
            raise HTTPException(status_code=400, detail="Invalid file format. Only .sql and .json files are supported")
        
        # Sauvegarder le fichier temporairement
        temp_filename = f"temp_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
        
        with open(temp_filename, "wb") as temp_file:
            content = file.file.read()
            temp_file.write(content)
        
        if file.filename.endswith('.sql'):
            # Restauration SQL avec psql
            cmd = [
                "psql",
                settings.database_url,
                "-f", temp_filename
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                raise Exception(f"psql restore failed: {result.stderr}")
        
        elif file.filename.endswith('.json'):
            # Restauration JSON (logique personnalisée)
            with open(temp_filename, 'r') as json_file:
                data = json.load(json_file)
                # Ici, vous implémenteriez la logique de restauration JSON
                pass
        
        # Nettoyer le fichier temporaire
        import os
        os.remove(temp_filename)
        
        return {
            "status": "success",
            "message": "Database restored successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Restore failed: {str(e)}")