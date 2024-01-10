from dataclasses import dataclass, field
from functools import partial
from typing import Optional
from clarifai_grpc.channel.clarifai_channel import ClarifaiChannel  # type: ignore
from clarifai_grpc.grpc.api import resources_pb2, service_pb2_grpc, service_pb2  # type: ignore
from grpc import Channel  # type: ignore
from typing import Iterable
from src.utils import getenv
import asyncio


@dataclass
class Image:
    """Create an image from a url or base64 string."""

    url: Optional[str] = None
    base64: Optional[bytes] = None

    def __new__(cls, url: Optional[str] = None, base64: Optional[bytes] = None):
        if url and base64:
            raise ValueError("Cannot set both url and base64")
        if url:
            return resources_pb2.Image(url=url)
        if base64:
            return resources_pb2.Image(base64=base64)
        raise ValueError("Must set either url or base64")

    @classmethod
    def from_url(cls, url: str) -> "Image":
        return cls(url=url)

    @classmethod
    def from_base64(cls, base64: bytes) -> "Image":
        return cls(base64=base64)

    @classmethod
    def from_bytes(cls, bytes: bytes) -> "Image":
        return cls.from_base64(bytes)


def Data(
    image: Optional[resources_pb2.Image] = None, text: Optional[str] = None
) -> resources_pb2.Data:
    if image and text:
        return resources_pb2.Data(image=image, text=resources_pb2.Text(raw=text))
    if image:
        return resources_pb2.Data(image=image)
    if text:
        return resources_pb2.Data(text=resources_pb2.Text(raw=text))
    raise ValueError("Must set either image or text")


def Input(data: resources_pb2.Data) -> resources_pb2.Input:
    return resources_pb2.Input(data=data)


def Stub() -> service_pb2_grpc.V2Stub:
    channel: Channel = ClarifaiChannel.get_grpc_channel()
    stub = service_pb2_grpc.V2Stub(channel)
    return stub


def PostModelOutputsRequest(
    user_app_id: resources_pb2.UserAppIDSet,
    model_id: str,
    version_id: str,
    inputs: Iterable[resources_pb2.Input],
) -> service_pb2.PostModelOutputsRequest:
    return service_pb2.PostModelOutputsRequest(
        user_app_id=user_app_id,
        model_id=model_id,
        version_id=version_id,
        inputs=inputs,
    )


@dataclass
class AsyncClarifaiImageRecognition:
    """Process video bytes to frames and return a list of frames."""

    pat: str = field(default_factory=partial(getenv, "CLARIFAI_PAT"))
    user_id: str = field(default_factory=partial(getenv, "CLARIFAI_USER_ID"))
    app_id: str = field(default_factory=partial(getenv, "CLARIFAI_APP_ID"))
    model_id: str = field(default_factory=partial(getenv, "CLARIFAI_MODEL_ID"))
    model_version_id: str = field(
        default_factory=partial(getenv, "CLARIFAI_MODEL_VERSION_ID")
    )
    channel: Channel = field(init=False, repr=False)
    stub: service_pb2_grpc.V2Stub = field(init=False, repr=False)
    metadata: dict[str, str] = field(init=False, repr=False)
    userDataObject: resources_pb2.UserAppIDSet = field(init=False, repr=False)

    def __post_init__(self):
        self.channel = ClarifaiChannel.get_grpc_channel()
        self.stub = service_pb2_grpc.V2Stub(self.channel)
        self.metadata = {"authorization": f"Key {self.pat}"}
        self.userDataObject = resources_pb2.UserAppIDSet(
            user_id=self.user_id, app_id=self.app_id
        )

    async def analyze_image(self, image_bytes: bytes):
        """Return the best frame from a video."""
        image = Image.from_bytes(image_bytes)
        data = Data(image=image)
        input = Input(data=data)
        request = PostModelOutputsRequest(
            user_app_id=self.userDataObject,
            model_id=self.model_id,
            version_id=self.model_version_id,
            inputs=[input],
        )
        response: service_pb2.MultiOutputResponse = await asyncio.to_thread(
            self.stub.PostModelOutputs, request, metadata=tuple(self.metadata.items())
        )
        if response.status.code != 10000:
            raise Exception(f"Image Recognition Failed: {response.status.description}")
        return self.find_object_locations(response.outputs[0].data.regions)

    def find_object_locations(self, regions: list) -> list[dict]:
        """Find the bounding box coordinates of the object."""
        result = []
        for region in regions:
            location_info = {
                "top": round(region.region_info.bounding_box.top_row, 3),
                "left": round(region.region_info.bounding_box.left_col, 3),
                "bottom": round(region.region_info.bounding_box.bottom_row, 3),
                "right": round(region.region_info.bounding_box.right_col, 3),
            }
            for concept in region.data.concepts:
                object_info = {
                    "id": concept.id,
                    "name": concept.name,
                    "value": round(concept.value, 4),
                    "location": location_info,
                }
                result.append(object_info)
        return result
