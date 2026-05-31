#!/usr/bin/env nu

const DEFAULT_ARCHIVE_BRANCH = "pdf-archive"
const DEFAULT_MAX_BUILDS = "50"
const DEFAULT_PDF_PATH = "Куприянов_И221_диплом.pdf"
const ARCHIVE_ROOT = "pdfs"
const WORKTREE_DIR = ".pdf-archive-worktree"
const HASH_SCRIPT = "scripts/ci/pdf_semantic_hash.py"

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

def archive-remote-url [repo: string, token: string] {
    if $repo == "" {
        run-git [remote get-url origin]
    } else if $token == "" {
        error make {
            msg: $"PDF_ARCHIVE_TOKEN is required to push PDF builds to external repository ($repo)."
        }
    } else if ($token | str starts-with "ghs_") {
        error make {
            msg: $"PDF_ARCHIVE_TOKEN must be a personal access token with Contents read/write access to ($repo), not the workflow GITHUB_TOKEN."
        }
    } else {
        $"https://x-access-token:($token)@github.com/($repo).git"
    }
}

def pdf-semantic-hash [path: string] {
    let result = (^python $HASH_SCRIPT $path | complete)
    ensure-success $result $"failed to compute semantic PDF hash for ($path)"
    $result.stdout | str trim
}

def pdf-file-in-build [build_dir: string] {
    if not ($build_dir | path exists) {
        return ""
    }

    let metadata_path = ($build_dir | path join "metadata.json")
    if ($metadata_path | path exists) {
        let metadata = (open $metadata_path)
        let pdf_file = ($metadata | get --optional pdf_file | default "")
        if $pdf_file != "" {
            let pdf_path = ($build_dir | path join $pdf_file)
            if ($pdf_path | path exists) {
                return $pdf_path
            }
        }
    }

    let pdfs = (ls $build_dir | where type == file | where name =~ '\.pdf$' | sort-by name)
    if ($pdfs | is-empty) { "" } else { ($pdfs | first).name }
}

def main [] {
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
    let remote_url = (archive-remote-url $repo $token)
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
    if ($remote_ref.exit_code == 0) and (($remote_ref.stdout | str trim) != "") {
        run-git [fetch $remote_url $archive_branch --depth 1]
        run-git [worktree add $WORKTREE_DIR FETCH_HEAD]
    } else {
        mkdir $WORKTREE_DIR
        run-git [-C $WORKTREE_DIR init]
        run-git [-C $WORKTREE_DIR checkout --orphan $archive_branch]
    }

    run-git [-C $WORKTREE_DIR config user.name "github-actions[bot]"]
    run-git [-C $WORKTREE_DIR config user.email "41898282+github-actions[bot]@users.noreply.github.com"]

    let archive_root = ($WORKTREE_DIR | path join $ARCHIVE_ROOT)
    let builds = if ($archive_root | path exists) {
        ls $archive_root | where type == dir | sort-by name --reverse
    } else {
        []
    }

    if not ($builds | is-empty) {
        let latest_build = ($builds | first)
        let latest_pdf = (pdf-file-in-build $latest_build.name)
        if $latest_pdf != "" {
            let current_hash = (pdf-semantic-hash $pdf_path)
            let latest_hash = (pdf-semantic-hash $latest_pdf)
            if $current_hash == $latest_hash {
                print $"PDF archive unchanged after metadata normalization; latest build remains ($latest_build.name | path basename)."
                return
            }
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
