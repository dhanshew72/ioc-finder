ACTIVATE_VENV=. .venv/bin/activate

.PHONY: dev-env
dev-env: clean
	python3 -m venv .venv
	$(ACTIVATE_VENV); pip3 install -r requirements-dev.txt

.PHONY: clean
clean:
	rm -rf .venv

.PHONY: test
test:
	$(ACTIVATE_VENV); pytest -c setup.cfg --cov-report term-missing
