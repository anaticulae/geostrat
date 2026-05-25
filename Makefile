.PHONY: docker-build docker-run build clean

VERSION := $(shell git rev-parse --short HEAD 2>/dev/null || echo "latest")
CURDIR := $(CURDIR)

NAME = geostrat
IMAGE := $(NAME):$(VERSION)
IMAGE_BASE := ghcr.io/anaticulae/$(IMAGE)

docker-build:
	docker build -t $(IMAGE_BASE) .

docker-upload:
	docker push $(IMAGE_BASE)

docker-doctest: docker-build
	docker run -v $(CURDIR):/var/workdir\
			-v /tmp/power:/tmp/power\
			$(IMAGE_BASE) "baw test docs"

docker-fasttest: docker-build
	docker run -v $(CURDIR):/var/workdir\
			-v /tmp/power:/tmp/power\
			$(IMAGE_BASE) "baw test fast"

docker-longtest: docker-build
	docker run -v $(CURDIR):/var/workdir\
			-v /tmp/power:/tmp/power\
			$(IMAGE_BASE) "baw test long"

docker-alltest: docker-build
	docker run -v $(CURDIR):/var/workdir\
			-v /tmp/power:/tmp/power\
			$(IMAGE_BASE) "baw test all"

docker-lint: docker-build
	docker run -v $(CURDIR):/var/workdir $(IMAGE_BASE) "baw lint all"

docker-decrypt: docker-build
	docker run -v $(CURDIR):/var/workdir\
			-v /tmp/power:/tmp/power\
			-e HOVERPOWER_STORE=/var/workdir/hoverpower/repo\
			-e HOVERPOWER_SECRET=$(HOVERPOWER_SECRET)\
			$(IMAGE_BASE) "powerdecrypt"

docker-release: docker-build
	docker run -v $(CURDIR):/var/workdir\
			-e GH_TOKEN=$(GH_TOKEN) $(IMAGE_BASE)\
			"baw release --no_test --no_linter"
