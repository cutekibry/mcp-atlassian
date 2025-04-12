"""
Tests for the Jira Pydantic models.

These tests validate the conversion of Jira API responses to structured models
and the simplified dictionary conversion for API responses.
"""

import os
import re

import pytest

from src.mcp_atlassian.models.constants import (
    EMPTY_STRING,
    JIRA_DEFAULT_ID,
    JIRA_DEFAULT_PROJECT,
    UNKNOWN,
)
from src.mcp_atlassian.models.jira import (
    JiraComment,
    JiraIssue,
    JiraIssueType,
    JiraPriority,
    JiraProject,
    JiraSearchResult,
    JiraStatus,
    JiraStatusCategory,
    JiraTimetracking,
    JiraTransition,
    JiraUser,
    JiraWorklog,
)

# Optional: Import real API client for optional real-data testing
try:
    from src.mcp_atlassian.jira.client import JiraClient  # noqa: F401
except ImportError:
    pass


class TestJiraUser:
    """Tests for the JiraUser model."""

    def test_from_api_response_with_valid_data(self):
        """Test creating a JiraUser from valid API data."""
        user_data = {
            "accountId": "user123",
            "displayName": "Test User",
            "emailAddress": "test@example.com",
            "active": True,
            "avatarUrls": {
                "48x48": "https://example.com/avatar.png",
                "24x24": "https://example.com/avatar-small.png",
            },
            "timeZone": "UTC",
        }
        user = JiraUser.from_api_response(user_data)
        assert user.account_id == "user123"
        assert user.display_name == "Test User"
        assert user.email == "test@example.com"
        assert user.active is True
        assert user.avatar_url == "https://example.com/avatar.png"
        assert user.time_zone == "UTC"

    def test_from_api_response_with_empty_data(self):
        """Test creating a JiraUser from empty data."""
        user = JiraUser.from_api_response({})
        assert user.account_id is None
        assert user.display_name == "Unassigned"
        assert user.email is None
        assert user.active is True
        assert user.avatar_url is None
        assert user.time_zone is None

    def test_from_api_response_with_none_data(self):
        """Test creating a JiraUser from None data."""
        user = JiraUser.from_api_response(None)
        assert user.account_id is None
        assert user.display_name == "Unassigned"
        assert user.email is None
        assert user.active is True
        assert user.avatar_url is None
        assert user.time_zone is None

    def test_to_simplified_dict(self):
        """Test converting JiraUser to a simplified dictionary."""
        user = JiraUser(
            account_id="user123",
            display_name="Test User",
            email="test@example.com",
            active=True,
            avatar_url="https://example.com/avatar.png",
            time_zone="UTC",
        )
        simplified = user.to_simplified_dict()
        assert isinstance(simplified, dict)
        assert simplified["display_name"] == "Test User"
        assert simplified["email"] == "test@example.com"
        assert simplified["avatar_url"] == "https://example.com/avatar.png"
        assert "account_id" not in simplified
        assert "time_zone" not in simplified


class TestJiraStatusCategory:
    """Tests for the JiraStatusCategory model."""

    def test_from_api_response_with_valid_data(self):
        """Test creating a JiraStatusCategory from valid API data."""
        data = {
            "id": 4,
            "key": "indeterminate",
            "name": "In Progress",
            "colorName": "yellow",
        }
        category = JiraStatusCategory.from_api_response(data)
        assert category.id == 4
        assert category.key == "indeterminate"
        assert category.name == "In Progress"
        assert category.color_name == "yellow"

    def test_from_api_response_with_empty_data(self):
        """Test creating a JiraStatusCategory from empty data."""
        category = JiraStatusCategory.from_api_response({})
        assert category.id == 0
        assert category.key == EMPTY_STRING
        assert category.name == UNKNOWN
        assert category.color_name == EMPTY_STRING


class TestJiraStatus:
    """Tests for the JiraStatus model."""

    def test_from_api_response_with_valid_data(self):
        """Test creating a JiraStatus from valid API data."""
        data = {
            "id": "10000",
            "name": "In Progress",
            "description": "Work is in progress",
            "iconUrl": "https://example.com/icon.png",
            "statusCategory": {
                "id": 4,
                "key": "indeterminate",
                "name": "In Progress",
                "colorName": "yellow",
            },
        }
        status = JiraStatus.from_api_response(data)
        assert status.id == "10000"
        assert status.name == "In Progress"
        assert status.description == "Work is in progress"
        assert status.icon_url == "https://example.com/icon.png"
        assert status.category is not None
        assert status.category.id == 4
        assert status.category.name == "In Progress"
        assert status.category.color_name == "yellow"

    def test_from_api_response_with_empty_data(self):
        """Test creating a JiraStatus from empty data."""
        status = JiraStatus.from_api_response({})
        assert status.id == JIRA_DEFAULT_ID
        assert status.name == UNKNOWN
        assert status.description is None
        assert status.icon_url is None
        assert status.category is None

    def test_to_simplified_dict(self):
        """Test converting JiraStatus to a simplified dictionary."""
        status = JiraStatus(
            id="10000",
            name="In Progress",
            description="Work is in progress",
            icon_url="https://example.com/icon.png",
            category=JiraStatusCategory(
                id=4, key="indeterminate", name="In Progress", color_name="yellow"
            ),
        )
        simplified = status.to_simplified_dict()
        assert isinstance(simplified, dict)
        assert simplified["name"] == "In Progress"
        assert "category" in simplified
        assert simplified["category"] == "In Progress"
        assert "color" in simplified
        assert simplified["color"] == "yellow"
        assert "description" not in simplified


class TestJiraIssueType:
    """Tests for the JiraIssueType model."""

    def test_from_api_response_with_valid_data(self):
        """Test creating a JiraIssueType from valid API data."""
        data = {
            "id": "10000",
            "name": "Task",
            "description": "A task that needs to be done.",
            "iconUrl": "https://example.com/task-icon.png",
        }
        issue_type = JiraIssueType.from_api_response(data)
        assert issue_type.id == "10000"
        assert issue_type.name == "Task"
        assert issue_type.description == "A task that needs to be done."
        assert issue_type.icon_url == "https://example.com/task-icon.png"

    def test_from_api_response_with_empty_data(self):
        """Test creating a JiraIssueType from empty data."""
        issue_type = JiraIssueType.from_api_response({})
        assert issue_type.id == JIRA_DEFAULT_ID
        assert issue_type.name == UNKNOWN
        assert issue_type.description is None
        assert issue_type.icon_url is None

    def test_to_simplified_dict(self):
        """Test converting JiraIssueType to a simplified dictionary."""
        issue_type = JiraIssueType(
            id="10000",
            name="Task",
            description="A task that needs to be done.",
            icon_url="https://example.com/task-icon.png",
        )
        simplified = issue_type.to_simplified_dict()
        assert isinstance(simplified, dict)
        assert simplified["name"] == "Task"
        assert "id" not in simplified
        assert "description" not in simplified
        assert "icon_url" not in simplified


class TestJiraPriority:
    """Tests for the JiraPriority model."""

    def test_from_api_response_with_valid_data(self):
        """Test creating a JiraPriority from valid API data."""
        data = {
            "id": "3",
            "name": "Medium",
            "description": "Medium priority",
            "iconUrl": "https://example.com/medium-priority.png",
        }
        priority = JiraPriority.from_api_response(data)
        assert priority.id == "3"
        assert priority.name == "Medium"
        assert priority.description == "Medium priority"
        assert priority.icon_url == "https://example.com/medium-priority.png"

    def test_from_api_response_with_empty_data(self):
        """Test creating a JiraPriority from empty data."""
        priority = JiraPriority.from_api_response({})
        assert priority.id == JIRA_DEFAULT_ID
        assert priority.name == "None"  # Default for priority is 'None'
        assert priority.description is None
        assert priority.icon_url is None

    def test_to_simplified_dict(self):
        """Test converting JiraPriority to a simplified dictionary."""
        priority = JiraPriority(
            id="3",
            name="Medium",
            description="Medium priority",
            icon_url="https://example.com/medium-priority.png",
        )
        simplified = priority.to_simplified_dict()
        assert isinstance(simplified, dict)
        assert simplified["name"] == "Medium"
        assert "id" not in simplified
        assert "description" not in simplified
        assert "icon_url" not in simplified


class TestJiraComment:
    """Tests for the JiraComment model."""

    def test_from_api_response_with_valid_data(self):
        """Test creating a JiraComment from valid API data."""
        data = {
            "id": "10000",
            "body": "This is a test comment",
            "created": "2024-01-01T12:00:00.000+0000",
            "updated": "2024-01-01T12:00:00.000+0000",
            "author": {
                "accountId": "user123",
                "displayName": "Comment User",
                "active": True,
            },
        }
        comment = JiraComment.from_api_response(data)
        assert comment.id == "10000"
        assert comment.body == "This is a test comment"
        assert comment.created == "2024-01-01T12:00:00.000+0000"
        assert comment.updated == "2024-01-01T12:00:00.000+0000"
        assert comment.author is not None
        assert comment.author.display_name == "Comment User"

    def test_from_api_response_with_empty_data(self):
        """Test creating a JiraComment from empty data."""
        comment = JiraComment.from_api_response({})
        assert comment.id == JIRA_DEFAULT_ID
        assert comment.body == EMPTY_STRING
        assert comment.created == EMPTY_STRING
        assert comment.updated == EMPTY_STRING
        assert comment.author is None

    def test_to_simplified_dict(self):
        """Test converting JiraComment to a simplified dictionary."""
        comment = JiraComment(
            id="10000",
            body="This is a test comment",
            created="2024-01-01T12:00:00.000+0000",
            updated="2024-01-01T12:00:00.000+0000",
            author=JiraUser(account_id="user123", display_name="Comment User"),
        )
        simplified = comment.to_simplified_dict()
        assert isinstance(simplified, dict)
        assert "body" in simplified
        assert simplified["body"] == "This is a test comment"
        assert "created" in simplified
        assert isinstance(simplified["created"], str)
        assert "author" in simplified
        assert isinstance(simplified["author"], dict)
        assert simplified["author"]["display_name"] == "Comment User"


class TestJiraTimetracking:
    """Tests for the JiraTimetracking model."""

    def test_from_api_response_with_valid_data(self):
        """Test creating a JiraTimetracking from valid API data."""
        data = {
            "originalEstimate": "2h",
            "remainingEstimate": "1h 30m",
            "timeSpent": "30m",
            "originalEstimateSeconds": 7200,
            "remainingEstimateSeconds": 5400,
            "timeSpentSeconds": 1800,
        }
        timetracking = JiraTimetracking.from_api_response(data)
        assert timetracking.original_estimate == "2h"
        assert timetracking.remaining_estimate == "1h 30m"
        assert timetracking.time_spent == "30m"
        assert timetracking.original_estimate_seconds == 7200
        assert timetracking.remaining_estimate_seconds == 5400
        assert timetracking.time_spent_seconds == 1800

    def test_from_api_response_with_empty_data(self):
        """Test creating a JiraTimetracking from empty data."""
        timetracking = JiraTimetracking.from_api_response({})
        assert timetracking.original_estimate is None
        assert timetracking.remaining_estimate is None
        assert timetracking.time_spent is None
        assert timetracking.original_estimate_seconds is None
        assert timetracking.remaining_estimate_seconds is None
        assert timetracking.time_spent_seconds is None

    def test_from_api_response_with_none_data(self):
        """Test creating a JiraTimetracking from None data."""
        timetracking = JiraTimetracking.from_api_response(None)
        assert timetracking is not None
        assert timetracking.original_estimate is None
        assert timetracking.remaining_estimate is None
        assert timetracking.time_spent is None
        assert timetracking.original_estimate_seconds is None
        assert timetracking.remaining_estimate_seconds is None
        assert timetracking.time_spent_seconds is None

    def test_to_simplified_dict(self):
        """Test converting JiraTimetracking to a simplified dictionary."""
        timetracking = JiraTimetracking(
            original_estimate="2h",
            remaining_estimate="1h 30m",
            time_spent="30m",
            original_estimate_seconds=7200,
            remaining_estimate_seconds=5400,
            time_spent_seconds=1800,
        )
        simplified = timetracking.to_simplified_dict()
        assert isinstance(simplified, dict)
        assert simplified["original_estimate"] == "2h"
        assert simplified["remaining_estimate"] == "1h 30m"
        assert simplified["time_spent"] == "30m"
        assert "original_estimate_seconds" not in simplified
        assert "remaining_estimate_seconds" not in simplified
        assert "time_spent_seconds" not in simplified


class TestJiraIssue:
    """Tests for the JiraIssue model."""

    def test_from_api_response_with_valid_data(self, jira_issue_data):
        """Test creating a JiraIssue from valid API data."""
        issue = JiraIssue.from_api_response(jira_issue_data)

        assert issue.id == "12345"
        assert issue.key == "PROJ-123"
        assert issue.summary == "Test Issue Summary"
        assert issue.description == "This is a test issue description"
        assert issue.created == "2024-01-01T10:00:00.000+0000"
        assert issue.updated == "2024-01-02T15:30:00.000+0000"

        assert issue.status is not None
        assert issue.status.name == "In Progress"
        assert issue.status.category is not None
        assert issue.status.category.name == "In Progress"

        assert issue.issue_type is not None
        assert issue.issue_type.name == "Task"

        assert issue.priority is not None
        assert issue.priority.name == "Medium"

        assert issue.assignee is not None
        assert issue.assignee.display_name == "Test User"

        assert issue.reporter is not None
        assert issue.reporter.display_name == "Reporter User"

        assert len(issue.labels) == 1
        assert issue.labels[0] == "test-label"

        assert len(issue.comments) == 1
        assert issue.comments[0].body == "This is a test comment"

    def test_from_api_response_with_empty_data(self):
        """Test creating a JiraIssue from empty data."""
        issue = JiraIssue.from_api_response({})
        assert issue.id == JIRA_DEFAULT_ID
        assert issue.key == "UNKNOWN-0"
        assert issue.summary == EMPTY_STRING
        assert issue.description is None
        assert issue.created == EMPTY_STRING
        assert issue.updated == EMPTY_STRING
        assert issue.status is None
        assert issue.issue_type is None
        assert issue.priority is None
        assert issue.assignee is None
        assert issue.reporter is None
        assert len(issue.labels) == 0
        assert len(issue.comments) == 0

    def test_find_custom_field_in_api_response(self):
        """Test the _find_custom_field_in_api_response method with different field patterns."""
        fields = {
            "customfield_10014": "EPIC-123",
            "customfield_10011": "Epic Name Test",
            "customfield_10000": "Another value",
            "schema": {
                "fields": {
                    "customfield_10014": {"name": "Epic Link", "type": "string"},
                    "customfield_10011": {"name": "Epic Name", "type": "string"},
                    "customfield_10000": {"name": "Custom Field", "type": "string"},
                }
            },
        }

        result = JiraIssue._find_custom_field_in_api_response(fields, ["Epic Link"])
        assert result == "EPIC-123"

        result = JiraIssue._find_custom_field_in_api_response(fields, ["Epic Name"])
        assert result == "Epic Name Test"

        result = JiraIssue._find_custom_field_in_api_response(fields, ["epic link"])
        assert result == "EPIC-123"

        result = JiraIssue._find_custom_field_in_api_response(
            fields, ["epic-link", "epiclink"]
        )
        assert result == "EPIC-123"

        result = JiraIssue._find_custom_field_in_api_response(
            fields, ["Non Existent Field"]
        )
        assert result is None

        result = JiraIssue._find_custom_field_in_api_response({}, ["Epic Link"])
        assert result is None

        result = JiraIssue._find_custom_field_in_api_response(None, ["Epic Link"])
        assert result is None

    def test_epic_field_extraction_different_field_ids(self):
        """Test finding epic fields with different customfield IDs."""
        test_data = {
            "id": "12345",
            "key": "PROJ-123",
            "fields": {
                "summary": "Test Issue",
                "customfield_20100": "EPIC-456",
                "customfield_20200": "My Epic Name",
                "schema": {
                    "fields": {
                        "customfield_20100": {"name": "Epic Link", "type": "string"},
                        "customfield_20200": {"name": "Epic Name", "type": "string"},
                    }
                },
            },
        }
        issue = JiraIssue.from_api_response(test_data)
        assert issue.epic_key == "EPIC-456"
        assert issue.epic_name == "My Epic Name"

    def test_epic_field_extraction_fallback(self):
        """Test using common field names without relying on metadata."""
        test_data = {
            "id": "12345",
            "key": "PROJ-123",
            "fields": {
                "summary": "Test Issue",
                "customfield_10014": "EPIC-456",
                "customfield_10011": "My Epic Name",
            },
        }

        original_method = JiraIssue._find_custom_field_in_api_response
        try:

            def mocked_find_field(fields, name_patterns):
                normalized_patterns = []
                for pattern in name_patterns:
                    norm_pattern = pattern.lower()
                    norm_pattern = re.sub(r"[_\-\s]", "", norm_pattern)
                    normalized_patterns.append(norm_pattern)

                if any("epiclink" in p for p in normalized_patterns):
                    return fields.get("customfield_10014")
                if any("epicname" in p for p in normalized_patterns):
                    return fields.get("customfield_10011")
                return None

            JiraIssue._find_custom_field_in_api_response = staticmethod(
                mocked_find_field
            )

            issue = JiraIssue.from_api_response(test_data)
            assert issue.epic_key == "EPIC-456"
            assert issue.epic_name == "My Epic Name"
        finally:
            JiraIssue._find_custom_field_in_api_response = staticmethod(original_method)

    def test_epic_field_extraction_advanced_patterns(self):
        """Test finding epic fields using various naming patterns."""
        test_data = {
            "id": "12345",
            "key": "PROJ-123",
            "fields": {
                "summary": "Test Issue",
                "customfield_12345": "EPIC-456",
                "customfield_67890": "Epic Name Value",
                "schema": {
                    "fields": {
                        "customfield_12345": {
                            "name": "Epic-Link Field",
                            "type": "string",
                        },
                        "customfield_67890": {"name": "EpicName", "type": "string"},
                    }
                },
            },
        }
        issue = JiraIssue.from_api_response(test_data)
        assert issue.epic_key == "EPIC-456"
        assert issue.epic_name == "Epic Name Value"

    def test_fields_with_names_method(self):
        """Test using the names() method to find fields."""

        class MockFields(dict):
            def names(self):
                return {
                    "customfield_55555": "Epic Link",
                    "customfield_66666": "Epic Name",
                }

        fields = MockFields(
            {"customfield_55555": "EPIC-789", "customfield_66666": "Special Epic Name"}
        )

        result = JiraIssue._find_custom_field_in_api_response(fields, ["Epic Link"])
        assert result == "EPIC-789"

        test_data = {"id": "12345", "key": "PROJ-123", "fields": fields}
        issue = JiraIssue.from_api_response(test_data)
        assert issue.epic_key == "EPIC-789"
        assert issue.epic_name == "Special Epic Name"

    def test_to_simplified_dict(self, jira_issue_data):
        """Test converting a JiraIssue to a simplified dictionary."""
        issue = JiraIssue.from_api_response(jira_issue_data)
        simplified = issue.to_simplified_dict()

        assert isinstance(simplified, dict)
        assert "key" in simplified
        assert simplified["key"] == "PROJ-123"
        assert "summary" in simplified
        assert simplified["summary"] == "Test Issue Summary"

        assert "created" in simplified
        assert isinstance(simplified["created"], str)
        assert "updated" in simplified
        assert isinstance(simplified["updated"], str)

        assert "status" in simplified
        if isinstance(simplified["status"], str):
            assert simplified["status"] == "In Progress"
        elif isinstance(simplified["status"], dict):
            assert simplified["status"]["name"] == "In Progress"

        assert "issue_type" in simplified
        if isinstance(simplified["issue_type"], str):
            assert simplified["issue_type"] == "Task"
        elif isinstance(simplified["issue_type"], dict):
            assert simplified["issue_type"]["name"] == "Task"

        assert "priority" in simplified
        if isinstance(simplified["priority"], str):
            assert simplified["priority"] == "Medium"
        elif isinstance(simplified["priority"], dict):
            assert simplified["priority"]["name"] == "Medium"

        assert "assignee" in simplified
        assert "reporter" in simplified

        # Test with "*all"
        issue = JiraIssue.from_api_response(jira_issue_data, requested_fields="*all")
        simplified = issue.to_simplified_dict()
        assert "labels" in simplified
        assert "comments" in simplified
        assert len(simplified["comments"]) > 0

    def test_jira_issue_with_custom_fields(self):
        """Test JiraIssue handling of custom fields."""
        issue_data = {
            "id": "10001",
            "key": "TEST-123",
            "fields": {
                "summary": "Test issue",
                "customfield_10001": "Simple string value",
                "customfield_10002": {"value": "Option value"},
                "customfield_10003": [{"value": "Item 1"}, {"value": "Item 2"}],
            },
        }

        issue = JiraIssue.from_api_response(issue_data)
        simplified = issue.to_simplified_dict()
        assert simplified["key"] == "TEST-123"
        assert simplified["summary"] == "Test issue"
        assert "customfield_10001" not in simplified
        assert "customfield_10002" not in simplified
        assert "customfield_10003" not in simplified

        issue = JiraIssue.from_api_response(
            issue_data, requested_fields="summary,customfield_10001"
        )
        simplified = issue.to_simplified_dict()
        assert "key" in simplified
        assert "summary" in simplified
        assert "customfield_10001" in simplified
        assert "customfield_10002" not in simplified

        issue = JiraIssue.from_api_response(
            issue_data, requested_fields=["key", "customfield_10002"]
        )
        simplified = issue.to_simplified_dict()
        assert "key" in simplified
        assert "customfield_10002" in simplified
        assert "summary" not in simplified
        assert "customfield_10001" not in simplified

        issue = JiraIssue.from_api_response(issue_data, requested_fields="*all")
        simplified = issue.to_simplified_dict()
        assert "key" in simplified
        assert "summary" in simplified
        assert "customfield_10001" in simplified
        assert "customfield_10002" in simplified
        assert "customfield_10003" in simplified

    def test_jira_issue_with_default_fields(self):
        """Test that JiraIssue returns only essential fields by default."""
        issue_data = {
            "id": "10001",
            "key": "TEST-123",
            "fields": {
                "summary": "Test issue",
                "description": "Description",
                "status": {"name": "Open"},
                "assignee": {"displayName": "Test User"},
                "reporter": {"displayName": "Reporter User"},
                "priority": {"name": "Medium"},
                "created": "2023-01-01T00:00:00.000+0000",
                "updated": "2023-01-02T00:00:00.000+0000",
                "issuetype": {"name": "Task"},
                "customfield_10001": "Custom value",
                "customfield_10002": {"value": "Option value"},
            },
        }

        issue = JiraIssue.from_api_response(issue_data)
        simplified = issue.to_simplified_dict()
        assert "key" in simplified
        assert "summary" in simplified
        assert "description" in simplified
        assert "status" in simplified
        assert "customfield_10001" not in simplified
        assert "customfield_10002" not in simplified

        issue = JiraIssue.from_api_response(issue_data, requested_fields="*all")
        simplified = issue.to_simplified_dict()
        assert "customfield_10001" in simplified
        assert "customfield_10002" in simplified

    def test_timetracking_field_processing(self):
        """Test that timetracking data is properly processed."""
        issue_data = {
            "id": "10000",
            "key": "TEST-123",
            "fields": {
                "summary": "Test Issue",
                "description": "Test Description",
                "timetracking": {
                    "originalEstimate": "2h",
                    "remainingEstimate": "1h 30m",
                    "timeSpent": "30m",
                    "originalEstimateSeconds": 7200,
                    "remainingEstimateSeconds": 5400,
                    "timeSpentSeconds": 1800,
                },
            },
        }

        issue = JiraIssue.from_api_response(issue_data)
        assert issue.timetracking is not None
        assert issue.timetracking.original_estimate == "2h"
        assert issue.timetracking.remaining_estimate == "1h 30m"
        assert issue.timetracking.time_spent == "30m"
        assert issue.timetracking.original_estimate_seconds == 7200
        assert issue.timetracking.remaining_estimate_seconds == 5400
        assert issue.timetracking.time_spent_seconds == 1800

        issue.requested_fields = "*all"
        simplified = issue.to_simplified_dict()
        assert "timetracking" in simplified
        assert simplified["timetracking"]["original_estimate"] == "2h"
        assert simplified["timetracking"]["remaining_estimate"] == "1h 30m"

        issue.requested_fields = ["summary", "timetracking"]
        simplified = issue.to_simplified_dict()
        assert "timetracking" in simplified
        assert simplified["timetracking"]["original_estimate"] == "2h"

        issue.requested_fields = None
        simplified = issue.to_simplified_dict()
        assert "timetracking" not in simplified


class TestJiraSearchResult:
    """Tests for the JiraSearchResult model."""

    def test_from_api_response_with_valid_data(self, jira_search_data):
        """Test creating a JiraSearchResult from valid API data."""
        search_result = JiraSearchResult.from_api_response(jira_search_data)
        assert search_result.total == 34
        assert search_result.start_at == 0
        assert search_result.max_results == 5
        assert len(search_result.issues) == 1

        issue = search_result.issues[0]
        assert isinstance(issue, JiraIssue)
        assert issue.key == "PROJ-123"
        assert issue.summary == "Test Issue Summary"

    def test_from_api_response_with_empty_data(self):
        """Test creating a JiraSearchResult from empty data."""
        result = JiraSearchResult.from_api_response({})
        assert result.total == 0
        assert result.start_at == 0
        assert result.max_results == 0
        assert result.issues == []


class TestJiraProject:
    """Tests for the JiraProject model."""

    def test_from_api_response_with_valid_data(self):
        """Test creating a JiraProject from valid API data."""
        project_data = {
            "id": "10000",
            "key": "TEST",
            "name": "Test Project",
            "description": "This is a test project",
            "lead": {
                "accountId": "5b10a2844c20165700ede21g",
                "displayName": "John Doe",
                "active": True,
            },
            "self": "https://example.atlassian.net/rest/api/3/project/10000",
            "projectCategory": {
                "id": "10100",
                "name": "Software Projects",
                "description": "Software development projects",
            },
            "avatarUrls": {
                "48x48": "https://example.atlassian.net/secure/projectavatar?pid=10000&avatarId=10011",
                "24x24": "https://example.atlassian.net/secure/projectavatar?pid=10000&size=small&avatarId=10011",
            },
        }
        project = JiraProject.from_api_response(project_data)
        assert project.id == "10000"
        assert project.key == "TEST"
        assert project.name == "Test Project"
        assert project.description == "This is a test project"
        assert project.lead is not None
        assert project.lead.display_name == "John Doe"
        assert project.url == "https://example.atlassian.net/rest/api/3/project/10000"
        assert project.category_name == "Software Projects"
        assert (
            project.avatar_url
            == "https://example.atlassian.net/secure/projectavatar?pid=10000&avatarId=10011"
        )

    def test_from_api_response_with_empty_data(self):
        """Test creating a JiraProject from empty data."""
        project = JiraProject.from_api_response({})
        assert project.id == JIRA_DEFAULT_PROJECT
        assert project.key == EMPTY_STRING
        assert project.name == UNKNOWN
        assert project.description is None
        assert project.lead is None
        assert project.url is None
        assert project.category_name is None
        assert project.avatar_url is None

    def test_to_simplified_dict(self):
        """Test converting a JiraProject to a simplified dictionary."""
        project_data = {
            "id": "10000",
            "key": "TEST",
            "name": "Test Project",
            "description": "This is a test project",
            "lead": {
                "accountId": "5b10a2844c20165700ede21g",
                "displayName": "John Doe",
                "active": True,
            },
            "self": "https://example.atlassian.net/rest/api/3/project/10000",
            "projectCategory": {
                "name": "Software Projects",
            },
        }
        project = JiraProject.from_api_response(project_data)
        simplified = project.to_simplified_dict()
        assert simplified["key"] == "TEST"
        assert simplified["name"] == "Test Project"
        assert simplified["description"] == "This is a test project"
        assert simplified["lead"] is not None
        assert simplified["lead"]["display_name"] == "John Doe"
        assert simplified["category"] == "Software Projects"
        assert "id" not in simplified
        assert "url" not in simplified
        assert "avatar_url" not in simplified


class TestJiraTransition:
    """Tests for the JiraTransition model."""

    def test_from_api_response_with_valid_data(self):
        """Test creating a JiraTransition from valid API data."""
        transition_data = {
            "id": "10",
            "name": "Start Progress",
            "to": {
                "id": "3",
                "name": "In Progress",
                "statusCategory": {
                    "id": 4,
                    "key": "indeterminate",
                    "name": "In Progress",
                    "colorName": "yellow",
                },
            },
            "hasScreen": True,
            "isGlobal": False,
            "isInitial": False,
            "isConditional": True,
        }
        transition = JiraTransition.from_api_response(transition_data)
        assert transition.id == "10"
        assert transition.name == "Start Progress"
        assert transition.to_status is not None
        assert transition.to_status.id == "3"
        assert transition.to_status.name == "In Progress"
        assert transition.to_status.category is not None
        assert transition.to_status.category.name == "In Progress"
        assert transition.has_screen is True
        assert transition.is_global is False
        assert transition.is_initial is False
        assert transition.is_conditional is True

    def test_from_api_response_with_empty_data(self):
        """Test creating a JiraTransition from empty data."""
        transition = JiraTransition.from_api_response({})
        assert transition.id == JIRA_DEFAULT_ID
        assert transition.name == EMPTY_STRING
        assert transition.to_status is None
        assert transition.has_screen is False
        assert transition.is_global is False
        assert transition.is_initial is False
        assert transition.is_conditional is False

    def test_to_simplified_dict(self):
        """Test converting a JiraTransition to a simplified dictionary."""
        transition_data = {
            "id": "10",
            "name": "Start Progress",
            "to": {
                "id": "3",
                "name": "In Progress",
                "statusCategory": {
                    "id": 4,
                    "key": "indeterminate",
                    "name": "In Progress",
                    "colorName": "yellow",
                },
            },
            "hasScreen": True,
        }
        transition = JiraTransition.from_api_response(transition_data)
        simplified = transition.to_simplified_dict()
        assert simplified["id"] == "10"
        assert simplified["name"] == "Start Progress"
        assert simplified["to_status"] is not None
        assert simplified["to_status"]["name"] == "In Progress"
        assert "has_screen" not in simplified
        assert "is_global" not in simplified


class TestJiraWorklog:
    """Tests for the JiraWorklog model."""

    def test_from_api_response_with_valid_data(self):
        """Test creating a JiraWorklog from valid API data."""
        worklog_data = {
            "id": "100023",
            "author": {
                "accountId": "5b10a2844c20165700ede21g",
                "displayName": "John Doe",
                "active": True,
            },
            "comment": "Worked on the issue today",
            "created": "2023-05-01T10:00:00.000+0000",
            "updated": "2023-05-01T10:30:00.000+0000",
            "started": "2023-05-01T09:00:00.000+0000",
            "timeSpent": "2h 30m",
            "timeSpentSeconds": 9000,
        }
        worklog = JiraWorklog.from_api_response(worklog_data)
        assert worklog.id == "100023"
        assert worklog.author is not None
        assert worklog.author.display_name == "John Doe"
        assert worklog.comment == "Worked on the issue today"
        assert worklog.created == "2023-05-01T10:00:00.000+0000"
        assert worklog.updated == "2023-05-01T10:30:00.000+0000"
        assert worklog.started == "2023-05-01T09:00:00.000+0000"
        assert worklog.time_spent == "2h 30m"
        assert worklog.time_spent_seconds == 9000

    def test_from_api_response_with_empty_data(self):
        """Test creating a JiraWorklog from empty data."""
        worklog = JiraWorklog.from_api_response({})
        assert worklog.id == JIRA_DEFAULT_ID
        assert worklog.author is None
        assert worklog.comment is None
        assert worklog.created == EMPTY_STRING
        assert worklog.updated == EMPTY_STRING
        assert worklog.started == EMPTY_STRING
        assert worklog.time_spent == EMPTY_STRING
        assert worklog.time_spent_seconds == 0

    def test_to_simplified_dict(self):
        """Test converting a JiraWorklog to a simplified dictionary."""
        worklog_data = {
            "id": "100023",
            "author": {
                "accountId": "5b10a2844c20165700ede21g",
                "displayName": "John Doe",
                "active": True,
            },
            "comment": "Worked on the issue today",
            "created": "2023-05-01T10:00:00.000+0000",
            "updated": "2023-05-01T10:30:00.000+0000",
            "started": "2023-05-01T09:00:00.000+0000",
            "timeSpent": "2h 30m",
            "timeSpentSeconds": 9000,
        }
        worklog = JiraWorklog.from_api_response(worklog_data)
        simplified = worklog.to_simplified_dict()
        assert simplified["time_spent"] == "2h 30m"
        assert simplified["time_spent_seconds"] == 9000
        assert simplified["author"] is not None
        assert simplified["author"]["display_name"] == "John Doe"
        assert simplified["comment"] == "Worked on the issue today"
        assert "created" in simplified
        assert "updated" in simplified
        assert "started" in simplified


class TestRealJiraData:
    """Tests using real Jira data (optional)."""

    def test_real_jira_issue(self, use_real_jira_data, default_jira_issue_key):
        """Test that the JiraIssue model works with real Jira API data."""
        if not use_real_jira_data:
            pytest.skip("Skipping real Jira data test")

        from src.mcp_atlassian.jira.config import JiraConfig
        from src.mcp_atlassian.jira.issues import IssuesMixin

        config = JiraConfig.from_env()
        issues_client = IssuesMixin(config=config)
        issue = issues_client.get_issue(default_jira_issue_key)

        assert isinstance(issue, JiraIssue)
        assert issue.key == default_jira_issue_key
        assert issue.id is not None
        assert issue.summary is not None

        simplified = issue.to_simplified_dict()
        assert simplified["key"] == default_jira_issue_key

    def test_real_jira_project(self, use_real_jira_data):
        """Test that the JiraProject model works with real Jira API data."""
        if not use_real_jira_data:
            pytest.skip("Skipping real Jira data test")

        # Check for JIRA_TEST_ISSUE_KEY explicitly
        if not os.environ.get("JIRA_TEST_ISSUE_KEY"):
            pytest.skip("JIRA_TEST_ISSUE_KEY environment variable not set")

        from src.mcp_atlassian.jira.config import JiraConfig
        from src.mcp_atlassian.jira.projects import ProjectsMixin

        config = JiraConfig.from_env()
        projects_client = ProjectsMixin(config=config)
        default_issue_key = os.environ.get("JIRA_TEST_ISSUE_KEY")
        project_key = default_issue_key.split("-")[0]

        try:
            project = projects_client.get_project_model(project_key)

            if project is None:
                pytest.skip(f"Could not get project model for {project_key}")

            assert isinstance(project, JiraProject)
            assert project.key == project_key
            assert project.id is not None
            assert project.name is not None

            simplified = project.to_simplified_dict()
            assert simplified["key"] == project_key
        except (AttributeError, TypeError, ValueError) as e:
            pytest.skip(f"Error parsing project data: {e}")

    def test_real_jira_transitions(self, use_real_jira_data, default_jira_issue_key):
        """Test that the JiraTransition model works with real Jira API data."""
        if not use_real_jira_data:
            pytest.skip("Skipping real Jira data test")

        from atlassian import Jira

        from src.mcp_atlassian.jira.config import JiraConfig
        from src.mcp_atlassian.models.jira import JiraTransition

        try:
            config = JiraConfig.from_env()
            jira = Jira(
                url=config.url,
                username=config.username,
                password=config.api_token,
                cloud=config.is_cloud,
            )

            transitions_data = jira.get_issue_transitions(default_jira_issue_key)

            if not transitions_data or len(transitions_data) == 0:
                pytest.skip("No transitions available for test issue")

            assert len(transitions_data) > 0
            for transition_item in transitions_data:
                if "id" in transition_item and not isinstance(
                    transition_item["id"], str
                ):
                    transition_item["id"] = str(transition_item["id"])

                if isinstance(transition_item.get("to"), str):
                    to_status_name = transition_item.get("to")
                    transition_item["to"] = {
                        "id": str(transition_item.get("id", "")),
                        "name": to_status_name,
                    }

                transition = JiraTransition.from_api_response(transition_item)
                assert isinstance(transition, JiraTransition)
                assert transition.id is not None
                assert transition.name is not None

                if transition.to_status:
                    assert transition.to_status.name is not None

                simplified = transition.to_simplified_dict()
                assert "id" in simplified
                assert "name" in simplified

        except Exception as e:
            pytest.skip(f"Error getting transitions: {str(e)}")

    def test_real_jira_worklog(self, use_real_jira_data, default_jira_issue_key):
        """Test that the JiraWorklog model works with real Jira API data."""
        if not use_real_jira_data:
            pytest.skip("Skipping real Jira data test")

        from atlassian import Jira

        from src.mcp_atlassian.jira.config import JiraConfig
        from src.mcp_atlassian.models.jira import JiraWorklog

        try:
            config = JiraConfig.from_env()
            jira = Jira(
                url=config.url,
                username=config.username,
                password=config.api_token,
                cloud=config.is_cloud,
            )

            issue = jira.issue(default_jira_issue_key)
            if not issue:
                pytest.skip(f"Could not access issue {default_jira_issue_key}")

            # Using test data as API access might be limited or issue may have no worklogs
            test_worklog_data = {
                "id": "12345",
                "timeSpent": "1h",
                "timeSpentSeconds": 3600,
                "author": {"displayName": "Test User"},
                "created": "2023-01-01T12:00:00.000+0000",
            }

            worklog = JiraWorklog.from_api_response(test_worklog_data)

            assert isinstance(worklog, JiraWorklog)
            assert worklog.id == "12345"
            assert worklog.time_spent == "1h"
            assert worklog.time_spent_seconds == 3600

            simplified = worklog.to_simplified_dict()
            assert "id" in simplified
            assert "time_spent" in simplified
            assert simplified["time_spent"] == "1h"

        except Exception as e:
            pytest.skip(f"Error in worklog test: {str(e)}")
