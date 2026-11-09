# Frozen MECG learning release

The textbook extension includes the router plus exam-prep and practice-exam-factory from Rahil's MacBook. The live repository was concurrently expanded to additional tutor skills during packaging; those edits were preserved. This particular teaching release was frozen separately to a coherent three-package installer/configuration. It is not a claim about the final scope of the concurrently edited checkout.

Final ZIP SHA-256: f5d1bae9d3b9678cb63bc642e1f07c73ffe42864e3108a5acadccf45d34f45bf. Final artifacts and receipts: main/output/pdf/mecg-ai-textbook/. Original imported exam files match the 15-file source manifest. The frozen release passes 31 tests on Linux and 31 on Mac Python 3.13.17. Preview, six-link install, repeat, three-package inventory, both skill resolutions, doctor and owned-link removal passed in isolated Mac folders. Global skill roots/accounts/T3 settings were not changed by the fixture. Full exam generation was not run.

A Mac-only assertion issue was fixed in the frozen release test: compare (p / n).resolve() with (self.source / n).resolve(), because macOS /var can alias /private/var. This test-only correction was deliberately not written over the concurrently edited live test file. The source code in the frozen ZIP is authoritative for this teaching release.
