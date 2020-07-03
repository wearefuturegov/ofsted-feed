Place your Ofsted certificate and credential in this folder. You will need to generate the following files:

 * `privkey.pem`
 * `pubkey.pem`
 * `username.txt`: 1-line file containing the username
 * `password.txt`: 1-line file containing the password

The content of these should look something like this for `privkey.pem`:

    -----BEGIN RSA PRIVATE KEY-----
    [base64 content]
    -----END RSA PRIVATE KEY-----

and this for `pubkey.pem`:

    -----BEGIN PUBLIC KEY-----
    [base64 content]
    -----END PUBLIC KEY-----


