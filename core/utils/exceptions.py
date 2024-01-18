class ValidationError(Exception):
    """
    Exception raised when a validation fails.

    Attributes:
        message (str): explanation of the error
        status_code (int): HTTP status code to return
    """

    def __init__(self, message: str, status_code: int = 400) -> None:
        """
        Initialize the ValidationError.

        Args:
            message (str): explanation of the error
            status_code (int): HTTP status code to return
        """
        super().__init__(message)
        self.message = message
        self.status_code = status_code
