from fastapi import FastAPI, Request, HTTPException
from routes.agent_routes import router as agent_router
from routes.mission_routes import router as mission_router
from routes.report_routes import router as report_router
from contextlib import asynccontextmanager
from database.db_connection import db_connection
from logs.logger_config import logger
from fastapi.responses import JSONResponse

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info('Server up, open connection')
    db_connection.create_database()
    db_connection.create_tables()
    yield
    db_connection.close()
    logger.info('Server down')

app = FastAPI(lifespan=lifespan)


@app.middleware('http')
async def middelware(req: Request, call_next):
    logger.info(f'{req.method} {req.url.path} called')
    return await call_next(req)

@app.exception_handler(HTTPException)
def http_exception(req: Request, e: HTTPException):
    logger.error(f'{e.detail['detail']}: {e.detail['detail_id']}')
    return JSONResponse(
        status_code=e.status_code,
        content={'detail': e.detail['detail']}
    )

app.include_router(agent_router, prefix='/agents')
app.include_router(mission_router, prefix='/missions')
app.include_router(report_router, prefix='/reports')
