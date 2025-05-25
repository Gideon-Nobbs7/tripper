from fastapi import HTTPException, status


class GeocodeError(HTTPException):
    def __init__(self, detail: str = "Zero coordinates returned. Be specific about your location"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)
