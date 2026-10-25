<?php
declare(strict_types=1);

/*
 * POST-only protected endpoint.
 *
 * Render Environment Variables:
 *   PASSPHRASE = long random secret shared with the client encryption code
 *   SITE_URL   = (optional) your existing website URL, e.g. https://example.com/
 *
 * Expected JSON POST:
 *   {"iv":"BASE64","cipher":"BASE64","tag":"BASE64"}
 *
 * AES-256-GCM key = SHA-256(PASSPHRASE)
 * Decrypted JSON example: {"action":"LOAD","ts":UNIX_SECONDS}
 */

header('Cache-Control: no-store, max-age=0');
header('X-Content-Type-Options: nosniff');

function respond(int $status, array $body): never {
    http_response_code($status);
    header('Content-Type: application/json; charset=utf-8');
    echo json_encode($body, JSON_UNESCAPED_SLASHES);
    exit;
}

if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') {
    header('Allow: POST');
    respond(405, ['ok' => false, 'error' => 'POST required']);
}

$passphrase = getenv('PASSPHRASE');
if ($passphrase === false || trim($passphrase) === '') {
    error_log('PASSPHRASE environment variable is not configured');
    respond(503, ['ok' => false, 'error' => 'Server configuration error']);
}

$contentType = strtolower(trim(explode(';', $_SERVER['CONTENT_TYPE'] ?? '')[0]));
if ($contentType !== 'application/json') {
    respond(415, ['ok' => false, 'error' => 'Content-Type must be application/json']);
}

$raw = file_get_contents('php://input');
if ($raw === false || strlen($raw) > 16384) {
    respond(413, ['ok' => false, 'error' => 'Invalid request size']);
}

$req = json_decode($raw, true);
if (!is_array($req) || !isset($req['iv'], $req['cipher'], $req['tag']) ||
    !is_string($req['iv']) || !is_string($req['cipher']) || !is_string($req['tag'])) {
    respond(400, ['ok' => false, 'error' => 'Invalid encrypted request']);
}

$iv = base64_decode($req['iv'], true);
$ciphertext = base64_decode($req['cipher'], true);
$tag = base64_decode($req['tag'], true);

if ($iv === false || strlen($iv) !== 12 ||
    $ciphertext === false || strlen($ciphertext) > 8192 ||
    $tag === false || strlen($tag) !== 16) {
    respond(400, ['ok' => false, 'error' => 'Invalid encrypted fields']);
}

$key = hash('sha256', $passphrase, true);
$plaintext = openssl_decrypt(
    $ciphertext,
    'aes-256-gcm',
    $key,
    OPENSSL_RAW_DATA,
    $iv,
    $tag
);

if ($plaintext === false) {
    respond(403, ['ok' => false, 'error' => 'POST verification failed']);
}

$payload = json_decode($plaintext, true);
if (!is_array($payload) || ($payload['action'] ?? '') !== 'LOAD' ||
    !isset($payload['ts']) || !is_numeric($payload['ts'])) {
    respond(403, ['ok' => false, 'error' => 'Invalid verified payload']);
}

$now = time();
$ts = (int)$payload['ts'];
if (abs($now - $ts) > 120) {
    respond(403, ['ok' => false, 'error' => 'Request expired; retry']);
}

/*
 * Verification succeeded. If SITE_URL is configured, redirecting would
 * lose the authenticated POST flow in many clients. Return the destination
 * in JSON instead; the app can then load the existing site as a separate step.
 */
$siteUrl = getenv('SITE_URL');
if ($siteUrl !== false && filter_var($siteUrl, FILTER_VALIDATE_URL) &&
    in_array(parse_url($siteUrl, PHP_URL_SCHEME), ['https'], true)) {
    respond(200, ['ok' => true, 'verified' => true, 'site_url' => $siteUrl]);
}

respond(200, [
    'ok' => true,
    'verified' => true,
    'message' => 'POST verified successfully. Set SITE_URL in Render to return your existing website URL.'
]);
