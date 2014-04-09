import mock
from . import test_interface, helpers
from artifice import database
from artifice import models
from datetime import timedelta, datetime
from .constants import TENANT_ID


class TestDatabaseModule(test_interface.TestInterface):

    def test_adding_to_db(self):
        """Tests adding all the data to the database."""

        usage = helpers.get_usage(self.start, self.end)
        timestamp = datetime.now()

        db = database.Database(self.session)
        db.insert_tenant(TENANT_ID,
                         "demo", "", timestamp)

        # patch to mock out the novaclient call
        with mock.patch('artifice.helpers.flavor_name') as flavor_name:
            flavor_name.side_effect = lambda x: x

            db.enter(usage.values(), self.start, self.end, timestamp)

            count = 0
            for val in usage.values():
                for service in val.usage():
                    count += 1

        self.assertEqual(self.session.query(models.UsageEntry).count(), count)
        self.assertEqual(self.session.query(models.Resource).count(),
                         len(usage.values()))
        self.assertEqual(self.session.query(models.Tenant).count(), 1)

    def test_get_from_db(self):
        """Test to ensure the data in the database matches the data entered."""
        num_resources = 32
        num_tenants = 5

        helpers.fill_db(self.session, num_tenants, num_resources, self.end)

        db = database.Database(self.session)

        for i in range(num_tenants):
            usage = db.usage(self.start, self.start + timedelta(days=60),
                             "tenant_id_" + str(i))
            self.assertEqual(usage.count(), num_resources)