$PASSPHRASE = getenv('CRAVAULT_PASSPHRASE');

if ($PASSPHRASE === false || strlen($PASSPHRASE) < 32) {
    http_response_code(500);
    exit('Server configuration error');
}

$key = hash('sha256', $PASSPHRASE, true);
