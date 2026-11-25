# Metabase application database protection

The analytics PostgreSQL database is not the Metabase application database.
The latter stores dashboards, questions, users, settings and connection details.
The original Compose file does not explicitly persist it. Never run compose down,
rm, up --force-recreate, or volume pruning against the existing installation
before a tested backup and recovery plan exists.

## 1. Inventory (PowerShell; read-only)

```powershell
docker inspect small_business_metabase --format '{{.Image}}'
docker inspect small_business_metabase --format '{{json .Mounts}}'
docker exec small_business_metabase sh -c 'printf "%s\n" "$MB_DB_TYPE" "$MB_DB_FILE"'
docker exec small_business_metabase sh -c 'find / -name "*.mv.db" -o -name "*.h2.db" 2>/dev/null'
```

Record the actual Metabase version from Admin > Troubleshooting and the image ID.
Do not assume the latest tag identifies the running version. Record dashboard
counts and representative KPI values. If using an external application database,
use its native backup procedure instead of the H2 procedure below. Preserve
any encryption key and configuration securely outside Git.

## 2. Cold H2 backup

Schedule downtime and stop Metabase only. Confirm the exact file path from
inventory; the example path below is not universal. Run each command separately
and stop on any failure. Store backups on access-controlled, encrypted storage.

```powershell
$Backup = Join-Path (Get-Location) ("backups/metabase-" + (Get-Date -Format yyyyMMdd-HHmmss))
New-Item -ItemType Directory -Path $Backup -ErrorAction Stop
docker stop small_business_metabase
# Replace this path with the confirmed H2 file path:
docker cp small_business_metabase:/metabase.db/metabase.db.mv.db "$Backup/metabase.db.mv.db"
Get-FileHash "$Backup/metabase.db.mv.db" -Algorithm SHA256
docker start small_business_metabase
```

Check that the copy is nonempty, retain the checksum separately and make a
second protected copy. If the copy fails, restart the original container and
investigate; do not remove it. Back up the analytics PostgreSQL database separately
before any PostgreSQL upgrade. Do not copy a live H2 file.

## 3. Restore rehearsal

Use a separate test container, a new named volume and a different localhost port
(e.g. 3001). Use the exact original image ID, not the new pinned tag. Populate
the new volume with a COPY of the backup named metabase.db.mv.db, with ownership
and permissions compatible with the image's runtime user. Set MB_DB_TYPE=h2
and MB_DB_FILE=/metabase-data/metabase.db (omit the .mv.db suffix). Mount the
volume at /metabase-data. Keep the test instance isolated from production data
sources and outbound notifications; use a disposable analytics database copy
if testing queries. Confirm the original dashboard, questions, users and settings
are present. Do not proceed if the restore fails.

## 4. Persistent deployment

The optional docker-compose.metabase-persistence.yml overlay provides a named
volume for H2. It is suitable for fresh local demos or a verified H2 restore,
not an automatic migration. The pipeline uses --no-recreate to preserve existing
containers. Consequently existing containers do NOT receive new image, network
or privilege settings until an explicit maintenance cutover.

For an existing installation, plan a cutover only after the rehearsal. Keep
the original stopped container and its storage intact (rename it if necessary;
do not let Compose adopt or remove it). Restore into the target named volume
before starting the replacement. Verify ownership, exact application version,
Compose project identity and port availability. Do not start an empty volume
expecting it to discover the old dashboard. Test the replacement and retain the
original until acceptance. Roll back by stopping the replacement and restarting
the original, without modifying its storage. Do not reuse a database upgraded
by a newer Metabase release with an older release.

## 5. Longer-term target: PostgreSQL application database

H2 is appropriate only for this local demo. For a durable deployment use a
dedicated PostgreSQL application database and dedicated non-superuser owner,
separate from the analytics database and its read-only reporting role.
Use Metabase's official load-from-h2 migration procedure with the exact source
Metabase version and a fresh empty destination database. Rehearse using a
backup copy; validate dashboards and permissions before upgrading Metabase.
Back up the application database with pg_dump and test pg_restore. Never
automatically migrate or overwrite an existing destination.

Official references:
- https://www.metabase.com/docs/latest/installation-and-operation/backing-up-metabase-application-data
- https://www.metabase.com/docs/latest/installation-and-operation/migrating-from-h2
- https://www.metabase.com/docs/latest/installation-and-operation/running-metabase-on-docker

Runtime compatibility, restore success and image registry availability must
be verified locally before merge.
