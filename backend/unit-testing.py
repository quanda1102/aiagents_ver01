import unittest

from faqLookup import faq_look_up, personal_info
from tasks_management import TaskManagement
# Unit testing for the faq_look_up function
class TestFAQLookup(unittest.TestCase):

    def test_returns_personal_info_for_identity_query(self):
        """Tests that asking 'who are you' returns the correct bio."""
        self.assertEqual(faq_look_up("ban la gi"), personal_info)
        # You can add more variations here
        self.assertEqual(faq_look_up("ban la ai?"), personal_info)

    def test_returns_greeting_for_hello(self):
        """Tests that a greeting returns the correct friendly response."""
        self.assertEqual(faq_look_up("xin chao"), "Hi my friend")
        self.assertEqual(faq_look_up("hello there"), "Hi my friend")

    def test_returns_no_result_for_unknown_query(self):
        """Tests the fallback case for unrecognized questions."""
        self.assertEqual(faq_look_up("some other question"), "no result")

class TestTaskManagement(unittest.TestCase):
    """Unit testing for the task management API"""
    def test_create_task(self):
        """Tests that the create_task function creates the correct task."""
        self.assertEqual(TaskManagement.create_task("Do homework"), "task created")
        self.assertEqual(TaskManagement.create_task("Do the dishes"), "task created")
        self.assertEqual(TaskManagement.create_task("Do the laundry"), "task created")
    
    def test_update_task(self):
        """Tests that the update_task function updates the correct task."""
        self.assertEqual(TaskManagement.update_task("Do homework"), "updated")

    def test_get_task(self):
        """Tests that the get_task function gets the correct task."""
        self.assertEqual(TaskManagement.get_task("Do homework"), "task")
        self.assertEqual(TaskManagement.get_task("Do the dishes"), "task")
        self.assertEqual(TaskManagement.get_task("Do the laundry"), "task")

    def test_delete_task(self):
        """Tests that the delete_task function deletes the correct task."""
        self.assertEqual(TaskManagement.delete_task("Do homework"), "task deleted")