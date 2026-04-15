"""Platform-specific deployment generators."""

from zork.deploy.platforms.docker import DockerGenerator
from zork.deploy.platforms.fly import FlyGenerator
from zork.deploy.platforms.railway import RailwayGenerator
from zork.deploy.platforms.render import RenderGenerator

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
