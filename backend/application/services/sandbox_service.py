import ast
from typing import Optional
from infrastructure.adapters.output.docker.code_executor import CodeExecutor

class SandboxService:
    def __init__(self, code_executor: Optional[CodeExecutor] = None):
        self.executor = code_executor or CodeExecutor()

    DANGEROUS_PATTERNS = [
        "import os", "from os", "import subprocess", "from subprocess",
        "import shutil", "from shutil", "import sys", "from sys",
        "__import__", "eval(", "exec(", "open(",
        "import socket", "from socket", "import requests", "from requests",
        "__builtins__", "import ctypes", "from ctypes",
    ]

    def validate_code(self, code: str) -> Optional[str]:
        for pattern in self.DANGEROUS_PATTERNS:
            if pattern in code:
                return f"Error de seguridad: '{pattern}' no está permitido"
        try:
            ast.parse(code)
        except SyntaxError as e:
            return f"Error de sintaxis: {e}"
        return None

    async def execute_code(self, code: str) -> dict:
        error = self.validate_code(code)
        if error:
            return {"stdout": "", "stderr": error, "exit_code": -1, "timed_out": False, "validation_error": True}

        result = await self.executor.execute(code)

        stderr = result.get("stderr", "")
        exit_code = result.get("exit_code", -1)
        if stderr and not result.get("timed_out"):
            pass

        return result

    async def execute_and_compare(self, code: str, expected_output: str, solution_type: str = "output", test_code: str = None) -> dict:
        code_to_run = code
        if solution_type == "test" and test_code:
            code_to_run = code + "\n\n" + test_code

        result = await self.execute_code(code_to_run)

        if result.get("validation_error"):
            return {"passed": False, "output": "", "error": result["stderr"], "score": 0}

        if result.get("timed_out"):
            return {"passed": False, "output": "", "error": result["stderr"], "score": 0}

        if result["exit_code"] != 0:
            return {"passed": False, "output": result["stdout"], "error": result["stderr"], "score": 0}

        output = result["stdout"]

        if solution_type == "output" and expected_output:
            expected = expected_output.replace("\\n", "\n").strip()
            actual = output.strip()
            passed = (expected == actual)
            score = 100.0 if passed else 0.0
        else:
            passed = True
            score = 100.0

        return {"passed": passed, "output": output, "error": None, "score": score}
