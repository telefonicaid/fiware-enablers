class test::install($version='default_version'){

  notify {"test":}

  $custom_att_01=hiera('test', 'att1')
  $custom_att_02=hiera('test', 'att2')

  file {"test_puppet":
          path => "/tmp/test_puppet",
          ensure => present,
          mode => 0640,
          content => "Operation: install; Product: test-att-01; Version: ${version}; Att01: ${custom_att_01}; Att02: ${custom_att_02}"
  }
}
