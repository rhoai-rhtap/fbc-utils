#!/bin/bash

set -euo pipefail

repo="${1:?Specify github repository. ex: rhbk/rhbk-fbc}"
pr="${2:?Specify pull request number. ex: 44}"

call_gh() {
    set -euo pipefail
    api_path="$1"
    shift
    curl -sSfL \
        -H "Accept: application/vnd.github+json" \
        -H "X-GitHub-Api-Version: 2022-11-28" \
        "$@" \
        "https://api.github.com/$api_path"
}

echo "=> Querying $repo/pull/$pr" >&2
commit="$(call_gh "repos/$repo/pulls/$pr/commits" | jq -r '.[0] | .sha')"
echo "=> Head commit ${commit:0:10}" >&2

error=""
while IFS=$'\t' read -r id status conclusion html_url details_url
do
    if [[ "$status" == "completed" ]] && [[ "$conclusion" == "success" ]]
    then
        # ex: https://console.redhat.com/preview/application-pipeline/ns/rhbk-release-tenant/pipelinerun/rhbk-fbc-component-v4-12-on-pull-request-4rpfs
        IFS=$'\t' read -r konflux_namespace konflux_component < <(sed -r 's|^.*/application-pipeline/ns/([^/]+)/pipelinerun/([^/]+)-on-pull-request[^/]*$|\1\t\2|;tx;d;:x' <<<"$details_url")

        konflux_application="$(sed 's/-component//' <<<"$konflux_component")"

        # ex: quay.io/redhat-user-workloads/rhbk-release-tenant/rhbk-fbc-v4-13/rhbk-fbc-component-v4-13:on-pr-51476f518900c699e66c4d0fdd33dbb9524e83de
        image_coord="quay.io/redhat-user-workloads/$konflux_namespace/$konflux_application/$konflux_component:on-pr-$commit"

        # Verify it exists
        skopeo inspect --no-tags "docker://$image_coord" >/dev/null

        echo "$image_coord"
    else
        echo "$id is $status ($conclusion), see $html_url" >&2
        error="yes"
    fi
done < <(
    call_gh "repos/$repo/commits/$commit/check-runs" \
        | jq -r '.check_runs
            | .[]
            | select(.external_id | contains("-on-pull-request-"))
            | [.external_id, .status, .conclusion, .html_url, .details_url]
            | @tsv' \
        | sort -V
)

if [ -n "$error" ]
then
    echo "ERROR: one or more checks have not completed successfully"
    exit 10
fi
