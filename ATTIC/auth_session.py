# -*- coding: utf-8 -*-
"""This module provides functionality for managing an auth session."""

from time import time
from flask import session


TTL = 1800
"""The 'time to live' for the auth session in seconds.

When the session has been inactive for this long, it will be
automatically stopped.

The inactivity timer is reset every time a successful call (i.e. passing
auth and security checks) is done to a Micron method, while an active
auth session exists.
"""

SESSION_KEY = 'fm_AS'
"""The key that is used to store the auth session data in the session.

It has no special meaning, but it is only used as a non-obvious key
to prevent conflicts with other users of the session object.
"""


def start(roles=None, details=None):
    """Starts an auth session, indicated that the client related to the
    current Flask session is to be considered authenticated.  Along with
    starting the auth session, roles and user details can be stored,
    but these are both optional.

    :param roles:
        A list of role names that apply to the user. These can be used in
        conjunction with the role=<role> argument of the ``@micron.method()``
        decorator to add role authorization to methods.
    :param details:
        An arbitrary data structure containing custom details about the
        authenticated user (e.g. a dict containing user id, username and
        display name).  This information is not used, nor required by the core
        of Micron, but it is a courtesy to the application to make it possible
        to have these data around.

    :returns:
        The stored auth session data.
    """
    data = {'roles': roles, 'details': details, 'started_at': round(time())}
    _set_new_valid_until(data)
    return _store_in_session(data)


def stop():
    """Stops the session by clearing the auth session data."""
    _store_in_session(None)


def get():
    """Retrieves the stored session data.

    :returns:
        A dict containing the currently stored auth session data or None
        when there is no started and active (i.e. not expired) auth session.
    """
    data = _load_from_session()
    if data is not None and data.get('valid_until', 0) > time():
        return data
    return None


def keep_alive():
    """Resets the expiration timer for the auth session by refreshing
    the valid_until time.

    :returns:
        None in case no active auth session exist,
        updated auth session data otherwise.
    """
    data = get()
    if data is None:
        return None
    _set_new_valid_until(data)
    return _store_in_session(data)


def _load_from_session():
    """Retrieves the auth session data from the session object.

    :returns:
        The session data or None when no data is stored.
    """
    return session.get(SESSION_KEY, None)


def _store_in_session(data):
    """Stores auth session data in the session object.

    :param data:
        The data to store in the session.

    :returns:
        The data that was stored in the session.
    """
    session[SESSION_KEY] = data
    return data


def _set_new_valid_until(data):
    data['valid_until'] = round(time()) + TTL
    data['ttl'] = TTL


def is_active():
    """Checks whether or not an auth session is active.

    :returns:
        True when an auth session is started and active.
        False when an auth session is not started or expired.
    """
    return get() is not None


def has_role(role):
    """Checks whether or not the current auth user is authorized
    for the requested role.

    :param role:
        The role to check.

    :returns:
        True in case an auth session is active and the auth user
        is authorized for the requested role.
    """
    data = get()
    return (
        data is not None and
        data['roles'] is not None and
        role in data['roles']
    )
