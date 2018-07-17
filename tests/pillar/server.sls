gitlab:
  server:
    enabled: true
    server_name: 'repo1.domain.com'
    source:
      engine: pkg
    database:
      engine: 'postgresql'
      host: 'locslhost'
      name: 'gitlab'
      password: 'LfTno5mYdZmRfoPV'
      user: 'gitlab'
    mail:
      engine: 'smtp'
      host: 'localhost'
      port: 25
      domain: 'domain.com'
      use_tls: false
      from: 'gitlab@domain.com'
      no_reply: 'no-reply@domain.com'