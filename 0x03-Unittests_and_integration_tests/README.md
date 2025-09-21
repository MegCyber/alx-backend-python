#!/usr/bin/env python3
# Unit Tests and Integration Tests Project

This project demonstrates comprehensive unit testing and integration testing practices in Python using the `unittest` framework, along with mocking, parameterization, and fixtures.

## Project Structure

```
0x03-Unittests_and_integration_tests/
├── utils.py              # Utility functions (access_nested_map, get_json, memoize)
├── client.py             # GitHub organization client class
├── fixtures.py           # Test fixtures for integration tests
├── test_utils.py         # Unit tests for utils module
├── test_client.py        # Unit and integration tests for client module
└── README.md            # This file
```

## Key Concepts Covered

### Unit Testing vs Integration Testing

- **Unit Tests**: Test individual functions in isolation, mocking external dependencies
- **Integration Tests**: Test end-to-end functionality with minimal mocking

### Testing Patterns

1. **Parameterized Tests**: Testing multiple input/output combinations with `@parameterized.expand`
2. **Mocking**: Using `unittest.mock.patch` to replace external dependencies
3. **Property Mocking**: Mocking class properties and cached methods
4. **Fixtures**: Using predefined test data for consistent testing

## Files Overview

### utils.py
Contains utility functions:
- `access_nested_map()`: Safely access nested dictionary values
- `get_json()`: Fetch JSON data from URLs
- `memoize`: Decorator for caching method results

### client.py
GitHub API client with:
- `GithubOrgClient`: Class for interacting with GitHub organization API
- Methods for fetching organization data and repositories
- License filtering functionality

### test_utils.py
Unit tests for utils module:
- `TestAccessNestedMap`: Tests for nested dictionary access
- `TestGetJson`: Tests for HTTP JSON fetching (mocked)
- `TestMemoize`: Tests for memoization decorator

### test_client.py
Tests for client module:
- `TestGithubOrgClient`: Unit tests with mocking
- `TestIntegrationGithubOrgClient`: Integration tests with fixtures

## Running the Tests

Execute individual test files:

```bash
# Run utils tests
python -m unittest test_utils.py

# Run client tests  
python -m unittest test_client.py

# Run specific test class
python -m unittest test_utils.TestAccessNestedMap

# Run specific test method
python -m unittest test_utils.TestAccessNestedMap.test_access_nested_map
```

## Test Examples

### Parameterized Testing
```python
@parameterized.expand([
    ({"a": 1}, ("a",), 1),
    ({"a": {"b": 2}}, ("a", "b"), 2),
])
def test_access_nested_map(self, nested_map, path, expected):
    self.assertEqual(access_nested_map(nested_map, path), expected)
```

### Mocking HTTP Calls
```python
@patch('utils.requests.get')
def test_get_json(self, mock_get):
    mock_response = Mock()
    mock_response.json.return_value = {"payload": True}
    mock_get.return_value = mock_response
    
    result = get_json("http://example.com")
    mock_get.assert_called_once_with("http://example.com")
```

### Integration Testing with Fixtures
```python
@parameterized_class([{
    "org_payload": org_payload,
    "repos_payload": repos_payload,
    "expected_repos": expected_repos,
}])
class TestIntegrationGithubOrgClient(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.get_patcher = patch('requests.get', side_effect=side_effect)
        cls.get_patcher.start()
```

## Requirements

- Python 3.7+
- parameterized library
- unittest.mock (built-in)
- requests library

Install dependencies:
```bash
pip install parameterized requests
```

## Best Practices Demonstrated

1. **Test Organization**: Separate test files for different modules
2. **Mock External Dependencies**: HTTP calls, database operations
3. **Use Descriptive Test Names**: Clear indication of what's being tested
4. **Test Edge Cases**: Invalid inputs, error conditions
5. **Parameterized Tests**: Reduce code duplication
6. **Integration Testing**: Test complete workflows
7. **Proper Setup/Teardown**: Use `setUpClass`/`tearDownClass` for expensive operations

## Learning Objectives Achieved

- ✅ Difference between unit and integration tests
- ✅ Common testing patterns (mocking, parameterization, fixtures)
- ✅ Using `unittest.mock` for dependency injection
- ✅ Testing error conditions and edge cases
- ✅ Mocking properties and cached methods
- ✅ Integration testing with realistic fixtures
- ✅ Proper test organization and structure