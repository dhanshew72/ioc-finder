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
build: clean-build
	mkdir -p build/package
	$(ACTIVATE_VENV); pip install -r requirements.txt -t build/package
	cp -r . build/package/src
	cd build && zip -r package.zip package && cd ..

.PHONY: clean-build
clean-build:
	rm -rf build

.PHONY: deploy
deploy: build
	aws s3 cp build/package.zip s3://ioc-deploy/extraction/package.zip
