from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os 
from sqlalchemy import text

from .api_routers import llm_test
from .api_routers import prompt
from db.utils import make_db_from_env, get_conn

def create_app() -> FastAPI:

    app = FastAPI(
        title="API Server",
        description="A simple API server for demonstration",
        version="1.0.0"
    )

    # CORS 미들웨어 설정
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  
        allow_credentials=True,
        allow_methods=["*"],  
        allow_headers=["*"],  
    )

    app.mount("/static", StaticFiles(directory="static"), name="static")

    app.include_router(llm_test.router)
    app.include_router(prompt.router)

    async def _startup() -> None:
        try:
            app.state.cloudsql_db = make_db_from_env()
            try:
                engine = app.state.cloudsql_db.get_engine()
                with engine.connect() as conn:
                    pass
            except Exception as e:
                raise RuntimeError(f"DB 연결 테스트 실패: {e}")
        except Exception as e:
            raise

    ## Shutdown: 리소스 정리
    async def _shutdown() -> None:
        db: CloudSQLDatabase = getattr(app.state, "cloudsql_db", None)
        if db:
            db.close()

    ## 등록
    app.add_event_handler("startup", _startup)
    app.add_event_handler("shutdown", _shutdown)

    @app.get("/_internal/health/db")
    def _db_health(conn = Depends(get_conn)):
        try:
            result = conn.execute(text("SELECT 1"))
            return {"ok": True}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"DB health check failed: {e}")

    return app

