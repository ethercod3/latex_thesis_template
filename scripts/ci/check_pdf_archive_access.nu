#!/usr/bin/env nu

const DEFAULT_ARCHIVE_REPOSITORY = "ethercod3/diploma-pdf-archive"
const DEFAULT_ARCHIVE_BRANCH = "main"

def env-or [name: string, fallback: string] {
    let value = ($env | get --optional $name | default "")
    if ($value | str trim) == "" { $fallback } else { $value }
}

def clear-github-extraheader [] {
    let _local = (^git config --unset-all http.https://github.com/.extraheader | complete)
    let _global = (^git config --global --unset-all http.https://github.com/.extraheader | complete)
}

def main [] {
    let repo = (env-or "PDF_ARCHIVE_REPOSITORY" $DEFAULT_ARCHIVE_REPOSITORY)
    let branch = (env-or "PDF_ARCHIVE_BRANCH" $DEFAULT_ARCHIVE_BRANCH)
    let token = (env-or "PDF_ARCHIVE_TOKEN" "")

    if $token == "" {
        error make {
            msg: $"PDF_ARCHIVE_TOKEN is required to access ($repo)."
        }
    }

    if ($token | str starts-with "ghs_") {
        error make {
            msg: $"PDF_ARCHIVE_TOKEN must be a personal access token with Contents read/write access to ($repo), not the workflow GITHUB_TOKEN."
        }
    }

    let remote_url = $"https://x-access-token:($token)@github.com/($repo).git"
    clear-github-extraheader
    let result = (^git ls-remote --heads $remote_url $branch | complete)

    if $result.exit_code != 0 {
        let details = ([$result.stdout $result.stderr] | str join "\n" | str trim)
        error make {
            msg: $"Cannot fetch ($branch) from PDF archive repository ($repo). Check PDF_ARCHIVE_TOKEN repository access and Contents permissions.\n($details)"
        }
    }

    if ($result.stdout | str trim) == "" {
        print $"PDF archive repository ($repo) is reachable, but branch ($branch) does not exist yet."
    } else {
        print $"PDF archive repository access is OK: ($repo) branch ($branch)."
    }
}
