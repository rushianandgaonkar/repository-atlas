# Repository Atlas

An iOS-inspired, searchable catalog of rushianandgaonkar’s public GitHub repositories. Includes 10-item pagination, a scrollable setup dialog, upstream statistics, and a browser-local shortlist.

## First-time setup

1. Open **Settings → Pages**.
2. Under **Build and deployment → Source**, select **GitHub Actions**.
3. Open **Actions → Sync and publish catalog → Run workflow → Run workflow** on `main`.
4. Wait for both build and deploy to turn green.
5. Visit https://rushianandgaonkar.github.io/repository-atlas/.

If the first automatic run fails before Pages is enabled, enable it using step 2 and rerun the workflow. No personal access token or paid AI account is needed. The built-in GitHub Actions token is used only on the runner, never in the website.

## Automatic updates

The workflow refreshes the catalog at 00:17, 06:17, 12:17 and 18:17 UTC. Scheduled runs can be delayed. GitHub can disable scheduled workflows in public repositories after 60 days without repository activity; if that happens, re-enable the workflow from Actions. Forking another repository does not count as activity in this catalog repository.

Each successful run fetches all pages of public repositories, excludes this catalog and private repositories, refreshes metadata and upstream counts, and deploys the generated site. A failed build does not replace the last deployed site. The page shows the last successful data-build time; reload after a deployment to see changes.

New forks and newly uploaded public repositories appear under **New — needs review**. Repositories made private or deleted disappear after the next successful run. A folder only on your computer cannot be discovered by GitHub.

## Summaries and setup

`curated.json` preserves the reviewed categories, summaries and installation instructions. Live GitHub descriptions are retained as `githubDescription` in the generated catalog data. New repositories get their GitHub description and a README setup link, without invented installation commands.

To review a new repository, copy its record from the deployed `catalog.json` into `curated.json`, then edit category, description, requirements, steps, command, doc and readmeVerified. Instructions should be checked manually before marking reviewed. Commit to main to rebuild.

## Files

- `template.html`: UI, styles and client-side interactions; do not open directly because it has build placeholders.
- `curated.json`: public-only reviewed records.
- `scripts/sync.py`: standard-library-only data fetcher and builder.
- `.github/workflows/sync.yml`: schedule, manual trigger and Pages deployment.

## Local preview

Run `python3 scripts/sync.py`, then `python3 -m http.server 8000 --directory _site` and open http://localhost:8000. Public unauthenticated GitHub API limits may be too low for a full inventory plus all upstream lookups; Actions uses its built-in token. Do not put credentials in HTML or commit them.

No ChatGPT Plus, OpenAI API subscription, paid domain or AI service is required. GitHub hosting/Actions remain subject to GitHub’s current free-plan terms.
