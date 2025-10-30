<?php
// PHP Proxy for FirstPerson FastAPI Application
header('Content-Type: text/html; charset=utf-8');

// Get the request URI and method
$request_uri = $_SERVER['REQUEST_URI'];
$request_method = $_SERVER['REQUEST_METHOD'];

// FastAPI server details
$fastapi_host = '127.0.0.1';
$fastapi_port = '8000';
$fastapi_url = "http://{$fastapi_host}:{$fastapi_port}";

// Check if FastAPI server is running
$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, $fastapi_url);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_TIMEOUT, 5);
curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, 5);
curl_setopt($ch, CURLOPT_NOBODY, true);

$server_running = curl_exec($ch);
$http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
curl_close($ch);

if ($server_running === false || $http_code !== 200) {
    echo "<h1>FirstPerson Chat - Server Status</h1>";
    echo "<p><strong>FastAPI Server Status:</strong> Not Running</p>";
    echo "<p><strong>Expected URL:</strong> {$fastapi_url}</p>";
    echo "<p><strong>HTTP Code:</strong> {$http_code}</p>";
    echo "<p>Please start the FastAPI server using:</p>";
    echo "<pre>nohup python3 -m uvicorn fastapi_app:app --host 127.0.0.1 --port 8000 > app.log 2>&1 &</pre>";
    exit;
}

// If server is running, proxy the request
$proxy_url = $fastapi_url . $request_uri;

$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, $proxy_url);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true);
curl_setopt($ch, CURLOPT_TIMEOUT, 30);

// Handle different HTTP methods
if ($request_method === 'POST') {
    curl_setopt($ch, CURLOPT_POST, true);
    curl_setopt($ch, CURLOPT_POSTFIELDS, file_get_contents('php://input'));
}

// Forward headers
$headers = [];
foreach ($_SERVER as $key => $value) {
    if (strpos($key, 'HTTP_') === 0) {
        $header = str_replace(' ', '-', ucwords(str_replace('_', ' ', strtolower(substr($key, 5)))));
        if ($header !== 'Host') {
            $headers[] = $header . ': ' . $value;
        }
    }
}
curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);

$response = curl_exec($ch);
$content_type = curl_getinfo($ch, CURLINFO_CONTENT_TYPE);
$http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);

// Set the content type
if ($content_type) {
    header('Content-Type: ' . $content_type);
}

http_response_code($http_code);
curl_close($ch);

echo $response;
?>