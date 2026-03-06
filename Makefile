.PHONY: setup demo demo-offline test test-demo test-production clean

setup:
	python3 -m venv .venv
	. .venv/bin/activate && pip install -r requirements.txt

demo:
	. .venv/bin/activate && python pipelines/pipeline.py

demo-offline:
	python3 pipelines/pipeline_demo.py

test:
	$(MAKE) test-demo

test-demo:
	TEST_MODE=demo python3 tests/run_tests.py

test-production:
	TEST_MODE=production PRODUCTION_TESTS_CONFIRM=1 python3 tests/run_tests.py

clean:
	rm -rf .venv data/processed
