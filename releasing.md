# Release procedure for LotusRPC 🌼

1. Create tag in git on the `main` branch with format major.minor.revision
    - Tag message should be `LotusRPC v{major}.{minor}.{revision}`
2. Appropriate actions are triggered automatically to
    - Build lotusrpc package
    - Upload to PyPI
    - Create GitHub release
    - Upload artifacts to GitHub release
      - Python distribution
      - Release notes (CHANGES.md)
    - Commit release notes to repo `main` branch
3. Manually trigger the workflow to deploy documentation that includes new release notes. Since committing the release notes in a workflow in step 2 does not automatically trigger a new workflow, it has to be started manually
