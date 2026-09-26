"""Helpers for API Gateway proxy events and responses."""
import json


class HttpError(Exception):
    def __init__(self, status, message):
        super().__init__(message)
        self.status = status


def current_user(event):
    """The caller's user id, as set by the API Gateway authorizer."""
    try:
        return event["requestContext"]["authorizer"]["principalId"]
    except (KeyError, TypeError):
        raise HttpError(401, "not signed in")


def query(event):
    return event.get("queryStringParameters") or {}


def json_body(event):
    try:
        return json.loads(event.get("body") or "{}")
    except json.JSONDecodeError:
        raise HttpError(400, "body must be JSON")


def respond(status, payload):
    return {
        "statusCode": status,
        "headers": {"content-type": "application/json"},
        "body": json.dumps(payload),
    }


def handles_errors(handler):
    """Turn HttpError into an error response, like the Lambda wrapper in production."""
    def wrapped(event, context):
        try:
            return handler(event, context)
        except HttpError as err:
            return respond(err.status, {"error": str(err)})
    wrapped.__name__ = handler.__name__
    return wrapped
