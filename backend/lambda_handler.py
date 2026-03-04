from mangum import Mangum

from backend.src.main import app

handler = Mangum(app, lifespan="off")
