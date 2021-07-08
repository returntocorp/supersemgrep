from functools import partial
import json


from pathlib import Path
from . import base

from gql import gql, Client


class Loader(base.Loader):
    NEEDS = {
        base.Option(
            name="github_token",
            instructions="Create a personal access token with 'repo' scope at https://github.com/settings/tokens/new.",
            persist=True,
        ),
        base.Option(
            name="github_namespace",
            instructions="Enter a GitHub user or organization.",
        ),
    }

    def create_target(self, directory: Path) -> None:
        transport = base.CachedRequestsHTTPTransport(
            url="https://api.github.com/graphql",
            headers={"Authorization": f"bearer {self.options['github_token']}"},
            caching_kwargs={"allowable_methods": ("GET", "POST")},
        )
        client = Client(transport=transport, fetch_schema_from_transport=True)

        query = gql(
            """
query getRepos($namespace: String!) {
  repositoryOwner(login: $namespace) {
    __typename
    repositories(first: 100, isLocked: false, affiliations: OWNER, ownerAffiliations: OWNER) {
      __typename
      nodes {
        __typename
        branchProtectionRules(first: 5) {
          nodes {
            __typename
            allowsForcePushes
            allowsDeletions
            dismissesStaleReviews
            isAdminEnforced
            matchingRefs(first: 5) {
              __typename
              nodes {
                __typename
                name
              }
            }
            requiresStrictStatusChecks
            requiresStatusChecks
            requiresLinearHistory
            requiresConversationResolution
            requiresCommitSignatures
            requiresCodeOwnerReviews
            requiresApprovingReviews
            requiredApprovingReviewCount
            requiredStatusCheckContexts
            restrictsPushes
            restrictsReviewDismissals
          }
        }
        codeOfConduct {
          __typename
          name
        }
        licenseInfo {
          __typename
          key
        }
        defaultBranchRef {
          __typename
          name
        }
        hasWikiEnabled
        hasProjectsEnabled
        hasIssuesEnabled
        isArchived
        isPrivate
        nameWithOwner
        name
        url
        rebaseMergeAllowed
        isSecurityPolicyEnabled
        stargazerCount
      }
    }
  }
}
            """
        )
        result = client.execute(
            query, variable_values={"namespace": self.options["github_namespace"]}
        )
        json_path = directory / f"{self.options['github_namespace']}-repos.json"
        json_path.write_text(json.dumps(result, indent=2))
