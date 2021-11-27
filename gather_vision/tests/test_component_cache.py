import uuid

from django.test import TestCase

from gather_vision.process.component.cache import Cache
from gather_vision.process.component.logger import Logger


class TestComponentCache(TestCase):
    def setUp(self) -> None:
        self._logger = Logger()
        self._cache = Cache(self._logger, "testing")

    def tearDown(self) -> None:
        self._cache.clear()

    def test_get_miss(self):
        # arrange
        key = f"test-{uuid.uuid4()}"

        # act
        found, result = self._cache.get(key)

        # assert
        self.assertFalse(found)
        self.assertIsNone(result)

    def test_get_hit(self):
        # arrange
        key = "test-" + str(uuid.uuid4())
        value = str(uuid.uuid4())

        # act
        self._cache.set(key, value)
        found, result = self._cache.get(key)

        # assert
        self.assertTrue(found)
        self.assertEqual(value, result)

    def test_get_or_set_miss(self):
        # arrange
        key = str(uuid.uuid4())
        value = str(uuid.uuid4())

        # act
        result = self._cache.get_or_set(key, value)

        # assert
        self.assertEqual(value, result)

    def test_get_or_set_hit(self):
        # arrange
        key = str(uuid.uuid4())
        value = str(uuid.uuid4())

        # act
        self._cache.set(key, value)
        result = self._cache.get_or_set(key, value)

        # assert
        self.assertEqual(value, result)
