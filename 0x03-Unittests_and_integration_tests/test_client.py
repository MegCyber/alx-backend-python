#!/usr/bin/env python3
"""
Unit tests for client module
"""
import unittest
from unittest.mock import patch, PropertyMock, Mock
from parameterized import parameterized, parameterized_class
from client import GithubOrgClient
from fixtures import org_payload, repos_payload, expected_repos, apache2_repos


class TestGithubOrgClient(unittest.TestCase):
    """Test cases for GithubOrgClient class"""
    
    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch('client.get_json')
    def test_org(self, org_name, mock_get_json):
        """Test that GithubOrgClient.org returns correct value"""
        # Configure mock
        test_payload = {"login": org_name}
        mock_get_json.return_value = test_payload
        
        # Create client and call org
        client = GithubOrgClient(org_name)
        result = client.org
        
        # Assertions
        mock_get_json.assert_called_once_with(f"https://api.github.com/orgs/{org_name}")
        self.assertEqual(result, test_payload)
    
    def test_public_repos_url(self):
        """Test GithubOrgClient._public_repos_url property"""
        with patch.object(GithubOrgClient, 'org', new_callable=PropertyMock) as mock_org:
            test_payload = {"repos_url": "https://api.github.com/orgs/google/repos"}
            mock_org.return_value = test_payload
            
            client = GithubOrgClient("google")
            result = client._public_repos_url
            
            self.assertEqual(result, test_payload["repos_url"])
    
    @patch('client.get_json')
    def test_public_repos(self, mock_get_json):
        """Test GithubOrgClient.public_repos method"""
        # Mock get_json to return test payload
        test_repos = [
            {"name": "repo1", "license": {"key": "mit"}},
            {"name": "repo2", "license": {"key": "apache-2.0"}},
        ]
        mock_get_json.return_value = test_repos
        
        # Mock _public_repos_url
        with patch.object(GithubOrgClient, '_public_repos_url', new_callable=PropertyMock) as mock_url:
            test_url = "https://api.github.com/orgs/google/repos"
            mock_url.return_value = test_url
            
            client = GithubOrgClient("google")
            result = client.public_repos()
            
            # Expected result is list of repo names
            expected = ["repo1", "repo2"]
            self.assertEqual(result, expected)
            
            # Verify mocks were called once
            mock_get_json.assert_called_once_with(test_url)
            mock_url.assert_called_once()
    
    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
    ])
    def test_has_license(self, repo, license_key, expected):
        """Test GithubOrgClient.has_license method"""
        client = GithubOrgClient("test_org")
        result = client.has_license(repo, license_key)
        self.assertEqual(result, expected)


@parameterized_class([
    {
        "org_payload": org_payload,
        "repos_payload": repos_payload,
        "expected_repos": expected_repos,
        "apache2_repos": apache2_repos
    }
])
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration tests for GithubOrgClient"""
    
    @classmethod
    def setUpClass(cls):
        """Set up class with fixtures"""
        def side_effect(url):
            """Side effect function for requests.get mock"""
            mock_response = Mock()
            if url == f"https://api.github.com/orgs/{cls.org_payload['login']}":
                mock_response.json.return_value = cls.org_payload
            elif url == cls.org_payload["repos_url"]:
                mock_response.json.return_value = cls.repos_payload
            return mock_response
        
        cls.get_patcher = patch('requests.get', side_effect=side_effect)
        cls.get_patcher.start()
    
    @classmethod
    def tearDownClass(cls):
        """Tear down class by stopping patcher"""
        cls.get_patcher.stop()
    
    def test_public_repos(self):
        """Integration test for public_repos method"""
        client = GithubOrgClient(self.org_payload["login"])
        repos = client.public_repos()
        self.assertEqual(repos, self.expected_repos)
    
    def test_public_repos_with_license(self):
        """Integration test for public_repos method with license filter"""
        client = GithubOrgClient(self.org_payload["login"])
        repos = client.public_repos(license="apache-2.0")
        self.assertEqual(repos, self.apache2_repos)


if __name__ == '__main__':
    unittest.main()