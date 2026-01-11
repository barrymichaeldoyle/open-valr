const http = require("http");
const https = require("https");
const { createProxyServer } = require("http-proxy");

const TARGET = "https://api.valr.com";

const proxy = createProxyServer({
  target: TARGET,
  changeOrigin: true,
  secure: true,
  agent: new https.Agent({ keepAlive: true }),
});

// clean headers just before the request leaves for VALR
proxy.on("proxyReq", (proxyReq) => {
  proxyReq.setHeader("Host", "api.valr.com");
  proxyReq.setHeader("Accept", "application/json");
  proxyReq.setHeader("User-Agent", "curl/8.0.0");
});

// error handler
proxy.on("error", (err, req, res) => {
  console.error("Proxy error:", err.message);
  if (!res.headersSent) {
    res.writeHead(500, { "Content-Type": "application/json" });
  }
  res.end(JSON.stringify({ error: "Proxy error", detail: err.message }));
});

http
  .createServer((req, res) => {
    // add CORS headers for Swagger / browser testing
    res.setHeader("Access-Control-Allow-Origin", "*");
    res.setHeader(
      "Access-Control-Allow-Methods",
      "GET, POST, PUT, DELETE, OPTIONS"
    );
    res.setHeader("Access-Control-Allow-Headers", "*");
    if (req.method === "OPTIONS") return res.end();
    proxy.web(req, res);
  })
  .listen(8082, () => {
    console.log("✅ Lightweight proxy running → http://localhost:8082");
  });
