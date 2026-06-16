import pytest
import asyncio
from unittest.mock import MagicMock, patch


_await = lambda c: asyncio.run(c)


class TestCodeExecutor:

    def make(self, **kwargs):
        from infrastructure.adapters.output.docker.code_executor import CodeExecutor
        return CodeExecutor(**kwargs)

    def _mock_container(self, exit_code=0, stdout="", stderr=""):
        container = MagicMock()
        container.id = "cont-123"
        container.wait.return_value = {"StatusCode": exit_code}
        def logs_side_effect(stdout=True, stderr=False):
            if stdout:
                return ("" if stdout is True else stdout).encode()
            return ("" if stderr is True else stderr).encode()
        actual_stdout = stdout
        actual_stderr = stderr
        def logs_side_effect(*, stdout=True, stderr=False):
            if stdout:
                return actual_stdout.encode()
            return actual_stderr.encode()
        container.logs.side_effect = logs_side_effect
        return container

    def _patch_docker(self, container):
        client = MagicMock()
        client.containers.run.return_value = container
        client.containers.get.return_value = container
        patcher = patch('infrastructure.adapters.output.docker.code_executor.docker.from_env',
                        return_value=client)
        return patcher

    def test_execute_success(self):
        container = self._mock_container(exit_code=0, stdout="Hello\n", stderr="")
        with self._patch_docker(container) as p:
            executor = self.make()
            result = _await(executor.execute('print("Hello")'))
            assert result["stdout"] == "Hello\n"
            assert result["stderr"] == ""
            assert result["exit_code"] == 0
            assert result["timed_out"] is False

    def test_execute_with_stderr(self):
        container = self._mock_container(exit_code=1, stdout="", stderr="Error\n")
        with self._patch_docker(container) as p:
            executor = self.make()
            result = _await(executor.execute('import sys; sys.stderr.write("Error\\n")'))
            assert result["stderr"] == "Error\n"
            assert result["exit_code"] == 1

    def test_execute_timeout(self):
        container = MagicMock()
        container.id = "cont-timeout"
        container.wait.side_effect = __import__('requests').exceptions.ReadTimeout("timeout")
        container.logs.return_value = b""

        with self._patch_docker(container):
            executor = self.make(timeout=5)
            result = _await(executor.execute('while True: pass'))
            assert result["timed_out"] is True
            assert result["exit_code"] == -1
            assert "Timeout" in result["stderr"]

    def test_execute_timeout_kill_fails(self):
        container = MagicMock()
        container.id = "cont-timeout2"
        container.wait.side_effect = __import__('requests').exceptions.ReadTimeout("timeout")
        container.logs.return_value = b""
        client = MagicMock()
        client.containers.run.return_value = container
        client.containers.get.side_effect = Exception("container gone")

        with patch('infrastructure.adapters.output.docker.code_executor.docker.from_env',
                   return_value=client):
            executor = self.make(timeout=5)
            result = _await(executor.execute('while True: pass'))
            assert result["timed_out"] is True
            assert result["exit_code"] == -1

    def test_execute_docker_exception(self):
        client = MagicMock()
        client.containers.run.side_effect = __import__('docker').errors.DockerException("no docker")
        with patch('infrastructure.adapters.output.docker.code_executor.docker.from_env',
                   return_value=client):
            executor = self.make()
            result = _await(executor.execute('print(1)'))
            assert "Error del sandbox" in result["stderr"]
            assert result["exit_code"] == -1

    def test_execute_unexpected_exception(self):
        client = MagicMock()
        client.containers.run.side_effect = RuntimeError("unexpected")
        with patch('infrastructure.adapters.output.docker.code_executor.docker.from_env',
                   return_value=client):
            executor = self.make()
            result = _await(executor.execute('print(1)'))
            assert "Error inesperado" in result["stderr"]
            assert result["exit_code"] == -1

    def test_execute_cleanup_in_finally(self):
        container = self._mock_container(exit_code=0, stdout="ok", stderr="")
        with self._patch_docker(container) as p:
            executor = self.make()
            _await(executor.execute('print("ok")'))
            container.remove.assert_called_once_with(force=True)

    def test_execute_cleanup_fails_silently(self):
        container = self._mock_container(exit_code=0, stdout="ok", stderr="")
        container.remove.side_effect = Exception("remove failed")
        with self._patch_docker(container) as p:
            executor = self.make()
            result = _await(executor.execute('print("ok")'))
            assert result["exit_code"] == 0

    def test_get_client_creates_on_first_call(self):
        with patch('infrastructure.adapters.output.docker.code_executor.docker.from_env') as m:
            client = MagicMock()
            m.return_value = client
            executor = self.make()
            c = executor._get_client()
            assert c is client
            m.assert_called_once()

    def test_get_client_reuses(self):
        with patch('infrastructure.adapters.output.docker.code_executor.docker.from_env') as m:
            client = MagicMock()
            m.return_value = client
            executor = self.make()
            c1 = executor._get_client()
            c2 = executor._get_client()
            assert c1 is c2
            m.assert_called_once()

    def test_close(self):
        with patch('infrastructure.adapters.output.docker.code_executor.docker.from_env') as m:
            client = MagicMock()
            m.return_value = client
            executor = self.make()
            executor._get_client()
            executor.close()
            client.close.assert_called_once()
            assert executor.__class__._client is None

    def test_close_no_client(self):
        executor = self.make()
        executor.close()

    def test_stdout_stderr_decoding(self):
        container = MagicMock()
        container.id = "cont-decode"
        container.wait.return_value = {"StatusCode": 0}
        container.logs.side_effect = lambda stdout=True, stderr=False: (
            b"stdout data" if stdout else b""
        )
        client = MagicMock()
        client.containers.run.return_value = container
        client.containers.get.return_value = container
        with patch('infrastructure.adapters.output.docker.code_executor.docker.from_env',
                   return_value=client):
            executor = self.make()
            result = _await(executor.execute('print(1)'))
            assert result["stdout"] == "stdout data"
