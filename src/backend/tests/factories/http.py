from core.http.errors import ApiError, ApiErrorDetail
from polyfactory.factories.pydantic_factory import ModelFactory


class ApiErrorDetailFactory(ModelFactory[ApiErrorDetail]):
    __model__ = ApiErrorDetail


class ApiErrorFactory(ModelFactory[ApiError]):
    __model__ = ApiError
