
image:

	@docker build -t luisalejandro/tweet-random-post-from-feed:latest .

tweet:

	@docker run -it --rm -u luisalejandro --env-file .env \
		-v $(PWD):/home/luisalejandro/tweet-random-post-from-feed \
		-w /home/luisalejandro/tweet-random-post-from-feed \
		luisalejandro/tweet-random-post-from-feed:latest python entrypoint.py

console:

	@docker run -it --rm -u luisalejandro --env-file .env \
		-v $(PWD):/home/luisalejandro/tweet-random-post-from-feed \
		-w /home/luisalejandro/tweet-random-post-from-feed \
		luisalejandro/tweet-random-post-from-feed:latest bash
