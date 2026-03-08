FROM commercialhaskell/stack:2.15.7 AS build
WORKDIR /app
COPY stack.yaml package.yaml ./
COPY src ./src
RUN stack build --copy-bins --local-bin-path /app/bin

FROM debian:bookworm-slim
WORKDIR /app
COPY --from=build /app/bin/haskell-backend ./haskell-backend
EXPOSE 8080
CMD ["./haskell-backend"]
