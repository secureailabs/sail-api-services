.PHONY: clean sail_client build_image

build_image:
	@./scripts.sh build_image apiservices

push_image: build_image
	@../scripts.sh push_image_to_registry apiservices

clean:
	@rm -rf Binary
