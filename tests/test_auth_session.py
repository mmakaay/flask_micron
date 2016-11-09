from time import time
from flask import session
from flask_micron import auth_session
from tests import MicronTestCase


class Tests(MicronTestCase):

    def setUp(self):
        super(Tests, self).setUp()
        auth_session.TTL = 1800

    def test_GivenNoStartedAuthSesssion_NoAuthSessionDataAvailable(self):
        auth_data = auth_session.get()
        self.assertIsNone(auth_data)

    def test_WhenStartingAuthSession_AuthSessionDataAvailable(self):
        auth_session.start()
        auth_data = auth_session.get()
        self.assertIsNotNone(auth_data)
        self.assertEqual(None, auth_data['roles'])
        self.assertEqual(None, auth_data['details'])

    def test_WhenStartingAuthSessionWithData_DataIsStoredInSession(self):
        auth_session.start(roles=['my', 'roles'], details={'username': 'john'})
        auth_data = auth_session.get()
        self.assertEqual(['my', 'roles'], auth_data['roles'])
        self.assertEqual({'username': 'john'}, auth_data['details'])

    def test_WhenStartingAuthSession_ExpiresAtAndTtlAreSet(self):
        auth_session.start()
        self.assertAlmostEqual(
            time() + auth_session.TTL,
            auth_session.get()['valid_until'],
            delta=1)

    def test_WhenStoppingStartedAuthSession_DataIsRemovedFromSession(self):
        auth_session.start()
        auth_session.stop()
        self.assertEqual(None, auth_session.get())

    def test_WhenStoppingNotStartedSession_NoExceptionIsThrown(self):
        auth_session.stop()

    def test_GivenStartedSession_GetReturnsData(self):
        auth_session.start(details='pypypy')
        data = auth_session.get()
        self.assertEqual('pypypy', data['details'])

    def test_GivenExpiredSession_GetReturnsNone(self):
        auth_session.TTL = -1
        auth_session.start()
        self.assertEqual(None, auth_session.get())

    def test_GivenStartedSession_IsActiveReturnsTrue(self):
        auth_session.start()
        self.assertTrue(auth_session.is_active())

    def test_GivenExpiredSession_IsActiveReturnsFalse(self):
        auth_session.TTL = -1
        auth_session.start()
        self.assertFalse(auth_session.is_active())

    def test_GivenActiveSession_KeepAliveUpdatesValidUntil(self):
        data = auth_session.start()
        data['valid_until'] += 100
        session[auth_session.SESSION_KEY] = data
        self.assertEqual(
            data['valid_until'],
            auth_session.get()['valid_until'])
        auth_session.keep_alive()
        self.assertAlmostEqual(
            time() + auth_session.TTL,
            auth_session.get()['valid_until'],
            delta=1)

    def test_GivenInactiveSession_KeepAliveDoesNothing(self):
        auth_session.keep_alive()
        self.assertIsNone(auth_session.get())

    def test_GivenInactiveSession_HasRoleReturnsFalse(self):
        self.assertFalse(auth_session.has_role('me'))

    def test_GivenActiveSessionWithoutRoles_HasRoleReturnsFalse(self):
        auth_session.start(roles=None)
        self.assertFalse(auth_session.has_role('me'))

    def test_GivenActiveSessionWithEmptyListOfRoles_HasRoleReturnsFalse(self):
        auth_session.start(roles=[])
        self.assertFalse(auth_session.has_role('me'))

    def test_GivenActiveSessionWithoutMatchingRole_HasRoleReturnsFalse(self):
        auth_session.start(roles=['you', 'him', 'them'])
        self.assertFalse(auth_session.has_role('me'))

    def test_GivenActiveSessionWithMatchingRole_HasRoleReturnsTrue(self):
        auth_session.start(roles=['you', 'him', 'them'])
        self.assertTrue(auth_session.has_role('him'))

    def test_GivenExpiredSessionWithMatchingRole_HasRoleReturnsFalse(self):
        auth_session.TTL = -1
        auth_session.start(roles=['you', 'him', 'them'])
        self.assertFalse(auth_session.has_role('him'))
