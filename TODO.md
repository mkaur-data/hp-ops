# ops todo

## high prio
- [ ] eu-01 recovery — waiting on Hetzner ticket HSX-447812
  - last update mar 19, they said "investigating"
  - if no response by apr 1, escalate or just spin up replacement on different provider
- [ ] cowrie.json rotation sometimes leaves empty file (seen twice in feb)
  - cleanup.sh handles it but should fix root cause
  - might be docker log driver config

## medium
- [ ] move exports to S3 instead of local disk
  - sarah started on this (see s3_export_draft.py) but parked it
  - need to figure out IAM role vs access key
- [ ] add CSV export format to weekly cron (mkaur asked for this for her spreadsheet)
- [ ] grafana alerting — currently only slack, should have grafana rules too
  - low effort but keeps getting pushed

## low / someday
- [x] ~~fix timezone in export_sessions.py~~ (mkaur fixed, 2026-03-05)
- [x] ~~htop shows wrong container count~~ (fixed when we added collector)
- [ ] write proper docs for sensor enrollment process
  - deploy_sensor.sh works but nobody except sarah knows the full flow
- [ ] investigate if we can run dionaea alongside cowrie
  - would give us SMB/FTP captures
  - worry: resource usage on the 4GB VPS boxes
- [ ] automate sensor_registry.json updates from heartbeats
  - currently manual — sarah updates status by hand
