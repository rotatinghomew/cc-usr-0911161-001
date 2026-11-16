人工智能合作组织成员承诺履约证据台

运行验收：
python3 -m treaty_tracker run --fixture fixtures/acceptance.json --database /tmp/treaty_tracker.sqlite3 --output /tmp/treaty_tracker-output

核验：
python3 -m treaty_tracker verify --database /tmp/treaty_tracker.sqlite3 --output /tmp/treaty_tracker-output

全量测试：
python3 -m unittest discover -s tests -v

按模块测试：
python3 -m unittest tests.progress_signal.test_commitment_health -v

构建检查：
python3 -m compileall -q treaty_tracker tests
