import docker
import tempfile
import os
import asyncio
from typing import Optional

class CodeExecutor:
    _client: Optional[docker.DockerClient] = None

    def __init__(self, image: str = "python:3.11-slim", memory_limit: str = "64m", cpu_limit: float = 0.5, timeout: int = 10):
        self.image = image
        self.memory_limit = memory_limit
        self.cpu_limit = cpu_limit
        self.timeout = timeout

    def _get_client(self) -> docker.DockerClient:
        if self._client is None:
            self._client = docker.from_env()
        return self._client

    async def execute(self, code: str, stdin: str = "") -> dict:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._execute_sync, code)

    def _execute_sync(self, code: str) -> dict:
        import requests
        import uuid

        client = self._get_client()
        container_id = None

        try:
            container = client.containers.run(
                self.image,
                ["python", "-c", code],
                mem_limit=self.memory_limit,
                cpu_quota=int(self.cpu_limit * 100000),
                network_disabled=True,
                read_only=True,
                security_opt=["no-new-privileges:true"],
                cap_drop=["ALL"],
                detach=True,
                remove=False,
            )
            container_id = container.id

            result = container.wait(timeout=self.timeout)
            stdout_b = container.logs(stdout=True, stderr=False)
            stderr_b = container.logs(stdout=False, stderr=True)

            return {
                "stdout": stdout_b.decode("utf-8", errors="replace"),
                "stderr": stderr_b.decode("utf-8", errors="replace"),
                "exit_code": result["StatusCode"],
                "timed_out": False,
            }
        except requests.exceptions.ReadTimeout:
            if container_id:
                try:
                    c = client.containers.get(container_id)
                    c.kill()
                    c.remove(force=True)
                except Exception as e:
                    import logging
                    logging.getLogger("robolearn").warning(f"Error cleaning up timed-out container: {e}")
            return {"stdout": "", "stderr": "Timeout: el código tardó demasiado en ejecutarse", "exit_code": -1, "timed_out": True}
        except docker.errors.DockerException as e:
            return {"stdout": "", "stderr": f"Error del sandbox: {str(e)}", "exit_code": -1, "timed_out": False}
        except Exception as e:
            return {"stdout": "", "stderr": f"Error inesperado: {str(e)}", "exit_code": -1, "timed_out": False}
        finally:
            if container_id:
                try:
                    c = client.containers.get(container_id)
                    c.remove(force=True)
                except Exception as e:
                    import logging
                    logging.getLogger("robolearn").warning(f"Error removing container {container_id}: {e}")

    def close(self):
        if self._client:
            self._client.close()
            self.__class__._client = None
