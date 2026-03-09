{-# LANGUAGE DataKinds #-}
{-# LANGUAGE TypeOperators #-}

module Main where

import Network.Wai (Application)
import Network.Wai.Handler.Warp (run)
import Servant

type Api = "health" :> Get '[JSON] String

server :: Server Api
server = pure "ok:haskell-servant"

api :: Proxy Api
api = Proxy

app :: Application
app = serve api server

main :: IO ()
main = run 8080 app
