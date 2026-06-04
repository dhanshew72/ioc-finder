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


.PHONY: build
build:
	docker build -t ioc-finder-app .

.PHONY: deploy
deploy: build
	docker tag ioc-finder-app:latest 515504445954.dkr.ecr.us-east-1.amazonaws.com/ioc-finder-app:latest
	docker push 515504445954.dkr.ecr.us-east-1.amazonaws.com/ioc-finder-app:latest
