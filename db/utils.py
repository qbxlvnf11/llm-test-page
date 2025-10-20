from fastapi.requests import Request
from fastapi import FastAPI, HTTPException, Depends

import sqlalchemy
from sqlalchemy.engine import Engine, Row
from sqlalchemy.exc import SQLAlchemyError
from google.cloud.sql.connector import Connector, IPTypes
import os
from typing import List, Optional, Generator

from db.cloud_sql_database_manager import CloudSQLDatabase
from config.db import db_settings
from config.base import settings

def get_conn(request: Request) -> Generator:
    """
    요청 의존성: 요청에서 앱 상태에 저장된 CloudSQLDatabase의 engine으로부터
    Connection을 얻어 yield 하고, 사용 후 반드시 close()합니다.
    엔드포인트에서 Depends(get_conn)로 주입하여 사용하세요.
    """
    db: CloudSQLDatabase = request.app.state.cloudsql_db
    if db is None:
        raise HTTPException(status_code=500, detail="Database not initialized")
    engine = db.get_engine()
    conn = engine.connect()
    try:
        yield conn
    finally:
        try:
            conn.close()
        except Exception:
            pass

def make_db_from_env() -> CloudSQLDatabase:
    """
    환경변수에서 Cloud SQL 설정을 읽어 CloudSQLDatabase 인스턴스를 생성합니다.
    필요한 환경변수:
      - CLOUD_SQL_INSTANCE
      - DB_USER
      - DB_PASS
      - DB_NAME
      - (선택) DB_API_DRIVER (기본 "psycopg2")
      - (선택) DB_DRIVER (기본 "postgresql+psycopg2")
      - (선택) DB_IP_TYPE ("public" 또는 "private", 기본 "public")
    """
    try:
        instance = db_settings.CLOUD_SQL_INSTANCE #os.environ["CLOUD_SQL_INSTANCE"]
        user = db_settings.DB_USER #os.environ["DB_USER"]
        password = db_settings.DB_PASSWORD #os.environ["DB_PASS"]
        name = db_settings.DB_NAME #os.environ["DB_NAME"]
    except KeyError as e:
        raise RuntimeError(f"필수 DB 환경변수가 설정되어 있지 않습니다: {e}")

    db_api_driver = db_settings.DB_API_DRIVER #os.environ.get("DB_API_DRIVER", "psycopg2")
    db_driver = db_settings.DB_DRIVER #os.environ.get("DB_DRIVER", "postgresql+psycopg2")
    ip_type = IPTypes.PUBLIC if os.environ.get("DB_IP_TYPE", "public") == "public" else IPTypes.PRIVATE

    return CloudSQLDatabase(
        instance_connection_name=instance,
        db_user=user,
        db_pass=password,
        db_name=name,
        db_api_driver=db_api_driver,
        cred_path=settings.GOOGLE_APPLICATION_CREDENTIALS,
        db_driver=db_driver,
        ip_type=ip_type,
    )  