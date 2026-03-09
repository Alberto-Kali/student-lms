FROM haskell:9.14-bookworm AS build

WORKDIR /build
COPY stack.yaml package.yaml ./
COPY src ./src

# Network to Hackage can be flaky in CI; retry build a few times.
RUN stack setup \
 && n=0 \
 && until [ "$n" -ge 3 ]; do \
      stack build --copy-bins --install-ghc --local-bin-path /out && break; \
      n=$((n+1)); \
      echo "stack build failed, retry $n/3"; \
      sleep 15; \
    done \
 && [ -x /out/haskell-backend ]

FROM debian:bookworm-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY --from=build /out/haskell-backend /usr/local/bin/haskell-backend
EXPOSE 8080
CMD ["haskell-backend"]
