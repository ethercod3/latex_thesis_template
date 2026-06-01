#!/usr/bin/env nu

const DEFAULT_ARCHIVE_BRANCH = "pdf-archive"
const DEFAULT_MAX_BUILDS = "50"
const DEFAULT_PDF_PATH = "Куприянов_И221_диплом.pdf"
const ARCHIVE_ROOT = "pdfs"
const WORKTREE_DIR = ".pdf-archive-worktree"
const PDF_SOURCE_PATHS = [
    "*.tex",
    "*.bib",
    "*.mmd",
    "*.py",
    "*.pdf",
    "*.docx",
    "*.sty",
    "*.cls",
    "*.bst",
    "*.toml",
    "*.yml",
    "*.yaml",
    ".latexmkrc",
]

def env-or [name: string, fallback: string] {
    let value = ($env | get --optional $name | default "")
    if ($value | str trim) == "" { $fallback } else { $value }
}

def ensure-success [result: record, message: string] {
    if $result.exit_code != 0 {
        let details = ([$result.stdout $result.stderr] | str join "\n" | str trim)
        error make { msg: $"($message)\n($details)" }
    }
}

def run-git [args: list<string>] {
    let result = (^git ...$args | complete)
    ensure-success $result $"git command failed: git ($args | str join ' ')"
    $result.stdout | str trim
}

def run-git-redacted [args: list<string>, display_args: list<string>] {
    let result = (^git ...$args | complete)
    ensure-success $result $"git command failed: git ($display_args | str join ' ')"
    $result.stdout | str trim
}

def clear-github-extraheader [] {
    let _local = (^git config --unset-all http.https://github.com/.extraheader | complete)
    let _global = (^git config --global --unset-all http.https://github.com/.extraheader | complete)
}

def archive-remote-url [repo: string, token: string, remote_url: string] {
    if $remote_url != "" {
        $remote_url
    } else if $repo == "" {
        error make {
            msg: "PDF_ARCHIVE_REPOSITORY or PDF_ARCHIVE_REMOTE_URL must be set before publishing the PDF archive."
        }
    } else if $token == "" {
        $"git@github.com:($repo).git"
    } else if ($token | str starts-with "ghs_") {
        error make {
            msg: $"PDF_ARCHIVE_TOKEN must be a personal access token with Contents read/write access to ($repo), not the workflow GITHUB_TOKEN."
        }
    } else {
        $"https://x-access-token:($token)@github.com/($repo).git"
    }
}

def source-commit-in-build [build_dir: string] {
    if not ($build_dir | path exists) {
        return ""
    }

    let metadata_path = ($build_dir | path join "metadata.json")
    if ($metadata_path | path exists) {
        let metadata = (open $metadata_path)
        $metadata | get --optional source_commit | default ""
    } else {
        ""
    }
}

def commit-exists [commit: string] {
    if $commit == "" {
        return false
    }

    let result = (^git cat-file -e $"($commit)^{commit}" | complete)
    $result.exit_code == 0
}

def changed-pdf-source-files [base_commit: string, source_commit: string] {
    let range = $"($base_commit)..($source_commit)"
    let result = (^git diff --name-only $range -- ...$PDF_SOURCE_PATHS | complete)
    ensure-success $result $"failed to compare PDF source changes for ($range)"
    $result.stdout | lines | where { ($in | str trim) != "" }
}

def git-identity [] {
    let env_name = ($env | get --optional GIT_COMMITTER_NAME | default "")
    let env_email = ($env | get --optional GIT_COMMITTER_EMAIL | default "")
    if ($env_name | str trim) != "" and ($env_email | str trim) != "" {
        return { name: $env_name, email: $env_email }
    }

    if (($env | get --optional GITHUB_ACTIONS | default "") == "true") {
        return {
            name: "github-actions[bot]",
            email: "41898282+github-actions[bot]@users.noreply.github.com",
        }
    }

    let name = (run-git [config user.name])
    let email = (run-git [config user.email])

    if ($name | str trim) == "" or ($email | str trim) == "" {
        error make { msg: "Git user.name and user.email must be configured before publishing the PDF archive." }
    }

    { name: $name, email: $email }
}

def main [
    --force # Publish a new archive build even if no committed PDF source files changed.
] {
    let archive_branch = (env-or "PDF_ARCHIVE_BRANCH" $DEFAULT_ARCHIVE_BRANCH)
    let max_builds = ((env-or "PDF_ARCHIVE_MAX_BUILDS" $DEFAULT_MAX_BUILDS) | into int)
    let pdf_path = (env-or "PDF_ARCHIVE_PDF_PATH" $DEFAULT_PDF_PATH)

    if $max_builds < 1 {
        error make { msg: "PDF_ARCHIVE_MAX_BUILDS must be greater than zero." }
    }

    if not ($pdf_path | path exists) {
        error make { msg: $"PDF file not found: ($pdf_path)" }
    }

    let repo = (env-or "PDF_ARCHIVE_REPOSITORY" "")
    let token = (env-or "PDF_ARCHIVE_TOKEN" "")
    let remote_url_override = (env-or "PDF_ARCHIVE_REMOTE_URL" "")
    let remote_url = (archive-remote-url $repo $token $remote_url_override)
    clear-github-extraheader
    let source_sha = (run-git [rev-parse HEAD])
    let short_sha = (run-git [rev-parse --short HEAD])
    let release_tag = (env-or "CURRENT_TAG" "unknown")
    let built_at = (date now | date to-timezone UTC | format date "%Y-%m-%dT%H:%M:%SZ")
    let build_id = $"(date now | date to-timezone UTC | format date '%Y-%m-%d_%H-%M-%S')_($short_sha)"

    if ($WORKTREE_DIR | path exists) {
        let removed_worktree = (^git worktree remove --force $WORKTREE_DIR | complete)
        if $removed_worktree.exit_code != 0 {
            rm -rf $WORKTREE_DIR
            run-git [worktree prune]
        }
    }

    let remote_ref = (^git ls-remote --heads $remote_url $archive_branch | complete)
    ensure-success $remote_ref $"failed to inspect PDF archive branch ($archive_branch)"
    if ($remote_ref.stdout | str trim) != "" {
        run-git [fetch $remote_url $archive_branch --depth 1]
        run-git [worktree add --detach $WORKTREE_DIR FETCH_HEAD]
    } else {
        mkdir $WORKTREE_DIR
        run-git [-C $WORKTREE_DIR init]
        run-git [-C $WORKTREE_DIR checkout --orphan $archive_branch]
    }

    let identity = (git-identity)
    run-git [-C $WORKTREE_DIR config user.name $identity.name]
    run-git [-C $WORKTREE_DIR config user.email $identity.email]

    let archive_root = ($WORKTREE_DIR | path join $ARCHIVE_ROOT)
    let builds = if ($archive_root | path exists) {
        ls $archive_root | where type == dir | sort-by name --reverse
    } else {
        []
    }

    if $force {
        print "Forced PDF archive publish: skipping source-change freshness check."
    } else if not ($builds | is-empty) {
        let latest_build = ($builds | first)
        let latest_source_commit = (source-commit-in-build $latest_build.name)
        if (commit-exists $latest_source_commit) {
            let changed_sources = (changed-pdf-source-files $latest_source_commit $source_sha)
            if ($changed_sources | is-empty) {
                print $"PDF archive unchanged: no committed PDF source changes since ($latest_source_commit | str substring 0..7). Latest build remains ($latest_build.name | path basename)."
                return
            }

            print $"PDF source changes since last publish: ($changed_sources | length) files."
        } else if $latest_source_commit != "" {
            print $"Last archive source commit ($latest_source_commit) is not available locally; publishing without source-change deduplication."
        }
    }

    let build_dir = ($WORKTREE_DIR | path join $ARCHIVE_ROOT $build_id)
    mkdir $build_dir

    let pdf_name = ($pdf_path | path basename)
    cp $pdf_path ($build_dir | path join $pdf_name)

    {
        built_at_utc: $built_at,
        source_commit: $source_sha,
        source_short_commit: $short_sha,
        release_tag: $release_tag,
        pdf_file: $pdf_name
    } | to json --indent 2 | save -f ($build_dir | path join "metadata.json")

    let builds = (ls $archive_root | where type == dir | sort-by name --reverse)
    for old_build in ($builds | skip $max_builds) {
        rm -rf $old_build.name
    }

    run-git [-C $WORKTREE_DIR add .]
    let status = (run-git [-C $WORKTREE_DIR status --porcelain])
    if $status == "" {
        print "PDF archive is already up to date."
        return
    }

    run-git [-C $WORKTREE_DIR commit -m $"Add PDF build ($build_id)"]
    run-git-redacted [-C $WORKTREE_DIR push $remote_url $"HEAD:($archive_branch)"] [-C $WORKTREE_DIR push "<PDF_ARCHIVE_REPOSITORY>" $"HEAD:($archive_branch)"]
    print $"Published PDF archive build ($build_id) to ($archive_branch)."
}
