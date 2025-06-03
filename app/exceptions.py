from fastapi import HTTPException, status


class UrlsException(HTTPException):
    status_code = 500
    detail = ""

    def __init__(self):
        super().__init__(status_code=self.status_code, detail=self.detail)


class CannotFindURLException(UrlsException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "URL not found"


class InactiveURLException(UrlsException):
    status_code = status.HTTP_409_CONFLICT
    detail = "URL is inactive"


class ExpiredURLException(UrlsException):
    status_code = status.HTTP_410_GONE
    detail = "URL has expired"


