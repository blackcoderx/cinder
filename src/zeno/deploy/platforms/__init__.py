"""Platform-specific deployment generators."""

from zeno.deploy.platforms.docker import DockerGenerator
from zeno.deploy.platforms.fly import FlyGenerator
from zeno.deploy.platforms.railway import RailwayGenerator
from zeno.deploy.platforms.render import RenderGenerator

PLATFORMS: dict[str, type] = {
    "docker": DockerGenerator,
    "railway": RailwayGenerator,
    "render": RenderGenerator,
    "fly": FlyGenerator,
}

__all__ = [
    "PLATFORMS",
    "DockerGenerator",
    "RailwayGenerator",
    "RenderGenerator",
    "FlyGenerator",
]
