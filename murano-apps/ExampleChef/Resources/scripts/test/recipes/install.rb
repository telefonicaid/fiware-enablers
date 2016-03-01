script "install" do
  interpreter "bash"
  user "root"
  cwd "/tmp"
  code <<-EOH
  echo "Operation: install; Product: #{node['test']['att1']}; Version: 0.0.1; Att01: #{node['test']['att1']}; Att02: #{node['test']['att2']}" > #{node['test']['att2']}_0.0.1_chef
  EOH
end
