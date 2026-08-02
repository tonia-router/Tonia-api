# tonia-api — OpenAPI contract + SDK client regeneration
IMAGE ?= openapitools/openapi-generator-cli:v7.14.0
export OPENAPI_GENERATOR_IMAGE := $(IMAGE)

.PHONY: check smoke generate generate-sdk clean-smoke secrets api-ref

check:
	python3 check_public_openapi.py
	python3 check_public_secrets.py

secrets:
	python3 check_public_secrets.py

api-ref:
	python3 render_api_reference.py

smoke: check
	./generate.sh

generate: smoke

generate-sdk: check
	./generate.sh --sdk-repos

clean-smoke:
	rm -rf ../.codegen-smoke
