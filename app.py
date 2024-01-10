"""A Socketio server to accept clips from the frontend"""

from aiohttp import web
import socketio  # type: ignore
from src.utils import getlistenv
import aiohttp_cors  # type: ignore
from src.image_recognition import AsyncClarifaiImageRecognition
from src.media_processor import AsyncVideoProcessor
from PIL import Image as PILImage  # type: ignore
from io import BytesIO


proc = AsyncVideoProcessor()
rec = AsyncClarifaiImageRecognition()

sio = socketio.AsyncServer(cors_allowed_origins=getlistenv("ALLOWED_HOSTS"))


@sio.on("connect")
def connect(sid, environ):
    print("connect ", sid)


@sio.on("disconnect")
def disconnect(sid):
    print("disconnect ", sid)


@sio.on("clip")
async def clip(sid, timestamp, blob):
    # create a file with the timestamp as the name
    # save the blob to the file
    # send the file to the model
    # send the result back to the frontend
    print("Got a clip!", timestamp, len(blob))
    await sio.send("Clip received!")
    frame = await proc.get_best_frame(blob)
    selected_image = PILImage.fromarray(frame)
    file = BytesIO()
    selected_image.save(file, format="PNG")
    file.seek(0)
    image_bytes = file.read()
    result = await rec.analyze_image(image_bytes)
    await sio.emit("recognition", [image_bytes, result])
    return True


def index(request: web.Request):
    """Serve the client-side application."""
    return web.Response(text="Hello World!")


async def create_app():
    app = web.Application()
    app.router.add_routes(
        [
            web.get("/", index),
        ]
    )
    # Configure default CORS settings.
    cors_defaults = {}
    for host in getlistenv("ALLOWED_HOSTS"):
        cors = aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
        )
        cors_defaults[host] = cors
    cors = aiohttp_cors.setup(app, defaults=cors_defaults)
    for route in list(app.router.routes()):
        cors.add(route)
    sio.attach(app)
    return app


if __name__ == "__main__":
    app = create_app()
    web.run_app(app)
