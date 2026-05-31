#!/usr/bin/env nu

const DEFAULT_ARCHIVE_BRANCH = "pdf-archive"
const DEFAULT_MAX_BUILDS = "50"
const DEFAULT_PDF_PATH = "Куприянов_И221_диплом.pdf"
const ARCHIVE_ROOT = "pdfs"
const WORKTREE_DIR = ".pdf-archive-worktree"

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

def archive-remote-url [repo: string, token: string] {
    if $repo == "" {
        run-git [remote get-url origin]
    } else if $token == "" {
        $"https://github.com/($repo).git"
    } else {
        $"https://x-access-token:($token)@github.com/($repo).git"
    }
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
        run-git [-C $WORKTREE_DIR remote remove origin]
        run-git [-C $WORKTREE_DIR remote add origin $remote_url]
    } else {
        mkdir $WORKTREE_DIR
        run-git [-C $WORKTREE_DIR init]
        run-git [-C $WORKTREE_DIR checkout --orphan $archive_branch]
        run-git [-C $WORKTREE_DIR remote add origin $remote_url]
    }

    run-git [-C $WORKTREE_DIR config user.name "github-actions[bot]"]
    run-git [-C $WORKTREE_DIR config user.email "41898282+github-actions[bot]@users.noreply.github.com"]

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

    let archive_root = ($WORKTREE_DIR | path join $ARCHIVE_ROOT)
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
    run-git [-C $WORKTREE_DIR push origin $"HEAD:($archive_branch)"]
    print $"Published PDF archive build ($build_id) to ($archive_branch)."
}
