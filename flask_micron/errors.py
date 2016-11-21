"""Provides exceptions used by Micron."""
import re


class MicronError(Exception):
    """The root of all Micron evil."""

    def __init__(self, caused_by, details=None):
        """Creates a new MicronError.

        Args:
            caused_by: Who is to blame for the error.
                The value must be either "server" or "client".
            details: (optional) A data structure providing details about
                the error. These details are all communicated to the client,
                so be sure not to include any sensitive information.
        """
        super(MicronError, self).__init__(self.description)
        self._details = details
        self._caused_by = None
        self.caused_by = caused_by

    @property
    def description(self):
        """A description for the error that occurred, derived from the
        error class docstring."""
        doc = type(self).__doc__
        if doc is None or doc.strip() == "":
            return "Missing docstring for error type '%s'" \
                   % type(self).__name__
        return re.sub(r'\s+', ' ', doc)

    @property
    def caused_by(self):
        """Indicates who is to blame for the error. The value for
        this property is either "server" or "client"."""
        return self._caused_by

    @caused_by.setter
    def caused_by(self, value):
        if value not in ["client", "server"]:
            raise ImplementationError(
                "The 'caused_by' value can only be 'client' or 'server', "
                "not '%s'" % value
            )
        self._caused_by = value

    @property
    def details(self):
        """A data structure providing details about the error that occurred."""
        return self._details


class MicronClientError(MicronError):
    """Base class for errors that are caused by the connecting client."""
    def __init__(self, details=None):
        super(MicronClientError, self).__init__("client", details)


class AccessDenied(MicronClientError):
    """A method was called for which the client does not have sufficient
    access rights."""


class AuthenticationRequired(MicronClientError):
    """A method was called for which authentication is required, but
    no active auth session exists for the client."""


class AuthenticationFailed(MicronClientError):
    """Username or password incorrect during authentication."""


class AuthorizationFailed(MicronClientError):
    """A method was called for which authorization is required, but
    the client does not meet the authorization criteria."""


class MicronServerError(MicronError):
    """Base class for errors that are caused by the server."""
    def __init__(self, details=None):
        super(MicronServerError, self).__init__("server", details)


class ImplementationError(MicronServerError):
    """Some code was found that is not written in accordance with the
    Micron framework requirements."""


class UnhandledException(MicronServerError):
    """During execution of a Micron method, an exception was raised
    that was not handled by the service."""
    def __init__(self, error):
        details = {
            'error_type': type(error).__name__,
            'error_message': str(error)
        }
        super(UnhandledException, self).__init__(details)
