import sqlalchemy
from sqlalchemy import text
from sqlalchemy.engine import Engine, Row
from sqlalchemy.exc import SQLAlchemyError
from google.cloud.sql.connector import Connector, IPTypes
from google.auth import load_credentials_from_file
import os
from typing import List, Optional

from config.base import settings

class CloudSQLDatabase:
    """
    Google Cloud SQL 데이터베이스 연결 및 CRUD 작업을 관리하는 클래스.
    SQLAlchemy 엔진을 생성하고 사용자 데이터 관리를 위한 메서드를 제공합니다.
    """
    
    def __init__(
        self,
        instance_connection_name: str,
        db_user: str,
        db_pass: str,
        db_name: str,
        db_api_driver: str,
        cred_path: str, 
        db_driver: str = "postgresql+psycopg2",
        ip_type: IPTypes = IPTypes.PUBLIC
    ):
        """
        CloudSQLDatabase 인스턴스를 초기화합니다.

        Args:
            instance_connection_name (str): 인스턴스 연결 이름.
            db_user (str): 데이터베이스 사용자.
            db_pass (str): 데이터베이스 비밀번호.
            db_name (str): 데이터베이스 이름.
            db_api_driver (str): Cloud SQL Connector용 순수 DBAPI 드라이버 (e.g., "psycopg2").
            db_driver (str, optional): SQLAlchemy용 전체 드라이버 문자열 (e.g., "postgresql+psycopg2"). Defaults to "postgresql+psycopg2".
            ip_type (IPTypes, optional): 연결할 IP 유형. Defaults to IPTypes.PUBLIC.
        """
        self.instance_connection_name = instance_connection_name
        self.db_user = db_user
        self.db_pass = db_pass
        self.db_name = db_name
        self.db_driver = db_driver
        self.db_api_driver = db_api_driver
        self.ip_type = ip_type

        credentials, _ = load_credentials_from_file(
            cred_path, scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        self.connector = Connector(credentials=credentials)
        self.engine = self._create_engine()

        print('✅ Complete to Build Cloud SQL!')

    def _getconn(self) -> sqlalchemy.engine.base.Connection:
        """
        Cloud SQL 커넥터를 통해 새 DB 연결 객체를 가져오는 내부 함수.
        """
        # connect() 메서드는 순수한 DBAPI 드라이버 이름을 인자로 받습니다.
        conn = self.connector.connect(
            self.instance_connection_name,
            self.db_api_driver,
            user=self.db_user,
            password=self.db_pass,
            db=self.db_name,
            ip_type=self.ip_type
        )
        return conn

    def _create_engine(self) -> Engine:
        """
        SQLAlchemy 연결 풀(엔진)을 생성합니다.
        """
        # SQLAlchemy는 전체 드라이버 문자열을 사용해야 합니다.
        return sqlalchemy.create_engine(
            sqlalchemy.engine.url.URL.create(drivername=self.db_driver, query={}),
            creator=self._getconn,
        )

    def get_engine(self) -> Engine:
        """
        생성된 SQLAlchemy 엔진(연결 풀)을 반환합니다.
        """
        return self.engine

    def close(self):
        """
        Cloud SQL 커넥터 리소스를 정리합니다. 애플리케이션 종료 시 호출해야 합니다.
        """
        if self.engine:
            self.engine.dispose()
        if self.connector:
            print("Cloud SQL 커넥터 리소스를 정리합니다...")
            self.connector.close()

    def get_data(self, table_name) -> List[Row]:
        
        select_stmt = sqlalchemy.text(f"SELECT * FROM {table_name} ORDER BY id;")
        try:
            with self.engine.connect() as conn:
                result = conn.execute(select_stmt)
                return result.fetchall()
        except SQLAlchemyError as e:
            print(f"모든 사용자 조회 실패: {e}")
            return []
    
    def get_table_columns(self, table_name: str):
        """
        주어진 테이블의 컬럼 정보를 조회합니다.
        """
        query = sqlalchemy.text("""
            SELECT 
                column_name, 
                data_type, 
                is_nullable, 
                column_default
            FROM information_schema.columns
            WHERE table_schema = 'public'
            AND table_name = :table_name
            ORDER BY ordinal_position;
        """)

        try:
            with self.engine.connect() as conn:
                result = conn.execute(query, {"table_name": table_name})
                columns = result.fetchall()
                print(f"[{table_name}] 테이블의 컬럼 정보:")
                for col in columns:
                    print(f" - {col.column_name} ({col.data_type}) "
                        f"{'NULL' if col.is_nullable == 'YES' else 'NOT NULL'} "
                        f"default={col.column_default}")
                return columns
        except SQLAlchemyError as e:
            print(f"컬럼 정보 조회 실패: {e}")
            return []

    def fetch_all(self, sql: str, params: dict = None):
        # sync 엔진용 편의 메서드
        with self.engine.connect() as conn:
            res = conn.execute(text(sql), params or {})
            return [dict(r) for r in res.fetchall()]

    async def fetch_all_async(self, sql: str, params: dict = None):
        # async 엔진용 편의 메서드
        async with self.engine.connect() as conn:
            res = await conn.execute(text(sql), params or {})
            return [dict(r) for r in res.fetchall()]