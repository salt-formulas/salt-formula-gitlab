gitlab:
  client:
    enabled: true
    server:
      url: http:/repo.domain.com/
      token: fdsfdsfdsfdsfds
    group:
      hovno53:
        enabled: true
        description: some tex2
    repository:
      name-space/repo-name:
        enabled: true
        import_url: https://repo01.domain.com/namespace/repo.git
        description: Repo description
        deploy_key:
          keyname:
            enabled: true
            key: public_part_of_ssh_key