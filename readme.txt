人工智能合作组织成员承诺履约证据台

运行验收：
python3 -m treaty_tracker run --fixture fixtures/acceptance.json --database /tmp/treaty_tracker.sqlite3 --output /tmp/treaty_tracker-output

核验：
python3 -m treaty_tracker verify --database /tmp/treaty_tracker.sqlite3 --output /tmp/treaty_tracker-output

输出目录中的 trend-analysis.json 为冻结的可比趋势分析（按成员、承诺领域、提交期间），
其哈希登记在 manifest.json 中；verify 会沿证据事件链与 record_versions 审查该报告，
旧报告只被核对、不会被重算。缺少跨期共同事项时 improvement_rate 保持 null，不做推算。

全量测试：
python3 -m unittest discover -s tests -v

按模块测试：
python3 -m unittest tests.progress_signal.test_commitment_health -v
python3 -m unittest tests.trends.test_comparable_trends -v

构建检查：
python3 -m compileall -q treaty_tracker tests
