from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from fastapi import Request
from fastapi.exception_handlers import http_exception_handler as _http_exception_handler


class AppException(HTTPException):
    def __init__(self, status_code: int, detail: str, code: str = None):
        super().__init__(status_code=status_code, detail=detail)
        self.code = code or f"ERR_{status_code}"


class NotFoundException(AppException):
    def __init__(self, detail: str = "Recurso no encontrado"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail, code="NOT_FOUND")


class UnauthorizedException(AppException):
    def __init__(self, detail: str = "No autenticado"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail, code="UNAUTHORIZED")


class ForbiddenException(AppException):
    def __init__(self, detail: str = "No tienes permisos para esta acción"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail, code="FORBIDDEN")


class BadRequestException(AppException):
    def __init__(self, detail: str = "Solicitud inválida"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail, code="BAD_REQUEST")


class ConflictException(AppException):
    def __init__(self, detail: str = "Conflicto"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail, code="CONFLICT")


class ValidationException(AppException):
    def __init__(self, detail: str = "Error de validación"):
        super().__init__(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail, code="VALIDATION_ERROR")


def register_error_handlers(app):
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"success": False, "error": exc.detail, "code": exc.code},
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        if isinstance(exc, AppException):
            return await app_exception_handler(request, exc)
        return JSONResponse(
            status_code=exc.status_code,
            content={"success": False, "error": exc.detail, "code": f"ERR_{exc.status_code}"},
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        import logging
        logger = logging.getLogger("robolearn")
        logger.error(f"Unhandled exception: {type(exc).__name__}: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": "Error interno del servidor", "code": "INTERNAL_ERROR"},
        )
